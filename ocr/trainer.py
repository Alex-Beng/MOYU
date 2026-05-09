"""训练数据收集 & 模型训练入口

支持三种后端：KNN、CNN、模板匹配

样本目录结构：
    data/
    ├── R/        ← 每个文件夹名即为标签
    │   ├── 001.png
    │   └── ...
    ├── R'/
    ├── R2/
    └── ...

训练流程：
    # 采集样本
    python -m ocr.trainer collect --video tests/scramble.mp4 --output data/

    # 训练 KNN
    python -m ocr.trainer train --backend knn --data data/ --output ocr/knn_model.pkl

    # 导出模板（用于模板匹配分类器）
    python -m ocr.trainer train --backend template --data data/ --output ocr/templates/

    # 训练 CNN → ONNX
    python -m ocr.trainer train --backend cnn --data data/ --output ocr/cnn_model.onnx
"""
import argparse
import logging
import pickle
from pathlib import Path

import cv2
import numpy as np

from ocr.classifier import LABELS
from ocr.segmentor import CHAR_SIZE, segment

logger = logging.getLogger(__name__)


def _preprocess_flat(img: np.ndarray) -> np.ndarray:
    """BGR → 灰度 + Otsu → 展平 float32（KNN 用）。"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary.flatten().astype(np.float32)


# ------------------------------------------------------------------
# 样本采集（通用，与后端无关）
# ------------------------------------------------------------------

def collect_from_video(video_path: str, output_dir: str):
    """从视频逐帧分割圆形气泡，交互标注类别。"""
    output = Path(output_dir)
    for label in LABELS:
        (output / label).mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % 5 != 0:
            continue

        chars = segment(frame)
        for char_img, (cx, cy, r) in chars:
            cv2.imshow("label_me", char_img)
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return
            if key == ord('s'):
                continue
            # 按序号 0-23 映射到 LABELS
            if ord('0') <= key <= ord('9'):
                idx = key - ord('0')
                if idx < len(LABELS):
                    label = LABELS[idx]
                    save_path = output / label / f"{frame_idx}_{cx}_{cy}.png"
                    cv2.imwrite(str(save_path), char_img)
                    logger.info("保存: %s", save_path)

    cap.release()
    cv2.destroyAllWindows()


def collect_from_images(images_dir: str, output_dir: str):
    """从已有截图（png/jpg）逐帧分割圆形气泡，交互标注。"""
    output = Path(output_dir)
    for label in LABELS:
        (output / label).mkdir(parents=True, exist_ok=True)

    img_dir = Path(images_dir)
    for img_path in sorted(img_dir.glob("*.png") + img_dir.glob("*.jpg")):
        frame = cv2.imread(str(img_path))
        if frame is None:
            continue
        chars = segment(frame)
        for char_img, (cx, cy, r) in chars:
            cv2.imshow("label_me", char_img)
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                cv2.destroyAllWindows()
                return
            if key == ord('s'):
                continue
            if ord('0') <= key <= ord('9'):
                idx = key - ord('0')
                if idx < len(LABELS):
                    label = LABELS[idx]
                    save_path = output / label / f"{img_path.stem}_{cx}_{cy}.png"
                    cv2.imwrite(str(save_path), char_img)
                    logger.info("保存: %s", save_path)
    cv2.destroyAllWindows()


# ------------------------------------------------------------------
# 加载样本数据
# ------------------------------------------------------------------

def _load_dataset(data_dir: str) -> tuple[np.ndarray, np.ndarray]:
    """从 data_dir/{label}/ 加载所有样本，返回 (features, labels)。"""
    data_path = Path(data_dir)
    features = []
    labels = []

    for label_idx, label in enumerate(LABELS):
        label_dir = data_path / label
        if not label_dir.exists():
            continue
        imgs = list(label_dir.glob("*.png")) + list(label_dir.glob("*.jpg"))
        logger.info("加载 %s: %d 张", label, len(imgs))
        for img_path in imgs:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            img = cv2.resize(img, CHAR_SIZE)
            feat = _preprocess_flat(img)
            features.append(feat)
            labels.append(label_idx)

    return np.array(features, dtype=np.float32), np.array(labels, dtype=np.int32)


# ------------------------------------------------------------------
# 训练 KNN
# ------------------------------------------------------------------

def train_knn(data_dir: str, model_output: str):
    """训练 KNN 并保存为 pickle。"""
    features, labels = _load_dataset(data_dir)
    if len(features) == 0:
        logger.error("未找到任何训练样本")
        return

    model_path = Path(model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump({"features": features, "labels": labels}, f)
    logger.info("KNN 模型已保存: %s (%d 样本，%d 类)", model_path, len(labels), len(set(labels)))


# ------------------------------------------------------------------
# 导出模板（用于模板匹配分类器）
# ------------------------------------------------------------------

def export_templates(data_dir: str, output_dir: str):
    """从每类样本中选第一张作为模板图，保存到 output_dir/{label}.png。"""
    data_path = Path(data_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    exported = 0
    for label in LABELS:
        label_dir = data_path / label
        if not label_dir.exists():
            continue
        imgs = sorted(label_dir.glob("*.png") + label_dir.glob("*.jpg"))
        if not imgs:
            continue
        # 取第一张作为模板
        src = cv2.imread(str(imgs[0]))
        if src is None:
            continue
        src = cv2.resize(src, CHAR_SIZE)
        dst = output / f"{label}.png"
        cv2.imwrite(str(dst), src)
        exported += 1
        logger.info("导出模板: %s → %s", label, dst)

    logger.info("模板导出完成: %d / %d 类", exported, len(LABELS))


# ------------------------------------------------------------------
# 训练 CNN → ONNX
# ------------------------------------------------------------------

def train_cnn(data_dir: str, model_output: str):
    """训练简单 CNN 并导出为 ONNX。

    需要安装: pip install torch onnx onnxruntime
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        logger.error("PyTorch 未安装，CNN 训练不可用。pip install torch")
        return

    features, labels = _load_dataset(data_dir)
    if len(features) == 0:
        logger.error("未找到任何训练样本")
        return

    # 简单 CNN 定义
    class SimpleCNN(nn.Module):
        def __init__(self, num_classes: int = len(LABELS)):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
            self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
            self.pool = nn.MaxPool2d(2, 2)
            h, w = CHAR_SIZE[1] // 4, CHAR_SIZE[0] // 4
            self.fc1 = nn.Linear(32 * h * w, 64)
            self.fc2 = nn.Linear(64, num_classes)

        def forward(self, x):
            x = self.pool(torch.relu(self.conv1(x)))
            x = self.pool(torch.relu(self.conv2(x)))
            x = x.view(x.size(0), -1)
            x = torch.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    # 构建数据
    # features 是展平的二值图，reshape 回 (N, 1, H, W)
    h, w = CHAR_SIZE[1], CHAR_SIZE[0]
    x = torch.tensor(features.reshape(-1, 1, h, w) / 255.0, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)

    model = SimpleCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 训练
    model.train()
    for epoch in range(20):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        if epoch % 5 == 0:
            logger.info("Epoch %d, Loss: %.4f", epoch, loss.item())

    # 导出 ONNX
    model.eval()
    model_path = Path(model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.randn(1, 1, h, w)
    torch.onnx.export(model, dummy, str(model_path),
                       input_names=["input"], output_names=["output"],
                       dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}})
    logger.info("CNN 模型已导出 ONNX: %s", model_path)


