"""魔方转动下发循环 —— tick 驱动 + 回包确认"""
import asyncio
import logging

logger = logging.getLogger(__name__)


class CubeLoop:
    """消费 move_queue 中的转动指令，调用 cube_api 下发。

    Tick 驱动（默认 200ms），支持指数退避重试 + 回包确认。
    Controller 在需要时直接调用 cube_api.get_state/get_facelets。

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

    def __init__(self, cube_api, cube_event_queue: asyncio.Queue, move_queue: asyncio.Queue, tick_interval: float = 0.2):
        self.cube_api = cube_api
        self.cube_event_queue = cube_event_queue
        self.move_queue = move_queue
        self.tick_interval = tick_interval

    async def run(self):
        """启动 move 消费任务。"""
        logger.info("CubeLoop 启动（tick=%.1fs）", self.tick_interval)
        await self._move_loop()

    async def _move_loop(self):
        """Tick 循环：检查 queue → 下发 + 回包确认 → 重试或丢弃。"""
        while True:
            moves = None
            try:
                moves = self.move_queue.get_nowait()
            except asyncio.QueueEmpty:
                pass

            if moves is not None:
                ok = await self._send_with_ack(moves)
                if ok:
                    if isinstance(moves, list):
                        n_moves = sum(1 for s in moves if "face" in s or "move" in s)
                        n_delays = sum(1 for s in moves if "delay" in s)
                        logger.info("转动下发确认成功: %d moves + %d delays", n_moves, n_delays)
                    else:
                        logger.info("转动下发确认成功: %s", moves)
                else:
                    logger.error("转动下发最终失败，丢弃: %s", moves)
                self.move_queue.task_done()

            await asyncio.sleep(self.tick_interval)

    async def _send_with_ack(self, moves, max_retries=3) -> bool:
        """下发 + 回包确认，指数退避重试。"""
        for attempt in range(max_retries):
            result = await self.cube_api.send_moves(moves)
            if self._ack_ok(result, moves):
                return True
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                logger.warning("下发未确认(attempt %d/%d)，%ds后重试", attempt + 1, max_retries, delay)
                await asyncio.sleep(delay)
        return False

    @staticmethod
    def _ack_ok(result: dict, moves) -> bool:
        """确认回包有效。

        - HTTP 失败/异常 → False
        - HTTP 200 + response 正常 → True
        - HTTP 200 + response 空/错乱 → warning + True（转动已入队，仅回包有损）
        """
        if not result.get("ok"):
            return False
        resp_text = result.get("response", "")
        if not resp_text or not resp_text.strip():
            logger.warning("回包内容异常(response=%r)，但 HTTP 已成功，仍认为下发有效", resp_text)
        return True
