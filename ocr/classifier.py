"""字符分类器 —— 支持 KNN / CNN / 模板匹配，可配置选择

字符集（共 24 类）：
    R  R' R2 R2'
    U  U' U2 U2'
    F  F' F2 F2'
    D  D' D2 D2'
    B  B' B2 B2'
    L  L' L2 L2'

用法：
    # KNN
    clf = create_classifier("knn", model_path="ocr/knn_model.pkl")

    # 模板匹配
    clf = create_classifier("template", templates_dir="ocr/templates/")

    # CNN
    clf = create_classifier("cnn", model_path="ocr/cnn_model.onnx")

    # 配置文件驱动
    clf = create_classifier.from_config({"type": "knn", "model_path": "..."})
"""
import logging
import pickle
from abc import ABC, abstractmethod
from pathlib import Path

import cv2
import numpy as np

from ocr.segmentor import CHAR_SIZE

logger = logging.getLogger(__name__)

# 支持的全部类别（有序，与训练数据标签对齐）
LABELS = [
    "R", "R'", "R2", "R2'",
    "L", "L'", "L2", "L2'",
    "U", "U'", "U2", "U2'",
    "D", "D'", "D2", "D2'",
    "F", "F'", "F2", "F2'",
    "B", "B'", "B2", "B2'",
    "EMPTY",
]


