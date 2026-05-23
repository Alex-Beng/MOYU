import os
import pickle
import re
from collections import deque
import random
from solve.ALLL import EX_ALLLS

DEBUG = False
DEBUG = True

ALLL_PROB = 0.5

def _dbg(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

SOLVED_FACELET = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

MOVE_CP = [
    [3, 0, 1, 2, 4, 5, 6, 7],
    [4, 1, 2, 0, 7, 5, 6, 3],
    [1, 5, 2, 3, 0, 4, 6, 7],
    [0, 1, 2, 3, 5, 6, 7, 4],
    [0, 2, 6, 3, 4, 1, 5, 7],
    [0, 1, 3, 7, 4, 5, 2, 6],
]

MOVE_CO = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [2, 0, 0, 1, 1, 0, 0, 2],
    [1, 2, 0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 2, 0, 0, 2, 1, 0],
    [0, 0, 1, 2, 0, 0, 2, 1],
]

MOVE_EP = [
    [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],
    [8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0],
    [0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11],
    [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],
    [0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11],
    [0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7],
]

MOVE_EO = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1],
]

CORNER_FACELET = [
    [8, 9, 20],
    [6, 18, 38],
    [0, 36, 47],
    [2, 45, 11],
    [29, 26, 15],
    [27, 44, 24],
    [33, 53, 42],
    [35, 17, 51],
]

CORNER_COLOR = [
    [0, 1, 2],
    [0, 2, 4],
    [0, 4, 5],
    [0, 5, 1],
    [3, 2, 1],
    [3, 4, 2],
    [3, 5, 4],
    [3, 1, 5],
]

EDGE_FACELET = [
    [5, 10],
    [7, 19],
    [3, 37],
    [1, 46],
    [32, 16],
    [28, 25],
    [30, 43],
    [34, 52],
    [23, 12],
    [21, 41],
    [50, 39],
    [48, 14],
]

EDGE_COLOR = [
    [0, 1],
    [0, 2],
    [0, 4],
    [0, 5],
    [3, 1],
    [3, 2],
    [3, 4],
    [3, 5],
    [2, 1],
    [2, 4],
    [5, 4],
    [5, 1],
]

CENTER_FACELET = [4, 13, 22, 31, 40, 49]

COLOR_CHARS = ['U', 'R', 'F', 'D', 'L', 'B']

MOVE_NAMES = ['U', 'U2', "U'", 'R', 'R2', "R'", 'F', 'F2', "F'", 'D', 'D2', "D'", 'L', 'L2', "L'", 'B', 'B2', "B'"]

ROTATION_FACE_MAP = {
    'x': {'U': 'F', 'F': 'D', 'D': 'B', 'B': 'U', 'R': 'R', 'L': 'L'},
    'y': {'U': 'U', 'R': 'B', 'F': 'R', 'L': 'F', 'B': 'L', 'D': 'D'},
    'z': {'U': 'L', 'R': 'U', 'D': 'R', 'L': 'D', 'F': 'F', 'B': 'B'},
}

DOUBLE_MOVE_MAP = {
    'u':  {1: ["D",  'y'],        2: ["D2", 'y', 'y'],        3: ["D'",  'y', 'y', 'y']},
    'd':  {1: ["U",  'y','y','y'],2: ["U2", 'y', 'y'],        3: ["U'",  'y']},
    'r':  {1: ["L",  'x'],        2: ["L2", 'x', 'x'],        3: ["L'",  'x', 'x', 'x']},
    'l':  {1: ["R",  'x','x','x'],2: ["R2", 'x', 'x'],        3: ["R'",  'x']},
    'f':  {1: ["B",  'z'],        2: ["B2", 'z', 'z'],        3: ["B'",  'z', 'z', 'z']},
    'b':  {1: ["F",  'z','z','z'],2: ["F2", 'z', 'z'],        3: ["F'",  'z']},
}

EMS_MOVE_MAP = {
    'E': {1: ["D'", "U",  'y','y','y'], 2: ["D2", "U2", 'y','y'], 3: ["D",  "U'", 'y']},
    'M': {1: ["L'", "R",  'x','x','x'], 2: ["L2", "R2", 'x','x'], 3: ["L",  "R'", 'x']},
    'S': {1: ["F'", "B",  'z'],         2: ["F2", "B2", 'z','z'], 3: ["F",  "B'", 'z','z','z']},
}

def apply_rotation(face, rot):
    return ROTATION_FACE_MAP[rot].get(face, face)

def convert_alg_to_basic(alg_str):
    raw = alg_str.strip('"')
    # Expand bracket notation: (moves)2 or (moves)2' — repeat bracketed sequence
    def expand_brackets(s):
        result = s
        # Keep expanding until no more brackets
        while True:
            m = re.search(r'\(([^)]+)\)([2\'2\']?)', result)
            if not m:
                break
            inner = m.group(1).strip()
            repeat_mod = m.group(2) if m.group(2) else ''
            # (X)2 means repeat twice, (X)2' means repeat twice then inverse? No — (X)2' = (X)(X'), but conventionally it's just (X)2 with a prime modifier on the whole thing
            # Standard convention: (seq)N where N=2 means repeat 2 times; (seq)2' means repeat 2 times then apply prime to last repetition
            # For simplicity: (seq)2 = seq seq, (seq)2' not standard but treat as seq seq'
            repeat_count = 2 if '2' in repeat_mod else 1
            expanded_inner = ' '.join([inner] * repeat_count)
            result = result[:m.start()] + ' ' + expanded_inner + ' ' + result[m.end():]
        return result

    raw = expand_brackets(raw)

    tokens = re.findall(r"[URFDLBurfdlbEMSxyz]2'?|[URFDLBurfdlbEMSxyz]['2]?", raw)

    MOD_COUNT = {'': 1, "'": 3, '2': 2, "2'": 2}

    expanded = []
    for t in tokens:
        if not t:
            continue
        base = t[0]
        mod = t[1] if len(t) > 1 else ''
        count = MOD_COUNT.get(mod, 1)

        if base in 'URFDLB':
            expanded.append(t)
        elif base in 'xyz':
            for _ in range(count % 4):
                expanded.append(base)
        elif base in 'urfdlb':
            seq = DOUBLE_MOVE_MAP[base].get(count % 4)
            if seq:
                expanded.extend(seq)
        elif base in 'EMS':
            seq = EMS_MOVE_MAP[base].get(count % 4)
            if seq:
                expanded.extend(seq)

    result = list(expanded)
    raw = ' '.join(list(expanded))
    i = len(result) - 1
    while i >= 0:
        t = result[i]
        if t in ('x', 'y', 'z'):
            rot = t
            for j in range(i + 1, len(result)):
                m = result[j]
                if m in ('x', 'y', 'z'):
                    continue
                face = m[0]
                mod_j = m[1] if len(m) > 1 else ''
                result[j] = apply_rotation(face, rot) + mod_j
            del result[i]
        i -= 1

    simplified = []
    i = 0
    while i < len(result):
        move = result[i]
        base = move[0]
        mod = move[1] if len(move) > 1 else ''
        total = MOD_COUNT.get(mod, 1)

        j = i + 1
        while j < len(result):
            next_move = result[j]
            next_base = next_move[0]
            if next_base != base:
                break
            next_mod = next_move[1] if len(next_move) > 1 else ''
            total = (total + MOD_COUNT.get(next_mod, 1)) % 4
            j += 1

        if total == 1:
            simplified.append(base)
        elif total == 2:
            simplified.append(base + '2')
        elif total == 3:
            simplified.append(base + "'")
        i = j

    return ' '.join(simplified), raw

F2L_PAIRS = [
    (4, 8),
    (5, 9),
    (6, 10),
    (7, 11),
]

F2L_MOVE_INDICES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17]

# F2L macro moves: triggers + U-layer turns
# Each trigger is a 3-move sequence (X U X', X U' X', X' U X, X' U' X)
# 4 side faces × 4 triggers = 16 triggers + 3 U-layer turns = 19 macro moves
# This reduces search depth by ~3x while having similar branching factor
F2L_MACRO_MODE = False  # Switch to enable macro-based F2L search
F2L_MACRO_FALLBACK = True # Switch to mecro mode when single mode can not find pair solve in depth
F2L_GREEDY_MODE = True  # If True, solve pairs sorted by heuristic (closest first)
F2L_RANDOM_MODE = False  # If True, solve pairs in random order (for speedup)

