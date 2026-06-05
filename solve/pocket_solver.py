"""二阶魔方（Pocket Cube）求解器 —— 仅使用 RUF 转动

二阶魔方只有 8 个角块，没有棱块和中心块。
本求解器使用 Ortega 方法的简化版本：
1. 第一层（First Face）：使底层同色
2. 定向顶层（Orient Top Layer, OLL）：使顶层同色
3. 排列顶层（Permute Both Layers, PBL）：完成求解

限制：仅使用 R、U、F 三个面的转动（适配三轴机械臂）
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 二阶魔方只有 8 个角块，编号 0-7
# 角块位置编号（与三阶魔方的角块编号一致）：
#   0=URF, 1=UFL, 2=ULB, 3=UBR
#   4=DFR, 5=DLF, 6=DBL, 7=DRB

# RUF 转动的角块置换表（仅涉及 8 个角块）
# 每个转动影响 4 个角块的位置和方向

# R 面顺时针转动（face=1）
MOVE_CP_R = [3, 1, 2, 7, 0, 5, 6, 4]  # 角块位置置换
MOVE_CO_R = [1, 0, 0, 2, 2, 0, 0, 1]  # 角块方向变化

# U 面顺时针转动（face=0）
MOVE_CP_U = [1, 2, 3, 0, 4, 5, 6, 7]
MOVE_CO_U = [0, 0, 0, 0, 0, 0, 0, 0]

# F 面顺时针转动（face=2）
MOVE_CP_F = [1, 5, 2, 3, 0, 4, 6, 7]
MOVE_CO_F = [2, 1, 0, 0, 1, 2, 0, 0]

MOVE_TABLES = {
    0: (MOVE_CP_U, MOVE_CO_U),  # U
    1: (MOVE_CP_R, MOVE_CO_R),  # R
    2: (MOVE_CP_F, MOVE_CO_F),  # F
}

FACE_NAMES = ['U', 'R', 'F', 'D', 'L', 'B']
RUF_FACES = [0, 1, 2]  # 仅使用 U, R, F


class PocketCube:
    """二阶魔方状态表示（仅角块）"""
    __slots__ = ('cp', 'co')

    def __init__(self, cp=None, co=None):
        self.cp = list(cp) if cp else list(range(8))
        self.co = list(co) if co else [0] * 8

    @staticmethod
    def solved():
        return PocketCube()

    def copy(self):
        return PocketCube(self.cp, self.co)

    def is_solved(self):
        return self.cp == list(range(8)) and self.co == [0] * 8

    def apply_move(self, face: int, times: int = 1):
        """应用转动（face: 0=U, 1=R, 2=F）"""
        if face not in MOVE_TABLES:
            raise ValueError(f"Invalid face {face} for RUF-only solver")
        
        t_cp, t_co = MOVE_TABLES[face]
        for _ in range(times % 4):
            old_cp = list(self.cp)
            old_co = list(self.co)
            for i in range(8):
                src = t_cp[i]
                self.cp[i] = old_cp[src]
                self.co[i] = (old_co[src] + t_co[i]) % 3

    def apply_moves_str(self, moves_str: str):
        """应用转动序列字符串"""
        for m in moves_str.strip().split():
            if not m:
                continue
            face_char = m[0].upper()
            if face_char not in ['U', 'R', 'F']:
                logger.warning(f"跳过非 RUF 转动: {m}")
                continue
            
            face = {'U': 0, 'R': 1, 'F': 2}[face_char]
            if len(m) == 1:
                self.apply_move(face, 1)
            elif m[1] == '2':
                self.apply_move(face, 2)
            elif m[1] == "'":
                self.apply_move(face, 3)

    def get_bottom_colors(self):
        """获取底层 4 个角块的 D 面颜色（用于判断第一层是否完成）"""
        # 底层角块：4=DFR, 5=DLF, 6=DBL, 7=DRB
        # 每个角块的 D 面颜色由其位置和方向决定
        colors = []
        for pos in [4, 5, 6, 7]:
            cubie = self.cp[pos]
            ori = self.co[pos]
            # 角块 cubie 在位置 pos，方向为 ori
            # D 面颜色是该角块的第 (3-ori)%3 个颜色
            # 简化：判断是否所有底层角块的 D 面都是同一颜色
            colors.append((cubie, ori))
        return colors

    def is_first_layer_done(self):
        """判断底层是否同色"""
        colors = self.get_bottom_colors()
        # 简化判断：底层 4 个角块都在正确位置且方向正确
        for i, pos in enumerate([4, 5, 6, 7]):
            if self.cp[pos] != pos or self.co[pos] != 0:
                return False
        return True

    def get_top_orientation(self):
        """获取顶层方向状态（用于 OLL）"""
        # 顶层角块：0=URF, 1=UFL, 2=ULB, 3=UBR
        ori_sum = sum(self.co[i] for i in range(4))
        return ori_sum

    def is_top_oriented(self):
        """判断顶层是否已定向（所有角块 U 面同色）"""
        return all(self.co[i] == 0 for i in range(4))


class PocketSolver:
    """二阶魔方求解器（RUF 限定）"""

    def __init__(self):
        self.max_depth = 11  # RUF 限定下的最大搜索深度
        self._build_tables()

    def _build_tables(self):
        """构建求解表（简化版 IDA*）"""
        # 对于二阶魔方，状态空间较小，可以使用简单的 BFS/IDA*
        # 这里使用预定义的算法库
        self.first_layer_algs = self._get_first_layer_algs()
        self.oll_algs = self._get_oll_algs()
        self.pbl_algs = self._get_pbl_algs()

    def _get_first_layer_algs(self):
        """第一层算法库（使用 RUF 完成底层）"""
        # 简化：使用常见的 RUF 组合
        return [
            "",
            "R U R'",
            "R U2 R'",
            "R U' R'",
            "F U F'",
            "F U2 F'",
            "F U' F'",
            "R U R' U R U2 R'",
            "F U F' U F U2 F'",
            "R U' R' U' R U R'",
            "F U' F' U' F U F'",
        ]

    def _get_oll_algs(self):
        """OLL 算法库（RUF 限定）"""
        return {
            # 顶层定向算法（使顶层同色）
            "sune": "R U R' U R U2 R'",
            "antisune": "R U2 R' U' R U' R'",
            "h": "F R U R' U' F' U F R U R' U' F'",
            "pi": "F R U R' U' R U R' U' F'",
            "u": "F R U R' U' F'",
            "t": "R U R' U' R' F R F'",
            "l": "F R' F' R U R U' R'",
        }

    def _get_pbl_algs(self):
        """PBL 算法库（RUF 限定）"""
        return {
            # 顶层排列算法
            "adjacent": "R U R' U' R' F R2 U' R' U' R U R' F'",
            "diagonal": "F R U' R' U' R U R' F' R U R' U' R' F R F'",
            "y_perm": "F R U' R' U' R U R' F' R U R' U' R' F R F'",
        }

    def solve(self, facelet_str: str) -> Optional[dict]:
        """求解二阶魔方
        
        Args:
            facelet_str: 54 字符的面片字符串（三阶格式，但只使用角块信息）
        
        Returns:
            包含求解步骤的字典，或 None（无解）
        """
        logger.info("开始求解二阶魔方（RUF 限定）")
        
        # 从三阶面片字符串提取角块信息
        cube = self._extract_corners_from_facelet(facelet_str)
        
        if cube.is_solved():
            logger.info("魔方已复原")
            return {
                "solution": "",
                "first_layer": "",
                "oll": "",
                "pbl": "",
            }

        # 第一步：完成底层
        first_layer_moves = self._solve_first_layer(cube)
        if first_layer_moves is None:
            logger.error("无法完成第一层")
            return None
        
        cube.apply_moves_str(first_layer_moves)
        logger.info(f"第一层完成: {first_layer_moves}")

        # 第二步：定向顶层（OLL）
        oll_moves = self._solve_oll(cube)
        if oll_moves is None:
            logger.error("无法完成 OLL")
            return None
        
        cube.apply_moves_str(oll_moves)
        logger.info(f"OLL 完成: {oll_moves}")

        # 第三步：排列顶层（PBL）
        pbl_moves = self._solve_pbl(cube)
        if pbl_moves is None:
            logger.error("无法完成 PBL")
            return None
        
        cube.apply_moves_str(pbl_moves)
        logger.info(f"PBL 完成: {pbl_moves}")

        if not cube.is_solved():
            logger.error("求解失败：最终状态未复原")
            return None

        solution = " ".join(filter(None, [first_layer_moves, oll_moves, pbl_moves]))
        logger.info(f"求解完成，总步数: {len(solution.split())}")

        return {
            "solution": solution,
            "first_layer": first_layer_moves,
            "oll": oll_moves,
            "pbl": pbl_moves,
        }

    def _extract_corners_from_facelet(self, facelet_str: str) -> PocketCube:
        """从三阶魔方面片字符串提取角块信息"""
        # 三阶魔方的角块面片位置（与 cfop_solver.py 一致）
        CORNER_FACELET = [
            [8, 9, 20],    # URF
            [6, 18, 38],   # UFL
            [0, 36, 47],   # ULB
            [2, 45, 11],   # UBR
            [29, 26, 15],  # DFR
            [27, 44, 24],  # DLF
            [33, 53, 42],  # DBL
            [35, 17, 51],  # DRB
        ]
        
        CORNER_COLOR = [
            [0, 1, 2],  # URF: U R F
            [0, 2, 4],  # UFL: U F L
            [0, 4, 5],  # ULB: U L B
            [0, 5, 1],  # UBR: U B R
            [3, 2, 1],  # DFR: D F R
            [3, 4, 2],  # DLF: D L F
            [3, 5, 4],  # DBL: D B L
            [3, 1, 5],  # DRB: D R B
        ]
        
        COLOR_CHARS = ['U', 'R', 'F', 'D', 'L', 'B']
        
        f = list(facelet_str)
        cube = PocketCube()
        
        for i in range(8):
            for j in range(8):
                for ori in range(3):
                    if all(f[CORNER_FACELET[i][(k + ori) % 3]] == COLOR_CHARS[CORNER_COLOR[j][k]] for k in range(3)):
                        cube.cp[i] = j
                        cube.co[i] = ori
                        break
        
        return cube

    def _solve_first_layer(self, cube: PocketCube) -> Optional[str]:
        """使用 IDA* 搜索完成第一层"""
        if cube.is_first_layer_done():
            return ""
        
        # 简化：使用 BFS 搜索（深度限制）
        from collections import deque
        
        queue = deque([(cube.copy(), "")])
        visited = set()
        
        while queue:
            state, path = queue.popleft()
            
            if len(path.split()) > self.max_depth:
                continue
            
            state_key = (tuple(state.cp), tuple(state.co))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            if state.is_first_layer_done():
                return path.strip()
            
            # 尝试所有 RUF 转动
            for face in RUF_FACES:
                for times in [1, 2, 3]:
                    new_state = state.copy()
                    new_state.apply_move(face, times)
                    
                    move_str = FACE_NAMES[face]
                    if times == 2:
                        move_str += "2"
                    elif times == 3:
                        move_str += "'"
                    
                    new_path = f"{path} {move_str}".strip()
                    queue.append((new_state, new_path))
        
        logger.warning("第一层搜索超时")
        return None

    def _solve_oll(self, cube: PocketCube) -> Optional[str]:
        """定向顶层（使顶层同色）"""
        if cube.is_top_oriented():
            return ""
        
        # 尝试预定义的 OLL 算法
        for alg_name, alg in self.oll_algs.items():
            for u_rot in range(4):
                test_cube = cube.copy()
                test_cube.apply_move(0, u_rot)  # U 面旋转
                test_cube.apply_moves_str(alg)
                
                if test_cube.is_top_oriented():
                    u_moves = "U" if u_rot == 1 else "U2" if u_rot == 2 else "U'" if u_rot == 3 else ""
                    return f"{u_moves} {alg}".strip() if u_rot > 0 else alg
        
        # 如果预定义算法无效，使用搜索
        return self._search_oll(cube)

    def _search_oll(self, cube: PocketCube) -> Optional[str]:
        """搜索 OLL 解法"""
        from collections import deque
        
        queue = deque([(cube.copy(), "")])
        visited = set()
        
        while queue:
            state, path = queue.popleft()
            
            if len(path.split()) > 8:
                continue
            
            state_key = (tuple(state.cp), tuple(state.co))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            if state.is_top_oriented():
                return path.strip()
            
            for face in RUF_FACES:
                for times in [1, 2, 3]:
                    new_state = state.copy()
                    new_state.apply_move(face, times)
                    
                    move_str = FACE_NAMES[face]
                    if times == 2:
                        move_str += "2"
                    elif times == 3:
                        move_str += "'"
                    
                    new_path = f"{path} {move_str}".strip()
                    queue.append((new_state, new_path))
        
        return None

    def _solve_pbl(self, cube: PocketCube) -> Optional[str]:
        """排列顶层（完成求解）"""
        if cube.is_solved():
            return ""
        
        # 尝试预定义的 PBL 算法
        for alg_name, alg in self.pbl_algs.items():
            for u_rot in range(4):
                test_cube = cube.copy()
                test_cube.apply_move(0, u_rot)
                test_cube.apply_moves_str(alg)
                
                if test_cube.is_solved():
                    u_moves = "U" if u_rot == 1 else "U2" if u_rot == 2 else "U'" if u_rot == 3 else ""
                    return f"{u_moves} {alg}".strip() if u_rot > 0 else alg
        
        # 搜索解法
        return self._search_pbl(cube)

    def _search_pbl(self, cube: PocketCube) -> Optional[str]:
        """搜索 PBL 解法"""
        from collections import deque
        
        queue = deque([(cube.copy(), "")])
        visited = set()
        
        while queue:
            state, path = queue.popleft()
            
            if len(path.split()) > 10:
                continue
            
            state_key = (tuple(state.cp), tuple(state.co))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            if state.is_solved():
                return path.strip()
            
            for face in RUF_FACES:
                for times in [1, 2, 3]:
                    new_state = state.copy()
                    new_state.apply_move(face, times)
                    
                    move_str = FACE_NAMES[face]
                    if times == 2:
                        move_str += "2"
                    elif times == 3:
                        move_str += "'"
                    
                    new_path = f"{path} {move_str}".strip()
                    queue.append((new_state, new_path))
        
        return None


def solve_pocket(facelet_str: str) -> Optional[dict]:
    """求解二阶魔方的便捷函数
    
    Args:
        facelet_str: 54 字符的面片字符串（三阶格式）
    
    Returns:
        求解结果字典或 None
    """
    solver = PocketSolver()
    return solver.solve(facelet_str)