def _preprocess_flat(img: np.ndarray) -> np.ndarray:
    """BGR 图 → 灰度 + Otsu 二值化 → 展平 float32 向量（KNN / 模板匹配用）。"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary.flatten().astype(np.float32)


# ------------------------------------------------------------------
# 抽象基类
# ------------------------------------------------------------------

class ClassifierBase(ABC):
    """分类器抽象基类，所有后端实现此接口。"""

    @abstractmethod
    def predict(self, char_img: np.ndarray) -> str:
        """预测单个字符图像 → 类别字符串（如 "R'"）。"""

    def predict_batch(self, char_imgs: list[np.ndarray]) -> list[str]:
        """批量预测。"""
        return [self.predict(img) for img in char_imgs]


# ------------------------------------------------------------------
# KNN 后端
# ------------------------------------------------------------------

class KNNClassifier(ClassifierBase):
    """OpenCV KNearest 分类器。

    模型文件为 pickle，包含 {"features": ndarray, "labels": ndarray}。
    """

    def __init__(self, model_path: str | Path):
        self._knn: cv2.ml.KNearest | None = None
        self.load(model_path)

    def load(self, path: str | Path):
        path = Path(path)
        if not path.exists():
            logger.warning("KNN 模型文件不存在: %s", path)
            return
        with open(path, "rb") as f:
            data = pickle.load(f)
        self._knn = cv2.ml.KNearest_create()
        self._knn.train(data["features"], cv2.ml.ROW_SAMPLE, data["labels"])
        logger.info("KNN 模型加载完成: %s (%d 样本)", path, len(data["labels"]))

    def predict(self, char_img: np.ndarray) -> str:
        if self._knn is None:
            return "?"
        feat = _preprocess_flat(char_img).reshape(1, -1)
        _, results, _, _ = self._knn.findNearest(feat, k=3)
        idx = int(results[0][0])
        return LABELS[idx] if 0 <= idx < len(LABELS) else "?"


# ------------------------------------------------------------------
# 模板匹配后端
# ------------------------------------------------------------------

class TemplateClassifier(ClassifierBase):
    """模板匹配分类器：与每类模板图做 cv2.matchTemplate，取最高匹配。

    模板目录结构：
        templates/
        ├── R.png
        ├── R'.png
        ├── R2.png
        ├── R2'.png
        └── ...  (每个 LABELS 对应一个 png)
    """

    def __init__(self, templates_dir: str | Path):
        self._templates: dict[str, np.ndarray] = {}
        self._load_templates(templates_dir)

    def _load_templates(self, dir_path: str | Path):
        dir_path = Path(dir_path)
        if not dir_path.exists():
            logger.warning("模板目录不存在: %s", dir_path)
            return
        for label in LABELS:
            tmpl_path = dir_path / f"{label}.png"
            tmpl = cv2.imread(str(tmpl_path))
            if tmpl is not None:
                tmpl = cv2.resize(tmpl, CHAR_SIZE)
                self._templates[label] = tmpl
        logger.info("模板匹配加载完成: %d / %d 类", len(self._templates), len(LABELS))

    def predict(self, char_img: np.ndarray) -> str:
        if not self._templates:
            return "?"
        img = cv2.resize(char_img, CHAR_SIZE)
        best_label = "?"
        best_score = -1.0
        for label, tmpl in self._templates.items():
            # 模板尺寸与输入相同，matchTemplate 需要至少 1x1 像素差异
            # 用滑窗方式在全尺寸图上做匹配（此处两者尺寸相同，直接比较）
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray_tmpl = cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray_img, gray_tmpl, cv2.TM_CCOEFF_NORMED)
            score = result[0][0]
            if score > best_score:
                best_score = score
                best_label = label
        return best_label


# ------------------------------------------------------------------
# CNN 后端（ONNX Runtime）
# ------------------------------------------------------------------

class CNNClassifier(ClassifierBase):
    """ONNX Runtime 推理分类器。

    模型输入：CHAR_SIZE 灰度图，归一化到 [0, 1]，shape (1, 1, H, W)
    模型输出：softmax logits，shape (1, num_classes)
    """

    def __init__(self, model_path: str | Path):
        self._session = None
        self._load(model_path)

    def _load(self, path: str | Path):
        try:
            import onnxruntime as ort
        except ImportError:
            logger.warning("onnxruntime 未安装，CNN 分类器不可用。pip install onnxruntime")
            return
        path = Path(path)
        if not path.exists():
            logger.warning("CNN 模型文件不存在: %s", path)
            return
        self._session = ort.InferenceSession(str(path))
        logger.info("CNN 模型加载完成: %s", path)

    def predict(self, char_img: np.ndarray) -> str:
        if self._session is None:
            return "?"
        gray = cv2.cvtColor(char_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, CHAR_SIZE)
        input_arr = gray.astype(np.float32) / 255.0
        input_arr = input_arr.reshape(1, 1, CHAR_SIZE[1], CHAR_SIZE[0])

        input_name = self._session.get_inputs()[0].name
        output = self._session.run(None, {input_name: input_arr})
        idx = int(np.argmax(output[0]))
        return LABELS[idx] if 0 <= idx < len(LABELS) else "?"


# ------------------------------------------------------------------
# 工厂函数
# ------------------------------------------------------------------

_BACKEND_MAP = {
    "knn":      KNNClassifier,
    "template":  TemplateClassifier,
    "cnn":       CNNClassifier,
}


def create_classifier(config: dict) -> ClassifierBase:
    """根据配置字典创建分类器实例。

    config 格式：
        {"type": "knn",      "model_path": "ocr/knn_model.pkl"}
        {"type": "template",  "templates_dir": "ocr/templates/"}
        {"type": "cnn",       "model_path": "ocr/cnn_model.onnx"}
    """
    backend_type = config.get("type", "knn")
    cls = _BACKEND_MAP.get(backend_type)
    if cls is None:
        raise ValueError(f"未知的分类器类型: {backend_type}，可选: {list(_BACKEND_MAP.keys())}")

    if backend_type == "knn":
        return cls(model_path=config.get("model_path", "ocr/knn_model.pkl"))
    elif backend_type == "template":
        return cls(templates_dir=config.get("templates_dir", "ocr/templates/"))
    elif backend_type == "cnn":
        return cls(model_path=config.get("model_path", "ocr/cnn_model.onnx"))


if __name__ == "__main__":
    """单独测试：python -m ocr.classifier <image.png> [--backend knn|template|cnn] [--model path]

    对单张字符图（已裁剪到 CHAR_SIZE）进行分类预测。

    示例：
        python -m ocr.classifier char.png --backend knn --model ocr/knn_model.pkl
        python -m ocr.classifier char.png --backend template --model ocr/templates/
    """
    import sys
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="字符图路径")
    parser.add_argument("--backend", default="knn", choices=["knn", "template", "cnn"])
    parser.add_argument("--model", default=None, help="模型路径（knn=.pkl, cnn=.onnx, template=目录）")
    args = parser.parse_args()

    img = cv2.imread(args.image)
    if img is None:
        print(f"无法读取图片: {args.image}")
        sys.exit(1)

    img = cv2.resize(img, CHAR_SIZE)

    config = {"type": args.backend}
    if args.model:
        if args.backend == "template":
            config["templates_dir"] = args.model
        else:
            config["model_path"] = args.model

    clf = create_classifier(config)
    label = clf.predict(img)
    print(f"预测结果: {label}")
    cv2.imshow(f"input → {label}", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()