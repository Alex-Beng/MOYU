"""BLE 连接 GAN i3 魔方 + Gen2 协议通知解析"""
import asyncio
import logging
import struct
from typing import AsyncIterator

from crypto.aes_cbc import derive_key_iv, decrypt_msg, GEN2_BASE_KEY, GEN2_BASE_IV

logger = logging.getLogger(__name__)

# Gen2 GAN i3 魔方 UUID
GEN2_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dc4179"
GEN2_STATE_CHAR_UUID = "28be4cb6-cd67-11e9-a32f-2a2ae2dbcce4"
GEN2_CMD_CHAR_UUID = "28be4a4a-cd67-11e9-a32f-2a2ae2dbcce4"

# 魔方面名称
FACE_NAMES = ["U", "R", "F", "D", "L", "B"]
DIR_NAMES = ["", "'", "2"]

# Kociemba 面片表（移植自 gan-cube-emu protocol.rs）
_CORNER_FACELET = [
    [8, 9, 20], [6, 18, 38], [0, 36, 47], [2, 45, 11],
    [29, 26, 15], [27, 44, 24], [33, 53, 42], [35, 17, 51],
]
_CORNER_COLOR = [
    [0, 1, 2], [0, 2, 4], [0, 4, 5], [0, 5, 1],
    [3, 2, 1], [3, 4, 2], [3, 5, 4], [3, 1, 5],
]
_EDGE_FACELET = [
    [5, 10], [7, 19], [3, 37], [1, 46], [32, 16], [28, 25],
    [30, 43], [34, 52], [23, 12], [21, 41], [50, 39], [48, 14],
]
_EDGE_COLOR = [
    [0, 1], [0, 2], [0, 4], [0, 5], [3, 1], [3, 2],
    [3, 4], [3, 5], [2, 1], [2, 4], [5, 4], [5, 1],
]
_CENTER_FACELET = [4, 13, 22, 31, 40, 49]
_FACELET_COLORS = "URFDLB"


def cp_co_ep_eo_to_facelets(cp, co, ep, eo) -> str:
    """从角/棱位置与方向还原 54 字符面片串（Kociemba 顺序 URFDLB）"""
    f = ["U"] * 54
    for i in range(6):
        f[_CENTER_FACELET[i]] = _FACELET_COLORS[i]
    for i in range(8):
        j = cp[i]
        ori = co[i]
        for k in range(3):
            f[_CORNER_FACELET[i][(k + ori) % 3]] = _FACELET_COLORS[_CORNER_COLOR[j][k]]
    for i in range(12):
        j = ep[i]
        ori = eo[i]
        for k in range(2):
            f[_EDGE_FACELET[i][(k + ori) % 2]] = _FACELET_COLORS[_EDGE_COLOR[j][k]]
    return "".join(f)


# 转动表（移植自 gan-cube-emu protocol.rs MOVE_TABLES）face 0-5 = U,R,F,D,L,B
_MOVE_TABLES_CP = [
    [3, 0, 1, 2, 4, 5, 6, 7], [4, 1, 2, 0, 7, 5, 6, 3], [1, 5, 2, 3, 0, 4, 6, 7],
    [0, 1, 2, 3, 5, 6, 7, 4], [0, 2, 6, 3, 4, 1, 5, 7], [0, 1, 3, 7, 4, 5, 2, 6],
]
_MOVE_TABLES_CO = [
    [0] * 8, [2, 0, 0, 1, 1, 0, 0, 2], [1, 2, 0, 0, 2, 1, 0, 0], [0] * 8,
    [0, 1, 2, 0, 0, 2, 1, 0], [0, 0, 1, 2, 0, 0, 2, 1],
]
_MOVE_TABLES_EP = [
    [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], [8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0],
    [0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11], [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],
    [0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11], [0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7],
]
_MOVE_TABLES_EO = [
    [0] * 12, [0] * 12, [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0], [0] * 12,
    [0] * 12, [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1],
]


def _apply_cw(state, face):
    cp, co, ep, eo = state
    t_cp, t_co, t_ep, t_eo = (_MOVE_TABLES_CP[face], _MOVE_TABLES_CO[face],
                              _MOVE_TABLES_EP[face], _MOVE_TABLES_EO[face])
    cp2 = [cp[s] for s in t_cp]
    co2 = [(co[s] + t_co[i]) % 3 for i, s in enumerate(t_cp)]
    ep2 = [ep[s] for s in t_ep]
    eo2 = [(eo[s] + t_eo[i]) % 2 for i, s in enumerate(t_ep)]
    return cp2, co2, ep2, eo2


