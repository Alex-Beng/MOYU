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
HOUGH_DP = 1.0
HOUGH_MIN_DIST = 123       # 相邻圆心最小距离（像素）
HOUGH_PARAM1 = 66         # Canny 高阈值
HOUGH_PARAM2 = 22         # 圆心检测累加器阈值，越小检测到越多（可能有假阳）
HOUGH_MIN_RADIUS = 51
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
    """单独测试 & 实时调参

    静态图片测试：
        python -m ocr.segmentor <image.png>

    scrcpy 实时标注（调参 HoughCircles）：
        python -m ocr.segmentor --live              # 全图检测
        python -m ocr.segmentor --live --roi 50,400,980,300  # 限定 ROI
        python -m ocr.segmentor --live --serial 192.168.1.5:5555
    """
    import argparse
    import sys
    import signal

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", help="静态图片路径")
    parser.add_argument("--live", action="store_true", help="scrcpy 实时标注模式")
    parser.add_argument("--roi", default=None, help="限定检测区域 x,y,w,h")
    parser.add_argument("--serial", default=None, help="adb 设备序列号")
    parser.add_argument("--fps", type=int, default=5, help="截图帧率")
    args = parser.parse_args()

    # ── 静态图片模式 ──
    if args.image and not args.live:
        frame = cv2.imread(args.image)
        if frame is None:
            print(f"无法读取图片: {args.image}")
            sys.exit(1)

        chars = segment(frame)
        print(f"检测到 {len(chars)} 个字符区域")

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

    # ── scrcpy 实时标注模式 ──
    elif args.live:
        from device.scrcpy_client import ScrcpyClient

        # 解析 ROI
        roi = None
        if args.roi:
            roi = tuple(int(x) for x in args.roi.split(","))
            if len(roi) != 4:
                print("--roi 格式应为 x,y,w,h")
                sys.exit(1)

        client = ScrcpyClient(serial=args.serial, max_fps=args.fps, max_width=0, bitrate=200_000_000)
        client.connect()

        cv2.namedWindow("segmentor live", cv2.WINDOW_NORMAL)
        cv2.createTrackbar("dp x10", "segmentor live", int(HOUGH_DP * 10), 30, lambda v: None)
        cv2.createTrackbar("minDist", "segmentor live", HOUGH_MIN_DIST, 200, lambda v: None)
        cv2.createTrackbar("param1", "segmentor live", HOUGH_PARAM1, 200, lambda v: None)
        cv2.createTrackbar("param2", "segmentor live", HOUGH_PARAM2, 100, lambda v: None)
        cv2.createTrackbar("minR", "segmentor live", HOUGH_MIN_RADIUS, 80, lambda v: None)
        cv2.createTrackbar("maxR", "segmentor live", HOUGH_MAX_RADIUS, 120, lambda v: None)

        _stop = False

        def _on_signal(*_):
            global _stop
            _stop = True

        signal.signal(signal.SIGINT, _on_signal)

        print("\n=== segmentor 实时标注 ===")
        print("Trackbar 可实时调整 HoughCircles 参数")
        print("Ctrl+C 退出")
        print("=" * 40)

        while not _stop:
            frame = client.last_frame
            if frame is None:
                cv2.waitKey(100)
                continue

            # 读取 trackbar
            dp = max(1, cv2.getTrackbarPos("dp x10", "segmentor live")) / 10.0
            min_dist = max(5, cv2.getTrackbarPos("minDist", "segmentor live"))
            p1 = max(1, cv2.getTrackbarPos("param1", "segmentor live"))
            p2 = max(1, cv2.getTrackbarPos("param2", "segmentor live"))
            min_r = max(5, cv2.getTrackbarPos("minR", "segmentor live"))
            max_r = max(min_r + 1, cv2.getTrackbarPos("maxR", "segmentor live"))

            # 检测区域
            if roi:
                x, y, w, h = roi
                search = frame[y:y+h, x:x+w]
            else:
                x, y, w, h = 0, 0, frame.shape[1], frame.shape[0]
                search = frame

            gray = cv2.cvtColor(search, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            circles = cv2.HoughCircles(
                blurred, cv2.HOUGH_GRADIENT,
                dp=dp, minDist=min_dist, param1=p1, param2=p2,
                minRadius=min_r, maxRadius=max_r,
            )

            vis = frame.copy()

            # 绘制 ROI 矩形
            if roi:
                cv2.rectangle(vis, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # 绘制检测到的圆
            n_circles = 0
            if circles is not None:
                circles = np.round(circles[0]).astype(int)
                n_circles = len(circles)
                for idx, (cx, cy, r) in enumerate(circles):
                    cx_real = cx + x
                    cy_real = cy + y
                    cv2.circle(vis, (cx_real, cy_real), r, (0, 255, 0), 2)
                    cv2.circle(vis, (cx_real, cy_real), 2, (0, 0, 255), -1)
                    cv2.putText(vis, str(idx), (cx_real - 6, cy_real + 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            # 叠加参数信息
            info = (
                f"dp={dp:.1f} minDist={min_dist} p1={p1} p2={p2} "
                f"minR={min_r} maxR={max_r}  circles={n_circles}"
            )
            cv2.putText(vis, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            h_vis, w_vis = vis.shape[:2]
            if w_vis > 800:
                scale = 800 / w_vis
                vis = cv2.resize(vis, (800, int(h_vis * scale)))

            cv2.imshow("segmentor live", vis)
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break

        client.disconnect()
        cv2.destroyAllWindows()