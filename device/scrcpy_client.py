"""scrcpy 客户端封装 —— 截图 / 点击 / 滑动 / 连接管理

基于 https://github.com/leng-yue/py-scrcpy-client
"""
import logging

import cv2
import numpy as np
import scrcpy

logger = logging.getLogger(__name__)


class ScrcpyClient:
    """封装 scrcpy.Client，提供截图、点击、滑动接口。

    scrcpy 客户端在独立线程运行帧循环，本类通过 last_frame 获取最新帧。
    对于自动化场景，max_fps=5 即可大幅降低 CPU 占用。
    """

    def __init__(self, serial: str | None = None, max_fps: int = 5, max_width: int = 1080):
        """
        Args:
            serial: adb 设备序列号，None 时自动选择唯一连接设备。
            max_fps: 最大帧率，自动化场景 5fps 足够。
            max_width: 最大分辨率宽度。
        """
        self.serial = serial
        self.max_fps = max_fps
        self.max_width = max_width
        self._client: scrcpy.Client | None = None
        self._connected = False

    def connect(self):
        """建立 scrcpy 连接并启动帧循环。"""
        logger.info("ScrcpyClient 连接中，serial=%s", self.serial)
        self._client = scrcpy.Client(
            device=self.serial,
            max_fps=self.max_fps,
            max_width=self.max_width,
        )
        # 注册帧回调（可选，主要用于调试可视化）
        self._client.add_listener(scrcpy.EVENT_FRAME, self._on_frame)
        self._client.add_listener(scrcpy.EVENT_INIT, self._on_init)
        # threaded=True：帧循环在独立线程，不阻塞主线程
        self._client.start(threaded=True)
        self._connected = True
        logger.info("ScrcpyClient 已连接")

    def _on_init(self):
        logger.info("scrcpy 初始化完成，设备: %s", self._client.device_name)

    def _on_frame(self, frame):
        # 帧回调不做处理，通过 last_frame 获取即可
        pass

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
        if not self._connected:
            logger.warning("scrcpy 未连接，忽略 tap")
            return
        logger.debug("tap (%d, %d)", x, y)
        self._client.control.touch(x, y, scrcpy.ACTION_DOWN)
        self._client.control.touch(x, y, scrcpy.ACTION_UP)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300):
        """从 (x1, y1) 滑动到 (x2, y2)。"""
        if not self._connected:
            logger.warning("scrcpy 未连接，忽略 swipe")
            return
        logger.debug("swipe (%d,%d) → (%d,%d)", x1, y1, x2, y2)
        self._client.control.swipe(x1, y1, x2, y2, duration_ms)