"""各状态 UI 检测逻辑 —— Controller 调用的高层接口"""
import logging

import numpy as np

from recipe.schema import Recipe
from vision.matcher import match_feature

logger = logging.getLogger(__name__)


class Detector:
    """根据 recipe 配置检测当前帧中的 UI 特征。

    Controller 在各状态处理函数中调用，判断屏幕上出现了什么 UI。
    流程控制（检测到什么→做什么）由 Controller 负责，Detector 只返回检测结果。

    用法：
        detector = Detector(recipe)
        matched, center = detector.detect(frame, "match_button")
        if matched:
            scrcpy.tap(*center)
    """

    def __init__(self, recipe: Recipe):
        self.recipe = recipe

    def detect(self, frame: np.ndarray, feature_name: str) -> tuple[bool, tuple[int, int] | None]:
        """检测单个 UI 特征。

        Returns:
            (matched, center) —— center 为匹配中心 (x, y)，未匹配时为 None。
        """
        return match_feature(frame, self.recipe, feature_name)

    def detect_any(self, frame: np.ndarray, feature_names: list[str]) -> tuple[str | None, tuple[int, int] | None]:
        """按顺序检测多个特征，返回第一个匹配的结果。

        Returns:
            (matched_name, center) —— 无匹配时 matched_name=None。
        """
        for name in feature_names:
            matched, center = self.detect(frame, name)
            if matched:
                return name, center
        return None, None


if __name__ == "__main__":
    """单独测试：python -m vision.detector <frame.png> <recipe.json> <feature_name>

    示例：
        python -m vision.detector screen.png recipe/recipes/example.json match_button
    """
    import sys
    from recipe.loader import RecipeLoader
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 4:
        print("Usage: python -m vision.detector <frame.png> <recipe.json> <feature_name>")
        sys.exit(1)

    frame = cv2.imread(sys.argv[1])
    if frame is None:
        print(f"无法读取图片: {sys.argv[1]}")
        sys.exit(1)

    loader = RecipeLoader(sys.argv[2])
    detector = Detector(loader.recipe)
    name = sys.argv[3]

    matched, center = detector.detect(frame, name)
    print(f"特征 '{name}': matched={matched}, center={center}")

    if matched and center:
        vis = frame.copy()
        cv2.circle(vis, center, 10, (0, 255, 0), 2)
        cv2.imshow("detector result", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()