"""Recipe 加载器 —— 读取/校验/热重载 recipe JSON 配置"""
import json
import logging
from pathlib import Path

from recipe.schema import Recipe, validate

logger = logging.getLogger(__name__)

RECIPES_DIR = Path(__file__).parent / "recipes"


class RecipeLoader:
    """加载 recipe 并返回 Recipe 对象。

    用法：
        loader = RecipeLoader("recipes/example.json")
        recipe = loader.recipe
        feat = recipe.feature("match_button")

    单独测试：
        loader = RecipeLoader()
        recipe = loader.recipe  # 使用默认 example
    """

    def __init__(self, path: str | Path | None = None):
        if path is None:
            path = RECIPES_DIR / "example.json"
        self.path = RECIPES_DIR / Path(path)
        self.recipe: Recipe | None = None
        self._raw: dict = {}
        self.load()

    def load(self):
        """从文件加载、校验并构建 Recipe 对象。"""
        if not self.path.exists():
            logger.warning("recipe 文件不存在: %s", self.path)
            return
        with open(self.path, encoding="utf-8") as f:
            self._raw = json.load(f)
        validate(self._raw)
        self.recipe = Recipe.from_dict(self._raw, base_dir=self.path.parent)
        logger.info("recipe 加载完成: %s (%s)", self.recipe.name, self.path)

    def reload(self):
        """热重载 recipe（文件变更后调用）。"""
        self.load()

    def switch(self, path: str | Path):
        """运行时切换到另一个 recipe 文件。"""
        self.path = RECIPES_DIR / Path(path)
        self.load()