"""主控制器 —— 编排各独立任务

运行模式（由 recipe.mode 控制）：
    semi   半自动：人类操作 UI，AI 只负责 scramble OCR + solve
    rank   排位赛：init(begin_rank) → scramble(segment循环) → solve → end_rank → re_rank → scramble
    holder 守擂赛：预留
    team   组队赛：预留

各任务模块是独立类，有自己的 run() 入口，可单独测试：
    - ScreenLoop : 持续截图 / UI 检测
    - CubeLoop   : 魔方状态轮询 / 转动下发

任务通过 asyncio.Queue 通信，Controller 只负责组装 & 启动。
"""
import asyncio
import logging
import time
from pathlib import Path

from recipe.loader import RecipeLoader
from vision.screen_loop import ScreenLoop, ScrcpySource
from vision.detector import Detector
from device.cube_loop import CubeLoop
from device.scrcpy_client import ScrcpyClient
from device.cube_api import CubeAPI
from ocr.segmentor import segment
from ocr.classifier import create_classifier
from ocr.parser import parse
from solve import solve_cfop

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class Controller:
    """主控制器 —— 编排各独立任务"""

    def __init__(self, classifier_config: dict | None = None):
        self.recipe = RecipeLoader()
        self.scrcpy = ScrcpyClient(max_width=0, bitrate=200_000_000)
        self.cube = CubeAPI()
        self.detector = Detector(self.recipe.recipe)

        self.classifier_config = classifier_config or {"type": "knn"}
        self.classifier = None

        self.ui_event_queue: asyncio.Queue = asyncio.Queue()
        self.cube_event_queue: asyncio.Queue = asyncio.Queue()
        self.move_queue: asyncio.Queue = asyncio.Queue()

        self.screen_loop = ScreenLoop(ScrcpySource(self.scrcpy), self.recipe, self.ui_event_queue)
        self.cube_loop = CubeLoop(self.cube, self.cube_event_queue, self.move_queue)

        self.mode: str = self.recipe.recipe.mode
        self._scramble_seen_move = False
        self._running = False
        self._init_state()
        logger.info("Controller 初始化, mode=%s, state=%s", self.mode, self.state)

    def _init_state(self):
        if self.mode == "semi":
            self.state = "scramble"
        elif self.mode == "rank":
            self.state = "init"
        else:
            self.state = "wait_init"

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------

    async def run(self):
        """启动所有任务。"""
        self.scrcpy.connect()
        await self.cube.open()

        if self.classifier_config:
            self.classifier = create_classifier(self.classifier_config)

        tasks = [
            asyncio.create_task(self._state_machine(), name="state_machine"),
            asyncio.create_task(self.screen_loop.run(), name="screen_loop"),
            asyncio.create_task(self.cube_loop.run(), name="cube_loop"),
        ]
        logger.info("所有任务已启动")
        self._running = True
        try:
            await asyncio.gather(*tasks)
        finally:
            self.scrcpy.disconnect()
            await self.cube.close()

    # ------------------------------------------------------------------
    # 状态机
    # ------------------------------------------------------------------

    async def _state_machine(self):
        """根据 mode 加载对应状态处理器。"""
        handlers = _get_handlers(self.mode)
        while True:
            if len(handlers) == 0:
                await asyncio.sleep(1)
                continue
            handler = handlers.get(self.state)
            if handler:
                next_state = await handler(self)
                if next_state and next_state != self.state:
                    logger.info("状态转移: %s -> %s", self.state, next_state)
                    self.state = next_state
            else:
                logger.warning("未知状态: %s (mode=%s)", self.state, self.mode)
                await asyncio.sleep(1)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    async def _wait_for_ui(self, feature_name: str, timeout: float = 30.0) -> tuple[bool, any, any]:
        """轮询检测 UI 特征直到出现或超时。"""
        elapsed = 0.0
        last_log = 0.0
        while elapsed < timeout:
            frame = self.scrcpy.last_frame
            if frame is not None:
                matched, center = self.detector.detect(frame, feature_name)
                if matched:
                    return True, frame, center
                if elapsed - last_log >= 2.0:
                    logger.debug("init: 帧可用 (%dx%d)，未检测到 %s", frame.shape[1], frame.shape[0], feature_name)
                    last_log = elapsed
            else:
                if elapsed - last_log >= 2.0:
                    logger.debug("init: 等待 scrcpy 首帧...")
                    last_log = elapsed
            await asyncio.sleep(0.5)
            elapsed += 0.5
        return False, self.scrcpy.last_frame, None

    async def _click_feature(self, feature_name: str) -> bool:
        """检测并点击特征。"""
        frame = self.scrcpy.last_frame
        if frame is None:
            return False
        matched, center = self.detector.detect(frame, feature_name)
        if matched and center:
            logger.info("点击 %s @ (%d, %d)", feature_name, *center)
            self.scrcpy.tap(*center)
            return True
        return False


