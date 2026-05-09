"""圆形轮廓检测 + 字符区域分割

固定流程，不依赖 recipe 配置。
打乱序列以圆形气泡方式展示在屏幕上，通过 HoughCircles 定位每个气泡，
裁剪后归一化到固定大小供分类器识别。
"""
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# 裁剪后归一化的字符图大小（分类器输入尺寸）
CHAR_SIZE = (64, 64)

# HoughCircles 参数（可根据实际屏幕调整）
HOUGH_DP = 1.2
HOUGH_MIN_DIST = 40       # 相邻圆心最小距离（像素）
HOUGH_PARAM1 = 80         # Canny 高阈值
HOUGH_PARAM2 = 30         # 圆心检测累加器阈值，越小检测到越多（可能有假阳）
HOUGH_MIN_RADIUS = 15
HOUGH_MAX_RADIUS = 60


def detect_circles(gray: np.ndarray) -> list[tuple[int, int, int]]:
    """在灰度图中检测圆形轮廓。

    Returns:
        [(cx, cy, r), ...] 按从左到右、从上到下排序。
    """
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=HOUGH_DP,
        minDist=HOUGH_MIN_DIST,
        param1=HOUGH_PARAM1,
        param2=HOUGH_PARAM2,
        minRadius=HOUGH_MIN_RADIUS,
        maxRadius=HOUGH_MAX_RADIUS,
    )
    if circles is None:
        return []
    circles = np.round(circles[0]).astype(int)
    # 从左到右、从上到下排序（先按行，再按列）
    circles = sorted(circles, key=lambda c: (c[1] // (HOUGH_MIN_DIST // 2), c[0]))
    return [(int(cx), int(cy), int(r)) for cx, cy, r in circles]


def crop_circle(frame: np.ndarray, cx: int, cy: int, r: int) -> np.ndarray:
    """裁剪圆形区域并归一化到 CHAR_SIZE。"""
    padding = 4
    x1 = max(0, cx - r - padding)
    y1 = max(0, cy - r - padding)
    x2 = min(frame.shape[1], cx + r + padding)
    y2 = min(frame.shape[0], cy + r + padding)
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return np.zeros((*CHAR_SIZE, 3), dtype=np.uint8)
    return cv2.resize(crop, CHAR_SIZE)


def segment(frame: np.ndarray) -> list[tuple[np.ndarray, tuple[int, int, int]]]:
    """从帧中检测圆形气泡并分割出字符图像。

    Args:
        frame: BGR ndarray（整帧或打乱区域截图）

    Returns:
        [(char_img, (cx, cy, r)), ...] —— 按从左到右、从上到下排序的字符图列表。
        char_img 已归一化到 CHAR_SIZE，BGR 格式。
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 轻微模糊降噪，提高 HoughCircles 稳定性
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    circles = detect_circles(blurred)

    result = []
    for cx, cy, r in circles:
        char_img = crop_circle(frame, cx, cy, r)
        result.append((char_img, (cx, cy, r)))

    logger.debug("检测到 %d 个圆形气泡", len(result))
    return result


if __name__ == "__main__":
    """单独测试：python -m ocr.segmentor <image.png>

    显示圆形轮廓检测结果，并弹出每个裁剪字符图。
    """
    import sys
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 2:
        print("Usage: python -m ocr.segmentor <image.png>")
        sys.exit(1)

    frame = cv2.imread(sys.argv[1])
    if frame is None:
        print(f"无法读取图片: {sys.argv[1]}")
        sys.exit(1)

    chars = segment(frame)
    print(f"检测到 {len(chars)} 个字符区域")

    # 在原图上标注圆形
    vis = frame.copy()
    for i, (char_img, (cx, cy, r)) in enumerate(chars):
        cv2.circle(vis, (cx, cy), r, (0, 255, 0), 2)
        cv2.putText(vis, str(i), (cx - 8, cy + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("segmentor: circles", vis)
    print("按任意键逐个查看裁剪结果，q 退出")
    cv2.waitKey(0)

    for i, (char_img, (cx, cy, r)) in enumerate(chars):
        cv2.imshow(f"char[{i}] ({cx},{cy},r={r})", char_img)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        if key == ord('q'):
            break