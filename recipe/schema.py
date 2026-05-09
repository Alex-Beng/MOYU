"""Recipe JSON schema 定义与校验

Recipe 只负责描述 UI 特征（怎么检测），不负责流程控制。

结构：
{
    "name": "设备名称",
    "device": { "width": 1080, "height": 2400 },
    "ui": {
        "match_button": {
            "template": "templates/match_btn.png",
            "roi": [100, 200, 300, 80],
            "threshold": 0.85
        },
        "scramble_text": {
            "template": "templates/scramble_area.png",
            "roi": [50, 400, 800, 200],
            "threshold": 0.80
        },
        "result_screen": {
            "template": "templates/result.png",
            "roi": null,
            "threshold": 0.85
        }
    }
}

- ui 的 key 是特征名称（如 "match_button"），由 Controller 代码引用
- Controller 决定在哪个状态检测哪些特征、检测到后做什么动作、转移到哪
- Recipe 是纯配置，不含任何流程逻辑
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class UIFeature:
    """单条 UI 特征配置：描述屏幕上的一个可检测区域。"""
    template: str                                       # 模板图相对路径
    roi: tuple[int, int, int, int] | None = None       # (x, y, w, h)，null=全图
    threshold: float = 0.85                             # 匹配阈值

    @classmethod
    def from_dict(cls, d: dict) -> "UIFeature":
        roi = tuple(d["roi"]) if d.get("roi") else None
        return cls(
            template=d["template"],
            roi=roi,
            threshold=d.get("threshold", 0.85),
        )


@dataclass
class DeviceConfig:
    """设备基础参数。"""
    width: int
    height: int

    @classmethod
    def from_dict(cls, d: dict) -> "DeviceConfig":
        return cls(width=d["width"], height=d["height"])


@dataclass
class Recipe:
    """完整 recipe：纯配置，不含流程逻辑。"""
    name: str
    device: DeviceConfig
    ui: dict[str, UIFeature] = field(default_factory=dict)
    base_dir: Path = field(default_factory=Path)  # recipe 文件目录，解析模板图相对路径

    @classmethod
    def from_dict(cls, d: dict, base_dir: Path) -> "Recipe":
        device = DeviceConfig.from_dict(d["device"])
        ui = {k: UIFeature.from_dict(v) for k, v in d.get("ui", {}).items()}
        return cls(name=d["name"], device=device, ui=ui, base_dir=base_dir)

    def feature(self, name: str) -> UIFeature | None:
        """按名称获取 UI 特征配置。"""
        return self.ui.get(name)

    def template_path(self, feature: UIFeature) -> Path:
        """返回模板图的绝对路径。"""
        return self.base_dir / feature.template


def validate(d: dict):
    """校验 recipe dict，异常时抛出 ValueError。"""
    for key in ("name", "device", "ui"):
        if key not in d:
            raise ValueError(f"recipe 缺少必填字段: {key}")
    dev = d["device"]
    if "width" not in dev or "height" not in dev:
        raise ValueError("device 必须包含 width 和 height")
    for feat_name, feat in d.get("ui", {}).items():
        if "template" not in feat:
            raise ValueError(f"ui.{feat_name} 缺少 template")