def apply_move_state(cp, co, ep, eo, face, dir):
    """对状态应用一次转动，返回新状态。dir=0→CW×1，否则 CW×3（即 CCW）"""
    state = (list(cp), list(co), list(ep), list(eo))
    times = 1 if dir == 0 else 3
    for _ in range(times):
        state = _apply_cw(state, face)
    return state


class BitReader:
    """MSB 优先的位读取器（与 firmware BitReader 一致）"""
    def __init__(self, buf: bytes):
        self.buf = buf
        self.bit_pos = 0

    def read_bits(self, count: int) -> int:
        value = 0
        for _ in range(count):
            byte_idx = self.bit_pos // 8
            bit_idx = 7 - (self.bit_pos % 8)
            bit = (self.buf[byte_idx] >> bit_idx) & 1
            value = (value << 1) | bit
            self.bit_pos += 1
        return value


class Gen2MoveEvent:
    def __init__(self, face: int, direction: int, elapsed_ms: int):
        self.face = face
        self.direction = direction
        self.elapsed_ms = elapsed_ms

    @property
    def notation(self) -> str:
        return f"{FACE_NAMES[self.face]}{DIR_NAMES[self.direction]}"

    def __repr__(self):
        return f"Gen2MoveEvent({self.notation}, elapsed={self.elapsed_ms}ms)"


class Gen2GyroEvent:
    def __init__(self, qw: float, qx: float, qy: float, qz: float, vx: int, vy: int, vz: int):
        self.qw = qw
        self.qx = qx
        self.qy = qy
        self.qz = qz
        self.vx = vx
        self.vy = vy
        self.vz = vz

    @property
    def q2_sum(self) -> float:
        return self.qw * self.qw + self.qx * self.qx + self.qy * self.qy + self.qz * self.qz

    def __repr__(self):
        return f"Gen2GyroEvent(qw={self.qw:.4f}, qx={self.qx:.4f}, qy={self.qy:.4f}, qz={self.qz:.4f}, q2_sum={self.q2_sum:.4f})"


class Gen2FaceletsEvent:
    def __init__(self, serial: int, cp: list[int], co: list[int], ep: list[int], eo: list[int]):
        self.serial = serial
        self.cp = cp
        self.co = co
        self.ep = ep
        self.eo = eo

    def __repr__(self):
        return f"Gen2FaceletsEvent(serial={self.serial})"


