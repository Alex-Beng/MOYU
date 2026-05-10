"""主控制器 —— 基于 asyncio + create_task 的并发架构"""
import asyncio
import logging

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

logger = logging.getLogger(__name__)


class Controller:
    """主控制器 —— 编排各独立任务

    两种运行模式（由 recipe.mode 控制）：
        full  全自动：wait_init → init → scramble → solve → reinit → init
        semi  半自动：scramble → solve → scramble  (UI 操作由人类完成)

    各任务模块是独立类，有自己的 run() 入口，可单独测试：
        - ScreenLoop : 持续截图 / UI 检测
        - CubeLoop   : 魔方状态轮询 / 转动下发

    任务通过 asyncio.Queue 通信，Controller 只负责组装 & 启动。
    """

    def __init__(self, classifier_config: dict | None = None):
        self.recipe = RecipeLoader()
        self.scrcpy = ScrcpyClient()
        self.cube = CubeAPI()
        self.detector = Detector(self.recipe.recipe)

        # 分类器配置（OCR 识别用）
        self.classifier_config = classifier_config or {"type": "knn"}
        self.classifier = None  # 延迟初始化

        # 任务间通信队列
        self.ui_event_queue: asyncio.Queue = asyncio.Queue()
        self.cube_event_queue: asyncio.Queue = asyncio.Queue()
        self.move_queue: asyncio.Queue = asyncio.Queue()

        # 独立任务实例
        self.screen_loop = ScreenLoop(ScrcpySource(self.scrcpy), self.recipe, self.ui_event_queue)
        self.cube_loop = CubeLoop(self.cube, self.cube_event_queue, self.move_queue)

        # 运行模式: "full" 全自动 / "semi" 半自动
        self.mode: str = self.recipe.recipe.mode
        self.state: str = "scramble" if self.mode == "semi" else "wait_init"
        self._running = False
        logger.info("Controller 初始化, mode=%s, state=%s", self.mode, self.state)

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------

    async def run(self):
        """启动所有任务并等待它们运行。"""
        # 初始化设备连接
        self.scrcpy.connect()
        await self.cube.open()

        # 延迟初始化分类器（OCR 用）
        if self.classifier_config:
            self.classifier = create_classifier(self.classifier_config)

        # 启动后台任务
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
        """根据 recipe.mode 加载对应状态处理器，驱动状态转移。"""
        if self.mode == "semi":
            _handlers = {
                "scramble": self._handle_scramble,
                "solve":    self._handle_solve,
            }
        else:
            _handlers = {
                "wait_init": self._handle_wait_init,
                "init":      self._handle_init,
                "scramble":  self._handle_scramble,
                "solve":     self._handle_solve,
                "reinit":    self._handle_reinit,
            }
        while True:
            handler = _handlers.get(self.state)
            if handler:
                next_state = await handler()
                if next_state and next_state != self.state:
                    logger.info("状态转移: %s → %s", self.state, next_state)
                    self.state = next_state
            else:
                logger.warning("未知状态: %s", self.state)
                await asyncio.sleep(1)

    # ------------------------------------------------------------------
    # 状态处理协程
    # ------------------------------------------------------------------

    async def _wait_for_ui(self, feature_name: str, timeout: float = 30.0) -> bool:
        """等待指定 UI 特征出现。

        Args:
            feature_name: recipe 中的特征名称
            timeout: 超时时间（秒）

        Returns:
            True if 特征出现，False if 超时
        """
        try:
            while timeout > 0:
                # 尝试从队列获取 UI 事件（带超时）
                event = await asyncio.wait_for(self.ui_event_queue.get(), timeout=1.0)
                self.ui_event_queue.task_done()
                # TODO: 解析 event，判断是否为目标特征
                # if event.get("feature") == feature_name:
                #     return True
                timeout -= 1.0
        except asyncio.TimeoutError:
            pass
        return False

    async def _wait_for_cube_state(self, key: str, expected, timeout: float = 30.0) -> bool:
        """等待魔方状态满足条件。

        Args:
            key: 状态字段名（如 "connected"）
            expected: 期望值
            timeout: 超时时间

        Returns:
            True if 状态满足，False if 超时
        """
        try:
            while timeout > 0:
                event = await asyncio.wait_for(self.cube_event_queue.get(), timeout=1.0)
                self.cube_event_queue.task_done()
                if event.get(key) == expected:
                    return True
                timeout -= 1.0
        except asyncio.TimeoutError:
            pass
        return False

    async def _handle_wait_init(self) -> str:
        """等待手机与 ESP 连接、电脑与设备连接。

        条件：
            - cube_event_queue 中收到 connected=True
        """
        logger.info("等待设备连接...")
        connected = await self._wait_for_cube_state("connected", True, timeout=60.0)
        if connected:
            logger.info("设备已连接，进入 init 状态")
            return "init"
        else:
            logger.warning("设备连接超时，保持 wait_init")
            return "wait_init"

    async def _handle_init(self) -> str:
        """检测 UI 状态，开启匹配，等待打乱 UI 出现。

        步骤：
            1. 点击 "match_button" 特征位置（如果有）
            2. 等待 "scramble_area" 特征出现
        """
        logger.info("init: 等待打乱 UI 出现...")

        # 可选：点击匹配按钮（如果 recipe 中有定义）
        matched, center = self.detector.detect(self.scrcpy.last_frame, "match_button")
        if matched and center:
            logger.info("init: 点击匹配按钮 %s", center)
            self.scrcpy.tap(*center)
            await asyncio.sleep(1.0)

        # 等待打乱区域 UI 出现
        # TODO: 实际需要从 screen_loop 的帧中检测
        # 这里简化：等待 5 秒后进入 scramble（实际应检测特征）
        await asyncio.sleep(5.0)
        logger.info("init: 检测到打乱 UI，进入 scramble")
        return "scramble"

    async def _handle_scramble(self) -> str:
        """OCR 识别打乱序列，下发到 ESP32，等待打乱 UI 消失。

        步骤：
            1. 截取打乱区域（scramble_area ROI）
            2. segmentor 检测圆形气泡 → 裁剪字符图
            3. classifier 识别每个字符
            4. parser 转换为标准 move 序列
            5. 下发打乱序列到 ESP32（同步魔方状态）
            6. 等待打乱 UI 消失（进入 solve）
        """
        logger.info("scramble: OCR 识别打乱序列...")

        frame = self.scrcpy.last_frame
        if frame is None:
            logger.warning("scramble: 无帧，跳过")
            await asyncio.sleep(1.0)
            return "scramble"

        # 检测打乱区域是否还在画面中
        feat = self.recipe.recipe.feature("scramble_area")
        matched, _ = self.detector.detect(frame, "scramble_area")
        if not matched:
            logger.info("scramble: 打乱区域未检测到，可能已消失")
            await asyncio.sleep(1.0)
            return "solve"

        if feat and feat.roi:
            x, y, w, h = feat.roi
            scramble_frame = frame[y:y+h, x:x+w]
        else:
            scramble_frame = frame

        chars = segment(scramble_frame)
        if chars:
            char_imgs = [c[0] for c in chars]
            if self.classifier:
                labels = self.classifier.predict_batch(char_imgs)
                moves = parse(labels)
                logger.info("scramble: 识别结果 = %s", moves)

                if moves:
                    # 下发打乱序列到 ESP32，同步魔方状态
                    logger.info("scramble: 下发打乱序列到 ESP32")
                    await self.move_queue.put(moves)
            else:
                logger.warning("scramble: 分类器未初始化")
        else:
            logger.warning("scramble: 未检测到字符区域")

        await asyncio.sleep(1.0)

        # 再次检测打乱区域是否消失
        frame = self.scrcpy.last_frame
        if frame:
            matched, _ = self.detector.detect(frame, "scramble_area")
            if not matched:
                logger.info("scramble: 打乱 UI 消失，进入 solve")
                return "solve"

        if self.mode == "semi":
            # 半自动：打乱区还在说明人类还在操作，保持 scramble
            logger.info("scramble: 打乱 UI 仍在，等待人类完成操作...")
            return "scramble"
        else:
            # 全自动：检查是否已进入结算 UI
            matched_result, _ = self.detector.detect(frame, "result_screen")
            if matched_result:
                logger.info("scramble: 检测到结算 UI，进入 reinit")
                return "reinit"
            return "solve"

    async def _handle_solve(self) -> str:
        """从 ESP32 获取面片状态 → 求解 → 下发转动。

        步骤：
            1. 从 cube_api 获取当前 kociemba 格式面片字符串
            2. 调用 CFOP 求解器生成解法
            3. 将解法推入 move_queue
            4. 半自动: 直接回到 scramble 等待新打乱
               全自动: 检测新 UI（新打乱 or 结算）
        """
        logger.info("solve: 获取面片状态...")

        facelets = await self.cube.get_facelets()
        if not facelets or len(facelets) != 54:
            logger.warning("solve: 无效面片: %s", facelets)
            return "reinit" if self.mode == "full" else "scramble"

        logger.info("solve: facelets = %s", facelets)

        try:
            result = solve_cfop(facelets)
        except Exception as e:
            logger.error("solve: CFOP 求解失败: %s", e)
            return "reinit" if self.mode == "full" else "scramble"

        solution = result["solution"]
        total = len(solution.split())
        logger.info("solve: 解法 = %s (%d 步)", solution, total)

        await self.move_queue.put(solution)
        logger.info("solve: 已下发转动指令到 move_queue")

        if self.mode == "semi":
            # 半自动：直接回到 scramble，等待人类完成 UI 操作后出现新打乱
            logger.info("solve: 半自动模式，返回 scramble 等待新打乱")
            return "scramble"

        await asyncio.sleep(2.0)

        frame = self.scrcpy.last_frame
        if frame:
            matched_scramble, _ = self.detector.detect(frame, "scramble_area")
            matched_result, _ = self.detector.detect(frame, "result_screen")
            if matched_scramble:
                logger.info("solve: 检测到新打乱 UI")
                return "scramble"
            elif matched_result:
                logger.info("solve: 检测到结算 UI")
                return "reinit"

        logger.info("solve: 保持 solve，等待明确 UI 变化")
        return "solve"

    async def _handle_reinit(self) -> str:
        """点击各种结算 UI，直至回到 init。

        步骤：
            1. 检测结算 UI（result_screen）
            2. 点击确认/返回按钮
            3. 等待回到 init 状态（匹配按钮 UI）
        """
        logger.info("reinit: 点击结算 UI，返回 init...")

        # 点击结算确认按钮（如果有配置）
        matched, center = self.detector.detect(self.scrcpy.last_frame, "result_screen")
        if matched and center:
            logger.info("reinit: 点击结算 UI 中心 %s", center)
            self.scrcpy.tap(*center)
            await asyncio.sleep(2.0)

        # 等待回到 init 状态
        # 这里简化：等待几秒后直接返回 init
        await asyncio.sleep(3.0)
        logger.info("reinit: 返回 init")
        return "init"


# ------------------------------------------------------------------
# 单独测试入口
# ------------------------------------------------------------------

if __name__ == "__main__":
    """单独测试 Controller（Mock 模式）。

    示例：
        python controller.py                    # 使用默认配置
        python controller.py --classifier knn   # 指定 KNN 分类器
    """
    import sys
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--classifier", default="knn", choices=["knn", "template", "cnn"])
    parser.add_argument("--mode", default=None, choices=["full", "semi"],
                        help="覆盖 recipe 中的 mode 配置（测试用）")
    args = parser.parse_args()

    classifier_config = {"type": args.classifier}

    async def main():
        # 使用 MockCubeAPI 测试（不需要真实 ESP32）
        from device.cube_api import MockCubeAPI

        controller = Controller(classifier_config=classifier_config)
        # 替换为 Mock
        controller.cube = MockCubeAPI()
        controller.scrcpy = ScrcpyClient()  # 无真实连接，last_frame 返回 None
        if args.mode:
            controller.mode = args.mode
            controller.state = "scramble" if args.mode == "semi" else "wait_init"
            logger.info("测试模式覆盖: mode=%s, state=%s", controller.mode, controller.state)
        await controller.run()

    asyncio.run(main())
