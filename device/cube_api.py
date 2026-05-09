"""Cube API —— 通过 HTTP 向 ESP32-C3 (gan-cube-emu) 下发魔方转动指令

基于 gan-cube-emu 的 HTTP API：
    POST /api/move    单步转动 {"face": 0-5, "dir": 0-1}
    POST /api/moves   批量转动 [{"face":0,"dir":0}, ...]
    GET  /api/state   获取当前魔方状态 JSON
    GET  /api/facelets kociemba 格式面片字符串

face 映射 (GAN 协议)：
    0=U, 1=R, 2=F, 3=D, 4=L, 5=B

dir 映射：
    0=CW (顺时针 90°)
    1=CCW (逆时针 90°)
    180° 转动拆为两步同方向 CW

用法：
    api = CubeAPI(host="192.168.4.1")
    await api.open()
    state = await api.get_state()
    facelets = await api.get_facelets()
    await api.send_moves("R U R' U'")       # 自动转换标准记号 → face/dir
    await api.send_move_raw(face=1, dir=0)   # 直接指定 face/dir
    await api.close()

单独测试：
    api = MockCubeAPI()
    await api.open()
    ...
"""
import logging

import aiohttp

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# 标准记号 → (face, dir) 映射
# ------------------------------------------------------------------

# GAN 协议 face 编号: 0=U, 1=R, 2=F, 3=D, 4=L, 5=B
FACE_MAP = {
    "U": 0, "R": 1, "F": 2, "D": 3, "L": 4, "B": 5,
}

# dir: 0=CW(90°), 1=CCW(90°)
# R → CW, R' → CCW, R2 → CW+CW (两步)
DIR_CW = 0
DIR_CCW = 1


def parse_move_notation(moves: str) -> list[dict]:
    """将标准魔方记号字符串转换为 face/dir 列表。

    "R u R' U'" → [{"face":1,"dir":0}, {"face":0,"dir":0}, {"face":1,"dir":1}, {"face":0,"dir":1}]

    180° 转动 (R2, U2 等) 拆为两步同方向 CW。
    R2' 等价于 R2（两步 CW），因为 180° 无顺逆之分。

    Args:
        moves: 空格分隔的标准记号，如 "R U R' U' D2"

    Returns:
        [{"face": int, "dir": int}, ...]
    """
    import re
    tokens = re.findall(r"[URFDLBurfdlb]['2]?", moves.strip())
    result = []
    for token in tokens:
        if not token:
            continue
        face_char = token[0].upper()
        face = FACE_MAP.get(face_char)
        if face is None:
            logger.warning("未知面: %s (token: %s)", face_char, token)
            continue

        # 解析修饰符: ' = CCW, 2 = 180°
        if "2" in token:
            # 180° = 两步 CW
            result.append({"face": face, "dir": DIR_CW})
            result.append({"face": face, "dir": DIR_CW})
        elif "'" in token:
            result.append({"face": face, "dir": DIR_CCW})
        else:
            result.append({"face": face, "dir": DIR_CW})
    return result


