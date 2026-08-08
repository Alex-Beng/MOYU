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
import random
import subprocess
import time
from pathlib import Path
from device.telnet import AsyncTelnetServer
from recipe.loader import RecipeLoader
from vision.screen_loop import ScreenLoop, ScrcpySource
from vision.detector import Detector
from device.cube_loop import CubeLoop
from device.scrcpy_client import ScrcpyClient
from device.cube_api import CubeAPI, parse_move_notation
from ocr.segmentor import segment
from ocr.classifier import create_classifier
from ocr.parser import parse
from solve import solve_cfop
from solve.solve import solve_pocket

import cv2
import numpy as np

logger = logging.getLogger(__name__)
DEBUG = False


class Controller:
    """主控制器 —— 编排各独立任务"""

    def __init__(self, classifier_config: dict | None = None, single_step: bool = False, initial_state: str | None = None, recipe_path: str | None = None, telnet_port: int | None = None, web_port: int = 8080, max_solves: int = 0):
        self.recipe = RecipeLoader(recipe_path) if recipe_path else RecipeLoader()
        self.scrcpy = ScrcpyClient(max_width=0, max_fps=10, bitrate=200_000_000)
        self._telnet_port = telnet_port
        self._web_port = web_port
        self.cube = CubeAPI(single_step=single_step)
        self.detector = Detector(self.recipe.recipe)

        self.classifier_config =  classifier_config or {"type": "cnn"}
        self.classifier = None

        self.ui_event_queue: asyncio.Queue = asyncio.Queue()
        self.cube_event_queue: asyncio.Queue = asyncio.Queue()
        self.move_queue: asyncio.Queue = asyncio.Queue()

        self.screen_loop = ScreenLoop(ScrcpySource(self.scrcpy), self.recipe, self.ui_event_queue)
        self.cube_loop = CubeLoop(self.cube, self.cube_event_queue, self.move_queue)

        self.mode: str = self.recipe.recipe.mode
        self._scramble_seen_move = False
        self._no_scramble_cnt = 0
        self._last_move = None
        self._scramble_move_history: list[str] = []
        self._scramble_skip_cnt = 0
        self._running = False
        self._paused = False
        self._start_time = time.monotonic()
        self._max_solves = max_solves
        self._solve_count = 0
        self._tasks = None
        self._init_state()
        if initial_state is not None:
            self.state = initial_state
        logger.info("Controller 初始化, mode=%s, state=%s", self.mode, self.state)

    def _init_state(self):
        if self.mode == "semi":
            self.state = "scramble"
        elif self.mode == "rank":
            self.state = "init"
        elif self.mode == "holder":
            self.state = "init"
        elif self.mode == "team":
            self.state = "init"
        elif self.mode == "week":
            self.state = "init"
        elif self.mode == "solo":
            self.state = "init"
        elif self.mode == "remote":
            self.state = "scramble"
        else:
            self.state = "wait_init"

    # ------------------------------------------------------------------
    # 暂停 / 继续
    # ------------------------------------------------------------------

    def pause(self):
        """暂停状态机。"""
        self._paused = True
        logger.info("⏸ 已暂停")

    def resume(self):
        """继续状态机。"""
        self._paused = False
        logger.info("▶ 已继续")

    @property
    def is_paused(self):
        return self._paused

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
        self._tasks = tasks

        if self._telnet_port:
            telnet_task = asyncio.create_task(self._start_telnet(), name="telnet_server")
            tasks.append(telnet_task)
            logger.info(f"Telnet REPL 启动在端口 {self._telnet_port}")

        if self._web_port > 0:
            from web.frame_server import WebFrameServer
            web_task = asyncio.create_task(WebFrameServer(self, port=self._web_port).start(), name="web_server")
            tasks.append(web_task)

        logger.info("所有任务已启动")
        self._running = True
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
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
            while self._paused:
                await asyncio.sleep(0.5)
            if len(handlers) == 0:
                await asyncio.sleep(1)
                continue
            handler = handlers.get(self.state)
            if handler:
                next_state = await handler(self)
                if next_state and next_state != self.state:
                    prev_state = self.state
                    if next_state == "solve":
                        self._solve_count += 1
                        logger.info("solve 次数: %d/%d", self._solve_count, self._max_solves or 0)
                    logger.info("状态转移: %s -> %s", self.state, next_state)
                    self.state = next_state
                    await self._apply_delay()
                    if self._max_solves > 0 and prev_state == "solve" and self._solve_count >= self._max_solves:
                        logger.info("已完成 %d 次 solve，达到目标次数，锁屏退出", self._max_solves)
                        subprocess.run(["adb", "shell", "input", "keyevent", "26"], capture_output=True)
                        for task in self._tasks:
                            if not task.done():
                                task.cancel()
                        return
            else:
                logger.warning("未知状态: %s (mode=%s)", self.state, self.mode)
                await asyncio.sleep(1)

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    async def _start_telnet(self):
        namespace = {
            'controller': self,
            'recipe': self.recipe.recipe,
            'cube': self.cube,
            'scrcpy': self.scrcpy,
            'detector': self.detector,
            'logger': logger,
        }
        srv = AsyncTelnetServer('0.0.0.0', self._telnet_port, namespace)
        await srv.start()

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _drain_queue(q: asyncio.Queue):
        """清空 asyncio.Queue 中所有残留项。"""
        while not q.empty():
            try:
                q.get_nowait()
                q.task_done()
            except asyncio.QueueEmpty:
                break

    async def _apply_delay(self):
        """根据当前状态设置 ESP32 转动延迟。"""
        recipe = self.recipe.recipe
        if self.state == "scramble":
            self._drain_queue(self.move_queue)
            await self.cube.clear_moves()
            self._scramble_move_history = []
            self._scramble_skip_cnt = 0
            if recipe.scramble_delay is not None:
                await self.cube.set_delay(recipe.scramble_delay)
                logger.debug("scramble_delay = %d ms", recipe.scramble_delay)
        elif self.state == "solve" and recipe.solve_delay is not None:
            await self.cube.set_delay(recipe.solve_delay)
            logger.debug("solve_delay = %d ms", recipe.solve_delay)

    def _build_phased_moves(self, result: dict) -> list:
        """根据 CFOP 求解结果和 recipe 的 per-phase delay 构建带内联 delay 的 moves 列表。"""
        recipe = self.recipe.recipe
        steps = []

        def _parse(move_str):
            if recipe.move_format == "str":
                return [{"move": t} for t in move_str.split() if t]
            return parse_move_notation(move_str)

        if result.get("cross"):
            if recipe.cross_time:
                steps.append({"time": recipe.cross_time})
            if recipe.cross_delay:
                steps.append({"delay": recipe.cross_delay})
            steps.extend(_parse(result["cross"]))

        if result.get("f2l"):
            if recipe.f2l_time:
                steps.append({"time": recipe.f2l_time})
            if recipe.f2l_delay:
                steps.append({"delay": recipe.f2l_delay})
            steps.extend(_parse(result["f2l"]))

        if result.get("alll"):
            if recipe.alll_time:
                print("alll_time", recipe.alll_time)
                steps.append({"time": recipe.alll_time})
            if recipe.alll_delay:
                steps.append({"delay": recipe.alll_delay})
            steps.extend(_parse(result["alll"]))
        else:
            if result.get("oll"):
                if recipe.oll_time:
                    print("oll_time", recipe.oll_time)
                    steps.append({"time": recipe.oll_time})
                if recipe.oll_delay:
                    steps.append({"delay": recipe.oll_delay})
                steps.extend(_parse(result["oll"]))
            if result.get("pll"):
                if recipe.pll_time:
                    steps.append({"time": recipe.pll_time})
                if recipe.pll_delay:
                    steps.append({"delay": recipe.pll_delay})
                steps.extend(_parse(result["pll"]))

        return steps

    def _build_pocket_moves(self, result: dict) -> list:
        """根据二阶求解结果构建 moves 列表。"""
        recipe = self.recipe.recipe
        steps = []

        def _parse(move_str):
            if recipe.move_format == "str":
                return [{"move": t} for t in move_str.split() if t]
            return parse_move_notation(move_str)

        # cross = first_layer; oll = oll; pbl = alll
        if result.get("first_layer"):
            if recipe.cross_time:
                steps.append({"time": recipe.cross_time})
            if recipe.cross_delay:
                steps.append({"delay": recipe.cross_delay})
            steps.extend(_parse(result["first_layer"]))

        if result.get("oll"):
            if recipe.oll_time:
                print("oll_time", recipe.oll_time)
                steps.append({"time": recipe.oll_time})
            if recipe.oll_delay:
                steps.append({"delay": recipe.oll_delay})
            steps.extend(_parse(result["oll"]))
        if result.get("pbl"):
            if recipe.alll_time:
                print("alll_time", recipe.alll_time)
                steps.append({"time": recipe.alll_time})
            if recipe.alll_delay:
                steps.append({"delay": recipe.alll_delay})
            steps.extend(_parse(result["pbl"]))

        return steps

    async def _do_solve(self, facelets: str) -> dict | None:
        """根据 recipe.cube 和 recipe.solve_method 选择求解器。

        三阶: solve_cfop, 二阶: solve_pocket (ortega/eg)
        返回求解结果 dict 或 None。
        """
        recipe = self.recipe.recipe
        if recipe.cube == "pocket":
            return solve_pocket(facelets, method=recipe.solve_method)
        else:
            return solve_cfop(facelets, rotation=recipe.rotation, alll_prob=recipe.alll_prob)

    async def _wait_for_ui(self, feature_name: str, timeout: float = 30.0) -> tuple[bool, any, any]:
        """轮询检测 UI 特征直到出现或超时。"""
        elapsed = 0.0
        last_log = 0.0
        if DEBUG:
            cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        while elapsed < timeout:
            frame = self.scrcpy.last_frame
            if frame is not None:
                if DEBUG:
                    cv2.imshow("frame", frame)
                    key = cv2.waitKey(1) & 0xFF
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
        # cv2.destroyAllWindows()
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

    def set_state(self, state: str):
        """运行时强制跳转状态（Web 终端 / Telnet 调用）。"""
        if state not in _get_handlers(self.mode):
            logger.warning("当前 mode=%s 不支持状态: %s", self.mode, state)
            return
        self.state = state
        self._scramble_seen_move = False
        self._no_scramble_cnt = 0
        self._scramble_move_history = []
        logger.info("状态已强制跳转: %s", state)

    async def switch_recipe(self, path: str, state: str | None = None):
        """运行时切换 recipe 并可选跳转状态。"""
        self.recipe.switch(path)
        self.mode = self.recipe.recipe.mode
        self.detector = Detector(self.recipe.recipe)
        self._drain_queue(self.move_queue)
        await self.cube.clear_moves()
        if self.classifier_config:
            self.classifier = create_classifier(self.classifier_config)
        self._init_state()
        if state is not None:
            self.state = state
        logger.info("recipe 已切换: %s, mode=%s, state=%s", path, self.mode, self.state)