# Move indices: U=0, U2=1, U'=2, R=3, R2=4, R'=5, F=6, F2=7, F'=8, L=12, L2=13, L'=14, B=15, B2=16, B'=17
F2L_TRIGGERS = [
    # R triggers: R U R', R U' R', R' U R, R' U' R
    [3, 0, 5], [3, 2, 5], [5, 0, 3], [5, 2, 3],
    # F triggers: F U F', F U' F', F' U F, F' U' F
    [6, 0, 8], [6, 2, 8], [8, 0, 6], [8, 2, 6],
    # L triggers: L U L', L U' L', L' U L, L' U' L
    [12, 0, 14], [12, 2, 14], [14, 0, 12], [14, 2, 12],
    # B triggers: B U B', B U' B', B' U B, B' U' B
    [15, 0, 17], [15, 2, 17], [17, 0, 15], [17, 2, 15],
]
F2L_U_MOVES = [[0], [1], [2]]  # U, U2, U'
F2L_D_MOVES = [[9], [11], [10]]  # D, D', D2 (for keyhole F2L)
# F2L_D_MOVES = [] 
F2L_MACRO_MOVES = F2L_TRIGGERS + F2L_U_MOVES + F2L_D_MOVES  # 22 macro operations
N_F2L_MACROS = len(F2L_MACRO_MOVES)

F2L_MACRO_NAMES = [
    "RUR'", "RU'R'", "R'UR", "R'U'R",
    "FUF'", "FU'F'", "F'UF", "F'U'F",
    "LUL'", "LU'L'", "L'UL", "L'U'L",
    "BUB'", "BU'B'", "B'UB", "B'U'B",
    "U", "U2", "U'",
    "D", "D'", "D2",
]

OPPOSITE_FACE = {0: 3, 3: 0, 1: 4, 4: 1, 2: 5, 5: 2}


class CubieCube:
    __slots__ = ('cp', 'co', 'ep', 'eo')

    def __init__(self, cp=None, co=None, ep=None, eo=None):
        self.cp = list(cp) if cp else list(range(8))
        self.co = list(co) if co else [0] * 8
        self.ep = list(ep) if ep else list(range(12))
        self.eo = list(eo) if eo else [0] * 12

    @staticmethod
    def solved():
        return CubieCube()

    def copy(self):
        return CubieCube(self.cp, self.co, self.ep, self.eo)

    def apply_cw(self, face):
        t_cp = MOVE_CP[face]
        t_co = MOVE_CO[face]
        t_ep = MOVE_EP[face]
        t_eo = MOVE_EO[face]
        old_cp = list(self.cp)
        old_co = list(self.co)
        old_ep = list(self.ep)
        old_eo = list(self.eo)
        for i in range(8):
            src = t_cp[i]
            self.cp[i] = old_cp[src]
            self.co[i] = (old_co[src] + t_co[i]) % 3
        for i in range(12):
            src = t_ep[i]
            self.ep[i] = old_ep[src]
            self.eo[i] = (old_eo[src] + t_eo[i]) % 2

    def apply_move(self, face, dir):
        times = 1 if dir == 0 else 3  # dir=0: CW, dir=1: CCW (3 CW turns)
        for _ in range(times):
            self.apply_cw(face)

    def apply_move_idx(self, idx):
        face = idx // 3
        turn_type = idx % 3  # 0=CW, 1=half turn, 2=CCW
        if turn_type == 0:
            self.apply_cw(face)
        elif turn_type == 1:
            self.apply_cw(face)
            self.apply_cw(face)
        else:  # turn_type == 2: CCW
            self.apply_cw(face)
            self.apply_cw(face)
            self.apply_cw(face)

    def apply_move_idx_inv(self, idx):
        """Apply inverse of move idx: CW↔CCW, half-turn is self-inverse."""
        face = idx // 3
        turn_type = idx % 3
        inv_turn = {0: 2, 1: 1, 2: 0}[turn_type]
        if inv_turn == 0:
            self.apply_cw(face)
        elif inv_turn == 1:
            self.apply_cw(face)
            self.apply_cw(face)
        else:
            self.apply_cw(face)
            self.apply_cw(face)
            self.apply_cw(face)

    def apply_move_idx_copy(self, idx):
        s = self.copy()
        s.apply_move_idx(idx)
        return s

    def _apply_rotation(self, axis):
        if axis == 'x':
            temp = self.cp[:]
            self.cp = [temp[i] for i in [4, 1, 2, 0, 7, 5, 6, 3]]
            temp = self.co[:]
            self.co = [(temp[i] + (2 if i in [0, 7] else 1 if i in [3, 4] else 0)) % 3 for i in [4, 1, 2, 0, 7, 5, 6, 3]]
            temp = self.ep[:]
            self.ep = [temp[i] for i in [8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0]]
            temp = self.eo[:]
            self.eo = [temp[i] for i in [8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0]]
        elif axis == 'y':
            temp = self.cp[:]
            self.cp = [temp[i] for i in [3, 0, 1, 2, 4, 5, 6, 7]]
            temp = self.co[:]
            self.co = [temp[i] for i in [3, 0, 1, 2, 4, 5, 6, 7]]
            temp = self.ep[:]
            self.ep = [temp[i] for i in [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11]]
            temp = self.eo[:]
            self.eo = [temp[i] for i in [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11]]
        elif axis == 'z':
            temp = self.cp[:]
            self.cp = [temp[i] for i in [1, 5, 2, 3, 0, 4, 6, 7]]
            temp = self.co[:]
            self.co = [(temp[i] + (1 if i in [0, 5] else 2 if i in [1, 4] else 0)) % 3 for i in [1, 5, 2, 3, 0, 4, 6, 7]]
            temp = self.ep[:]
            self.ep = [temp[i] for i in [0, 8, 2, 3, 4, 1, 6, 7, 5, 9, 10, 11]]
            temp = self.eo[:]
            new_eo = []
            for i in [0, 8, 2, 3, 4, 1, 6, 7, 5, 9, 10, 11]:
                idx_in_old = i
                if idx_in_old in [1, 5, 8]:
                    new_eo.append((temp[idx_in_old] + 1) % 2)
                else:
                    new_eo.append(temp[idx_in_old])
            self.eo = new_eo

    def apply_moves_str(self, moves_str):
        s = self.copy()
        for m in moves_str.strip().split():
            if not m:
                continue
            face = COLOR_CHARS.index(m[0])
            if len(m) == 1:
                s.apply_move(face, 0)
            elif m[1] == '2':
                s.apply_move(face, 0)
                s.apply_move(face, 0)
            elif m[1] == "'":
                s.apply_move(face, 1)
        return s

    @staticmethod
    def from_facelet(s):
        f = list(s)
        cc = [f[c] for c in CENTER_FACELET]
        cube = CubieCube()
        for i in range(8):
            for j in range(8):
                ori = 0
                for ori in range(3):
                    if all(f[CORNER_FACELET[i][(k + ori) % 3]] == COLOR_CHARS[CORNER_COLOR[j][k]] for k in range(3)):
                        cube.cp[i] = j
                        cube.co[i] = ori
                        break
        for i in range(12):
            for j in range(12):
                for ori in range(2):
                    if f[EDGE_FACELET[i][(0 + ori) % 2]] == COLOR_CHARS[EDGE_COLOR[j][0]] and \
                       f[EDGE_FACELET[i][(1 + ori) % 2]] == COLOR_CHARS[EDGE_COLOR[j][1]]:
                        cube.ep[i] = j
                        cube.eo[i] = ori
                        break
        return cube

    def to_facelet(self):
        f = list(SOLVED_FACELET)
        for i in range(6):
            f[CENTER_FACELET[i]] = COLOR_CHARS[i]
        for i in range(8):
            j = self.cp[i]
            ori = self.co[i]
            for k in range(3):
                f[CORNER_FACELET[i][(k + ori) % 3]] = COLOR_CHARS[CORNER_COLOR[j][k]]
        for i in range(12):
            j = self.ep[i]
            ori = self.eo[i]
            for k in range(2):
                f[EDGE_FACELET[i][(k + ori) % 2]] = COLOR_CHARS[EDGE_COLOR[j][k]]
        return ''.join(f)

    def is_solved(self):
        return self.cp == list(range(8)) and self.co == [0]*8 and self.ep == list(range(12)) and self.eo == [0]*12

    def apply_u_rot(self, count):
        s = self.copy()
        for _ in range(count):
            s.apply_cw(0)
        return s


def invert_move_str(m):
    if len(m) == 1:
        return m + "'"
    elif m[1] == "'":
        return m[0]
    elif m[1] == '2':
        return m
    return m


def invert_alg(alg):
    moves = alg.strip().split()
    return ' '.join(invert_move_str(m) for m in reversed(moves))


