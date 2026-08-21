"""独立代理收集脚本 —— 连接真实 GAN i3 魔方，记录转动/陀螺仪到 CSV，并批量转发到 ESP32

用法：
    python -m tools.gan_proxy                              # 纯收集，仅记录 CSV
    python -m tools.gan_proxy --host 192.168.50.246        # 收集 + 转发到 ESP32
    python -m tools.gan_proxy --address AA:BB:CC:DD:EE:FF  # 跳过扫描，指定 BLE 地址
    python -m tools.gan_proxy --no-csv                     # 仅终端输出
    python -m tools.gan_proxy --verbose                    # 显示面片等调试信息
    python -m tools.gan_proxy --flush-ms 50                # 设定 debounce 间隔（默认 100ms）
    python -m tools.gan_proxy --viz                       # 打开 3D 魔方朝向可视化窗口
"""
import argparse
import asyncio
import math
import sys
import threading
from datetime import datetime

import cv2
import numpy as np

from device.ble_cube import (
    BLECubeConnection,
    Gen2ProtocolParser,
    Gen2MoveEvent,
    Gen2GyroEvent,
    Gen2FaceletsEvent,
    scan_for_gen2,
)
from device.proxy_logger import ProxyLogger
from device.cube_api import CubeAPI


def _format_ts() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:12]


def _quat_to_rotm(qw, qx, qy, qz):
    x2, y2, z2 = qx * qx, qy * qy, qz * qz
    xy, xz, yz = qx * qy, qx * qz, qy * qz
    wx, wy, wz = qw * qx, qw * qy, qw * qz
    return np.array([
        [1 - 2 * (y2 + z2), 2 * (xy - wz), 2 * (xz + wy)],
        [2 * (xy + wz), 1 - 2 * (x2 + z2), 2 * (yz - wx)],
        [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (x2 + y2)],
    ])


def _quat_to_gravity(qw, qx, qy, qz):
    gx = 2 * (qx * qz - qw * qy)
    gy = 2 * (qw * qx + qy * qz)
    gz = qw * qw - qx * qx - qy * qy + qz * qz
    return gx, gy, gz


_CUBE_VERTS = np.array([
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1,  1], [1, -1,  1], [1, 1,  1], [-1, 1,  1],
], dtype=np.float32)

_CUBE_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]

_EDGE_COLORS = [
    (200, 200, 200), (200, 200, 200), (200, 200, 200), (200, 200, 200),
    (200, 200, 200), (200, 200, 200), (200, 200, 200), (200, 200, 200),
    (0, 0, 255), (0, 255, 0), (255, 0, 0), (200, 200, 200),
]


def _render_cube(qw, qx, qy, qz, size=400):
    R = _quat_to_rotm(qw, qx, qy, qz)
    # 视角旋转：世界 Z 轴 → 屏幕 Y 轴方向（重力朝下）
    R_view = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=np.float32)
    verts = (_CUBE_VERTS @ R.T) @ R_view.T * (size * 0.3)
    cx, cy = size // 2, size // 2
    pts = np.round(verts[:, :2] + [cx, cy]).astype(int)
    img = np.zeros((size, size, 3), dtype=np.uint8)
    for (i, j), color in zip(_CUBE_EDGES, _EDGE_COLORS):
        cv2.line(img, tuple(pts[i]), tuple(pts[j]), color, 2)
    # 固定重力箭头（始终朝下）
    g_len = size * 0.35
    g_end = np.array([cx, cy + g_len]).astype(int)
    g_start = np.array([cx, cy]).astype(int)
    cv2.arrowedLine(img, tuple(g_start), tuple(g_end), (0, 0, 255), 2, tipLength=0.2)
    cv2.putText(img, f"qw={qw:.3f} qx={qx:.3f}", (8, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 100), 1)
    cv2.putText(img, f"qy={qy:.3f} qz={qz:.3f}", (8, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 100), 1)
    cv2.putText(img, f"qy={qy:.3f} qz={qz:.3f}", (8, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 100), 1)
    return img