# ======================================================================
# Semi 模式：人类操作 UI，AI 只负责 scramble OCR + solve
# ======================================================================

async def _semi_scramble(self: Controller) -> str:
    """OCR 识别打乱序列，下发 ESP32，等待打乱 UI 消失后进入 solve。"""
    logger.info("semi/scramble: OCR 识别打乱序列...")
    frame = self.scrcpy.last_frame
    if frame is None:
        await asyncio.sleep(0.5)
        return "scramble"

    feat = self.recipe.recipe.feature("scramble_area")
    if feat and feat.roi:
        x, y, w, h = feat.roi
        crop = frame[y:y+h, x:x+w]
    else:
        crop = frame

    chars = segment(crop)
    if chars and self.classifier:
        char_imgs = [c[0] for c in chars]
        labels = self.classifier.predict_batch(char_imgs)
        moves = parse(labels)
        if moves:
            logger.info("scramble: 识别=%s", moves)
            await self.move_queue.put(moves)

    await asyncio.sleep(5.0)

    frame = self.scrcpy.last_frame
    if frame and self.detector:
        still_there, _ = self.detector.detect(frame, "scramble_area")
        if not still_there:
            logger.info("scramble: UI 消失，进入 solve")
            return "solve"
    return "scramble"


async def _semi_solve(self: Controller) -> str:
    """获取面片 → CFOP 求解 → 下发转动 → 回到 scramble。"""
    logger.info("semi/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        return "scramble"

    try:
        result = solve_cfop(facelets)
        solution = result["solution"]
        logger.info("solve: %s (%d步)", solution, len(solution.split()))
        await self.move_queue.put(solution)
    except Exception as e:
        logger.error("solve 失败: %s", e)
    return "scramble"


# ======================================================================
# Rank 模式：全自动排位赛
#   init(begin_rank) → scramble(segment循环) → solve → end_rank → re_rank → scramble
# ======================================================================

async def _rank_init(self: Controller) -> str:
    """检测并点击 begin_rank 按钮进入排位。"""
    logger.info("rank/init: 等待 begin_rank...")
    self._scramble_seen_move = False
    ok, _, _ = await self._wait_for_ui("begin_rank", timeout=60.0)
    if ok:
        await self._click_feature("begin_rank")
        await asyncio.sleep(2.0)
        return "scramble"
    return "init"


async def _rank_scramble(self: Controller) -> str:
    """持续检测打乱区域是否有字符气泡。

    有气泡 → 说明还在打乱界面，OCR 识别后下发，保持 scramble
    无气泡 → 说明已进入还原阶段，切换到 solve
    """
    frame = self.scrcpy.last_frame
    if frame is None:
        await asyncio.sleep(0.5)
        return "scramble"

    feat = self.recipe.recipe.feature("scramble_area")
    if feat and feat.roi:
        x, y, w, h = feat.roi
        crop = frame[y:y+h, x:x+w]
    else:
        crop = frame

    chars = segment(crop)
    if chars:
        logger.debug("rank/scramble: 检测到 %d 个字符区域，识别中...", len(chars))
        if self.classifier:
            char_imgs = [c[0] for c in chars]
            labels = self.classifier.predict_batch(char_imgs)

            # 保存每步所有字符区域到 debug/，便于后续重新打标训练
            ts = int(time.time())
            for idx, (char_img, (cx, cy, r)) in enumerate(chars):
                debug_dir = Path("debug") / "scramble"
                debug_dir.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(debug_dir / f"{ts}_{idx}.png"), char_img)

            moves = parse(labels)
            if moves:
                self._scramble_seen_move = True
                logger.info("rank/scramble: 帧=%d 分类=%s 识别=%s", ts, labels, moves)
                await self.move_queue.put(moves)
            else:
                logger.debug("rank/scramble: 分类=%s (无有效转动)", labels)
        await asyncio.sleep(1.0)
        return "scramble"
    else:
        if self._scramble_seen_move:
            logger.info("rank/scramble: 无字符区域，进入 solve")
            self._scramble_seen_move = False
            await asyncio.sleep(1.0)
            return "solve"
        logger.debug("rank/scramble: 无字符区域，等待出现转动气泡...")
        await asyncio.sleep(1.0)
        return "scramble"


