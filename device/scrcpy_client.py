"""scrcpy 客户端封装 —— 截图 / 点击 / 滑动 / 连接管理

基于 https://github.com/leng-yue/py-scrcpy-client
"""
import logging
import time

import cv2
import numpy as np
import scrcpy

logger = logging.getLogger(__name__)


class ScrcpyClient:
    """封装 scrcpy.Client，提供截图、点击、滑动接口。

    scrcpy 客户端在独立线程运行帧循环，本类通过 last_frame 获取最新帧。
    对于自动化场景，max_fps=5 即可大幅降低 CPU 占用。
    """

    def __init__(self, serial: str | None = None, max_fps: int = 5, max_width: int = 1080, bitrate: int | None = None):
        """
        Args:
            serial: adb 设备序列号，None 时自动选择唯一连接设备。
            max_fps: 最大帧率，自动化场景 5fps 足够。
            max_width: 最大分辨率宽度，0 表示不限制。
            bitrate: 视频码率 (bps)，None 使用 scrcpy 默认值。
        """
        self.serial = serial
        self.max_fps = max_fps
        self.max_width = max_width
        self.bitrate = bitrate
        self._client: scrcpy.Client | None = None
        self._connected = False

    def connect(self):
        """建立 scrcpy 连接并启动帧循环。"""
        logger.info("ScrcpyClient 连接中，serial=%s", self.serial)
        kwargs = dict(
            device=self.serial,
            max_fps=self.max_fps,
            max_width=self.max_width,
        )
        if self.bitrate is not None:
            kwargs["bitrate"] = self.bitrate
        self._client = scrcpy.Client(**kwargs)
        self._client.add_listener(scrcpy.EVENT_FRAME, self._on_frame)
        self._client.add_listener(scrcpy.EVENT_INIT, self._on_init)
        self._client.add_listener(scrcpy.EVENT_DISCONNECT, self._on_disconnect)
        self._client.start(threaded=True)
        self._connected = True
        logger.info("ScrcpyClient 已连接")

    def reconnect(self, max_retries: int = 3, delay: float = 2.0) -> bool:
        """断开并重新连接 scrcpy。

        Args:
            max_retries: 最大重试次数。
            delay: 每次重试间隔（秒）。

        Returns:
            是否重连成功。
        """
        self.disconnect()
        for attempt in range(1, max_retries + 1):
            logger.info("ScrcpyClient 重连尝试 %d/%d...", attempt, max_retries)
            try:
                self.connect()
                return True
            except Exception as e:
                logger.warning("ScrcpyClient 重连失败 (%s)，%d 秒后重试", e, delay)
                time.sleep(delay)
        logger.error("ScrcpyClient 重连耗尽 %d 次，放弃", max_retries)
        return False

    def _on_init(self):
        logger.info("scrcpy 初始化完成，设备: %s", self._client.device_name)

    def _on_frame(self, frame):
        pass

    def _on_disconnect(self):
        self._connected = False
        logger.warning("scrcpy 连接断开")

    def disconnect(self):
        """断开 scrcpy 连接。"""
        if self._client:
            self._client.stop()
        self._connected = False
        logger.info("ScrcpyClient 已断开")

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def last_frame(self) -> np.ndarray | None:
        """获取最新一帧（BGR ndarray）。未连接或无帧时返回 None。"""
        if self._client:
            return self._client.last_frame
        return None

    def tap(self, x: int, y: int):
        """点击屏幕坐标 (x, y)。"""
        if not self._connected or not self._client:
            logger.warning("scrcpy 未连接，忽略 tap")
            return
        logger.debug("tap (%d, %d)", x, y)
        self._client.control.touch(x, y, scrcpy.ACTION_DOWN)
        self._client.control.touch(x, y, scrcpy.ACTION_UP)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300):
        """从 (x1, y1) 滑动到 (x2, y2)。"""
        if not self._connected or not self._client:
            logger.warning("scrcpy 未连接，忽略 swipe")
            return
        logger.debug("swipe (%d,%d) → (%d,%d)", x1, y1, x2, y2)
        self._client.control.swipe(x1, y1, x2, y2, duration_ms)