def comb_idx(chosen, n, k):
    cnk = _cnk_table()
    idx = 0
    r = k
    for i in range(n):
        if chosen[i]:
            idx += cnk[n - 1 - i][r]
            r -= 1
    return idx


def perm_idx(perm, n):
    idx = 0
    used = [False] * n
    for i in range(n):
        cnt = 0
        for j in range(perm[i]):
            if not used[j]:
                cnt += 1
        idx = idx * (n - i) + cnt
        used[perm[i]] = True
    return idx


def perm_from_idx(idx, n):
    perm = [0] * n
    used = [False] * n
    for i in range(n):
        fact_val = 1
        for k in range(1, n - i):
            fact_val *= k
        cnt = idx // fact_val
        idx = idx % fact_val
        j = 0
        while j < n:
            if not used[j]:
                if cnt == 0:
                    perm[i] = j
                    used[j] = True
                    break
                cnt -= 1
            j += 1
    return perm


_cnk_cache = None


def _cnk_table():
    global _cnk_cache
    if _cnk_cache is None:
        _cnk_cache = [[0] * 13 for _ in range(13)]
        for i in range(13):
            _cnk_cache[i][0] = 1
            for j in range(1, i + 1):
                _cnk_cache[i][j] = _cnk_cache[i-1][j-1] + _cnk_cache[i-1][j]
    return _cnk_cache


def get_cross_perm_coord(state):
    positions = [0] * 12
    pieces = [0] * 12
    r = 4
    comb_val = 0
    cnk = _cnk_table()
    perm_pieces = []
    for i in range(12):
        if state.ep[i] in (4, 5, 6, 7):
            comb_val += cnk[11 - i][r]
            r -= 1
            perm_pieces.append(state.ep[i] - 4)
    perm_order = perm_idx(perm_pieces, 4)
    return comb_val * 24 + perm_order


def get_cross_flip_coord(state):
    r = 4
    comb_val = 0
    cnk = _cnk_table()
    flip_bits = 0
    bit_pos = 0
    for i in range(12):
        if state.ep[i] in (4, 5, 6, 7):
            comb_val += cnk[11 - i][r]
            r -= 1
            if state.eo[i]:
                flip_bits |= (1 << bit_pos)
            bit_pos += 1
    return comb_val * 16 + flip_bits


N_CROSS_PERM = 495 * 24 # 12! / 4! * 4!
N_CROSS_FLIP = 495 * 16 # 12! / 2^4

PERM_MOVE = None
FLIP_MOVE = None
PERM_PRUN = None
FLIP_PRUN = None

PAIR_MOVE = None
PAIR_PRUN = None
MACRO_PAIR_MOVE = None
MACRO_PAIR_PRUN = None
ALLL_RECOGNITION = None

OLL_ALGS = {
    1: "R U2 R2 F R F' U2 R' F R F'",
    2: "y' R U' R2 D' r U r' D R2 U R'",
    3: "r' R2 U R' U r U2 r' U M'",
    4: "y' R' F2 R2 U2 R' F' R U2 R2 F2 R",
    5: "r' U2 R U R' U r",
    6: "r U2 R' U' R U' r'",
    7: "r U R' U R U2 r'",
    8: "y2 r' U' R U' R' U2 r",
    9: "y R U R' U' R' F R2 U R' U' F'",
    10: "R U R' U R' F R F' R U2 R'",
    11: "r' R2 U R' U R U2 R' U M'",
    12: "y' M' R' U' R U' R' U2 R U' M",
    13: "F U R U2 R' U' R U R' F'",
    14: "R' F R U R' F' R F U' F'",
    15: "r' U' r R' U' R U r' U r",
    16: "r U r' R U R' U' r U' r'",
    17: "R U R' U R' F R F' U2 R' F R F'",
    18: "y R U2 R2 F R F' U2 M' U R U' r'",
    19: "y S' R U R' S U' R' F R F'",
    20: "r U R' U' M2 U R U' R' U' M'",
    21: "R U R' U R U' R' U R U2 R'",
    22: "R U2 R2 U' R2 U' R2 U2 R",
    23: "R2 D R' U2 R D' R' U2 R'",
    24: "r U R' U' r' F R F'",
    25: "R U2 R D R' U2 R D' R2",
    26: "y R U2 R' U' R U' R'",
    27: "R U R' U R U2 R'",
    28: "r U R' U' M U R U' R'",
    29: "r2 D' r U r' D r2 U' r' U' r",
    30: "y' r' D' r U' r' D r2 U' r' U r U r'",
    31: "R' U' F U R U' R' F' R",
    32: "S R U R' U' R' F R f'",
    33: "R U R' U' R' F R F'",
    34: "y f R f' U' r' U' R U M'",
    35: "R U2 R2 F R F' R U2 R'",
    36: "y R U R2 F' U' F U R2 U2 R'",
    37: "F R' F' R U R U' R'",
    38: "R U R' U R U' R' U' R' F R F'",
    39: "y' f' r U r' U' r' F r S",     
    40: "y R' F R U R' U' F' U R",      
    41: "y2 R U R' U R U2 R' F R U R' U' F'",
    42: "R' U' R U' R' U2 R F R U R' U' F'", 
    43: "y R' U' F' U F R",   
    44: "f R U R' U' f'",     
    45: "F R U R' U' F'",     
    46: "R' U' R' F R F' U R",
    47: "y' F R' F' R U2 R U' R' U R U2 R'", 
    48: "F R U R' U' R U R' U' F'",     
    49: "y2 r U' r2 U r2 U r2 U' r",    
    50: "r' U r2 U' r2 U' r2 U r'",     
    51: "y2 F U R U' R' U R U' R' F'",  
    52: "y2 R' F' U' F U' R U R' U R",  
    53: "r' U' R U' R' U R U' R' U2 r", 
    54: "r U R' U R U' R' U R U2 r'",   
    55: "y R' F U R U' R2 F' R2 U R' U' R",  
    56: "r U r' U R U' R' U R U' R' r U' r'",
    57: "R U R' U' M' U R U' r'",       
}

PLL_ALGS = {
    'Aa': "x R' U R' D2 R U' R' D2 R2 x'",
    'Ab': "x R2 D2 R U R' D2 R U' R x'",
    'E': "x' R U' R' D R U R' D' R U R' D R U' R' D' x",
    'F': "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
    'Ga': "R2 U R' U R' U' R U' R2 D U' R' U R D'",
    'Gb': "R' U' R U D' R2 U R' U R U' R U' R2 D",
    'Gc': "R2 U' R U' R U R' U R2 D' U R U' R' D",
    'Gd': "R U R' U' D R2 U' R U' R' U R' U R2 D'",
    'H': "M2 U M2 U2 M2 U M2",
    'Ja': "R' U L' U2 R U' R' U2 R L x'",
    'Jb': "R U R' F' R U R' U' R' F R2 U' R'",
    'Na': "R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R'",
    'Nb': "R' U R U' R' F' U' F R U R' F R' F' R U' R",
    'Ra': "R U R' F' R U2 R' U2 R' F R U R U2 R'",
    'Rb': "R' U2 R U2 R' F R U R' U' R' F' R2",
    'T': "R U R' U' R' F R2 U' R' U' R U R' F'",
    'Ua': "R U' R U R U R U' R' U' R2",
    'Ub': "R2 U R U R' U' R' U' R' U R'",
    'V': "R' U R' U' R D' R' D R' U D' R2 U' R2 D R2",
    'Y': "F R U' R' U' R U R' F' R U R' U' R' F R F'",
    'Z': "M' U M2 U M2 U M' U2 M2",
}

# ALLL (1-look Last Layer) formula set: OLL + PLL algorithms combined
# Each formula is a standalone last-layer solver
ALLL_ALGS = {}
for k, v in OLL_ALGS.items():
    ALLL_ALGS[f"OLL_{k}"] = v
for k, v in PLL_ALGS.items():
    ALLL_ALGS[f"PLL_{k}"] = v
ALLL_ALGS.update(EX_ALLLS)

def expand_rotations(tokens):
    return tokens

def apply_alg_str(state, alg_str):
    basic_alg, _ = convert_alg_to_basic(alg_str)
    tokens = basic_alg.strip().split()
    s = state.copy()
    for t in tokens:
        if not t:
            continue
        base = t[0]
        mod = t[1] if len(t) > 1 else ''
        face = COLOR_CHARS.index(base)
        count = {'': 1, '2': 2, "'": 3}.get(mod, 1)
        for _ in range(count):
            s.apply_cw(face)
    return s


EDGE_MOVE_PERM = [
    [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],
    [8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0],
    [0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11],
    [0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11],
    [0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11],
    [0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7],
]

