"""截图 + UI 检测循环"""
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator

import cv2
import numpy as np

from device.scrcpy_client import ScrcpyClient

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# FrameSource 抽象 —— 实现此接口即可接入 ScreenLoop
# ------------------------------------------------------------------

class FrameSource(ABC):
    """帧来源抽象基类。"""

    @abstractmethod
    def frames(self) -> AsyncIterator[np.ndarray]:
        """异步生成帧（BGR ndarray）。"""


class ScrcpySource(FrameSource):
    """真实设备来源：从 ScrcpyClient.last_frame 获取最新帧。

    scrcpy 客户端在独立线程运行帧循环，这里按 fps 间隔轮询 last_frame。
    """

    def __init__(self, client: "ScrcpyClient", fps: float = 5.0):
        self.client = client
        self.interval = 1.0 / fps
        self._last_log = 0.0

    async def frames(self) -> AsyncIterator[np.ndarray]:
        while True:
            await asyncio.sleep(self.interval)
            frame = self.client.last_frame
            if frame is not None:
                # 帧龄 = 现在 - 该帧到达时刻；用于发现 scrcpy 画面滞后现实。
                age = self.client.frame_age
                if age is not None:
                    now = time.monotonic()
                    if now - self._last_log >= 1.0:
                        self._last_log = now
                        logger.info(
                            "[frame-age] age=%.2fs seq=%d",
                            age,
                            self.client.frame_seq,
                        )
                    if age > 1.0:
                        logger.warning(
                            "[frame-age] 画面滞后严重: age=%.2fs (>1s)，决策可能基于过期画面",
                            age,
                        )
                yield frame


class ImageSource(FrameSource):
    """图片 mock：循环返回单张或多张图片。

    用法（测试）：
        src = ImageSource(["tests/frames/init.png", "tests/frames/scramble.png"])
        asyncio.run(ScreenLoop(src, recipe, queue).run())
    """

    def __init__(self, paths: list[str] | str, interval: float = 0.5):
        if isinstance(paths, str):
            paths = [paths]
        self.paths = [Path(p) for p in paths]
        self.interval = interval

    async def frames(self) -> AsyncIterator[np.ndarray]:
        while True:
            for path in self.paths:
                frame = cv2.imread(str(path))
                if frame is None:
                    logger.warning("无法读取图片: %s", path)
                else:
                    yield frame
                await asyncio.sleep(self.interval)


class VideoSource(FrameSource):
    """视频文件 mock：逐帧播放，结束后循环。

    用法（测试）：
        src = VideoSource("tests/videos/test_run.mp4", fps=10)
        asyncio.run(ScreenLoop(src, recipe, queue).run())
    """

    def __init__(self, path: str, fps: float | None = None):
        self.path = path
        self.fps = fps  # None 表示使用视频原始帧率

    async def frames(self) -> AsyncIterator[np.ndarray]:
        while True:
            cap = cv2.VideoCapture(self.path)
            native_fps = cap.get(cv2.CAP_PROP_FPS) or 10.0
            interval = 1.0 / (self.fps or native_fps)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # 视频结束，重新循环
                yield frame
                await asyncio.sleep(interval)
            cap.release()


# ------------------------------------------------------------------
# ScreenLoop
# ------------------------------------------------------------------

class ScreenLoop:
    """持续从 FrameSource 取帧并推送 UI 事件到 ui_event_queue。

    生产环境：
        loop = ScreenLoop(ScrcpySource(scrcpy), recipe, queue)

    Mock 测试（图片）：
        loop = ScreenLoop(ImageSource("tests/frames/init.png"), recipe, queue)

    Mock 测试（视频）：
        loop = ScreenLoop(VideoSource("tests/videos/run.mp4"), recipe, queue)
    """

    def __init__(self, source: FrameSource, recipe, ui_event_queue: asyncio.Queue):
        self.source = source
        self.recipe = recipe
        self.ui_event_queue = ui_event_queue

    async def run(self):
        """主循环：取帧 → 检测 → 推送事件。"""
        logger.info("ScreenLoop 启动，来源: %s", type(self.source).__name__)
        async for frame in self.source.frames():
            # TODO: 基于 recipe 配置做模板匹配 / UI 检测
            # event = detect(frame, self.recipe)
            # await self.ui_event_queue.put(event)
            _ = frame  # 占位，避免 unused 警告


if __name__ == "__main__":
    """单独测试：python -m vision.screen_loop [image_or_video|device]

    无参数：接入真实手机 scrcpy 串流，按 q 退出
    传 device:<serial>：指定 adb 序列号，如 device:192.168.1.5:5555
    传图片：python -m vision.screen_loop screen.png
    传视频：python -m vision.screen_loop test.mp4
    """
    import sys
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def _test():
        arg = sys.argv[1] if len(sys.argv) > 1 else None
        queue: asyncio.Queue = asyncio.Queue()

        if arg is None or arg.startswith("device:"):
            serial = arg.split(":", 1)[1] if arg else None
            from device.scrcpy_client import ScrcpyClient
            client = ScrcpyClient(serial=serial, max_fps=60)
            client.connect()
            source = ScrcpySource(client, fps=60)
            print(f"已连接 scrcpy，serial={serial or '自动'}，按 q 退出")
            try:
                count = 0
                async for frame in source.frames():
                    cv2.imshow("scrcpy", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    count += 1
                    print(f"\r帧 {count}: shape={frame.shape}", end="", flush=True)
            finally:
                client.disconnect()
                cv2.destroyAllWindows()
                print("\nScreenLoop 测试完成")
            return

        if arg.endswith((".mp4", ".avi", ".mov")):
            source = VideoSource(arg)
        else:
            source = ImageSource(arg)

        count = 0
        async for frame in source.frames():
            cv2.imshow("preview", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            print(f"帧 {count}: shape={frame.shape}")
            count += 1
            if count >= 10:
                break
        cv2.destroyAllWindows()
        print("ScreenLoop 测试完成")

    asyncio.run(_test())
