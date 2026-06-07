"""二阶魔方（Pocket Cube）求解器 —— 仅使用 RUF 转动

二阶魔方只有 8 个角块，没有棱块和中心块。

# Ortega 方法：
1. 第一层（First Face）：使底层同色（co[4:8]=0）
2. OLL：识别表定向顶层（co[0:4]=0）
3. PBL：预计算 BFS 表排列两层

继承三阶的cubie cube，仅使用co cp
添加限制：仅使用 R、U、F 三个面的转动
"""
import logging
from typing import Optional, Dict, Tuple
from collections import deque
from .cfop_solver import CubieCube, invert_alg
from .pocket_pbl_table import load_eg_table

logger = logging.getLogger(__name__)

FACE_NAMES = ['U', 'R', 'F', 'D', 'L', 'B']
RUF_FACES = [0, 1, 2]


class PocketCube(CubieCube):
    """二阶魔方状态表示（仅角块）"""
    __slots__ = ('cp', 'co')

    @staticmethod
    def solved():
        return PocketCube()

    def copy(self):
        return PocketCube(self.cp, self.co)

    def apply_cw(self, face):
        if face not in RUF_FACES:
            return
        super().apply_cw(face)

    def apply_move(self, face, dir):
        if face not in RUF_FACES:
            return
        super().apply_move(face, dir)

    def is_solved(self):
        return self.cp == list(range(8)) and self.co == [0] * 8

    def is_first_layer_done(self):
        """底层4个角块朝向全为0（底面同色），不要求位置正确"""
        return all(self.co[i] == 0 for i in range(4, 8)) and set(self.cp[i] for i in range(4, 8)) == set(range(4, 8))

    def is_top_oriented(self):
        """顶层4个角块朝向全为0（顶面同色）"""
        return all(self.co[i] == 0 for i in range(4))

    def state_key(self):
        """完整状态key"""
        return (tuple(self.cp), tuple(self.co))


def apply_alg_str(state: PocketCube, alg_str: str) -> PocketCube:
    """应用算法字符串到魔方状态"""
    if not alg_str:
        return state
    s = state.copy()
    for move in alg_str.strip().split():
        if not move:
            continue
        face_idx = FACE_NAMES.index(move[0])
        if len(move) == 1:
            s.apply_cw(face_idx)
        elif move[1] == '2':
            s.apply_cw(face_idx)
            s.apply_cw(face_idx)
        elif move[1] == "'":
            s.apply_cw(face_idx)
            s.apply_cw(face_idx)
            s.apply_cw(face_idx)
    return s


# =============================================
# Ortega 算法库（仅使用 RUF）
# =============================================

# OLL 算法：使顶层同色（co[0:4]=0）
# 注意：RUF 下 F/R 会改变底层朝向，但 PBL 会处理
ORTEGA_OLL_ALGS = {
    "sune":     "R U R' U R U2 R'",
    "antisune": "R U2 R' U' R U' R'",
    "t":        "R U R' U' R' F R F'",
    "l":        "F R' F' R U R U' R'",
    "u":        "F R U R' U' F'",
    "h":        "R2 U2 R' U2 R2",
    "pi":       "F R U R' U' R U R' U' F'",
}

# PBL 算法仅作参考（实际求解使用 EG 表 BFS）
ORTEGA_PBL_ALGS = {
    "adj_adj":    "R U R' U' R' F R2 U' R' U' R U R' F'",
    "adj_diag":   "F R U' R' U' R U R' F' R U R' U' R' F R F'",
    "diag_diag":  "F R U' R' U' R U R' F' R U R' U' R' F R F'",
}


def build_oll_recognition() -> Dict:
    """构建 OLL 识别表

    通过预设公式 + AUF 变体构建：
    对每个 OLL 算法 × 4 AUF pre，
    将逆作用于 solved 状态，得到该算法能解决的 co[0:4] 状态。

    OLL 只看顶层朝向（co[0:4]），不看排列。
    """
    table = {}
    solved = PocketCube.solved()
    AUF_STRS = {0: '', 1: 'U', 2: 'U2', 3: "U'"}

    for name, alg in ORTEGA_OLL_ALGS.items():
        for pre in range(4):
            pre_str = AUF_STRS[pre]
            full_alg = (pre_str + ' ' + alg).strip() if pre_str else alg
            inv = invert_alg(full_alg)
            s = apply_alg_str(solved.copy(), inv)

            co_key = tuple(s.co[i] for i in range(4))
            if co_key not in table or len(full_alg.split()) < len(table[co_key][1].split()):
                table[co_key] = (name, full_alg)

    table[(0, 0, 0, 0)] = ('skip', '')
    return table