EDGE_MOVE_EO = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1],
]


def _apply_edge_move_full(ep, eo, face):
    new_ep = [ep[EDGE_MOVE_PERM[face][i]] for i in range(12)]
    new_eo = [(eo[EDGE_MOVE_PERM[face][i]] + EDGE_MOVE_EO[face][i]) % 2 for i in range(12)]
    return new_ep, new_eo


def build_cross_move_tables():
    perm_move = [[0] * N_CROSS_PERM for _ in range(18)]
    flip_move = [[0] * N_CROSS_FLIP for _ in range(18)]

    solved_ep = list(range(12))
    solved_eo = [0] * 12

    all_states = {}
    for face in range(6):
        for turn in range(1, 4):
            ep, eo = list(solved_ep), list(solved_eo)
            for _ in range(turn):
                ep, eo = _apply_edge_move_full(ep, eo, face)

    for move_idx in range(18):
        face = move_idx // 3
        turns = (move_idx % 3) + 1

        for ps in range(N_CROSS_PERM):
            ep, eo = _decode_perm_to_edge(ps)
            for _ in range(turns):
                ep, eo = _apply_edge_move_full(ep, eo, face)
            perm_move[move_idx][ps] = _encode_perm_from_edge(ep, eo)

        for fs in range(N_CROSS_FLIP):
            ep, eo = _decode_flip_to_edge(fs)
            for _ in range(turns):
                ep, eo = _apply_edge_move_full(ep, eo, face)
            flip_move[move_idx][fs] = _encode_flip_from_edge(ep, eo)

    return perm_move, flip_move


def _decode_perm_to_edge(ps):
    comb = ps // 24
    perm_order = perm_from_idx(ps % 24, 4)
    cnk = _cnk_table()
    # Use non-cross values for initial positions to avoid duplicates with cross pieces (4-7)
    non_cross = [0, 1, 2, 3, 8, 9, 10, 11]
    ep = list(range(12))
    eo = [0] * 12
    # First, place non-cross pieces at positions that won't be cross positions
    cross_pos = []
    comb_copy = comb
    r_copy = 4
    for i in range(12):
        if comb_copy >= cnk[11 - i][r_copy]:
            comb_copy -= cnk[11 - i][r_copy]
            cross_pos.append(i)
            r_copy -= 1
    non_cross_idx = 0
    for i in range(12):
        if i not in cross_pos:
            ep[i] = non_cross[non_cross_idx]
            non_cross_idx += 1
    # Now place cross pieces at their positions
    for idx, pos in enumerate(cross_pos):
        ep[pos] = perm_order[idx] + 4
        eo[pos] = 0
    return ep, eo


def _decode_flip_to_edge(fs):
    comb = fs // 16
    flip_bits = fs % 16
    cnk = _cnk_table()
    # Use non-cross values for initial positions to avoid duplicates with cross pieces (4-7)
    non_cross = [0, 1, 2, 3, 8, 9, 10, 11]
    ep = list(range(12))
    eo = [0] * 12
    # Determine which positions hold cross pieces
    cross_pos = []
    comb_copy = comb
    r_copy = 4
    for i in range(12):
        if comb_copy >= cnk[11 - i][r_copy]:
            comb_copy -= cnk[11 - i][r_copy]
            cross_pos.append(i)
            r_copy -= 1
    non_cross_idx = 0
    for i in range(12):
        if i not in cross_pos:
            ep[i] = non_cross[non_cross_idx]
            eo[i] = 0
            non_cross_idx += 1
    # Now place cross pieces with flip info
    piece = 4
    bit_pos = 0
    for pos in cross_pos:
        ep[pos] = piece
        eo[pos] = (flip_bits >> bit_pos) & 1
        piece += 1
        bit_pos += 1
    return ep, eo


def _encode_perm_from_edge(ep, eo):
    cnk = _cnk_table()
    r = 4
    comb_val = 0
    perm_pieces = []
    for i in range(12):
        if ep[i] >= 4 and ep[i] <= 7:
            comb_val += cnk[11 - i][r]
            perm_pieces.append(ep[i] - 4)
            r -= 1
    perm_order = perm_idx(perm_pieces, 4)
    return comb_val * 24 + perm_order


def _encode_flip_from_edge(ep, eo):
    cnk = _cnk_table()
    r = 4
    comb_val = 0
    flip_bits = 0
    bit_pos = 0
    for i in range(12):
        if ep[i] >= 4 and ep[i] <= 7:
            comb_val += cnk[11 - i][r]
            if eo[i]:
                flip_bits |= (1 << bit_pos)
            bit_pos += 1
            r -= 1
    return comb_val * 16 + flip_bits


def build_cross_prun(perm_move, flip_move):
    # The solved cross state has edges 4,5,6,7 at D-layer positions 4,5,6,7
    # We need to find the correct coords for this state
    solved = CubieCube.solved()
    solved_perm = get_cross_perm_coord(solved)
    solved_flip = get_cross_flip_coord(solved)

    perm_prun = bytearray([0xff] * N_CROSS_PERM)
    perm_prun[solved_perm] = 0
    queue = deque([solved_perm])
    while queue:
        idx = queue.popleft()
        d = perm_prun[idx]
        for m in range(18):
            nxt = perm_move[m][idx]
            if perm_prun[nxt] == 0xff:
                perm_prun[nxt] = d + 1
                queue.append(nxt)

    flip_prun = bytearray([0xff] * N_CROSS_FLIP)
    flip_prun[solved_flip] = 0
    queue = deque([solved_flip])
    while queue:
        idx = queue.popleft()
        d = flip_prun[idx]
        for m in range(18):
            nxt = flip_move[m][idx]
            if flip_prun[nxt] == 0xff:
                flip_prun[nxt] = d + 1
                queue.append(nxt)

    return perm_prun, flip_prun


def get_pair_coord(state, pair_idx):
    corner_piece, edge_piece = F2L_PAIRS[pair_idx]
    cp_slot = state.cp.index(corner_piece)
    co_val = state.co[cp_slot]
    ep_slot = state.ep.index(edge_piece)
    eo_val = state.eo[ep_slot]
    return (cp_slot * 3 + co_val) * 24 + (ep_slot * 2 + eo_val)


def pair_is_solved(state, pair_idx):
    corner_piece, edge_piece = F2L_PAIRS[pair_idx]
    cp_slot = state.cp.index(corner_piece)
    ep_slot = state.ep.index(edge_piece)
    return cp_slot == corner_piece and state.co[cp_slot] == 0 and \
           ep_slot == edge_piece and state.eo[ep_slot] == 0


def pair_solved_coord(pair_idx):
    corner_piece, edge_piece = F2L_PAIRS[pair_idx]
    return (corner_piece * 3 + 0) * 24 + (edge_piece * 2 + 0)


def build_pair_move_tables():
    pair_move = [[[0] * 576 for _ in range(15)] for _ in range(4)]
    for pair_idx in range(4):
        for mi, move_idx in enumerate(F2L_MOVE_INDICES):
            face = move_idx // 3
            turns = (move_idx % 3) + 1
            for pc in range(576):
                s = _pair_to_cube(pc, pair_idx)
                for _ in range(turns):
                    s.apply_cw(face)
                pair_move[pair_idx][mi][pc] = get_pair_coord(s, pair_idx)
    return pair_move