class CubeAPI:
    """封装 aiohttp 对 gan-cube-emu ESP32 HTTP 接口的调用。

    ESP32 AP 模式默认 192.168.4.1。
    """

    def __init__(self, host: str = "192.168.4.1", port: int = 80, timeout: float = 5.0):
        self.base_url = f"http://{host}:{port}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def open(self):
        """初始化 aiohttp Session。"""
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        logger.info("CubeAPI session 已创建，目标: %s", self.base_url)

    async def close(self):
        """关闭 aiohttp Session。"""
        if self._session:
            await self._session.close()
            self._session = None
            logger.info("CubeAPI session 已关闭")

    async def _request(self, method: str, path: str, **kwargs) -> dict | str:
        """通用 HTTP 请求，自动处理异常。"""
        if not self._session:
            logger.warning("session 未初始化，跳过请求")
            return {}
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(method, url, **kwargs) as resp:
                resp.raise_for_status()
                # /api/facelets 返回纯文本，其他返回 JSON
                if path == "/api/facelets":
                    return await resp.text()
                return await resp.json()
        except aiohttp.ClientError as e:
            logger.warning("请求失败 %s %s: %s", method, url, e)
            return {}

    # ------------------------------------------------------------------
    # 转动下发
    # ------------------------------------------------------------------

    async def send_move_raw(self, face: int, dir: int) -> dict:
        """单步转动，直接指定 face/dir。

        Args:
            face: 0-5 (U/R/F/D/L/B)
            dir: 0=CW, 1=CCW
        """
        return await self._request("POST", "/api/move", json={"face": face, "dir": dir})

    async def send_moves_raw(self, steps: list[dict]) -> dict:
        """批量转动，直接指定 [{"face":0,"dir":0}, ...]。"""
        return await self._request("POST", "/api/moves", json=steps)

    async def send_moves(self, moves: str) -> dict:
        """下发标准记号转动序列，自动转换为 face/dir。

        Args:
            moves: 标准记号，如 "R U R' U'"
        """
        steps = parse_move_notation(moves)
        if not steps:
            logger.warning("解析后无有效转动: %s", moves)
            return {}
        logger.info("下发转动: %s → %d 步", moves, len(steps))
        return await self.send_moves_raw(steps)

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    async def get_state(self) -> dict:
        """获取当前魔方状态 JSON。"""
        return await self._request("GET", "/api/state")

    async def get_facelets(self) -> str:
        """获取 kociemba 格式面片字符串。"""
        result = await self._request("GET", "/api/facelets")
        return result if isinstance(result, str) else ""

    async def poll(self) -> dict:
        """轮询状态（兼容 CubeLoop 的旧接口）。"""
        return await self.get_state()


# ------------------------------------------------------------------
# Mock —— 用于单独测试 CubeLoop，不需要真实 ESP32
# ------------------------------------------------------------------

class MockCubeAPI:
    """模拟 gan-cube-emu HTTP 接口，用于测试。"""

    def __init__(self):
        self.connected = True
        self.battery = 80
        self._moves_log: list[dict] = []     # 记录每条 send_moves 的 steps
        self._facelets = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
        self._state = {
            "connected": True,
            "battery": 80,
            "facelets": self._facelets,
        }

    async def open(self):
        logger.info("MockCubeAPI: open")

    async def close(self):
        logger.info("MockCubeAPI: close")

    async def send_move_raw(self, face: int, dir: int) -> dict:
        logger.info("MockCubeAPI: move face=%d dir=%d", face, dir)
        self._moves_log.append({"face": face, "dir": dir})
        return {"ok": True}

    async def send_moves_raw(self, steps: list[dict]) -> dict:
        logger.info("MockCubeAPI: moves %s", steps)
        self._moves_log.extend(steps)
        return {"ok": True}

    async def send_moves(self, moves: str) -> dict:
        steps = parse_move_notation(moves)
        logger.info("MockCubeAPI: send_moves %s → %d 步", moves, len(steps))
        self._moves_log.extend(steps)
        return {"ok": True}

    async def get_state(self) -> dict:
        return self._state

    async def get_facelets(self) -> str:
        return self._facelets

    async def poll(self) -> dict:
        return self._state

    @property
    def moves_log(self) -> list[dict]:
        """已下发的转动记录（测试断言用）。"""
        return self._moves_log


if __name__ == "__main__":
    """单独测试（两种模式）：

    1. Mock 测试（无需 ESP32）：
        python -m device.cube_api

    2. 真实设备测试：
        python -m device.cube_api 192.168.4.1
    """
    import sys
    import asyncio
    logging.basicConfig(level=logging.INFO)

    host = sys.argv[1] if len(sys.argv) > 1 else None

    async def _test():
        if host:
            api = CubeAPI(host=host)
            print(f"目标: http://{host}")
        else:
            api = MockCubeAPI()
            print("使用 MockCubeAPI")

        await api.open()

        print("\n--- get_state ---")
        state = await api.get_state()
        print(state)

        print("\n--- get_facelets ---")
        facelets = await api.get_facelets()
        print(facelets)

        print("\n--- send_moves R U R' U' ---")
        result = await api.send_moves("R U R' U'")
        print(result)

        if isinstance(api, MockCubeAPI):
            print(f"\nmoves_log: {api.moves_log}")

        await api.close()

    asyncio.run(_test())