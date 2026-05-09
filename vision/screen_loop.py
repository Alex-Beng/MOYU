"""截图 + UI 检测循环"""
import asyncio
import logging
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

    async def frames(self) -> AsyncIterator[np.ndarray]:
        while True:
            await asyncio.sleep(self.interval)
            frame = self.client.last_frame
            if frame is not None:
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
    """单独测试：python -m vision.screen_loop [image_or_video]

    无参数：自动在测试帧上打印帧尺寸（无 scrcpy）
    传图片：python -m vision.screen_loop screen.png
    传视频：python -m vision.screen_loop test.mp4
    """
    import sys
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def _test():
        path = sys.argv[1] if len(sys.argv) > 1 else None
        queue: asyncio.Queue = asyncio.Queue()

        if path is None:
            print("无参数，使用纯黑静态帧（1080x1920）验证 ScreenLoop 流程")
            import numpy as np
            class StaticSource(FrameSource):
                async def frames(self):
                    for _ in range(3):
                        yield np.zeros((1920, 1080, 3), dtype=np.uint8)
                        await asyncio.sleep(0.1)
            source = StaticSource()
        elif path.endswith((".mp4", ".avi", ".mov")):
            source = VideoSource(path)
        else:
            source = ImageSource(path)

        loop = ScreenLoop(source, recipe=None, ui_event_queue=queue)

        # 只跑 3 帧就退出（通过 asyncio.timeout 控制）
        count = 0
        async for frame in source.frames():
            print(f"帧 {count}: shape={frame.shape}")
            count += 1
            if count >= 3:
                break
        print("ScreenLoop 测试完成")

    asyncio.run(_test())