def _pair_to_cube(pc, pair_idx):
    corner_piece, edge_piece = F2L_PAIRS[pair_idx]
    cp_slot = pc // (24 * 3)
    co_val = (pc // 24) % 3
    ep_slot = (pc % 24) // 2
    eo_val = pc % 2
    cube = CubieCube()
    # Clear the slot that will hold the pair piece, and place pair piece at its slot
    # We need to ensure corner_piece only appears once in cp, edge_piece only once in ep
    # Remove the pair piece from wherever it was by default
    for i in range(8):
        if cube.cp[i] == corner_piece and i != cp_slot:
            # Swap: put whatever was at cp_slot into this position
            cube.cp[i] = cube.cp[cp_slot]
            break
    cube.cp[cp_slot] = corner_piece
    cube.co[cp_slot] = co_val

    for i in range(12):
        if cube.ep[i] == edge_piece and i != ep_slot:
            cube.ep[i] = cube.ep[ep_slot]
            break
    cube.ep[ep_slot] = edge_piece
    cube.eo[ep_slot] = eo_val
    return cube


def build_pair_prun(pair_move):
    pair_prun = [bytearray([0xff] * 576) for _ in range(4)]
    for pair_idx in range(4):
        solved = pair_solved_coord(pair_idx)
        pair_prun[pair_idx][solved] = 0
        queue = deque([solved])
        while queue:
            idx = queue.popleft()
            d = pair_prun[pair_idx][idx]
            if d > 11:
                continue
            for mi in range(15):
                nxt = pair_move[pair_idx][mi][idx]
                if pair_prun[pair_idx][nxt] == 0xff:
                    pair_prun[pair_idx][nxt] = d + 1
                    queue.append(nxt)
    return pair_prun


def build_macro_pair_move_tables():
    """Build move table for macro operations (triggers + U-layer turns).
    Each macro maps pair_coord -> new_pair_coord.
    Triggers are 3-move sequences applied sequentially."""
    macro_move = [[[0] * 576 for _ in range(N_F2L_MACROS)] for _ in range(4)]
    for pair_idx in range(4):
        for macro_idx, macro_seq in enumerate(F2L_MACRO_MOVES):
            for pc in range(576):
                s = _pair_to_cube(pc, pair_idx)
                for m in macro_seq:
                    s.apply_move_idx(m)
                macro_move[pair_idx][macro_idx][pc] = get_pair_coord(s, pair_idx)
    return macro_move


def build_macro_pair_prun(macro_move):
    """Build pruning table for macro operations.
    Each entry gives the minimum number of macro operations to solve the pair."""
    macro_prun = [bytearray([0xff] * 576) for _ in range(4)]
    for pair_idx in range(4):
        solved = pair_solved_coord(pair_idx)
        macro_prun[pair_idx][solved] = 0
        queue = deque([solved])
        while queue:
            idx = queue.popleft()
            d = macro_prun[pair_idx][idx]
            if d >= 15:
                continue
            for macro_idx in range(N_F2L_MACROS):
                nxt = macro_move[pair_idx][macro_idx][idx]
                if macro_prun[pair_idx][nxt] == 0xff:
                    macro_prun[pair_idx][nxt] = d + 1
                    queue.append(nxt)
    return macro_prun


def _f2l_macro_ida(state, pair_idx, remaining, last_macro_face, path, macro_prun, protected_pairs):
    """IDA* search using macro operations (triggers + U/D-layer turns).
    remaining: number of macro operations left.
    last_macro_face: the primary face of the last macro (for pruning)."""
    global _f2l_nodes
    _f2l_nodes += 1
    h = macro_prun[pair_idx][get_pair_coord(state, pair_idx)]
    if h > remaining:
        return False
    if remaining == 0:
        if not pair_is_solved(state, pair_idx):
            return False
        for pp in protected_pairs:
            if not pair_is_solved(state, pp):
                return False
        if not _check_cross_intact(state):
            return False
        return True
    for macro_idx, macro_seq in enumerate(F2L_MACRO_MOVES):
        # Determine the primary face for pruning
        if len(macro_seq) == 3:  # trigger: first move's face
            macro_face = macro_seq[0] // 3
        elif macro_seq[0] // 3 == 0:  # U-layer single move
            macro_face = 0
        else:  # D-layer single move (D, D', D2)
            macro_face = 3  # D face index
        # Pruning: skip same face, or opposite after lower-index face
        if macro_face == last_macro_face:
            continue
        if macro_face == OPPOSITE_FACE.get(last_macro_face, -1) and macro_face < last_macro_face:
            continue
        # Apply the macro sequence
        ns = state.copy()
        for m in macro_seq:
            ns.apply_move_idx(m)
        path.append(macro_idx)
        if _f2l_macro_ida(ns, pair_idx, remaining - 1, macro_face, path, macro_prun, protected_pairs):
            return True
        path.pop()
    return False


def solve_f2l_pair_macro(state, pair_idx, macro_prun, max_depth=8, protected_pairs=None):
    """Solve a single F2L pair using macro operations.
    max_depth is in macro operations (each trigger = 3 moves, U = 1 move)."""
    if protected_pairs is None:
        protected_pairs = set()
    if pair_is_solved(state, pair_idx):
        if _check_cross_intact(state) and all(pair_is_solved(state, pp) for pp in protected_pairs):
            return []
    global _f2l_nodes
    for depth in range(1, max_depth + 1):
        _f2l_nodes = 0
        _dbg(f"DEBUG: f2l pair {pair_idx} macro searching depth={depth}")
        path = []
        if _f2l_macro_ida(state, pair_idx, depth, -1, path, macro_prun, protected_pairs):
            _dbg(f"DEBUG: f2l pair {pair_idx} macro found at depth={depth}, nodes={_f2l_nodes}")
            # Convert macro indices to actual move sequences
            moves = []
            for macro_idx in path:
                moves.extend(F2L_MACRO_MOVES[macro_idx])
            return moves
        _dbg(f"DEBUG: f2l pair {pair_idx} macro depth={depth} exhausted, nodes={_f2l_nodes}")
    return None


def get_next_moves(all_moves, last_face):
    allowed = []
    for m in all_moves:
        face = m // 3
        if face == last_face:
            continue
        opp = OPPOSITE_FACE.get(last_face, -1)
        if face == opp and last_face > opp:
            continue
        allowed.append(m)
    return allowed


def solve_cross(state, perm_prun, flip_prun, perm_move, flip_move, max_depth=8):
    perm0 = get_cross_perm_coord(state)
    flip0 = get_cross_flip_coord(state)
    if perm_prun[perm0] == 0 and flip_prun[flip0] == 0:
        return []
    for depth in range(1, max_depth + 1):
        _dbg(f"DEBUG: cross searching depth={depth}")
        path = []
        if _cross_ida(perm0, flip0, depth, -1, path, perm_prun, flip_prun, perm_move, flip_move):
            return path
    return None


def _cross_ida(perm, flip, remaining, last_face, path, perm_prun, flip_prun, perm_move, flip_move):
    h = max(perm_prun[perm], flip_prun[flip])
    if h > remaining:
        return False
    if remaining == 0:
        return perm_prun[perm] == 0 and flip_prun[flip] == 0
    next_moves = get_next_moves(range(18), last_face)
    for m in next_moves:
        np = perm_move[m][perm]
        nf = flip_move[m][flip]
        path.append(m)
        if _cross_ida(np, nf, remaining - 1, m // 3, path, perm_prun, flip_prun, perm_move, flip_move):
            return True
        path.pop()
    return False


def _check_cross_intact(state):
    for e in [4, 5, 6, 7]:
        if state.ep[e] != e or state.eo[e] != 0:
            return False
    return True


def solve_f2l_pair(state, pair_idx, pair_prun, pair_move, max_depth=10, protected_pairs=None):
    if protected_pairs is None:
        protected_pairs = set()
    if pair_is_solved(state, pair_idx):
        if _check_cross_intact(state) and all(pair_is_solved(state, pp) for pp in protected_pairs):
            return []
    global _f2l_nodes
    for depth in range(1, max_depth + 1):
        _f2l_nodes = 0
        _dbg(f"DEBUG: f2l pair {pair_idx} searching depth={depth}")
        path = []
        if _f2l_ida(state, pair_idx, depth, -1, path, pair_prun, pair_move, protected_pairs):
            _dbg(f"DEBUG: f2l pair {pair_idx} found at depth={depth}, nodes={_f2l_nodes}")
            return path
        _dbg(f"DEBUG: f2l pair {pair_idx} depth={depth} exhausted, nodes={_f2l_nodes}")
    return None


_f2l_nodes = 0

def _f2l_ida(state: 'CubieCube', pair_idx, remaining, last_face, path, pair_prun, pair_move, protected_pairs):
    global _f2l_nodes
    _f2l_nodes += 1
    h = pair_prun[pair_idx][get_pair_coord(state, pair_idx)]
    if h > remaining:
        return False
    if remaining == 0:
        if not pair_is_solved(state, pair_idx):
            return False
        for pp in protected_pairs:
            if not pair_is_solved(state, pp):
                return False
        if not _check_cross_intact(state):
            return False
        return True
    next_moves = get_next_moves(F2L_MOVE_INDICES, last_face)
    for mi, m in enumerate(next_moves):
        ns = state.apply_move_idx_copy(m)
        path.append(m)
        if _f2l_ida(ns, pair_idx, remaining - 1, m // 3, path, pair_prun, pair_move, protected_pairs):
            return True
        path.pop()
    return False


def solve_f2l(state: 'CubieCube', pair_prun, pair_move):
    if F2L_MACRO_MODE:
        return _solve_f2l_macro(state)
    return _solve_f2l_single(state, pair_prun, pair_move)


def _solve_f2l_single(state: 'CubieCube', pair_prun, pair_move):
    """Original F2L solver using single-move IDA* with macro fallback on timeout."""
    import time
    full_moves = []
    solved_pairs = set()
    for i in range(4):
        if pair_is_solved(state, i):
            solved_pairs.add(i)
            _dbg(f"DEBUG: pair {i} already solved")
    
    for step in range(4):
        remaining = [i for i in range(4) if i not in solved_pairs]
        if not remaining:
            break
        
        if F2L_GREEDY_MODE:
            heuristic = [(pair_prun[pidx][get_pair_coord(state, pidx)], pidx) for pidx in remaining]
            heuristic.sort()
            _dbg(f"DEBUG: remaining pairs heuristics: {[(h, p) for h, p in heuristic]}")
        elif F2L_RANDOM_MODE:
            random.shuffle(remaining)
            heuristic = [(0, pidx) for pidx in remaining]
        else:
            heuristic = [(0, pidx) for pidx in remaining]
        
        found = False
        for _, pair_idx in heuristic:
            _dbg(f"DEBUG: solving F2L pair {pair_idx}")
            start_time = time.time()
            path = solve_f2l_pair(state, pair_idx, pair_prun, pair_move, max_depth=6, protected_pairs=solved_pairs)
            elapsed = time.time() - start_time
            
            if path is not None:
                full_moves.extend(path)
                for m in path:
                    state.apply_move_idx(m)
                _dbg(f"DEBUG: pair {pair_idx} solved with {len(path)} moves ({elapsed:.3f}s)")
                if not pair_is_solved(state, pair_idx):
                    return None
                solved_pairs.add(pair_idx)
                found = True
                break
            elif path is None:
                if F2L_MACRO_FALLBACK:
                    _dbg(f"DEBUG: pair {pair_idx} single search timed out ({elapsed:.3f}s), falling back to macro")
                    macro_path = solve_f2l_pair_macro(state, pair_idx, MACRO_PAIR_PRUN, max_depth=8, protected_pairs=solved_pairs)
                    if macro_path is not None:
                        full_moves.extend(macro_path)
                        for m in macro_path:
                            state.apply_move_idx(m)
                        _dbg(f"DEBUG: pair {pair_idx} solved with macro ({len(macro_path)} moves)")
                        if not pair_is_solved(state, pair_idx):
                            return None
                        solved_pairs.add(pair_idx)
                        found = True
                        break
                else:
                    path = solve_f2l_pair(state, pair_idx, pair_prun, pair_move, max_depth=11, protected_pairs=solved_pairs)
                    if path is not None:
                        full_moves.extend(path)
                        for m in path:
                            state.apply_move_idx(m)
                        _dbg(f"DEBUG: pair {pair_idx} solved with extended search ({len(path)} moves)")
                        if not pair_is_solved(state, pair_idx):
                            return None
                        solved_pairs.add(pair_idx)
                        found = True
                        break
        
        if not found:
            _dbg(f"DEBUG: F2L failed at step {step}")
            return None

    # Verify F2L is complete
    top_corners = set(state.cp[i] for i in range(4))
    top_edges = set(state.ep[i] for i in range(4))
    if top_corners != {0, 1, 2, 3} or top_edges != {0, 1, 2, 3}:
        return None

    return full_moves, state


def _solve_f2l_macro(state):
    """F2L solver using macro operations (triggers + U/D-layer turns)."""
    macro_prun = MACRO_PAIR_PRUN
    if macro_prun is None:
        _dbg("DEBUG: macro pruning tables not available, falling back to single-move mode")
        return _solve_f2l_single(state, PAIR_PRUN, PAIR_MOVE)
    
    full_moves = []
    solved_pairs = set()
    for i in range(4):
        if pair_is_solved(state, i):
            solved_pairs.add(i)
            _dbg(f"DEBUG: pair {i} already solved")
    
    for pair_idx in range(4):
        if pair_idx in solved_pairs:
            continue
        _dbg(f"DEBUG: solving F2L pair {pair_idx} (macro mode)")
        moves = solve_f2l_pair_macro(state, pair_idx, macro_prun, max_depth=8, protected_pairs=solved_pairs)
        if moves is None:
            _dbg(f"DEBUG: F2L pair {pair_idx} FAILED (macro mode)")
            return None
        full_moves.extend(moves)
        for m in moves:
            state.apply_move_idx(m)
        _dbg(f"DEBUG: pair {pair_idx} solved with {len(moves)} moves (macro mode)")
        if not pair_is_solved(state, pair_idx):
            return None
        solved_pairs.add(pair_idx)

    # Verify F2L is complete
    top_corners = set(state.cp[i] for i in range(4))
    top_edges = set(state.ep[i] for i in range(4))
    if top_corners != {0, 1, 2, 3} or top_edges != {0, 1, 2, 3}:
        return None

    return full_moves, state


OLL_RECOGNITION = None
PLL_RECOGNITION = None


def build_oll_recognition():
    table = {}
    solved = CubieCube.solved()

    # Build table by applying each OLL algorithm's inverse (without AUF variations)
    for name, alg in OLL_ALGS.items():
        basic_alg, _ = convert_alg_to_basic(alg)
        inv = invert_alg(basic_alg)
        s = apply_alg_str(solved.copy(), inv)
        co_tuple = tuple(s.co[i] for i in range(4))
        eo_tuple = tuple(s.eo[i] for i in range(4))
        key = (co_tuple, eo_tuple)

        # Don't overwrite - first one wins
        if key not in table:
            table[key] = (name, basic_alg)

    # Add solved state
    solved_key = ((0,0,0,0),(0,0,0,0))
    table[solved_key] = 'skip'

    return table


def build_pll_recognition():
    table = {}
    solved = CubieCube.solved()
    AUF_STRS = {0: '', 1: 'U', 2: 'U2', 3: "U'"}

    for name, alg in PLL_ALGS.items():
        basic_alg, _ = convert_alg_to_basic(alg)
        for pre in range(4):
            for post in range(4):
                pre_str = AUF_STRS[pre]
                post_str = AUF_STRS[post]
                full_alg = ' '.join(p for p in [pre_str, basic_alg, post_str] if p)
                inv_full = invert_alg(full_alg)
                s = apply_alg_str(solved.copy(), inv_full)
                cp_key = tuple(s.cp[i] for i in range(4))
                ep_key = tuple(s.ep[i] for i in range(4))
                key = (cp_key, ep_key)
                if key not in table or len(full_alg) < len(table[key][1]):
                    table[key] = (name, full_alg)

    key_skip = (tuple(range(4)), tuple(range(4)))
    table[key_skip] = ('skip', '')
    return table


def _check_d_intact(state: 'CubieCube'):
    for e in range(4, 8):
        if state.ep[e] != e or state.eo[e] != 0:
            return False
    for c in range(4, 8):
        if state.cp[c] != c or state.co[c] != 0:
            return False
    return True

def build_alll_recognition():
    table = {}
    solved = CubieCube.solved()
    AUF_STRS = {0: '', 1: 'U', 2: 'U2', 3: "U'"}
    _dbg(f"DEBUG: Building ALLL recognition table... all algs={len(ALLL_ALGS)}")
    for name, alg in ALLL_ALGS.items():
        basic_alg, _ = convert_alg_to_basic(alg)
        for pre in range(4):
            for post in range(4):
                pre_str = AUF_STRS[pre]
                post_str = AUF_STRS[post]
                full_alg = ' '.join(p for p in [pre_str, basic_alg, post_str] if p)
                inv_full = invert_alg(full_alg)
                s = apply_alg_str(solved.copy(), inv_full)
                if not _check_d_intact(s):
                    continue
                cp_key = tuple(s.cp[i] for i in range(4))
                co_key = tuple(s.co[i] for i in range(4))
                ep_key = tuple(s.ep[i] for i in range(4))
                eo_key = tuple(s.eo[i] for i in range(4))
                all_key = (cp_key, co_key, ep_key, eo_key)
                if all_key not in table or len(full_alg) < len(table[all_key][1]):
                    table[all_key] = (name, full_alg)
    _dbg(f"DEBUG: ALLL recognition table built with {len(table)} entries")
    solved_key = (tuple(range(4)), (0, 0, 0, 0), tuple(range(4)), (0, 0, 0, 0))
    table[solved_key] = ('skip', '')
    return table


def recognize_oll(state: 'CubieCube', oll_rec):
    # Try all 4 AUF rotations
    for auf in range(4):
        test = state.apply_u_rot(auf)
        co_tuple = tuple(test.co[i] for i in range(4))
        eo_tuple = tuple(test.eo[i] for i in range(4))
        key = (co_tuple, eo_tuple)

        if key in oll_rec:
            result = oll_rec[key]
            if result == 'skip':
                return 'skip', '', auf, None
            return result[0], result[1], auf, key

    return None, None, 0, None


def recognize_pll(state: 'CubieCube', pll_rec):
    for auf in range(4):
        test = state.apply_u_rot(auf)
        cp_key = tuple(test.cp[i] for i in range(4))
        ep_key = tuple(test.ep[i] for i in range(4))
        key = (cp_key, ep_key)
        if key in pll_rec:
            name, alg = pll_rec[key]
            auf_str = {0: '', 1: 'U', 2: 'U2', 3: "U'"}[auf]
            if name == 'skip':
                return 'skip', auf_str
            return name, (auf_str + ' ' + alg).strip()
    return None, None


def solve_oll(state, oll_rec):
    name, alg, auf, key = recognize_oll(state, oll_rec)
    if name is not None:
        _dbg(f"DEBUG: recognized OLL case={name} auf={auf} key={key}")
        auf_str = {0: '', 1: 'U', 2: 'U2', 3: "U'"}.get(auf, '')
        full = (auf_str + ' ' + alg).strip() if name != 'skip' else ''
        if full:
            state = apply_alg_str(state, full)
        return full, state

    _dbg(f"DEBUG: OLL not recognized, state co={tuple(state.co[:4])} eo={tuple(state.eo[:4])} cp={tuple(state.cp[:4])} ep={tuple(state.ep[:4])}")
    return None, state


def solve_pll(state: 'CubieCube', pll_rec):
    name, alg = recognize_pll(state, pll_rec)
    _dbg(f"DEBUG: PLL recognized={name} alg={alg}")
    if name is None:
        _dbg(f"DEBUG: PLL not recognized, cp={tuple(state.cp[:4])} ep={tuple(state.ep[:4])}")
        return None, state
    if alg:
        state = apply_alg_str(state, alg)
    return alg, state


def recognize_alll(state: 'CubieCube', alll_rec):
    for auf in range(4):
        test = state.apply_u_rot(auf)
        cp_key = tuple(test.cp[i] for i in range(4))
        co_key = tuple(test.co[i] for i in range(4))
        ep_key = tuple(test.ep[i] for i in range(4))
        eo_key = tuple(test.eo[i] for i in range(4))
        key = (cp_key, co_key, ep_key, eo_key)
        if key in alll_rec:
            name, alg = alll_rec[key]
            auf_str = {0: '', 1: 'U', 2: 'U2', 3: "U'"}[auf]
            if name == 'skip':
                return 'skip', auf_str
            return name, (auf_str + ' ' + alg).strip()
    return None, None


def solve_alll(state: 'CubieCube', alll_rec):
    name, alg = recognize_alll(state, alll_rec)
    _dbg(f"DEBUG: ALLL recognized={name} alg={alg}")
    if name is None:
        return None, state
    if alg:
        state = apply_alg_str(state, alg)
    return alg, state


CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cfop_cache.pkl')

_tables_initialized = False


def init_tables():
    global PERM_MOVE, FLIP_MOVE, PERM_PRUN, FLIP_PRUN, PAIR_MOVE, PAIR_PRUN, MACRO_PAIR_MOVE, MACRO_PAIR_PRUN, OLL_RECOGNITION, PLL_RECOGNITION, ALLL_RECOGNITION, _tables_initialized
    if _tables_initialized:
        return
    cache_valid = False
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                tables = pickle.load(f)
                cache_valid = True
        except Exception:
            pass
    if cache_valid:
        PERM_MOVE = tables['perm_move']
        FLIP_MOVE = tables['flip_move']
        PERM_PRUN = tables['perm_prun']
        FLIP_PRUN = tables['flip_prun']
        PAIR_MOVE = tables['pair_move']
        PAIR_PRUN = tables['pair_prun']
        MACRO_PAIR_MOVE = tables.get('macro_pair_move', None)
        MACRO_PAIR_PRUN = tables.get('macro_pair_prun', None)
        OLL_RECOGNITION = tables['oll_rec']
        PLL_RECOGNITION = tables['pll_rec']
        ALLL_RECOGNITION = tables['alll_rec']
    else:
        print("Building CFOP tables (first run)...", flush=True)
        perm_move, flip_move = build_cross_move_tables()
        PERM_MOVE = perm_move
        FLIP_MOVE = flip_move
        perm_prun, flip_prun = build_cross_prun(perm_move, flip_move)
        PERM_PRUN = perm_prun
        FLIP_PRUN = flip_prun
        pair_move = build_pair_move_tables()
        PAIR_MOVE = pair_move
        pair_prun = build_pair_prun(pair_move)
        PAIR_PRUN = pair_prun
        macro_pair_move = build_macro_pair_move_tables()
        macro_pair_prun = build_macro_pair_prun(macro_pair_move)
        MACRO_PAIR_MOVE = macro_pair_move
        MACRO_PAIR_PRUN = macro_pair_prun
        oll_rec = build_oll_recognition()
        pll_rec = build_pll_recognition()
        OLL_RECOGNITION = oll_rec
        PLL_RECOGNITION = pll_rec
        alll_rec = build_alll_recognition()
        ALLL_RECOGNITION = alll_rec
        tables = {
            'perm_move': perm_move,
            'flip_move': flip_move,
            'perm_prun': perm_prun,
            'flip_prun': flip_prun,
            'pair_move': pair_move,
            'pair_prun': pair_prun,
            'macro_pair_move': macro_pair_move,
            'macro_pair_prun': macro_pair_prun,
            'oll_rec': oll_rec,
            'pll_rec': pll_rec,
            'alll_rec': alll_rec,
        }
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(tables, f)
    _tables_initialized = True


def moves_to_str(move_indices):
    return ' '.join(MOVE_NAMES[m] for m in move_indices) if move_indices else ''


def merge_consecutive_moves(move_indices):
    """Merge consecutive moves on the same face.
    E.g. [R', R] → [R2], [R, R2] → [R'], [U, U] → [U2], [U2, U2] → [].
    Move index encoding: face=idx//3, turn_type=idx%3 (0=CW, 1=half, 2=CCW).
    CW adds 1, half adds 2, CCW adds 3. Total mod 4: 0=eliminate, 1=CW, 2=half, 3=CCW."""
    if not move_indices:
        return []
    result = []
    i = 0
    while i < len(move_indices):
        face = move_indices[i] // 3
        total_turns = (move_indices[i] % 3) + 1  # CW=1, half=2, CCW=3
        j = i + 1
        while j < len(move_indices) and move_indices[j] // 3 == face:
            total_turns += (move_indices[j] % 3) + 1
            j += 1
        total_turns %= 4
        if total_turns == 1:
            result.append(face * 3 + 0)  # CW
        elif total_turns == 2:
            result.append(face * 3 + 1)  # half turn
        elif total_turns == 3:
            result.append(face * 3 + 2)  # CCW
        # total_turns == 0: eliminated (e.g. R R' or U2 U2)
        i = j
    return result


_CW  = [6, 3, 0, 7, 4, 1, 8, 5, 2]
_CCW = [2, 5, 8, 1, 4, 7, 0, 3, 6]
_180 = [8, 7, 6, 5, 4, 3, 2, 1, 0]
_ID  = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# (dst_face, src_face, inner_perm) for URFDLB order (U=0,R=1,F=2,D=3,L=4,B=5)
_ROTATION_RULES = {
    'z':  [(0,4,_CW),(1,0,_CW),(2,2,_CW),(3,1,_CW),(4,3,_CW),(5,5,_CCW)],
    "z'": [(0,1,_CCW),(1,3,_CCW),(2,2,_CCW),(3,4,_CCW),(4,0,_CCW),(5,5,_CW)],
    'z2': [(0,3,_180),(1,4,_180),(2,2,_180),(3,0,_180),(4,1,_180),(5,5,_180)],
    'x':  [(0,2,_ID),(1,1,_CW),(2,3,_ID),(3,5,_180),(4,4,_CCW),(5,0,_180)],
    "x'": [(0,5,_180),(1,1,_CCW),(2,0,_ID),(3,2,_ID),(4,4,_CW),(5,3,_180)],
}

# COLOR_CHARS = ['U','R','F','D','L','B']
# After rotation, the face that moved to position U should have its stickers relabeled to 'U', etc.
# _COLOR_MAP[rot] maps old face index -> new face index
_FACE_MOVE = {
    'z':  {4:0, 0:1, 2:2, 1:3, 3:4, 5:5},
    "z'": {1:0, 3:1, 2:2, 4:3, 0:4, 5:5},
    'z2': {3:0, 4:1, 2:2, 0:3, 1:4, 5:5},
    'x':  {2:0, 1:1, 3:2, 5:3, 4:4, 0:5},
    "x'": {5:0, 1:1, 0:2, 2:3, 4:4, 3:5},
}
_FACE_CHARS = ['U', 'R', 'F', 'D', 'L', 'B']


def _apply_facelet_rotation(facelet_str, rot_str):
    faces = [facelet_str[i*9:(i+1)*9] for i in range(6)]
    result = [''] * 6
    for dst, src, perm in _ROTATION_RULES[rot_str]:
        result[dst] = ''.join(faces[src][p] for p in perm)
    rearranged = ''.join(result)
    # Remap color characters: old face color -> new face color
    old_to_new = {}
    for old_face, new_face in _FACE_MOVE[rot_str].items():
        old_to_new[_FACE_CHARS[old_face]] = _FACE_CHARS[new_face]
    return ''.join(old_to_new.get(c, c) for c in rearranged)


def _parse_rotation(rot_str):
    if rot_str.endswith("'"):
        return rot_str[0], 3
    elif rot_str.endswith('2'):
        return rot_str[0], 2
    else:
        return rot_str, 1


class CFOPSolver:
    def __init__(self):
        init_tables()

    def solve(self, facelet_str, pre_rotation=None):
        if pre_rotation:
            facelet_str = _apply_facelet_rotation(facelet_str, pre_rotation)

        state = CubieCube.from_facelet(facelet_str)

        if state.is_solved():
            solution = pre_rotation if pre_rotation else ''
            return {
                'cross': '',
                'f2l': '',
                'oll': None,
                'pll': None,
                'alll': None,
                'solution': solution,
            }

        cross_moves = solve_cross(state, PERM_PRUN, FLIP_PRUN, PERM_MOVE, FLIP_MOVE)
        if cross_moves is None:
            _dbg("DEBUG: cross failed")
            return None
        cross_str = moves_to_str(cross_moves)
        _dbg(f"DEBUG: cross = {cross_str}")
        for m in cross_moves:
            state.apply_move_idx(m)

        f2l_result = solve_f2l(state, PAIR_PRUN, PAIR_MOVE)
        if f2l_result is None:
            _dbg("DEBUG: f2l failed")
            return None
        f2l_moves, state = f2l_result
        f2l_str = moves_to_str(f2l_moves)
        _dbg(f"DEBUG: f2l = {f2l_str}")

        alll_str = ''
        oll_str = ''
        pll_str = ''
        alll_found = False

        if ALLL_RECOGNITION and ALLL_PROB > 0 and (ALLL_PROB >= 1.0 or random.random() < ALLL_PROB):
            alll_str, state = solve_alll(state, ALLL_RECOGNITION)
            if alll_str is not None:
                alll_found = True
                _dbg(f"DEBUG: ALLL found, alg={alll_str}")
            else:
                _dbg("DEBUG: ALLL not found, falling back to OLL+PLL")

        if not alll_found:
            oll_str, state = solve_oll(state, OLL_RECOGNITION)
            if oll_str is None:
                _dbg("DEBUG: oll failed")
                f = state.to_facelet()
                u_pattern = ''.join('1' if f[i] == 'U' else '0' for i in range(9))
                _dbg(f"DEBUG: U-face pattern: {u_pattern}")
                _dbg(f"DEBUG: U-face colors: {f[:9]}")
                for auf in range(4):
                    test = state.apply_u_rot(auf)
                    f2 = test.to_facelet()
                    p2 = ''.join('1' if f2[i] == 'U' else '0' for i in range(9))
                    _dbg(f"DEBUG: auf={auf} pattern={p2} in_table={p2 in OLL_RECOGNITION}")
                return None
            _dbg(f"DEBUG: oll = {oll_str}")

            pll_str, state = solve_pll(state, PLL_RECOGNITION)
            if pll_str is None:
                _dbg("DEBUG: pll failed")
                _dbg(f"DEBUG: after oll cp={state.cp} co={state.co} ep={state.ep} eo={state.eo}")
                for auf in range(4):
                    test = state.apply_u_rot(auf)
                    cp_key = tuple(test.cp[i] for i in range(4))
                    ep_key = tuple(test.ep[i] for i in range(4))
                    key = (cp_key, ep_key)
                    _dbg(f"DEBUG: auf={auf} key={key} in_table={key in PLL_RECOGNITION}")
                return None
            _dbg(f"DEBUG: pll = {pll_str}")

        if DEBUG and not state.is_solved():
            _dbg(f"DEBUG: state not solved after LL, cp={state.cp} co={state.co} ep={state.ep} eo={state.eo}")

        solution_parts = [cross_str, f2l_str]
        if alll_found:
            solution_parts.append(alll_str)
        else:
            solution_parts.extend([oll_str, pll_str])
        solution = ' '.join(p for p in solution_parts if p)
        if pre_rotation:
            solution = pre_rotation + ' ' + solution if solution else pre_rotation

        if pre_rotation:
            def _to_basic(s):
                if not s:
                    return s
                basic, _ = convert_alg_to_basic(s)
                return basic.strip()
            cross_str  = _to_basic(pre_rotation + ' ' + cross_str  if cross_str  else pre_rotation)
            f2l_str    = _to_basic(pre_rotation + ' ' + f2l_str    if f2l_str    else '')
            oll_str    = _to_basic(pre_rotation + ' ' + oll_str    if oll_str    else '') if oll_str    else None
            pll_str    = _to_basic(pre_rotation + ' ' + pll_str    if pll_str    else '') if pll_str    else None
            alll_str   = _to_basic(pre_rotation + ' ' + alll_str   if alll_str   else '') if alll_str   else None
            basic_sol, _ = convert_alg_to_basic(solution)
            solution = basic_sol.strip()

        if DEBUG:
            verify = CubieCube.from_facelet(facelet_str)
            if pre_rotation:
                rot_axis, rot_count = _parse_rotation(pre_rotation)
                for _ in range(rot_count):
                    verify._apply_rotation(rot_axis)
            verify = apply_alg_str(verify, ' '.join(solution_parts))
            if verify.is_solved():
                _dbg("DEBUG: solution verified OK")
            else:
                _dbg(f"DEBUG: solution FAILED verification, final cp={verify.cp} co={verify.co} ep={verify.ep} eo={verify.eo}")

        result = {
            'cross': cross_str,
            'f2l': f2l_str,
            'solution': solution,
        }
        if alll_found:
            result['alll'] = alll_str
            result['oll'] = None
            result['pll'] = None
        else:
            result['alll'] = None
            result['oll'] = oll_str
            result['pll'] = pll_str
        return result


def main():
    global DEBUG
    DEBUG = True
    import sys
    import time
    if len(sys.argv) < 2:
        print("Usage: python cfop_solver.py [--scramble] [--rotation z|z'|z2|x|x'] <facelet_or_scramble>")
        print("  Default: treat input as facelet string")
        print("  --scramble: treat input as scramble moves")
        print("  --rotation: apply pre-rotation to change bottom face (z z' z2 x x')")
        sys.exit(1)

    use_scramble = False
    pre_rotation = None
    facelet = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--scramble':
            use_scramble = True
            i += 1
        elif args[i] == '--rotation':
            if i + 1 >= len(args):
                print("Error: --rotation requires a value (z, z', z2, x, x')")
                sys.exit(1)
            pre_rotation = args[i + 1]
            i += 2
        elif facelet is None:
            facelet = args[i]
            i += 1
        else:
            i += 1

    if facelet is None:
        print("Error: no input provided")
        sys.exit(1)

    if use_scramble:
        c1 = CubieCube.solved()
        c2 = apply_alg_str(c1, facelet)
        facelet = c2.to_facelet()
        print(f"Scramble: {facelet}")
        print(f"Facelet: {facelet}")
    else:
        if len(facelet) != 54:
            print("Invalid facelet string length")
            sys.exit(1)

    solver = CFOPSolver()
    start_time = time.time()
    result = solver.solve(facelet, pre_rotation=pre_rotation)
    elapsed_time = time.time() - start_time

    if result is None:
        print("No solution found")
        sys.exit(1)
    print(f"Cross: {result['cross']}")
    print(f"F2L: {result['f2l']}")
    alll_hit = result.get('alll') is not None
    if not alll_hit:
        print(f"OLL: {result['oll']}")
        print(f"PLL: {result['pll']}")
    else:
        print(f"ALL: {result['alll']}")
    print(f"Solution: {result['solution']}")
    print(f"Time: {elapsed_time:.3f}s")


if __name__ == '__main__':
    # FBLFURFBBRDUDRBRFBLLUUFFUBFRDDLDRLLRDUULLRBDFBULRBUDFD
    main()
