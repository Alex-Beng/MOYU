"""训练数据采集工具 —— 同时服务 OCR 分类器 & UI 模板匹配

两种采集模式，从 scrcpy 实时截图中交互式采集：

  ocr  采集字符样本：截图 → 分割圆形气泡 → 模型预判 → 人工确认/纠正 → 保存到 data/{label}/
       标注完成后若指定 --host，自动解析序列并下发转动到 ESP32
  ui   采集 UI 模板：截图 → 人工框选 ROI → 保存到 templates/

用法：
  # OCR 字符样本采集（无模型辅助）
  python -m tools.collect_training_data ocr --output data/

  # OCR + CNN 辅助打标 + 完成后下发转动
  python -m tools.collect_training_data ocr --model ocr/cnn_model.onnx --host 192.168.50.246

  # UI 模板采集
  python -m tools.collect_training_data ui --output recipe/recipes/templates/

  # 指定设备序列号
  python -m tools.collect_training_data ocr --serial 192.168.1.5:5555
"""

import argparse
import logging
import signal
import time
from pathlib import Path

import cv2
import numpy as np

from device.scrcpy_client import ScrcpyClient
from device.cube_api import CubeAPI, parse_move_notation
from ocr.classifier import LABELS, CNNClassifier, KNNClassifier, HOGSVMClassifier, ClassifierBase
from ocr.parser import parse
from ocr.segmentor import CHAR_SIZE, segment

logger = logging.getLogger(__name__)

_KEY_MAP: dict[int, int] = {}
for i, ch in enumerate("ik,8dec3jfytsla;hgnbwox.z"):
    _KEY_MAP[ord(ch)] = i


def _label_by_key(key: int) -> str | None:
    idx = _KEY_MAP.get(key)
    if idx is not None and idx < len(LABELS):
        return LABELS[idx]
    return None


# ─────────────────────────────────────────────────────────────────
# OCR 模式：截图 → 分割 → 模型辅助标注 → 下发转动
# ─────────────────────────────────────────────────────────────────

