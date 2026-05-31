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
    python -m ocr.trainer train --backend cnn --data data/ --output ocr/cnn_model.onnx --epochs 1 --batch-size 256

    # CNN data fix
    python -m ocr.trainer train --backend cnn --data datafix/ --output ocr/cnn_model_fix.onnx --epochs 1 --batch-size 256
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
    """从 data_dir/{label}/ 加载所有样本，返回 (features, labels)。
    features 为展平的二值向量（KNN 用）。
    """
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


def _load_dataset_grayscale(data_dir: str) -> tuple[np.ndarray, np.ndarray]:
    """从 data_dir/{label}/ 加载所有样本，返回 (features, labels)。
    features 为 (N, 1, H, W) 灰度值，归一化到 [0,1]（CNN 用）。
    """
    data_path = Path(data_dir)
    h, w = CHAR_SIZE[1], CHAR_SIZE[0]
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
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, CHAR_SIZE)
            features.append(gray)
            labels.append(label_idx)

    x = np.array(features, dtype=np.float32).reshape(-1, 1, h, w) / 255.0
    return x, np.array(labels, dtype=np.int32)


# ------------------------------------------------------------------
# 训练 KNN
# ------------------------------------------------------------------

def train_knn(data_dir: str, model_output: str, *args, **kwargs):
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

    # 全量准确率验证（留一法）
    correct = 0
    error_list = []
    x = np.array(features, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    for i in range(len(x)):
        if i % 50 == 0:
            logger.info("验证中: %d/%d", i, len(x))
        dists = np.sum((x - x[i]) ** 2, axis=1)
        dists[i] = np.inf
        nearest = np.argmin(dists)
        pred_i = y[nearest]
        if pred_i == y[i]:
            correct += 1
        else:
            error_list.append((i, LABELS[pred_i], LABELS[y[i]]))
    acc = correct / len(y) if len(y) else 0
    logger.info("KNN 准确率: %d/%d = %.2f%%", correct, len(y), acc * 100)
    if error_list:
        logger.info("分类错误: %s", "  ".join(f"{i}:pred={p} true={t}" for i, p, t in error_list[:20]))
        if len(error_list) > 20:
            logger.info("  ... 共 %d 个错误", len(error_list))


# ------------------------------------------------------------------
# 导出模板（用于模板匹配分类器）
# ------------------------------------------------------------------

def export_templates(data_dir: str, output_dir: str, *args, **kwargs):
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

def train_cnn(data_dir: str, model_output: str, epochs: int = 20, batch_size: int = 64):
    """训练简单 CNN 并导出为 ONNX。

    需要安装: pip install torch onnx onnxruntime
    """
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        logger.error("PyTorch 未安装，CNN 训练不可用。pip install torch")
        return

    features, labels = _load_dataset_grayscale(data_dir)
    if len(features) == 0:
        logger.error("未找到任何训练样本")
        return

    class SimpleCNN(nn.Module):
        def __init__(self, num_classes: int = len(LABELS)):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 16, 3, padding=1)
            self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
            self.pool = nn.MaxPool2d(2, 2)
            self.dropout = nn.Dropout(0.3)
            self.fc1 = nn.Linear(32 * (CHAR_SIZE[1]//4) * (CHAR_SIZE[0]//4), 512)
            self.fc2 = nn.Linear(512, num_classes)

        def forward(self, x):
            x = self.pool(torch.relu(self.conv1(x)))
            x = self.pool(torch.relu(self.conv2(x)))
            x = x.view(x.size(0), -1)
            x = torch.relu(self.fc1(x))
            x = self.dropout(x)
            x = self.fc2(x)
            return x

    h, w = CHAR_SIZE[1], CHAR_SIZE[0]
    x_tensor = torch.tensor(features, dtype=torch.float32)
    y_tensor = torch.tensor(labels, dtype=torch.long)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("训练设备: %s", device)

    model = SimpleCNN()
    model.to(device)
    weights_path = Path(model_output).with_suffix(".pt")

    if weights_path.exists():
        model.load_state_dict(torch.load(str(weights_path), weights_only=True, map_location=device))
        logger.info("从已有权重继续训练: %s", weights_path)
    else:
        logger.info("从头开始训练")
    lr = 0.0004 if weights_path.exists() else 0.001
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    dataset = TensorDataset(x_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)

    print(f"{'Epoch':>6}  {'Loss':>8}  {'Acc':>8}")
    print("-" * 24)

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        epoch_correct = 0
        epoch_total = 0
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch_x.size(0)
            pred = output.argmax(dim=1)
            epoch_correct += (pred == batch_y).sum().item()
            epoch_total += batch_x.size(0)
        avg_loss = epoch_loss / epoch_total
        acc = epoch_correct / epoch_total
        print(f"{epoch:6d}  {avg_loss:8.4f}  {acc:8.3f}")

    # 导出 ONNX
    model.eval().to("cpu")
    model_path = Path(model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.randn(1, 1, h, w)
    torch.onnx.export(model, dummy, str(model_path),
                       input_names=["input"], output_names=["output"],
                       dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}})
    logger.info("CNN 模型已导出 ONNX: %s", model_path)

    # 保存权重供续训
    torch.save(model.state_dict(), str(weights_path))
    logger.info("CNN 权重已保存: %s", weights_path)

    # 显示所有分类错误的图片
    x_cpu = x_tensor.to("cpu")
    y_cpu = y_tensor.to("cpu")
    with torch.no_grad():
        output = model.to("cpu")(x_cpu)
        preds = output.argmax(dim=1).numpy()
    gt_arr = labels
    errors = [(i, preds[i], gt) for i, gt in enumerate(gt_arr) if preds[i] != gt]
    if not errors:
        logger.info("全部正确，无错误图片")
        return

    cols = min(len(errors), 4)
    tile_h, tile_w = CHAR_SIZE[0] * 5, CHAR_SIZE[1] * 5
    rows = (len(errors) + cols - 1) // cols
    grid = np.zeros((rows * tile_h, cols * tile_w, 3), dtype=np.uint8) + 40
    for idx, (sample_idx, pred, gt_label) in enumerate(errors):
        r, c = idx // cols, idx % cols
        img = (features[sample_idx].reshape(h, w) * 255).astype(np.uint8)
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        resized = cv2.resize(img_color, (tile_w, tile_h))
        pred_label = LABELS[pred] if pred < len(LABELS) else "?"
        true_label = LABELS[gt_label]
        y0, x0 = r * tile_h, c * tile_w
        grid[y0:y0+tile_h, x0:x0+tile_w] = resized
        cv2.rectangle(grid, (x0, y0), (x0+tile_w, y0+40), (0, 0, 255), -1)
        cv2.putText(grid, f"pred={pred_label} true={true_label}", (x0+8, y0+28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    win_name = f"错误分类 ({len(errors)}/{len(gt_arr)})"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.imshow(win_name, grid)
    save_path = Path(model_output).with_suffix(".errors.png")
    cv2.imwrite(str(save_path), grid)
    logger.info("错误图片已保存: %s", save_path)
    logger.info("显示 %d 个错误样本，按任意键关闭...", len(errors))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ------------------------------------------------------------------
# 训练 HOG + SVM
# ------------------------------------------------------------------

def train_hog_svm(data_dir: str, model_output: str, *args, **kwargs):
    """提取 HOG 特征 + 训练 SVM，保存为 pickle。"""
    data_path = Path(data_dir)
    h, w = CHAR_SIZE[1], CHAR_SIZE[0]
    win_size = (w, h)
    block_size = (16, 16)
    block_stride = (8, 8)
    cell_size = (8, 8)
    nbins = 9
    hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins)

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
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, win_size)
            feat = hog.compute(gray).flatten()
            features.append(feat)
            labels.append(label_idx)

    if len(features) == 0:
        logger.error("未找到任何训练样本")
        return

    x = np.array(features, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    svm = cv2.ml.SVM_create()
    svm.setType(cv2.ml.SVM_C_SVC)
    svm.setKernel(cv2.ml.SVM_RBF)
    svm.setC(12.5)
    svm.setGamma(0.5)
    svm.train(x, cv2.ml.ROW_SAMPLE, y)

    model_path = Path(model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    svm.save(str(model_path))
    logger.info("HOG+SVM 模型已保存: %s (%d 样本)", model_path, len(labels))

    _, result = svm.predict(x)
    preds = result.flatten().astype(np.int32)
    correct = int((preds == y).sum())
    acc = correct / len(y) if len(y) else 0
    error_list = [(i, LABELS[int(preds[i])], LABELS[int(y[i])]) for i in range(len(y)) if preds[i] != y[i]]
    logger.info("HOG+SVM 准确率: %d/%d = %.2f%%", correct, len(y), acc * 100)
    if error_list:
        logger.info("分类错误: %s", "  ".join(f"{i}:pred={p} true={t}" for i, p, t in error_list[:20]))
        if len(error_list) > 20:
            logger.info("  ... 共 %d 个错误", len(error_list))


# ------------------------------------------------------------------
# CLI 入口
# ------------------------------------------------------------------

_TRAIN_BACKENDS = {
    "knn":      train_knn,
    "template":  export_templates,
    "cnn":       train_cnn,
    "hog_svm":   train_hog_svm,
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
    p_train.add_argument("--epochs", type=int, default=20, help="CNN 训练轮数（仅对 CNN 后端有效）")
    p_train.add_argument("--batch-size", type=int, default=64, help="CNN mini-batch 大小（仅对 CNN 后端有效）")
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
            "hog_svm": "ocr/hog_svm_model.pkl",
        }[args.backend]
        _TRAIN_BACKENDS[args.backend](args.data, output, args.epochs, args.batch_size)
    else:
        parser.print_help()