#region semi
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
        mid = frame.shape[0] // 2
        crop = frame[mid:, :]

    chars = segment(crop)
    if chars and self.classifier:
        # if not self._scramble_seen_move:
        #     await self.cube.clear_moves()
        char_imgs = [c[0] for c in chars]
        labels = self.classifier.predict_batch(char_imgs)
        moves = parse(labels)
        if moves:
            _dup = False
            for n in range(2, len(moves) + 1):
                if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                    _dup = True
                    break
            if _dup:
                logger.debug(f"semi/scramble: {moves} vs {self._scramble_move_history} 跳过")
                await asyncio.sleep(0.5)
                return "scramble"
            self._scramble_move_history = moves
            logger.info("scramble: 识别=%s", moves)
            await self.move_queue.put(moves)
            self._scramble_seen_move = True
            self._no_scramble_cnt = 0
        else:
            logger.debug("scramble: 分类=%s (无有效转动)", labels)
    else:
        self._no_scramble_cnt += 1
        if not chars and self._no_scramble_cnt > 1:
            # 无气泡持续3次以上 = 打乱结束
            if self._scramble_seen_move:
                logger.info("scramble: 无字符区域且已下发过转动，进入 solve")
                self._scramble_seen_move = False
                self._no_scramble_cnt = 0
                self._scramble_move_history = []
                return "solve"
            logger.debug("scramble: 无字符区域，等待打乱出现...")

    await asyncio.sleep(1.0)
    return "scramble"


