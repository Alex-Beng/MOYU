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
import time
from datetime import datetime

import cv2
import numpy as np

from device.ble_cube import (
    BLECubeConnection,
    Gen2ProtocolParser,
    Gen2MoveEvent,
    Gen2GyroEvent,
    Gen2FaceletsEvent,
    apply_move_state,
    cp_co_ep_eo_to_facelets,
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

# 6 个面（顶点索引）+ 外法线 + 标准 GAN 配色（BGR）
# 约定 X→R, Y→F, Z→U
_CUBE_FACES = [
    (4, 5, 6, 7),   # +Z → U（上，白）
    (0, 3, 2, 1),   # -Z → D（下，黄）
    (2, 6, 7, 3),   # +Y → B（后，蓝）
    (0, 1, 5, 4),   # -Y → F（前，绿）
    (1, 2, 6, 5),   # +X → R（右，红）
    (0, 4, 7, 3),   # -X → L（左，橙）
]
_FACE_NORMALS = [
    (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0),
]
_FACE_COLORS = [
    (255, 255, 255),  # U 白
    (0, 255, 255),    # D 黄
    (255, 0, 0),      # B 蓝
    (0, 255, 0),      # F 绿
    (0, 0, 255),      # R 红
    (0, 165, 255),    # L 橙
]
_EDGE_COLOR = (30, 30, 30)

# 每个面(Kociemba 顺序)在 54 面片串中的起始偏移：U,D,B,F,R,L
_FACELET_OFFSET = [0, 27, 45, 18, 9, 36]
_FACELET_BGR = {
    "U": (255, 255, 255), "R": (0, 0, 255), "F": (0, 255, 0),
    "D": (0, 255, 255), "L": (0, 165, 255), "B": (255, 0, 0),
}
# 每面的贴纸网格局部基（origin=tangent中心, row=行方向, col=列方向）
_FACE_GRID = [
    ((0, 0, 1), (0, -1, 0), (1, 0, 0)),     # U +Z
    ((0, 0, -1), (0, 1, 0), (1, 0, 0)),     # D -Z
    ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),    # B +Y
    ((0, -1, 0), (0, 0, -1), (1, 0, 0)),    # F -Y
    ((1, 0, 0), (0, 0, -1), (0, 1, 0)),     # R +X
    ((-1, 0, 0), (0, 0, -1), (0, -1, 0)),   # L -X
]

_STICKER = 2.0 / 3.0


def _build_face_cells():
    """为每个面生成 3x3 贴纸网格的局部 3D 角点 [6, 9, 4, 3]"""
    cells = []
    for origin, row, col in _FACE_GRID:
        o = np.array(origin, dtype=np.float32)
        r = np.array(row, dtype=np.float32)
        c = np.array(col, dtype=np.float32)
        face_cells = []
        for rc in range(3):
            for cc in range(3):
                center = o + r * (rc - 1) * _STICKER + c * (cc - 1) * _STICKER
                quad = np.array([
                    center + r * (-_STICKER/2) + c * (_STICKER/2),
                    center + r * (-_STICKER/2) + c * (-_STICKER/2),
                    center + r * (_STICKER/2) + c * (-_STICKER/2),
                    center + r * (_STICKER/2) + c * (_STICKER/2),
                ], dtype=np.float32)
                face_cells.append(quad)
        cells.append(face_cells)
    return np.array(cells)


_FACE_CELLS = _build_face_cells()


