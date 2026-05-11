"""模板匹配核心 —— 基于 recipe 配置的特征图匹配"""
import logging

import cv2
import numpy as np

from recipe.schema import Recipe, UIFeature

logger = logging.getLogger(__name__)


def match_feature(frame: np.ndarray, recipe: Recipe, feature_name: str) -> tuple[bool, tuple[int, int] | None]:
    """在 frame 中检测单个 UI 特征。

    Args:
        frame: BGR ndarray
        recipe: Recipe 配置对象
        feature_name: 特征名称（如 "match_button"）

    Returns:
        (matched, center) —— matched=True 时 center 为匹配中心 (x, y)。
    """
    feat = recipe.feature(feature_name)
    if feat is None:
        logger.warning("recipe 中未定义特征: %s", feature_name)
        return False, None

    tmpl_path = recipe.template_path(feat)
    template = cv2.imread(str(tmpl_path))
    if template is None:
        logger.warning("无法加载模板图: %s", tmpl_path)
        return False, None

    roi = feat.roi
    if roi:
        x, y, w, h = roi
        search_area = frame[y:y+h, x:x+w]
    else:
        search_area = frame

    result = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= feat.threshold:
        th, tw = template.shape[:2]
        cx = max_loc[0] + tw // 2
        cy = max_loc[1] + th // 2
        if roi:
            cx += roi[0]
            cy += roi[1]
        logger.debug("特征 %s 匹配成功，置信度 %.2f，中心 (%d, %d)", feature_name, max_val, cx, cy)
        return True, (cx, cy)

    return False, None


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 3:
        print("Usage: python -m vision.matcher <frame.png> <template.png> [roi_x roi_y roi_w roi_h]")
        sys.exit(1)

    frame = cv2.imread(sys.argv[1])
    template = cv2.imread(sys.argv[2])
    if frame is None or template is None:
        print("无法读取图片")
        sys.exit(1)

    roi = None
    if len(sys.argv) == 7:
        roi = tuple(int(x) for x in sys.argv[3:7])
        x, y, w, h = roi
        search_area = frame[y:y+h, x:x+w]
    else:
        search_area = frame

    result = cv2.matchTemplate(search_area, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    th, tw = template.shape[:2]
    cx = max_loc[0] + tw // 2
    cy = max_loc[1] + th // 2
    if roi:
        cx += roi[0]
        cy += roi[1]

    print(f"最大置信度: {max_val:.4f}")
    print(f"匹配中心: ({cx}, {cy})")

    vis = frame.copy()
    cv2.circle(vis, (cx, cy), 10, (0, 255, 0), 2)
    if roi:
        x, y, w, h = roi
        cv2.rectangle(vis, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.imshow("matcher result", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