async def _semi_solve(self: Controller) -> str:
    """获取面片 → 求解 → 下发转动 → 回到 scramble。"""
    logger.info("semi/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        logger.warning("semi/solve: facelets 无效 (len=%d): %r", len(facelets) if facelets else 0, facelets)
        await asyncio.sleep(1.0)
        return "scramble"

    try:
        result = await self._do_solve(facelets)
        solution = result["solution"]
        logger.info("semi/solve: %s (%d步)", solution, len(solution.split()))
        if self.recipe.recipe.cube == "pocket":
            await self.move_queue.put(self._build_pocket_moves(result))
        else:
            await self.move_queue.put(self._build_phased_moves(result))
    except Exception as e:
        logger.error("semi/solve 失败: %s", e, exc_info=True)
    return "scramble"
#endregion

#region rank
# ======================================================================
# Rank 模式：全自动排位赛
#   init(begin_rank) → scramble(segment循环) → solve → end_rank → re_rank → scramble
# ======================================================================

async def _rank_init(self: Controller) -> str:
    """检测并点击 begin_rank 按钮进入排位。"""
    logger.info("rank/init: 等待 begin_rank...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    ok, _, _ = await self._wait_for_ui("begin_rank", timeout=60.0)
    if ok:
        await self._click_feature("begin_rank")
        await asyncio.sleep(2.0)
        self._scramble_move_history = []
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
    if DEBUG:
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame", self.scrcpy.last_frame)
        cv2.waitKey(1) & 0xFF

    feat = self.recipe.recipe.feature("scramble_area")
    if feat and feat.roi:
        x, y, w, h = feat.roi
        crop = frame[y:y+h, x:x+w]
    else:
        mid = frame.shape[0] // 2
        crop = frame[mid:, :]

    chars = segment(crop)
    if chars:
        # if not self._scramble_seen_move:
        #     await self.cube.clear_moves()
        logger.debug("rank/scramble: 检测到 %d 个字符区域，识别中...", len(chars))
        if self.classifier:
            char_imgs = [c[0] for c in chars]
            labels = self.classifier.predict_batch(char_imgs)

            # 保存每步所有字符区域到 debug/，便于后续重新打标训练
            ts = int(time.time())
            for idx, (char_img, (cx, cy, r)) in enumerate(chars):
                label = labels[idx]
                if label == "EMPTY":
                    continue
                debug_dir = Path("debug") / "scramble"
                debug_dir.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(debug_dir / f"{ts}_{idx}_{label}.png"), char_img)

            moves = parse(labels)
            if moves and (self._last_move != moves or True):
                _dup = False
                for n in range(2, len(moves) + 1):
                    if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                        _dup = True
                        break
                if _dup:
                    self._scramble_skip_cnt += 1
                    logger.debug(f"rank/scramble: {moves} vs {self._scramble_move_history} 跳过 ({self._scramble_skip_cnt}/5)")
                    if self._scramble_skip_cnt >= 5:
                        logger.info("rank/scramble: 连续跳过5次，清历史重新下发")
                        self._scramble_skip_cnt = 0
                        self._scramble_move_history = []
                        self._last_move = None
                    await asyncio.sleep(0.5)
                    return "scramble"
                self._scramble_skip_cnt = 0
                self._scramble_move_history = moves
                self._scramble_seen_move = True
                self._no_scramble_cnt = 0
                self._last_move = moves
                logger.info("rank/scramble: 帧=%d 分类=%s 识别=%s", ts, labels, moves)
                await self.move_queue.put(moves)
                await asyncio.sleep(0.5)
            else:
                self._no_scramble_cnt += 1
                logger.debug("rank/scramble: 分类=%s (无有效转动)", labels)

                # 保底：可能退回到初始界面（begin_rank）——10个空气泡界面
                matched_bg, center_bg = self.detector.detect(frame, "begin_rank")
                if matched_bg and center_bg:
                    logger.info("rank/scramble: 检测到 begin_rank（退回初始界面），点击后重新等待")
                    self.scrcpy.tap(*center_bg)
                    await asyncio.sleep(2.0)
                    self._scramble_move_history = []
                    self._scramble_seen_move = False
                    self._no_scramble_cnt = 0
                    return "scramble"

                if self._scramble_seen_move and not moves and self._no_scramble_cnt > 1:
                    logger.info("rank/scramble: 无有效转动且持续多帧，可能打乱结束，进入 solve")
                    self._scramble_seen_move = False
                    self._no_scramble_cnt = 0
                    self._scramble_move_history = []
                    return "solve"
        await asyncio.sleep(1.0)
        return "scramble"
    else:
        self._no_scramble_cnt += 1
        if self._scramble_seen_move and self._no_scramble_cnt > 1:
            logger.info("rank/scramble: 无字符区域，进入 solve")
            self._scramble_seen_move = False
            self._no_scramble_cnt = 0
            self._scramble_move_history = []
            await asyncio.sleep(1.0)
            return "solve"
        logger.debug("rank/scramble: 无字符区域，等待出现转动气泡...")
        await asyncio.sleep(1.0)
        return "scramble"


async def _rank_solve(self: Controller) -> str:
    """获取面片 → 求解 → 下发转动 → 同时检测 scramble 和 end_rank。"""
    logger.info("rank/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        logger.warning("rank/solve: facelets 无效 (len=%d): %r", len(facelets) if facelets else 0, facelets)
        await asyncio.sleep(1.0)
        return "solve"

    try:
        result = await self._do_solve(facelets)
        solution = result["solution"]
        logger.info("rank/solve: %s (%d步)", solution, len(solution.split()))
        if self.recipe.recipe.cube == "pocket":
            await self.move_queue.put(self._build_pocket_moves(result))
        else:
            await self.move_queue.put(self._build_phased_moves(result))
    except Exception as e:
        logger.error("rank/solve 失败: %s", e, exc_info=True)

    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    self._last_move = None
    self._scramble_move_history = []
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
        
        matched_end, center_end = self.detector.detect(frame, "re_rank")
        if matched_end and center_end:
            logger.info("rank/solve: 检测到 re_rank，点击")
            self.scrcpy.tap(*center_end)
            await asyncio.sleep(2.0)
            return "scramble"

        feat = self.recipe.recipe.feature("scramble_area")
        if feat and feat.roi:
            x, y, w, h = feat.roi
            crop = frame[y:y+h, x:x+w]
        else:
            mid = frame.shape[0] // 2
            crop = frame[mid:, :]
        chars = segment(crop)
        if chars:
            logger.debug("rank/solve: 检测到 %d 个字符区域", len(chars))
            if self.classifier:
                char_imgs = [c[0] for c in chars]
                labels = self.classifier.predict_batch(char_imgs)
                moves = parse(labels)
                if moves:
                    _dup = False
                    for n in range(2, len(moves) + 1):
                        if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                            _dup = True
                            break
                    if _dup:
                        logger.debug(f"rank/solve: {moves} vs {self._scramble_move_history} 跳过")
                        await asyncio.sleep(0.5)
                        elapsed += 0.5
                        continue
                    self._scramble_seen_move = True
                    logger.info("rank/solve: 检测到新打乱，回到 scramble")
                    return "scramble"
        await asyncio.sleep(0.5)
        elapsed += 0.5
    return "solve"


async def _rank_re_rank(self: Controller) -> str:
    """检测并点击 re_rank 按钮，返回 scramble。"""
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    self._scramble_move_history = []
    logger.info("rank/re_rank: 等待 re_rank...")
    ok, _, center = await self._wait_for_ui("re_rank", timeout=5.0)
    if ok and center:
        logger.info("rank/re_rank: 点击 re_rank")
        self.scrcpy.tap(*center)
        await asyncio.sleep(2.0)
        self._scramble_move_history = []
        return "scramble"
    else:
        # 说明直接被踢回init界面了
        logger.info("rank/re_rank: 超时， 可能被踢回begin界面了")
        ok, _, center = await self._wait_for_ui("begin_rank", timeout=5.0)
        if ok and center:
            logger.info("rank/re_rank: 检测到 begin_rank，点击")
            self.scrcpy.tap(*center)
            await asyncio.sleep(2.0)
    return "re_rank"
#endregion

#region solo
# ======================================================================
# Solo 模式：日赛
#   init → (持续点击 begin_solo，直到打乱出现) → scramble → solve → (re_solo → init / 新打乱 → scramble)
# ======================================================================

async def _solo_init(self: Controller) -> str:
    """持续检测 begin_solo 并点击；当打乱气泡出现时跳转 scramble。"""
    logger.info("solo/init: 持续检测 begin_solo，等待打乱出现...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    self._scramble_move_history = []

    while True:
        frame = self.scrcpy.last_frame
        if frame is None:
            await asyncio.sleep(0.5)
            continue

        feat = self.recipe.recipe.feature("scramble_area")
        if feat and feat.roi:
            x, y, w, h = feat.roi
            crop = frame[y:y+h, x:x+w]
        else:
            mid = frame.shape[0] // 2
            crop = frame[mid:, :]
        chars = segment(crop)
        if chars:
            logger.info("solo/init: 检测到打乱气泡，跳转 scramble")
            return "scramble"

        matched, center = self.detector.detect(frame, "begin_solo")
        if matched and center:
            logger.info("solo/init: 点击 begin_solo")
            self.scrcpy.tap(*center)

        await asyncio.sleep(0.5)


async def _solo_scramble(self: Controller) -> str:
    """复用 rank scramble 逻辑。"""
    return await _rank_scramble(self)


async def _solo_solve(self: Controller) -> str:
    """获取面片 → 求解 → 下发转动 → 检测 re_solo 或新打乱。"""
    logger.info("solo/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        logger.warning("solo/solve: facelets 无效 (len=%d)", len(facelets) if facelets else 0)
        await asyncio.sleep(1.0)
        return "solve"

    try:
        result = await self._do_solve(facelets)
        solution = result["solution"]
        logger.info("solo/solve: %s (%d步)", solution, len(solution.split()))
        if self.recipe.recipe.cube == "pocket":
            await self.move_queue.put(self._build_pocket_moves(result))
        else:
            await self.move_queue.put(self._build_phased_moves(result))
    except Exception as e:
        logger.error("solo/solve 失败: %s", e, exc_info=True)

    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    self._last_move = None
    self._scramble_move_history = []
    logger.info("solo/solve: 检测 re_solo 或新打乱...")
    elapsed = 0.0
    while elapsed < 180.0:
        frame = self.scrcpy.last_frame
        if frame is None:
            await asyncio.sleep(0.5)
            elapsed += 0.5
            continue

        matched, center = self.detector.detect(frame, "re_solo")
        if matched and center:
            logger.info("solo/solve: 检测到 re_solo，点击后回到 init")
            self.scrcpy.tap(*center)
            await asyncio.sleep(2.0)
            return "init"

        feat = self.recipe.recipe.feature("scramble_area")
        if feat and feat.roi:
            x, y, w, h = feat.roi
            crop = frame[y:y+h, x:x+w]
        else:
            mid = frame.shape[0] // 2
            crop = frame[mid:, :]
        chars = segment(crop)
        if chars:
            if self.classifier:
                char_imgs = [c[0] for c in chars]
                labels = self.classifier.predict_batch(char_imgs)
                moves = parse(labels)
                if moves:
                    _dup = False
                    for n in range(2, len(moves) + 1):
                        if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                            _dup = True
                            break
                    if _dup:
                        await asyncio.sleep(0.5)
                        elapsed += 0.5
                        continue
                    self._scramble_seen_move = True
                    logger.info("solo/solve: 检测到新打乱，回到 scramble")
                    return "scramble"
        await asyncio.sleep(0.5)
        elapsed += 0.5
    return "solve"
#endregion

#region holder
# ======================================================================
# Holder 模式：擂台赛
#   init(begin_holder) → scramble → solve → re_holder → init
# ======================================================================

async def _holder_init(self: Controller) -> str:
    """检测并点击 begin_holder 按钮进入擂台挑战。"""
    logger.info("holder/init: 等待 begin_holder...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    ok, _, center = await self._wait_for_ui("begin_holder", timeout=60.0)
    if ok and center:
        logger.info("holder/init: 点击 begin_holder")
        self.scrcpy.tap(*center)
        await asyncio.sleep(2.0)
        self._scramble_move_history = []
        return "scramble"
    return "init"


async def _holder_scramble(self: Controller) -> str:
    """与 rank scramble 逻辑相同：持续检测气泡 → 识别 → 下发 → 等待气泡消失。"""
    return await _rank_scramble(self)


async def _holder_solve(self: Controller) -> str:
    """获取面片 → 求解 → 下发转动 → 等待 re_holder。"""
    logger.info("holder/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        await asyncio.sleep(1.0)
        return "solve"

    try:
        result = await self._do_solve(facelets)
        solution = result["solution"]
        logger.info("holder/solve: %s (%d步)", solution, len(solution.split()))
        if self.recipe.recipe.cube == "pocket":
            await self.move_queue.put(self._build_pocket_moves(result))
        else:
            await self.move_queue.put(self._build_phased_moves(result))
    except Exception as e:
        logger.error("holder/solve 失败: %s", e)

    logger.info("holder/solve: 等待 re_holder...")
    ok, _, center = await self._wait_for_ui("re_holder", timeout=120.0)
    if ok and center:
        logger.info("holder/solve: 点击 re_holder")
        self.scrcpy.tap(*center)
        await asyncio.sleep(2.0)
        return "re_holder"
    return "solve"


async def _holder_re_holder(self: Controller) -> str:
    """re_holder 点击后回到 init 等待下一把。"""
    logger.info("holder/re_holder: 返回 init")
    self._scramble_move_history = []
    await asyncio.sleep(1.0)
    return "init"
#endregion holder

#region team
# ======================================================================
# Team 模式：战队赛
#   init(begin_holder) → scramble → solve → re_holder → init
# ======================================================================

async def _team_init(self: Controller) -> str:
    """检测并点击 begin_team 按钮进入战队赛。"""
    logger.info("team/init: 等待 begin_team...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    ok, _, _ = await self._wait_for_ui("begin_team", timeout=10.0)
    if ok:
        await self._click_feature("begin_team")
        await asyncio.sleep(2.0)
        self._scramble_move_history = []
        return "scramble"
    return "init"

async def _team_scramble(self: Controller) -> str:
    """与 rank scramble 逻辑相同：持续检测气泡 → 识别 → 下发 → 等待气泡消失。"""
    return await _rank_scramble(self)

async def _team_solve(self: Controller) -> str:
    """获取面片 → 求解 → 下发转动 → 等待 re_holder。"""
    logger.info("team/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        await asyncio.sleep(1.0)
        return "solve"

    try:
        result = await self._do_solve(facelets)
        solution = result["solution"]
        logger.info("team/solve: %s (%d步)", solution, len(solution.split()))
        if self.recipe.recipe.cube == "pocket":
            await self.move_queue.put(self._build_pocket_moves(result))
        else:
            await self.move_queue.put(self._build_phased_moves(result))
    except Exception as e:
        logger.error("team/solve 失败: %s", e)

    self._scramble_move_history = []
    logger.info("team/solve: 同时检测 scramble 和 continue_team 和 re_team...")
    elapsed = 0.0
    while elapsed < 180.0:
        frame = self.scrcpy.last_frame
        if frame is None:
            await asyncio.sleep(0.5)
            elapsed += 0.5
            continue

        matched_end, center_end = self.detector.detect(frame, "continue_team")
        if matched_end and center_end:
            logger.info("team/solve: 检测到 continue_team，点击")
            self.scrcpy.tap(*center_end)
            await asyncio.sleep(2.0)
            return "re_team"
        
        matched_end, center_end = self.detector.detect(frame, "re_team")
        if matched_end and center_end:
            logger.info("team/solve: 检测到 re_team ，点击")
            self.scrcpy.tap(*center_end)
            await asyncio.sleep(2.0)
            return "init"

        feat = self.recipe.recipe.feature("scramble_area")
        if feat and feat.roi:
            x, y, w, h = feat.roi
            crop = frame[y:y+h, x:x+w]
        else:
            mid = frame.shape[0] // 2
            crop = frame[mid:, :]
        chars = segment(crop)
        if chars:
            logger.debug("team/solve: 检测到 %d 个字符区域", len(chars))
            if self.classifier:
                char_imgs = [c[0] for c in chars]
                labels = self.classifier.predict_batch(char_imgs)
                moves = parse(labels)
                if moves:
                    _dup = False
                    for n in range(2, len(moves) + 1):
                        if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                            _dup = True
                            break
                    if _dup:
                        logger.debug(f"team/solve: {moves} vs {self._scramble_move_history} 跳过")
                        await asyncio.sleep(0.5)
                        elapsed += 0.5
                        continue
                    self._scramble_seen_move = True
                    logger.info("team/solve: 检测到新打乱，回到 scramble")
                    return "scramble"
        await asyncio.sleep(0.5)
        elapsed += 0.5
    return "solve"

async def _team_re_team(self: Controller) -> str:
    """持续点击 re_team 直到模板匹配失败，再返回 init。"""
    logger.info("team/re_team: 持续点击 re_team 直到消失...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    while True:
        frame = self.scrcpy.last_frame
        if frame is None:
            await asyncio.sleep(0.2)
            continue
        matched, center = self.detector.detect(frame, "re_team")
        if not matched:
            logger.info("team/re_team: re_team 消失，跳转 init")
            self._scramble_move_history = []
            return "init"
        await self._click_feature("re_team")
        await asyncio.sleep(0.5)
#endregion

#region week
# ======================================================================
# Week 模式：周赛
#   init(begin_team) → scramble → solve → continue_week/re_week → init
# ======================================================================

async def _week_init(self: Controller) -> str:
    """检测并点击 begin_team 按钮进入周赛。"""
    logger.info("week/init: 等待 begin_team...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    ok, _, _ = await self._wait_for_ui("begin_team", timeout=10.0)
    if ok:
        await self._click_feature("begin_team")
        await asyncio.sleep(2.0)
        self._scramble_move_history = []
        return "scramble"
    return "init"


async def _week_scramble(self: Controller) -> str:
    """与 rank scramble 逻辑相同：持续检测气泡 → 识别 → 下发 → 等待气泡消失。"""
    return await _rank_scramble(self)


async def _week_solve(self: Controller) -> str:
    """获取面片 → 求解 → 下发转动 → 同时检测 scramble 和 continue_week 和 re_week。"""
    logger.info("week/solve: 求解...")
    facelets = await self.cube.get_facelets()
    if not facelets or len(facelets) != 54:
        await asyncio.sleep(1.0)
        return "solve"

    try:
        result = await self._do_solve(facelets)
        solution = result["solution"]
        logger.info("week/solve: %s (%d步)", solution, len(solution.split()))
        if self.recipe.recipe.cube == "pocket":
            moves = self._build_pocket_moves(result)
        else:
            moves = self._build_phased_moves(result)
        delay = random.uniform(0, 5)
        logger.info("week/solve: 随机延迟 %.1fs 后下发", delay)
        await asyncio.sleep(delay)
        await self.move_queue.put(moves)
    except Exception as e:
        logger.error("week/solve 失败: %s", e)

    self._scramble_move_history = []
    logger.info("week/solve: 同时检测 scramble 和 continue_week 和 re_week...")
    elapsed = 0.0
    while elapsed < 180.0:
        frame = self.scrcpy.last_frame
        if frame is None:
            await asyncio.sleep(0.5)
            elapsed += 0.5
            continue

        matched_end, center_end = self.detector.detect(frame, "continue_week")
        if matched_end and center_end:
            logger.info("week/solve: 检测到 continue_week，点击")
            await asyncio.sleep(1.0)
            self.scrcpy.tap(*center_end)
            return "re_week"

        matched_end, center_end = self.detector.detect(frame, "re_week")
        if matched_end and center_end:
            logger.info("week/solve: 检测到 re_week，点击")
            self.scrcpy.tap(*center_end)
            await asyncio.sleep(2.0)
            return "init"

        feat = self.recipe.recipe.feature("scramble_area")
        if feat and feat.roi:
            x, y, w, h = feat.roi
            crop = frame[y:y+h, x:x+w]
        else:
            mid = frame.shape[0] // 2
            crop = frame[mid:, :]
        chars = segment(crop)
        if chars:
            logger.debug("week/solve: 检测到 %d 个字符区域", len(chars))
            if self.classifier:
                char_imgs = [c[0] for c in chars]
                labels = self.classifier.predict_batch(char_imgs)
                moves = parse(labels)
                if moves:
                    _dup = False
                    for n in range(2, len(moves) + 1):
                        if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                            _dup = True
                            break
                    if _dup:
                        logger.debug(f"week/solve: {moves} vs {self._scramble_move_history} 跳过")
                        await asyncio.sleep(0.5)
                        elapsed += 0.5
                        continue
                    self._scramble_seen_move = True
                    logger.info("week/solve: 检测到新打乱，回到 scramble")
                    return "scramble"
        await asyncio.sleep(0.5)
        elapsed += 0.5
    return "solve"


async def _week_re_week(self: Controller) -> str:
    """检测并点击 re_week 返回周赛开始界面。"""
    logger.info("week/re_week: 等待 re_week...")
    self._scramble_seen_move = False
    self._no_scramble_cnt = 0
    ok, _, _ = await self._wait_for_ui("re_week", timeout=60.0)
    if ok:
        await self._click_feature("re_week")
        await asyncio.sleep(2.0)
        self._scramble_move_history = []
        return "init"
    return "re_week"
#endregion


#region remote
# ======================================================================
# remote 模式：vrc手动复原
#   scramble → solve(等待下一把打乱) → scramble
# ======================================================================

async def _remote_scramble(self: Controller) -> str:
    """与 rank scramble 逻辑相同：持续检测气泡 → 识别 → 下发 → 等待气泡消失。"""
    return await _rank_scramble(self)


async def _remote_solve(self: Controller) -> str:
    """等待下一把打乱出现：持续检测圆形区域，有有效转动时回到 scramble。"""
    self._scramble_move_history = []
    frame = self.scrcpy.last_frame
    if frame is None:
        await asyncio.sleep(0.5)
        return "solve"

    feat = self.recipe.recipe.feature("scramble_area")
    if feat and feat.roi:
        x, y, w, h = feat.roi
        crop = frame[y:y+h, x:x+w]
    else:
        mid = frame.shape[0] // 2
        crop = frame[mid:, :]
    chars = segment(crop)
    if chars and self.classifier:
        char_imgs = [c[0] for c in chars]
        labels = self.classifier.predict_batch(char_imgs)
        moves = parse(labels)
        if moves:
            _dup = False
            for n in range(2, len(moves) + 1):
                if len(self._scramble_move_history) >= n and self._scramble_move_history[-n:] == moves:
                    _dup = True
                    break
            if _dup:
                logger.debug(f"remote/solve: {moves} vs {self._scramble_move_history} 跳过")
                await asyncio.sleep(0.5)
                return "solve"
            logger.info("remote/solve: 检测到新打乱=%s，回到 scramble", moves)
            return "scramble"

    await asyncio.sleep(0.5)
    return "solve"
#endregion

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
    if mode == "holder":
        return {
            "init": _holder_init,
            "scramble": _holder_scramble,
            "solve": _holder_solve,
            "re_holder": _holder_re_holder,
        }
    if mode == "team":
        return {
            "init": _team_init,
            "scramble": _team_scramble,
            "solve": _team_solve,
            "re_team": _team_re_team,
        }
    if mode == "week":
        return {
            "init": _week_init,
            "scramble": _week_scramble,
            "solve": _week_solve,
            "re_week": _week_re_week,
        }
    if mode == "solo":
        return {
            "init": _solo_init,
            "scramble": _solo_scramble,
            "solve": _solo_solve,
        }
    if mode == "remote":
        return {
            "scramble": _remote_scramble,
            "solve": _remote_solve,
        }
    return {}


# ------------------------------------------------------------------
# 单独测试入口
# ------------------------------------------------------------------

if __name__ == "__main__":
    """单独测试 Controller。

    示例：
        python controller.py                                    # 按 recipe mode 运行
        python controller.py --classifier cnn --host 192.168.50.246 --single-step
    """
    import argparse
    from pathlib import Path

    LOG_DIR = Path("log")
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "controller.log", encoding="utf-8"),
        ],
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--recipe", default="example.json", help="recipe JSON 路径")
    parser.add_argument("--classifier", default="cnn",
                        choices=["knn", "template", "cnn", "hog_svm"],
                        help="分类器后端")
    parser.add_argument("--host", default="192.168.50.246", help="ESP32 IP")
    parser.add_argument("--mock", action="store_true", help="Mock 测试")
    parser.add_argument("--single-step", action="store_true", help="逐步下发转动 (debug)")
    parser.add_argument("--state", default=None, help="指定初始状态 (覆盖 mode 默认值，如 scramble/solve/re_rank)")
    parser.add_argument("--telnet", type=int, default=5556, metavar="PORT", help="启动 telnet REPL 服务器 (默认 5556，设为 0 禁用)")
    parser.add_argument("--web-port", type=int, default=8080, metavar="PORT", help="Web 终端端口 (默认 8080，设为 0 关闭)")
    parser.add_argument("--max-solves", type=int, default=0, metavar="N", help="达到 N 次 solve 后自动锁屏退出 (0=不限制)")
    args = parser.parse_args()

    classifier_config = {"type": args.classifier}

    async def main():
        controller = Controller(
            classifier_config=classifier_config,
            single_step=args.single_step,
            initial_state=args.state,
            recipe_path=args.recipe,
            telnet_port=args.telnet,
            web_port=args.web_port,
            max_solves=args.max_solves,
        )
        if args.mock:
            from device.cube_api import MockCubeAPI
            controller.cube = MockCubeAPI()
            controller.cube_loop.cube_api = controller.cube
            controller.scrcpy = ScrcpyClient()
            logger.info("Mock 模式")
        else:
            controller.cube = CubeAPI(host=args.host, single_step=args.single_step)
            controller.cube_loop.cube_api = controller.cube
        await controller.run()

    asyncio.run(main())