# ------------------------------------------------------------------
# CLI 入口
# ------------------------------------------------------------------

_TRAIN_BACKENDS = {
    "knn":      train_knn,
    "template":  export_templates,
    "cnn":       train_cnn,
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="OCR 训练工具")
    sub = parser.add_subparsers(dest="cmd")

    # collect
    p_collect = sub.add_parser("collect", help="采集样本")
    p_collect.add_argument("--source", choices=["video", "images"], default="video")
    p_collect.add_argument("--input", required=True, help="视频路径或图片目录")
    p_collect.add_argument("--output", default="data/")

    # train
    p_train = sub.add_parser("train", help="训练/导出模型")
    p_train.add_argument("--backend", choices=list(_TRAIN_BACKENDS.keys()), default="knn")
    p_train.add_argument("--data", default="data/")
    p_train.add_argument("--output", default=None, help="模型输出路径（默认根据 backend 自动选择）")

    args = parser.parse_args()
    if args.cmd == "collect":
        if args.source == "video":
            collect_from_video(args.input, args.output)
        else:
            collect_from_images(args.input, args.output)
    elif args.cmd == "train":
        output = args.output or {
            "knn": "ocr/knn_model.pkl",
            "template": "ocr/templates/",
            "cnn": "ocr/cnn_model.onnx",
        }[args.backend]
        _TRAIN_BACKENDS[args.backend](args.data, output)
    else:
        parser.print_help()