async def _rank_solve(self: Controller) -> str:
    """获取面片 → CFOP 求解 → 下发转动 → 同时检测 scramble 和 end_rank。"""
    logger.info("rank/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        await asyncio.sleep(1.0)
        return "solve"

    try:
        result = solve_cfop(facelets)
        solution = result["solution"]
        logger.info("rank/solve: %s (%d步)", solution, len(solution.split()))
        await self.move_queue.put(solution)
    except Exception as e:
        logger.error("rank/solve 失败: %s", e)

    self._scramble_seen_move = False
    logger.info("rank/solve: 同时检测 scramble 和 end_rank...")
    elapsed = 0.0
    while elapsed < 180.0:
        frame = self.scrcpy.last_frame
        if frame is None:
            await asyncio.sleep(0.5)
            elapsed += 0.5
            continue

        matched_end, center_end = self.detector.detect(frame, "end_rank")
        if matched_end and center_end:
            logger.info("rank/solve: 检测到 end_rank，点击")
            self.scrcpy.tap(*center_end)
            await asyncio.sleep(2.0)
            return "re_rank"

        feat = self.recipe.recipe.feature("scramble_area")
        if feat and feat.roi:
            x, y, w, h = feat.roi
            crop = frame[y:y+h, x:x+w]
        else:
            crop = frame
        chars = segment(crop)
        if chars:
            logger.debug("rank/solve: 检测到 %d 个字符区域", len(chars))
            if self.classifier:
                char_imgs = [c[0] for c in chars]
                labels = self.classifier.predict_batch(char_imgs)
                moves = parse(labels)
                if moves:
                    self._scramble_seen_move = True
                    logger.info("rank/solve: 检测到新打乱，回到 scramble")
                    return "scramble"
        await asyncio.sleep(0.5)
        elapsed += 0.5
    return "solve"


async def _rank_re_rank(self: Controller) -> str:
    """检测并点击 re_rank 按钮，返回 scramble。"""
    self._scramble_seen_move = False
    logger.info("rank/re_rank: 等待 re_rank...")
    ok, _, center = await self._wait_for_ui("re_rank", timeout=30.0)
    if ok and center:
        logger.info("rank/re_rank: 点击 re_rank")
        self.scrcpy.tap(*center)
        await asyncio.sleep(2.0)
        return "scramble"
    return "re_rank"


# ======================================================================
# 默认 handler（空操作）
# ======================================================================

async def _noop(self: Controller) -> str:
    await asyncio.sleep(1.0)
    return self.state


# ======================================================================
# Handler 路由表
# ======================================================================

def _get_handlers(mode: str) -> dict[str, any]:
    if mode == "semi":
        return {
            "scramble": _semi_scramble,
            "solve": _semi_solve,
        }
    if mode == "rank":
        return {
            "init": _rank_init,
            "scramble": _rank_scramble,
            "solve": _rank_solve,
            "re_rank": _rank_re_rank,
        }
    return {}


# ------------------------------------------------------------------
# 单独测试入口
# ------------------------------------------------------------------

if __name__ == "__main__":
    """单独测试 Controller。

    示例：
        python controller.py                                    # 按 recipe mode 运行
        python controller.py --classifier cnn --host 192.168.50.246
    """
    import argparse

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--classifier", default="cnn",
                        choices=["knn", "template", "cnn", "hog_svm"],
                        help="分类器后端")
    parser.add_argument("--host", default="192.168.50.246", help="ESP32 IP")
    parser.add_argument("--mock", action="store_true", help="Mock 测试")
    args = parser.parse_args()

    classifier_config = {"type": args.classifier}

    async def main():
        controller = Controller(classifier_config=classifier_config)
        if args.mock:
            from device.cube_api import MockCubeAPI
            controller.cube = MockCubeAPI()
            controller.cube_loop.cube_api = controller.cube
            controller.scrcpy = ScrcpyClient()
            logger.info("Mock 模式")
        else:
            controller.cube = CubeAPI(host=args.host)
            controller.cube_loop.cube_api = controller.cube
        await controller.run()

    asyncio.run(main())
