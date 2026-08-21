"""后台 BLE 监听任务 —— 接收真实魔方数据，记录 CSV + 转发到 ESP32"""
import asyncio
import logging

from device.ble_cube import (
    BLECubeConnection,
    Gen2ProtocolParser,
    Gen2MoveEvent,
    Gen2GyroEvent,
    Gen2FaceletsEvent,
    scan_for_gen2,
)
from device.proxy_logger import ProxyLogger

logger = logging.getLogger(__name__)

DEBOUNCE_SEC = 0.1


class ProxyLoop:
    def __init__(self, move_queue: asyncio.Queue, cube_api=None, ble_address: str | None = None):
        self.cube_api = cube_api
        self.ble_address = ble_address
        self._conn: BLECubeConnection | None = None
        self._parser: Gen2ProtocolParser | None = None
        self._logger: ProxyLogger | None = None
        self._move_buffer: list[dict] = []
        self._debounce_timer: float = 0.0
        self._running = False

    async def run(self):
        self._logger = ProxyLogger()
        self._running = True
        try:
            if not self.ble_address:
                addr = await scan_for_gen2(timeout=10.0)
                if not addr:
                    logger.error("未发现 GAN i3 魔方，proxy 模式退出")
                    return
                self.ble_address = addr

            self._conn = BLECubeConnection(self.ble_address)
            await self._conn.connect()
            self._parser = Gen2ProtocolParser(self._conn.mac)

            flush_task = asyncio.create_task(self._flush_loop())

            async for raw_data in self._conn.start_notify(None):
                if not self._running:
                    break
                event = self._parser.parse(raw_data)
                if event is None:
                    continue
                await self._handle_event(event)

        except asyncio.CancelledError:
            logger.info("ProxyLoop 被取消")
        except Exception as e:
            logger.error("ProxyLoop 异常: %s", e, exc_info=True)
        finally:
            await self._cleanup()

    async def _flush_loop(self):
        while self._running:
            loop = asyncio.get_event_loop()
            now = loop.time()
            remaining = self._debounce_timer - now if self._debounce_timer > 0 else DEBOUNCE_SEC
            await asyncio.sleep(max(0.01, remaining))
            if self._debounce_timer > 0 and loop.time() >= self._debounce_timer:
                self._debounce_timer = 0.0
                if self._move_buffer and self.cube_api:
                    batch = self._move_buffer[:]
                    self._move_buffer.clear()
                    try:
                        await self.cube_api.send_moves_raw(batch)
                    except Exception as e:
                        logger.error("批量发送失败 (%d moves): %s", len(batch), e)

    async def _handle_event(self, event):
        if isinstance(event, Gen2MoveEvent):
            logger.info("BLE 转动: %s (face=%d, dir=%d)", event.notation, event.face, event.direction)
            self._logger.log_move(event.face, event.direction)
            self._move_buffer.append({"face": event.face, "dir": event.direction})
            self._debounce_timer = asyncio.get_event_loop().time() + DEBOUNCE_SEC

        elif isinstance(event, Gen2GyroEvent):
            self._logger.log_gyro(event.qw, event.qx, event.qy, event.qz, event.vx, event.vy, event.vz)

        elif isinstance(event, Gen2FaceletsEvent):
            logger.debug("BLE 面片更新: serial=%d", event.serial)

    async def _cleanup(self):
        if self._move_buffer and self.cube_api:
            try:
                await self.cube_api.send_moves_raw(self._move_buffer)
            except Exception:
                pass
            self._move_buffer.clear()
        if self._conn:
            await self._conn.disconnect()
        if self._logger:
            self._logger.close()
        self._running = False