def _run_ocr_collect(client: ScrcpyClient, output_dir: str, classifier: ClassifierBase | None = None,
                     cube_host: str | None = None, single_step: bool = False):
    output = Path(output_dir)
    for label in LABELS:
        (output / label).mkdir(parents=True, exist_ok=True)

    cube = None
    if cube_host:
        import asyncio
        cube = CubeAPI(host=cube_host, single_step=single_step)

        async def _open_cube():
            await cube.open()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(_open_cube())
        print(f"ESP32 目标: http://{cube_host}")

    print("\n=== OCR 字符样本采集 ===")
    if classifier:
        print("  模型辅助: CNN 预判, [2]确认  [其他键]纠正")
    print("按键说明:")
    print("  SPACE    截取当前帧并分割字符")
    print("  [i]=R    [k]=R'   [,]=R2   [8]=R2'")
    print("  [d]=L    [e]=L'   [c]=L2   [3]=L2'")
    print("  [j]=U    [f]=U'   [y]=U2   [t]=U2'")
    print("  [s]=D    [l]=D'   [a]=D2   [;]=D2'")
    print("  [h]=F    [g]=F'   [n]=F2   [b]=F2'")
    print("  [w]=B    [o]=B'   [x]=B2   [.]=B2'")
    print("  [z]=EMPTY(空白过滤)")
    print("  [1] 跳过当前字符  [q] 退出")
    print("=" * 50)

    seq = 0

    while True:
        frame = client.last_frame
        if frame is None:
            print("\r等待画面...", end="", flush=True)
            cv2.waitKey(200)
            continue

        cv2.namedWindow("collect_ocr - SPACE截图", cv2.WINDOW_NORMAL)
        cv2.imshow("collect_ocr - SPACE截图", frame)

        key = cv2.waitKey(100) & 0xFF
        if key == ord(' '):
            chars = segment(frame)
            if len(chars) == 0:
                print("\n[错误] 未检测到字符区域")
                continue

            vis = frame.copy()
            for idx, (_, (cx, cy, r)) in enumerate(chars):
                cv2.circle(vis, (cx, cy), r, (0, 255, 0), 2)
                cv2.circle(vis, (cx, cy), 2, (0, 0, 255), -1)
                cv2.putText(vis, str(idx), (cx - 6, cy + 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            overview_win = f"检测到 {len(chars)} 个字符 - 按[空格]重采 [s]标注 [q]退出"
            cv2.namedWindow(overview_win, cv2.WINDOW_NORMAL)
            cv2.imshow(overview_win, vis)

            cols = min(len(chars), 8)
            rows = (len(chars) + cols - 1) // cols
            tile_h, tile_w = CHAR_SIZE[0] * 2, CHAR_SIZE[1] * 2
            grid = np.zeros((rows * tile_h, cols * tile_w, 3), dtype=np.uint8) + 40
            for idx, (char_img, _) in enumerate(chars):
                r, c = idx // cols, idx % cols
                resized = cv2.resize(char_img, (tile_w, tile_h))
                grid[r * tile_h:(r+1) * tile_h, c * tile_w:(c+1) * tile_w] = resized
                cv2.putText(grid, str(idx), (c * tile_w + 4, r * tile_h + 16),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            grid_win = "字符网格 (grid)"
            cv2.namedWindow(grid_win, cv2.WINDOW_NORMAL)
            cv2.imshow(grid_win, grid)

            print(f"\n共检测到 {len(chars)} 个字符区域，按[S]开始标注 [空格]重采 [q]退出", end="", flush=True)

            ok = False
            while True:
                k = cv2.waitKey(0) & 0xFF
                if k == ord('q'):
                    cv2.destroyAllWindows()
                    if cube:
                        loop.run_until_complete(cube.close())
                    return
                if k == ord(' '):
                    cv2.destroyWindow(overview_win)
                    cv2.destroyWindow(grid_win)
                    break
                if k == ord('s'):
                    ok = True
                    cv2.destroyWindow(overview_win)
                    cv2.destroyWindow(grid_win)
                    break

            if not ok:
                continue

            labeled = []
            ts = int(time.time())
            for idx, (char_img, (cx, cy, r)) in enumerate(chars):
                show_img = cv2.resize(char_img, (CHAR_SIZE[1] * 3, CHAR_SIZE[0] * 3))

                # 模型预判
                pred = "?"
                if classifier:
                    pred = classifier.predict(char_img)

                # 在图片上绘制预测标签
                h_show, w_show = show_img.shape[:2]
                label_color = (0, 255, 0) if pred != "?" else (0, 0, 255)
                cv2.rectangle(show_img, (0, 0), (w_show, 28), label_color, -1)
                cv2.putText(show_img, pred, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

                win_name = f"char[{idx}] - 按[回车]确认 或 按标签键纠正"
                cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
                cv2.imshow(win_name, show_img)
                print(f"\n字符 [{idx+1}/{len(chars)}] 位置 ({cx},{cy}) 模型预测={pred}", end="", flush=True)

                while True:
                    k = cv2.waitKey(0) & 0xFF
                    if k == ord('q'):
                        cv2.destroyAllWindows()
                        if cube:
                            loop.run_until_complete(cube.close())
                        return
                    if k == ord('1'):
                        print(" → 跳过", end="", flush=True)
                        cv2.destroyWindow(win_name)
                        break
                    # 按 2 确认模型预判
                    if k == 13 and classifier and pred and pred != "?":
                        seq += 1
                        save_path = output / pred / f"{ts}_{seq:04d}_{cx}_{cy}.png"
                        cv2.imwrite(str(save_path), char_img)
                        print(f" → {pred}(确认)  已保存 {save_path.name}", end="", flush=True)
                        labeled.append(pred)
                        cv2.destroyWindow(win_name)
                        break
                    label = _label_by_key(k)
                    if label:
                        seq += 1
                        save_path = output / label / f"{ts}_{seq:04d}_{cx}_{cy}.png"
                        cv2.imwrite(str(save_path), char_img)
                        print(f" → {label}  已保存 {save_path.name}", end="", flush=True)
                        labeled.append(label)
                        cv2.destroyWindow(win_name)
                        break

                if k == ord('q'):
                    return

            print(f"\n本帧完成，共 {seq} 张样本")

            if cube and labeled:
                moves = parse(labeled)
                if moves:
                    steps = parse_move_notation(moves)
                    print(f"  labeled: {labeled}")
                    print(f"  解析序列: {moves}")
                    print(f"  face/dir: {steps}")
                    loop.run_until_complete(cube.send_moves(moves))
                    print("  已下发转动到 ESP32")
                else:
                    print("  无有效转动序列")

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()
    if cube:
        loop.run_until_complete(cube.close())


# ─────────────────────────────────────────────────────────────────
# UI 模式：截图 → 人工框选 ROI → 保存模板
# ─────────────────────────────────────────────────────────────────

_ui_selecting = False
_ui_start = (0, 0)
_ui_end = (0, 0)


def _ui_mouse_cb(event, x, y, flags, param):
    global _ui_selecting, _ui_start, _ui_end
    if event == cv2.EVENT_LBUTTONDOWN:
        _ui_selecting = True
        _ui_start = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and _ui_selecting:
        _ui_end = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        _ui_selecting = False
        _ui_end = (x, y)


def _run_ui_collect(client: ScrcpyClient, output_dir: str):
    global _ui_start, _ui_end
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    print("\n=== UI 模板采集 ===")
    print("按键说明:")
    print("  SPACE    截取当前帧")
    print("  鼠标拖拽 框选 ROI 区域")
    print("  [s]      保存选中区域为模板")
    print("  [q]      退出")
    print("=" * 50)

    cv2.namedWindow("collect_ui", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("collect_ui", _ui_mouse_cb)

    _frozen: np.ndarray | None = None
    _seq = 0

    while True:
        if _frozen is None:
            frame = client.last_frame
            if frame is None:
                print("\r等待画面...", end="", flush=True)
                cv2.waitKey(200)
                continue
            display = frame.copy()
        else:
            display = _frozen.copy()

        if _ui_start != _ui_end:
            x1, y1 = _ui_start
            x2, y2 = _ui_end
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            w, h = abs(x2 - x1), abs(y2 - y1)
            cv2.putText(display, f"{w}x{h}", (x1, y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        cv2.imshow("collect_ui", display)

        key = cv2.waitKey(100) & 0xFF

        if key == ord(' '):
            frame = client.last_frame
            if frame is not None:
                _frozen = frame.copy()
                _ui_start = (0, 0)
                _ui_end = (0, 0)
                print("\n画面已冻结，请框选 ROI 区域")

        elif key == ord('s') and _frozen is not None:
            if _ui_start == _ui_end:
                print("  请先用鼠标框选区域")
                continue
            x1 = min(_ui_start[0], _ui_end[0])
            y1 = min(_ui_start[1], _ui_end[1])
            x2 = max(_ui_start[0], _ui_end[0])
            y2 = max(_ui_start[1], _ui_end[1])
            w, h = x2 - x1, y2 - y1
            if w < 8 or h < 8:
                print("  选区太小，请重新框选")
                continue

            name = input("  模板名称 (回车=继续框选): ").strip()
            if name:
                roi_img = _frozen[y1:y2, x1:x2]
                save_path = output / f"{name}.png"
                cv2.imwrite(str(save_path), roi_img)
                _seq += 1
                print(f"  已保存: {save_path}")
                print(f"  recipe ROI 配置: [{x1}, {y1}, {w}, {h}]")
                _ui_start = (0, 0)
                _ui_end = (0, 0)

        elif key == ord('r'):
            _frozen = None
            _ui_start = (0, 0)
            _ui_end = (0, 0)
            print("\n画面已恢复实时")

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()


# ─────────────────────────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="训练数据采集工具")
    sub = parser.add_subparsers(dest="mode")

    p_ocr = sub.add_parser("ocr", help="采集 OCR 字符样本")
    p_ocr.add_argument("--output", default="data/", help="样本保存目录 (默认 data/)")
    p_ocr.add_argument("--serial", default=None, help="adb 设备序列号")
    p_ocr.add_argument("--model", default=None, help="CNN ONNX 模型路径（辅助打标用）")
    p_ocr.add_argument("--host", default=None, help="ESP32 IP（标注完成后下发转动）")
    p_ocr.add_argument("--single-step", action="store_true", help="逐步下发转动 (debug)")

    p_ui = sub.add_parser("ui", help="采集 UI 模板图")
    p_ui.add_argument("--output", default="recipe/recipes/templates/", help="模板保存目录")
    p_ui.add_argument("--serial", default=None, help="adb 设备序列号")

    args = parser.parse_args()

    if args.mode not in ("ocr", "ui"):
        parser.print_help()
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    client = ScrcpyClient(serial=args.serial, max_fps=30, max_width=0, bitrate=200_000_000)
    client.connect()

    classifier = None
    if hasattr(args, "model") and args.model:
        if args.model.endswith(".onnx"):
            classifier = CNNClassifier(args.model)
        elif "hog_svm" in args.model:
            classifier = HOGSVMClassifier(args.model)
        elif args.model.endswith(".pkl"):
            classifier = KNNClassifier(args.model)
        else:
            print(f"无法识别的模型格式: {args.model}")
            classifier = None

    def _cleanup(*_):
        client.disconnect()
        cv2.destroyAllWindows()

    signal.signal(signal.SIGINT, _cleanup)

    try:
        if args.mode == "ocr":
            _run_ocr_collect(client, args.output, classifier=classifier, cube_host=args.host, single_step=args.single_step)
        else:
            _run_ui_collect(client, args.output)
    finally:
        client.disconnect()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
"""
用法：

CNN 辅助打标 + 自动下发转动：
python -m tools.collect_training_data ocr --model ocr/cnn_model.onnx --host 192.168.50.246

流程：
1. 按空格截图 → 模型自动预判每个字符
2. 窗口标题显示 模型预测=R，按 2 确认，按其他键纠正
3. 一帧标注完后自动调用 parser.parse() 生成转动序列 → HTTP 下发到 ESP32

纯手工打标（不辅助、不下发）：
python -m tools.collect_training_data ocr

# 训练 KNN
python -m ocr.trainer train --backend knn --data data/ --output ocr/knn_model.pkl
# 训练 CNN
python -m ocr.trainer train --backend cnn --data data/ --output ocr/cnn_model.onnx
# 训练 hog+svm
python -m ocr.trainer train --backend hog_svm --data data/ --output ocr/hog_svm_model.pkl

# 用 KNN 辅助打标
python -m tools.collect_training_data ocr --model ocr/knn_model.pkl --host 192.168.50.246

# 用 CNN 辅助打标
python -m tools.collect_training_data ocr --model ocr/cnn_model.onnx --host 192.168.50.246

# 用 hog+svm 辅助打标
python -m tools.collect_training_data ocr --model ocr/hog_svm_model.pkl --host  192.168.50.246

# ui 收集
python -m tools.collect_training_data ui --output templates/ --host  192.168.50.246
"""