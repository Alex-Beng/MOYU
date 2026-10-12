"""debug 图片交互式标注工具（网格 + 鼠标批量模式）

批量标注 controller 落盘的 debug 样本（debug/scramble/{ts}_{idx}_{label}.png），
文件名中段已带模型预测标签。整页样本默认视为正确（绿色）；鼠标左键点击格子在
绿→橙→红→绿 三态间循环，按 [l] 可一键对整页 CNN 重推理并覆盖为橙色，
按确认/翻页时把未标红项落盘。

三态循环（每格，初始为绿）：
  绿（初始）  按文件名原标签落盘 data/<原标签>/
  橙（点击1次）用 CNN(onnx) 重新推理，显示新预测，按 CNN 标签落盘 data/<CNN标签>/
  红（点击2次）视为标错，跳过不落盘（留在 debug/ 作为错误样本池）

用法：
  # 标注 debug/scramble/，默认移动到 data/
  python -m tools.annotate_debug

  # 指定来源与输出
  python -m tools.annotate_debug --input debug/scramble/ --output data/

  # 复制而非移动（保留 debug 原文件）
  python -m tools.annotate_debug --copy

  # 自定义每页网格
  python -m tools.annotate_debug --cols 4 --rows 4

  # 指定 CNN 模型（默认 ocr/cnn_model.onnx）
  python -m tools.annotate_debug --model ocr/cnn_model.onnx

按键说明：
  [鼠标左键]  点击格子：绿(原标签)→橙(CNN重推理)→红(跳过)→绿 循环
  [l]         对当前页全部格子 CNN 重推理并覆盖为橙色
  [回车/空格] 确认当前页：非红色项按对应标签落盘
  [n]         下一页（先落盘当前页）
  [p]         上一页（先落盘当前页）
  [q]         退出（不落盘当前页）
"""

import argparse
import logging
import shutil
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from ocr.classifier import LABELS, create_classifier

logger = logging.getLogger(__name__)

# 单元格三态：绿（原标签）→ 橙（CNN 重推理）→ 红（跳过）
STATE_GREEN = 0
STATE_ORANGE = 1
STATE_RED = 2

# 单元格布局：字符图放大到 CELL_W，顶部为标签条
CELL_W = 128
LABEL_H = 30
GAP = 8
BG_COLOR = 40

# 标签条颜色（BGR）
COLOR_PRED = (0, 220, 0)      # 绿：正常预测
COLOR_CNN = (0, 165, 255)     # 橙：CNN 重新推理
COLOR_SELECTED = (0, 0, 255)  # 红：标错（跳过）
COLOR_UNKNOWN = (0, 165, 255)  # 无法解析预测（自动视作跳过）

_LEGEND_LINES = [
    "  [LMB] cycle cell: green -> orange -> red",
    "  [l]   infer whole page with CNN (all -> orange)",
    "  [Enter]/[Space] accept page",
    "  [n] next page   [p] prev page   [q] quit",
    "",
    "  green  = accept filename label",
    "  orange = relabel with CNN(onnx) prediction",
    "  red    = skip (kept in debug)",
]


def _parse_predicted_label(stem: str) -> str | None:
    """从文件名 stem 解析预测标签（格式 {ts}_{idx}_{label}）。

    标签含 ' 与数字，从右往左匹配已知 LABELS，优先匹配更长的标签。
    """
    for label in sorted(LABELS, key=len, reverse=True):
        if stem.endswith("_" + label):
            return label
    return None


def _make_legend() -> np.ndarray:
    """生成一张常驻的说明图（ASCII，避免中文渲染问题）。"""
    w, line_h = 470, 32
    img = np.full((len(_LEGEND_LINES) * line_h + 12, w, 3), 30, dtype=np.uint8)
    for i, line in enumerate(_LEGEND_LINES):
        y = 12 + i * line_h + 22
        cv2.putText(img, line, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 230, 230), 1)
    return img