def _render_cube(qw, qx, qy, qz, size=400, facelets=None, view_yaw=0.0):
    R = _quat_to_rotm(qw, qx, qy, qz)
    # 视角旋转：世界 Z 轴 → 屏幕 Y 轴方向（重力朝下）
    R_view = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=np.float32)
    cyaw, syaw = np.cos(view_yaw), np.sin(view_yaw)
    R_yaw = np.array([[cyaw, 0, syaw], [0, 1, 0], [-syaw, 0, cyaw]], dtype=np.float32)
    verts3d = (((_CUBE_VERTS @ R.T) @ R_view.T) @ R_yaw.T) * (size * 0.3)
    cx, cy = size // 2, size // 2
    img = np.zeros((size, size, 3), dtype=np.uint8)

    def proj(v):
        # X 翻转修正左手镜像；Y 直接映射（重力朝下）
        return np.round(np.stack([cx - v[:, 0], cy + v[:, 1]], axis=1)).astype(int)

    # 面法线变换到视角坐标系（含 yaw）
    normals_view = [
        ((R_view @ (R @ np.array(n, dtype=np.float32))) @ R_yaw.T)
        for n in _FACE_NORMALS
    ]

    # 变换贴纸网格角点到视角坐标
    cells = (_FACE_CELLS @ R.T) @ R_view.T @ R_yaw.T

    for fi, (face, color, n_view) in enumerate(zip(_CUBE_FACES, _FACE_COLORS, normals_view)):
        nz = n_view[2]
        if nz <= 0:
            continue
        shade = 0.3 + 0.7 * nz
        if facelets is not None:
            off = _FACELET_OFFSET[fi]
            for cell_idx in range(9):
                ch = facelets[off + cell_idx]
                rgb = _FACELET_BGR.get(ch)
                if rgb is None:
                    continue
                quad = cells[fi][cell_idx] * (size * 0.3)
                pts = proj(quad)
                cv2.fillPoly(img, [pts], tuple(int(c * shade) for c in rgb))
        else:
            face_pts = proj(verts3d[list(face)])
            cv2.fillPoly(img, [face_pts], tuple(int(c * shade) for c in color))

    # 边缘叠加
    pts = proj(verts3d)
    for (i, j) in _CUBE_EDGES:
        cv2.line(img, tuple(pts[i]), tuple(pts[j]), _EDGE_COLOR, 1)

    # 固定重力箭头（始终朝下）
    g_len = size * 0.35
    g_end = np.array([cx, cy + g_len]).astype(int)
    g_start = np.array([cx, cy]).astype(int)
    cv2.arrowedLine(img, tuple(g_start), tuple(g_end), (0, 0, 255), 2, tipLength=0.2)
    cv2.putText(img, f"qw={qw:.3f} qx={qx:.3f}", (8, 20),
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
        self._latest_facelets: str | None = None
        self._state: tuple | None = None   # (cp, co, ep, eo)
        self._view_yaw: float = 0.0
        self._calibrated = False
        self._calib_start = 0.0
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
            self._calib_start = time.time()
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
            if self._state is not None:
                self._state = apply_move_state(*self._state, event.face, event.direction)
                fl = cp_co_ep_eo_to_facelets(*self._state)
                if self._logger:
                    self._logger.log_facelets(fl)
                if self._viz:
                    with self._viz_lock:
                        self._latest_facelets = fl
            self._move_buffer.append({"face": event.face, "dir": event.direction})
            self._debounce_timer = asyncio.get_event_loop().time() + self._debounce_sec

        elif isinstance(event, Gen2GyroEvent):
            if self._viz:
                with self._viz_lock:
                    self._latest_quat = (event.qw, event.qx, event.qy, event.qz)
            if not self._calibrated:
                if self._calib_start > 0 and time.time() - self._calib_start >= 10.0:
                    self._calibrated = True
                    print(f"[{_format_ts()}] 陀螺仪校准完成")
                elif self._calib_start > 0 and time.time() - self._calib_start < 0.5:
                    print(f"[{_format_ts()}] 陀螺仪校准中，等待 10s...")
            if self._logger and self._calibrated:
                self._logger.log_gyro(event.qw, event.qx, event.qy, event.qz, event.vx, event.vy, event.vz)

        elif isinstance(event, Gen2FaceletsEvent):
            if self._state is None:
                self._state = (list(event.cp), list(event.co), list(event.ep), list(event.eo))
                fl = cp_co_ep_eo_to_facelets(*self._state)
                if self._logger:
                    self._logger.log_facelets(fl)
                if self._viz:
                    with self._viz_lock:
                        self._latest_facelets = fl
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
                facelets = self._latest_facelets
                yaw = self._view_yaw
            img = _render_cube(*q, facelets=facelets, view_yaw=yaw)
            cv2.imshow("GAN i3 朝向", img)
            key = cv2.waitKeyEx(30)
            if key == ord("q") or key == 27:
                self._viz_stop.set()
                break
            elif key == 2555904:   # → 右
                self._view_yaw += 0.15
            elif key == 2424832:   # ← 左
                self._view_yaw -= 0.15


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