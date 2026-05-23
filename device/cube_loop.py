"""魔方转动下发循环 —— 纯事件驱动，不轮询状态"""
import asyncio
import logging

logger = logging.getLogger(__name__)


class CubeLoop:
    """消费 move_queue 中的转动指令，调用 cube_api 下发。

    不再轮询状态。Controller 在需要时直接调用 cube_api.get_state/get_facelets。

    可单独测试：
        # 真实设备
        api = CubeAPI(host="192.168.4.1")
        await api.open()
        asyncio.run(CubeLoop(api, move_queue).run())

        # Mock 测试
        api = MockCubeAPI()
        await api.open()
        asyncio.run(CubeLoop(api, move_queue).run())
    """

    def __init__(self, cube_api, cube_event_queue: asyncio.Queue, move_queue: asyncio.Queue):
        self.cube_api = cube_api
        self.cube_event_queue = cube_event_queue
        self.move_queue = move_queue

    async def run(self):
        """启动 move 消费任务。"""
        logger.info("CubeLoop 启动（事件驱动）")
        await self._move_loop()

    async def _move_loop(self):
        """消费 move_queue 中的转动指令，调用 cube_api 下发。"""
        while True:
            moves = await self.move_queue.get()
            result = await self.cube_api.send_moves(moves)
            if result.get("ok"):
                if isinstance(moves, list):
                    n_moves = sum(1 for s in moves if "face" in s)
                    n_delays = sum(1 for s in moves if "delay" in s)
                    logger.info("转动下发成功: %d moves + %d delays", n_moves, n_delays)
                else:
                    logger.info("转动下发成功: %s", moves)
            else:
                logger.warning("转动下发失败: %s，将重试", moves)
                await asyncio.sleep(1.0)
                await self.cube_api.send_moves(moves)
            self.move_queue.task_done()