def _render_cell(img: np.ndarray, predicted: str | None, state: int, cnn_label: str | None) -> np.ndarray:
    """渲染单个格子：字符图 + 顶部标签条（绿/橙/红三态）。"""
    if predicted is None:
        text = "pred=?"
        color = COLOR_UNKNOWN
    elif state == STATE_RED:
        text = f"pred={predicted}"
        color = COLOR_SELECTED
    elif state == STATE_ORANGE:
        text = f"cnn={cnn_label}" if cnn_label else "cnn=?"
        color = COLOR_CNN
    else:
        text = f"pred={predicted}"
        color = COLOR_PRED
    cv2.rectangle(img, (0, 0), (CELL_W, LABEL_H), (0, 0, 0), -1)
    cv2.rectangle(img, (0, 0), (CELL_W - 1, img.shape[0] - 1), color, 2)
    cv2.putText(img, text, (6, LABEL_H - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return img


def _build_grid(items, cell_state: dict, cnn_cache: dict, cols: int, rows: int) -> np.ndarray:
    """把当前页样本渲染成 cols×rows 网格图（每格按需 imread）。"""
    cell_h = CELL_W + LABEL_H
    grid_h = rows * cell_h + (rows + 1) * GAP
    grid_w = cols * CELL_W + (cols + 1) * GAP
    grid = np.full((grid_h, grid_w, 3), BG_COLOR, dtype=np.uint8)

    for i, (img_path, predicted) in enumerate(items):
        if i >= cols * rows:
            break
        r, c = divmod(i, cols)
        y0 = GAP + r * (cell_h + GAP)
        x0 = GAP + c * (CELL_W + GAP)

        img = cv2.imread(str(img_path))
        if img is None:
            cell = np.full((CELL_W, CELL_W, 3), 80, dtype=np.uint8)
            predicted = None
        else:
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cell = cv2.resize(img, (CELL_W, CELL_W), interpolation=cv2.INTER_NEAREST)
        cell = np.vstack([np.zeros((LABEL_H, CELL_W, 3), dtype=cell.dtype), cell])
        cell = _render_cell(cell, predicted, cell_state.get(i, STATE_GREEN), cnn_cache.get(i))
        grid[y0:y0 + cell.shape[0], x0:x0 + cell.shape[1]] = cell
    return grid


def _move_or_copy(src: Path, dst: Path, move: bool, dry_run: bool):
    if dry_run:
        return
    if move:
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(str(src), str(dst))


def _predict_cnn(clf, img_path: Path) -> str | None:
    """对单个字符图用 CNN 重新推理，返回预测标签（"?"/失败返回 None）。"""
    if clf is None:
        return None
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    label = clf.predict(img)
    return None if label in (None, "?") else label


def _preinfer_page(items, clf) -> tuple[dict, dict]:
    """对当前页每格预跑 CNN 推理，全部置为橙色，返回 (cell_state, cnn_cache)。"""
    cell_state = {i: STATE_ORANGE for i in range(len(items))}
    cnn_cache = {i: _predict_cnn(clf, items[i][0]) for i in range(len(items))}
    return cell_state, cnn_cache


def _on_mouse(event, x, y, flags, state):
    """鼠标左键：在 绿→橙→红→绿 三态间循环。

    进入橙色时用 CNN 重新推理（结果缓存）。窗口可拉伸，需先把窗口坐标归一化到图像坐标。
    """
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    cell_state = state["cell_state"]
    cnn_cache = state["cnn_cache"]
    items = state["page_items"]
    if not items:
        return

    # getWindowImageRect 返回屏幕坐标系下渲染区的位置/尺寸，而鼠标 x/y 相对图像内容区，
    # 故只用渲染区宽高做缩放，不能减 rx/ry 屏幕偏移。
    _rx, _ry, disp_w, disp_h = cv2.getWindowImageRect(state["win"])
    img_h, img_w = state["grid_shape"][:2]
    ix = int(x * img_w / disp_w)
    iy = int(y * img_h / disp_h)

    cell_h = CELL_W + LABEL_H
    c = (ix - GAP) // (CELL_W + GAP)
    r = (iy - GAP) // (cell_h + GAP)
    if c < 0 or c >= state["cols"] or r < 0 or r >= state["rows"]:
        return
    idx = r * state["cols"] + c
    if idx >= len(items):
        return
    nxt = (cell_state.get(idx, STATE_GREEN) + 1) % 3
    cell_state[idx] = nxt
    if nxt == STATE_ORANGE and idx not in cnn_cache:
        cnn_cache[idx] = _predict_cnn(state.get("clf"), items[idx][0])


def _accept_item(img_path: Path, predicted: str, out_path: Path, move: bool, dry_run: bool) -> bool:
    """按预测标签落盘单张样本，返回是否成功。"""
    if predicted is None:
        return False
    dst = out_path / predicted / img_path.name
    if dst.exists():
        dst = out_path / predicted / f"{img_path.stem}_dup{img_path.suffix}"
    _move_or_copy(img_path, dst, move, dry_run)
    return True


def run_annotate(input_dir: str, output_dir: str, move: bool = True, dry_run: bool = False,
                 cols: int = 4, rows: int = 4, model_path: str = "ocr/cnn_model.onnx"):
    in_path = Path(input_dir)
    out_path = Path(output_dir)

    images = sorted(p for p in in_path.rglob("*.png") if p.is_file())
    if not images:
        print(f"未找到图片: {in_path}")
        return

    for label in LABELS:
        (out_path / label).mkdir(parents=True, exist_ok=True)

    print("\n=== debug 样本标注（网格模式） ===")
    print(f"  来源: {in_path}  数量: {len(images)}")
    print(f"  输出: {out_path}  ({'移动' if move else '复制'})")
    print(f"  每页: {cols}x{rows} = {cols * rows} 张")
    print("  左键点击循环：绿(原标签)→橙(CNN重推理)→红(跳过)→绿；[l] 全页 CNN 重推理")
    print("  Enter 确认本页；n/p 翻页（翻页即落盘）；q 退出")
    print("=" * 50)

    clf = create_classifier({"type": "cnn", "model_path": model_path})
    if getattr(clf, "_session", None) is None:
        logger.warning("CNN 模型不可用（%s），橙色将退化为无预测", model_path)

    stats = Counter()
    label_counts = Counter()

    # 惰性加载：仅记录路径 + 预测标签，不预读图像
    records = [(img_path, _parse_predicted_label(img_path.stem)) for img_path in images]

    page_size = cols * rows
    page = 0
    total_pages = max(1, (len(records) + page_size - 1) // page_size)

    win = "annotate_debug - grid"
    legend = _make_legend()
    cv2.namedWindow("keymap", cv2.WINDOW_NORMAL)
    cv2.imshow("keymap", legend)

    state = {"cell_state": {}, "cnn_cache": {}, "clf": clf,
             "cols": cols, "rows": rows, "page_items": [],
             "win": win, "grid_shape": (0, 0), "page_key": None}

    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, _on_mouse, state)

    def _flush_page(items, cell_state, cnn_cache):
        """落盘当前页非红色项：绿色用原标签，橙色用 CNN 标签，红色跳过。"""
        for i, (img_path, predicted) in enumerate(items):
            st = cell_state.get(i, STATE_GREEN)
            if st == STATE_RED:
                stats["skipped"] += 1
                continue
            # 橙色用 CNN 新标签（失败退回原标签），绿色用原标签
            label = (cnn_cache.get(i) or predicted) if st == STATE_ORANGE else predicted
            if label is None:
                stats["skipped"] += 1
                continue
            if not img_path.exists():
                stats["unreadable"] += 1
                continue
            if _accept_item(img_path, label, out_path, move, dry_run):
                stats["labeled"] += 1
                label_counts[label] += 1
                print(f"[{label}] {img_path.name}")

    while records or page > 0:
        total_pages = max(1, (len(records) + page_size - 1) // page_size)
        if page >= total_pages:
            page = total_pages - 1
        start = page * page_size
        page_items = records[start:start + page_size]
        state["page_items"] = page_items
        # 换页时清空三态（默认全绿）与 CNN 缓存；同页多轮循环保留
        if state["page_key"] != (page, start):
            state["cell_state"] = {}
            state["cnn_cache"] = {}
            state["page_key"] = (page, start)

        grid = _build_grid(page_items, state["cell_state"], state["cnn_cache"], cols, rows)
        state["grid_shape"] = grid.shape
        cv2.putText(grid, f"page {page + 1}/{total_pages}  ({len(records)} left)",
                    (GAP + 2, grid.shape[0] - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.imshow(win, grid)
        cv2.imshow("keymap", legend)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('q'):
            print("\n用户退出（当前页未落盘）")
            break

        if key in (13, 32):  # Enter / Space：确认当前页
            _flush_page(page_items, state["cell_state"], state["cnn_cache"])
            records = records[:start] + records[start + len(page_items):]
            state["page_key"] = None

        elif key == ord('n'):  # 下一页（先落盘当前页）
            _flush_page(page_items, state["cell_state"], state["cnn_cache"])
            records = records[:start] + records[start + len(page_items):]
            state["page_key"] = None
            if page < max(1, (len(records) + page_size - 1) // page_size) - 1:
                page += 1

        elif key == ord('p'):  # 上一页（先落盘当前页）
            _flush_page(page_items, state["cell_state"], state["cnn_cache"])
            records = records[:start] + records[start + len(page_items):]
            state["page_key"] = None
            page = max(0, page - 1)

        elif key == ord('l'):  # 手动触发：全页 CNN 推理并覆盖为橙色
            state["cell_state"], state["cnn_cache"] = _preinfer_page(page_items, clf)

    cv2.destroyAllWindows()
    print("\n=== 统计 ===")
    print(f"  标注: {stats['labeled']}  跳过: {stats['skipped']}  不可读: {stats['unreadable']}")
    if label_counts:
        print("  各标签计数:")
        for label, cnt in sorted(label_counts.items()):
            print(f"    {label:>6}: {cnt}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="debug 图片交互式网格标注工具")
    parser.add_argument("--input", default="debug/scramble/", help="debug 图片目录（递归扫描）")
    parser.add_argument("--output", default="data/", help="数据输出目录")
    parser.add_argument("--copy", action="store_true", help="复制而非移动")
    parser.add_argument("--dry-run", action="store_true", help="只走流程不落盘")
    parser.add_argument("--cols", type=int, default=4, help="每页列数")
    parser.add_argument("--rows", type=int, default=4, help="每页行数")
    parser.add_argument("--model", default="ocr/cnn_model.onnx", help="CNN onnx 模型路径（橙色重推理用）")
    args = parser.parse_args()
    run_annotate(args.input, args.output, move=not args.copy, dry_run=args.dry_run,
                 cols=args.cols, rows=args.rows, model_path=args.model)