def build_pbl_recognition() -> Dict:
    """构建 PBL 识别表

    通过预设公式 + AUF 变体构建，与 cfop_solver 一致：
    对每个 PBL 算法 × 4 AUF pre × 4 AUF post，
    将逆作用于 solved 状态，得到该算法能解决的 (cp, co) 状态。
    """
    table = {}
    solved = PocketCube.solved()
    AUF_STRS = {0: '', 1: 'U', 2: 'U2', 3: "U'"}

    for name, alg in ORTEGA_PBL_ALGS.items():
        for pre in range(4):
            for post in range(4):
                pre_str = AUF_STRS[pre]
                post_str = AUF_STRS[post]
                full_alg = ' '.join(p for p in [pre_str, alg, post_str] if p)
                inv = invert_alg(full_alg)
                s = apply_alg_str(solved.copy(), inv)

                cp_key = tuple(s.cp[i] for i in range(8))
                co_key = tuple(s.co[i] for i in range(8))
                key = (cp_key, co_key)

                if key not in table or len(full_alg.split()) < len(table[key][1].split()):
                    table[key] = (name, full_alg)

    # 已还原状态
    solved_key = (tuple(range(8)), (0, 0, 0, 0, 0, 0, 0, 0))
    table[solved_key] = ('skip', '')
    return table


class PocketSolver:
    """二阶魔方求解器（RUF 限定）

    Ortega 方法 (method='ortega')：
    1. 第一层：BFS 使底层同色 (co[4:8]=0)
    2. OLL：识别表定向顶层 (co[0:4]=0)
    3. PBL：EG 表排列两层

    EG 方法 (method='eg')：
    1. 第一层：BFS 使底层同色 (co[4:8]=0)
    2. EG 表一步求解（跳过 OLL，直接用 EG 表）
    """

    def __init__(self, method='ortega'):
        self.method = method
        self.max_depth = 11
        self.oll_rec = build_oll_recognition()
        self.eg_table = load_eg_table()
        logger.info(f"初始化 PocketSolver: OLL表={len(self.oll_rec)} EG表={len(self.eg_table)}")

    def solve(self, facelet_str: str) -> Optional[dict]:
        full_cube = CubieCube.from_facelet(facelet_str)
        cube = PocketCube(full_cube.cp, full_cube.co)

        if cube.is_solved():
            return {"solution": "", "first_layer": "", "oll": "", "pbl": ""}

        # 第一步：完成底层
        fl_moves = self._solve_first_layer(cube)
        if fl_moves is None:
            logger.error("无法完成第一层")
            return None

        cube = apply_alg_str(cube, fl_moves)
        logger.info(f"第一层: {fl_moves}")

        # 第二步：OLL 定向顶层
        if self.method == 'ortega':
            oll_moves = self._solve_oll(cube)
        else:
            oll_moves = "" # pbl 表就是eg表

        if oll_moves:
            cube = apply_alg_str(cube, oll_moves)
            logger.info(f"OLL: {oll_moves}")

        # 第三步：PBL 排列两层
        pbl_moves = self._solve_pbl(cube)
        if pbl_moves is None:
            logger.error("无法排列两层")
            return None

        if pbl_moves:
            cube = apply_alg_str(cube, pbl_moves)
            logger.info(f"PBL: {pbl_moves}")

        if not cube.is_solved():
            logger.error("求解失败")
            return None

        solution = " ".join(filter(None, [fl_moves, oll_moves, pbl_moves])).strip()
        return {
            "solution": solution,
            "first_layer": fl_moves,
            "oll": oll_moves,
            "pbl": pbl_moves,
        }

    def _solve_first_layer(self, cube: PocketCube) -> Optional[str]:
        """BFS 搜索完成第一层"""
        if cube.is_first_layer_done():
            return ""

        queue = deque([(cube.copy(), "")])
        visited = set()
        MOVE_SUFFIXES = [('', 1), ('2', 2), ("'", 3)]

        while queue:
            state, path = queue.popleft()
            if len(path.split()) > self.max_depth:
                continue

            key = state.state_key()
            if key in visited:
                continue
            visited.add(key)

            if state.is_first_layer_done():
                return path.strip()

            for face in RUF_FACES:
                for suffix, turns in MOVE_SUFFIXES:
                    ns = state.copy()
                    for _ in range(turns):
                        ns.apply_cw(face)
                    ms = FACE_NAMES[face] + suffix
                    queue.append((ns, (path + ' ' + ms).strip()))

        return None

    def _solve_oll(self, cube: PocketCube) -> Optional[str]:
        """识别表定向顶层 (co[0:4]=0)"""
        if cube.is_top_oriented():
            return ""

        co_key = tuple(cube.co[i] for i in range(4))
        if co_key in self.oll_rec:
            name, alg = self.oll_rec[co_key]
            if name == 'skip':
                return ""
            return alg

        logger.error(f"OLL 未覆盖 co={co_key}")
        return None

    def _solve_pbl(self, cube: PocketCube) -> Optional[str]:
        """EG 表排列两层（表中存的是 solved→state 的正向路径，需取逆）"""
        if cube.is_solved():
            return ""

        key = (tuple(cube.cp), tuple(cube.co))
        if key in self.eg_table:
            fwd = self.eg_table[key]
            if not fwd:
                return ""
            return invert_alg(fwd)

        logger.error(f"PBL 未覆盖 state")
        return None


def solve_pocket(facelet_str: str, method: str = 'ortega') -> Optional[dict]:
    solver = PocketSolver(method=method)
    return solver.solve(facelet_str)