class Gen2ProtocolParser:
    """解析 Gen2 魔方的 BLE 通知数据"""

    MSG_TYPE_MOVE = 0x02
    MSG_TYPE_GYRO = 0x01
    MSG_TYPE_FACELETS = 0x04

    def __init__(self, mac: bytes):
        self.key, self.iv = derive_key_iv(mac, GEN2_BASE_KEY, GEN2_BASE_IV)
        logger.debug("派生密钥: key=%s iv=%s", self.key.hex(), self.iv.hex())

    def decrypt(self, data: bytes) -> bytes:
        return decrypt_msg(data, self.key, self.iv)

    def parse(self, data: bytes) -> object | None:
        if len(data) != 20:
            logger.warning("Gen2 通知长度异常: %d (期望 20)", len(data))
            return None
        try:
            plain = self.decrypt(data)
        except Exception as e:
            logger.warning("解密失败: %s", e)
            return None

        r = BitReader(plain)
        msg_type = r.read_bits(4)

        if msg_type == self.MSG_TYPE_MOVE:
            return self._parse_move(r)
        elif msg_type == self.MSG_TYPE_GYRO:
            return self._parse_gyro(r)
        elif msg_type == self.MSG_TYPE_FACELETS:
            return self._parse_facelets(r)
        else:
            logger.debug("未知 Gen2 通知类型: 0x%X", msg_type)
            return None

    def _parse_move(self, r: BitReader) -> Gen2MoveEvent | None:
        serial = r.read_bits(8)
        moves = []
        for _ in range(7):
            face = r.read_bits(4)
            direction = r.read_bits(1)
            moves.append((face, direction))
        elapsed_list = []
        for _ in range(7):
            elapsed = r.read_bits(16)
            elapsed_list.append(elapsed)
        for i, (face, direction) in enumerate(moves):
            if face < 6:
                return Gen2MoveEvent(face, direction, elapsed_list[i])
        return None

    def _parse_gyro(self, r: BitReader) -> Gen2GyroEvent:
        qw = self._read_sign_magnitude(r)
        qx = self._read_sign_magnitude(r)
        qy = self._read_sign_magnitude(r)
        qz = self._read_sign_magnitude(r)
        vx = self._read_nibble_signed(r)
        vy = self._read_nibble_signed(r)
        vz = self._read_nibble_signed(r)
        qw_f = qw / 32767.0
        qx_f = qx / 32767.0
        qy_f = qy / 32767.0
        qz_f = qz / 32767.0
        return Gen2GyroEvent(qw_f, qx_f, qy_f, qz_f, vx, vy, vz)

    def _parse_facelets(self, r: BitReader) -> Gen2FaceletsEvent:
        serial = r.read_bits(8)
        cp = [r.read_bits(3) for _ in range(7)]
        co = [r.read_bits(2) for _ in range(7)]
        ep = [r.read_bits(4) for _ in range(11)]
        eo = [r.read_bits(1) for _ in range(11)]
        # Gen2 只发送 7 角 / 11 棱，从魔方约束重建第 8 角 / 第 12 棱
        cp.append(next(i for i in range(8) if i not in cp))    # 缺失角排列索引
        co.append((-sum(co)) % 3)                               # Σco ≡ 0 (mod 3)
        ep.append(next(i for i in range(12) if i not in ep))   # 缺失棱排列索引
        eo.append(sum(eo) % 2)                                  # Σeo ≡ 0 (mod 2)
        return Gen2FaceletsEvent(serial, cp, co, ep, eo)

    @staticmethod
    def _read_i16(r: BitReader) -> int:
        val = r.read_bits(16)
        if val >= 0x8000:
            val -= 0x10000
        return val

    @staticmethod
    def _read_sign_magnitude(r: BitReader) -> int:
        val = r.read_bits(16)
        sign = -1 if (val >> 15) else 1
        mag = val & 0x7FFF
        return sign * mag

    @staticmethod
    def _read_nibble_signed(r: BitReader) -> int:
        val = r.read_bits(4)
        if val >= 8:
            val -= 16
        return val


class BLECubeConnection:
    """管理 BLE 连接与通知订阅"""

    def __init__(self, address: str | None = None, timeout: float = 10.0):
        self.address = address
        self.timeout = timeout
        self._client = None
        self.mac: bytes | None = None

    async def connect(self, address: str | None = None):
        from bleak import BleakClient
        if address:
            self.address = address
        if not self.address:
            raise ValueError("未指定 BLE 设备地址")
        self._client = BleakClient(self.address, timeout=self.timeout)
        await self._client.connect()
        mac_bytes = self._client.address.replace(":", "")
        self.mac = bytes.fromhex(mac_bytes)
        logger.info("BLE 已连接: %s (MAC=%s)", self.address, mac_bytes)

    async def disconnect(self):
        if self._client and self._client.is_connected:
            await self._client.disconnect()
            logger.info("BLE 已断开: %s", self.address)

    async def start_notify(self, handler) -> AsyncIterator[bytes]:
        if not self._client or not self._client.is_connected:
            raise RuntimeError("BLE 未连接")
        queue: asyncio.Queue[bytes] = asyncio.Queue()

        def callback(_sender: int, data: bytearray):
            queue.put_nowait(bytes(data))

        await self._client.start_notify(GEN2_STATE_CHAR_UUID, callback)
        logger.info("已订阅 State Char 通知")
        try:
            while True:
                data = await queue.get()
                yield data
        except asyncio.CancelledError:
            pass
        finally:
            try:
                await self._client.stop_notify(GEN2_STATE_CHAR_UUID)
            except Exception:
                pass

    async def send_command(self, data: bytes):
        if not self._client or not self._client.is_connected:
            raise RuntimeError("BLE 未连接")
        await self._client.write_gatt_char(GEN2_CMD_CHAR_UUID, data, response=False)


async def scan_for_gen2(timeout: float = 5.0) -> str | None:
    """扫描 GAN i3 魔方（设备名以 GANi3 开头），返回设备地址"""
    from bleak import BleakScanner
    logger.info("扫描 GAN i3 魔方... (timeout=%.1fs)", timeout)

    def match_gen2(device, adv_data):
        name = device.name or ""
        return name.startswith("GANi3")

    device = await BleakScanner.find_device_by_filter(match_gen2, timeout=timeout)
    if device:
        logger.info("发现 GAN i3: %s (%s)", device.name, device.address)
        return device.address
    logger.warning("未发现 GAN i3 魔方")
    return None