class GanProxy:
    def __init__(self, address: str | None, cube_api, no_csv: bool, verbose: bool, flush_ms: int = 100, viz: bool = False):
        self.address = address
        self.cube_api = cube_api
        self.no_csv = no_csv
        self.verbose = verbose
        self._debounce_sec = flush_ms / 1000.0
        self._conn = None
        self._parser = None
        self._logger = None
        self._move_buffer: list[dict] = []
        self._debounce_timer: float = 0.0
        self._running = False
        self._viz = viz
        self._latest_quat: tuple[float, float, float, float] | None = None
        self._viz_thread: threading.Thread | None = None
        self._viz_lock = threading.Lock()
        self._viz_stop = threading.Event()

    async def run(self):
        if not self.no_csv:
            self._logger = ProxyLogger()

        self._running = True
        flush_task = None
        if self._viz:
            self._viz_stop.clear()
            self._viz_thread = threading.Thread(target=self._viz_loop, daemon=True)
            self._viz_thread.start()
        try:
            addr = self.address
            if not addr:
                print(f"[{_format_ts()}] 扫描 GAN i3 魔方...")
                addr = await scan_for_gen2(timeout=10.0)
                if not addr:
                    print(f"[{_format_ts()}] 未发现 GAN i3 魔方")
                    return
                self.address = addr

            self._conn = BLECubeConnection(addr)
            await self._conn.connect()
            self._parser = Gen2ProtocolParser(self._conn.mac)
            print(f"[{_format_ts()}] 已连接: {addr}")
            print(f"[{_format_ts()}] 开始监听，Ctrl+C 退出")

            flush_task = asyncio.create_task(self._flush_loop())

            async for raw_data in self._conn.start_notify(None):
                if not self._running:
                    break
                event = self._parser.parse(raw_data)
                if event is None:
                    continue
                await self._handle_event(event)
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
            if flush_task:
                flush_task.cancel()
            await self._cleanup()

    async def _flush_loop(self):
        while self._running:
            loop = asyncio.get_event_loop()
            now = loop.time()
            remaining = self._debounce_timer - now if self._debounce_timer > 0 else self._debounce_sec
            await asyncio.sleep(max(0.01, remaining))
            if self._debounce_timer > 0 and loop.time() >= self._debounce_timer:
                self._debounce_timer = 0.0
                await self._flush_buffer()

    async def _flush_buffer(self):
        if not self._move_buffer:
            return
        batch = self._move_buffer[:]
        self._move_buffer.clear()
        if self.cube_api:
            try:
                await self.cube_api.send_moves_raw(batch)
            except Exception as e:
                print(f"[{_format_ts()}] 批量发送失败 ({len(batch)} moves): {e}")

    async def _handle_event(self, event):
        if isinstance(event, Gen2MoveEvent):
            print(f"[{_format_ts()}] 转动: {event.notation:>4s}  (face={event.face}, dir={event.direction})")
            if self._logger:
                self._logger.log_move(event.face, event.direction)
            self._move_buffer.append({"face": event.face, "dir": event.direction})
            self._debounce_timer = asyncio.get_event_loop().time() + self._debounce_sec

        elif isinstance(event, Gen2GyroEvent):
            if self._viz:
                with self._viz_lock:
                    self._latest_quat = (event.qw, event.qx, event.qy, event.qz)
            if self._logger:
                self._logger.log_gyro(event.qw, event.qx, event.qy, event.qz, event.vx, event.vy, event.vz)

        elif isinstance(event, Gen2FaceletsEvent):
            if self.verbose:
                print(f"[{_format_ts()}] 面片更新: serial={event.serial}")

    async def _cleanup(self):
        if self._viz:
            self._viz_stop.set()
            if self._viz_thread and self._viz_thread.is_alive():
                self._viz_thread.join(timeout=1.0)
            cv2.destroyAllWindows()
        if self._running:
            await self._flush_buffer()
        if self._conn:
            await self._conn.disconnect()
        if self._logger:
            self._logger.close()
        if self.cube_api:
            try:
                await self.cube_api.close()
            except Exception:
                pass

    def _viz_loop(self):
        cv2.namedWindow("GAN i3 朝向", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("GAN i3 朝向", 400, 400)
        default_quat = (1.0, 0.0, 0.0, 0.0)
        while not self._viz_stop.is_set():
            with self._viz_lock:
                q = self._latest_quat if self._latest_quat is not None else default_quat
            img = _render_cube(*q)
            cv2.imshow("GAN i3 朝向", img)
            key = cv2.waitKey(30) & 0xFF
            if key == ord("q") or key == 27:
                self._viz_stop.set()
                break


async def main():
    parser = argparse.ArgumentParser(description="GAN i3 代理收集脚本")
    parser.add_argument("--address", default=None, help="BLE 设备地址 (MAC)，跳过扫描")
    parser.add_argument("--host", default=None, help="ESP32 IP，提供后启用转动转发")
    parser.add_argument("--port", type=int, default=80, help="ESP32 端口 (默认 80)")
    parser.add_argument("--no-csv", action="store_true", help="仅终端输出，不记录 CSV")
    parser.add_argument("--verbose", action="store_true", help="显示面片等调试信息")
    parser.add_argument("--flush-ms", type=int, default=100, help="批量发送 debounce 间隔，毫秒 (默认 100)")
    parser.add_argument("--viz", action="store_true", help="打开 3D 魔方朝向可视化窗口")
    args = parser.parse_args()

    cube_api = None
    if args.host:
        cube_api = CubeAPI(host=args.host, port=args.port)
        await cube_api.open()
        await cube_api.set_delay(0)
        print(f"[{_format_ts()}] ESP32 转发已启用: {args.host}:{args.port} (delay=0)")
    else:
        print(f"[{_format_ts()}] 纯收集模式（无 ESP32 转发）")

    proxy = GanProxy(args.address, cube_api, args.no_csv, args.verbose, flush_ms=args.flush_ms, viz=args.viz)
    try:
        await proxy.run()
    except KeyboardInterrupt:
        print(f"\n[{_format_ts()}] 用户中断")
    finally:
        print(f"[{_format_ts()}] 已退出")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass