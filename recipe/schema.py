"""Recipe JSON schema 定义与校验

Recipe 包含 UI 特征定义和赛事模式，Controller 根据 mode 选择控制策略。

模式说明：
    semi   半自动：人类操作 UI，AI 只负责 scramble OCR + solve
    rank   排位赛：全自动，init(begin_rank) → scramble → solve → end_rank → re_rank
    holder 守擂赛：预留
    team   组队赛：预留

结构：
{
    "name": "设备名称",
    "mode": "rank",
    "device": { "width": 1080, "height": 2400 },
    "ui": {
        "begin_rank": {
            "template": "templates/begin_rank.png",
            "roi": [100, 200, 300, 80],
            "threshold": 0.85
        }
    }
}

- ui 的 key 是特征名称，由 Controller 代码引用
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
    desc: str = ""                                      # 描述文字

    @classmethod
    def from_dict(cls, d: dict) -> "UIFeature":
        roi = tuple(d["roi"]) if d.get("roi") else None
        return cls(
            template=d["template"],
            roi=roi,
            threshold=d.get("threshold", 0.85),
            desc=d.get("desc", ""),
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
    mode: str = "semi"
    cube: str = "rubik"            # "rubik" = 三阶, "pocket" = 二阶
    solve_method: str = "cfop"     # 三阶: "cfop", 二阶: "ortega"/"eg"
    scramble_delay: int | None = None
    solve_delay: int | None = None
    cross_delay: int | None = None
    f2l_delay: int | None = None
    oll_delay: int | None = None
    pll_delay: int | None = None
    alll_delay: int | None = None
    cross_time: int | None = None
    f2l_time: int | None = None
    oll_time: int | None = None
    pll_time: int | None = None
    alll_time: int | None = None
    rotation: str | None = None
    alll_prob: float = 0.2
    move_format: str = "dir"  # "dir" = face/dir, "str" = move string
    scrcpy_bitrate: int | None = None      # scrcpy 视频码率 (bps)，None=默认 8Mbps；WiFi adb 建议 2-3Mbps
    scrcpy_max_fps: int | None = None      # scrcpy 最大帧率，None=默认 10
    ui: dict[str, UIFeature] = field(default_factory=dict)
    base_dir: Path = field(default_factory=Path)

    @classmethod
    def from_dict(cls, d: dict, base_dir: Path) -> "Recipe":
        device = DeviceConfig.from_dict(d["device"])
        ui = {k: UIFeature.from_dict(v) for k, v in d.get("ui", {}).items()}
        return cls(
            name=d["name"], device=device, mode=d.get("mode", "semi"),
            cube=d.get("cube", "rubik"), solve_method=d.get("solve_method", "cfop"),
            scramble_delay=d.get("scramble_delay"), solve_delay=d.get("solve_delay"),
            cross_delay=d.get("cross_delay"), f2l_delay=d.get("f2l_delay"),
            oll_delay=d.get("oll_delay"), pll_delay=d.get("pll_delay"),
            alll_delay=d.get("alll_delay"), rotation=d.get("rotation"),
            cross_time=d.get("cross_time"), f2l_time=d.get("f2l_time"),
            oll_time=d.get("oll_time"), pll_time=d.get("pll_time"),
            alll_time=d.get("alll_time"),
            move_format=d.get("move_format", "dir"),
            alll_prob=d.get("alll_prob", 0.2),
            scrcpy_bitrate=d.get("scrcpy_bitrate"),
            scrcpy_max_fps=d.get("scrcpy_max_fps"),
            ui=ui, base_dir=base_dir,
        )

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
    if d.get("mode") not in (None, "semi", "rank", "holder", "team", "week", "remote", "solo", "proxy"):
        raise ValueError(f"不支持的 mode: {d.get('mode')}")
    cube = d.get("cube", "rubik")
    if cube not in ("rubik", "pocket"):
        raise ValueError(f"不支持的 cube: {cube}")
    solve_method = d.get("solve_method", "cfop" if cube == "rubik" else "eg")
    if cube == "rubik" and solve_method not in ("cfop",):
        raise ValueError(f"三阶不支持的 solve_method: {solve_method}")
    if cube == "pocket" and solve_method not in ("ortega", "eg"):
        raise ValueError(f"二阶不支持的 solve_method: {solve_method}")
    for feat_name, feat in d.get("ui", {}).items():
        if "template" not in feat:
            raise ValueError(f"ui.{feat_name} 缺少 template")