"""魔方状态轮询 + 转动下发循环"""
import asyncio
import logging

logger = logging.getLogger(__name__)


class CubeLoop:
    """持续轮询 ESP32 状态并消费 move_queue 中的转动指令。

    两个并发的子任务：
        - _poll_loop: 按 interval 轮询 ESP32 状态，推送到 cube_event_queue
        - _move_loop: 消费 move_queue 中的转动指令，调用 cube_api.send_moves

    可单独测试：
        # 真实设备
        api = CubeAPI(host="192.168.4.1")
        await api.open()
        asyncio.run(CubeLoop(api, event_queue, move_queue).run())

        # Mock 测试
        api = MockCubeAPI()
        await api.open()
        asyncio.run(CubeLoop(api, event_queue, move_queue).run())
    """

    def __init__(self, cube_api, cube_event_queue: asyncio.Queue, move_queue: asyncio.Queue,
                 poll_interval: float = 2.0):
        self.cube_api = cube_api
        self.cube_event_queue = cube_event_queue
        self.move_queue = move_queue
        self.poll_interval = poll_interval

    async def run(self):
        """启动两个并发子任务。"""
        logger.info("CubeLoop 启动")
        tasks = [
            asyncio.create_task(self._poll_loop(), name="cube_poll"),
            asyncio.create_task(self._move_loop(), name="cube_move"),
        ]
        await asyncio.gather(*tasks)

    async def _poll_loop(self):
        """按间隔轮询 ESP32 状态（/api/state + /api/facelets），推送到 cube_event_queue。"""
        while True:
            status = await self.cube_api.get_state()
            if status:
                status["facelets"] = await self.cube_api.get_facelets()
                await self.cube_event_queue.put(status)
            await asyncio.sleep(self.poll_interval)

    async def _move_loop(self):
        """消费 move_queue 中的转动指令，调用 cube_api 下发。"""
        while True:
            moves = await self.move_queue.get()
            result = await self.cube_api.send_moves(moves)
            if result.get("ok"):
                logger.info("转动下发成功: %s", moves)
            else:
                logger.warning("转动下发失败: %s，将重试", moves)
                # 重试一次
                await asyncio.sleep(1.0)
                await self.cube_api.send_moves(moves)
            self.move_queue.task_done()