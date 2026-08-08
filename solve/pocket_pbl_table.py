"""从全量 BFS 表中提取 EG 表

EG 表：co[4:8]=0 的状态 → solved 最短路径
PBL 表直接复用 EG 表（co=[0]*8 是 co[4:8]=0 的子集）
"""
import time
import os
import pickle
from collections import deque

FACE_NAMES = ['U', 'R', 'F', 'D', 'L', 'B']
RUF_FACES = [0, 1, 2]

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

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_EG_CACHE = os.path.join(_MODULE_DIR, '.pocket_eg_table.pkl')


def _apply_cw(cp, co, face):
    old_cp = list(cp)
    old_co = list(co)
    new_cp = [0] * 8
    new_co = [0] * 8
    t_cp = MOVE_CP[face]
    t_co = MOVE_CO[face]
    for i in range(8):
        src = t_cp[i]
        new_cp[i] = old_cp[src]
        new_co[i] = (old_co[src] + t_co[i]) % 3
    return tuple(new_cp), tuple(new_co)


def _build_full_bfs(max_depth=11):
    """BFS from solved，返回完整状态表"""
    print("Building full BFS table from solved...")
    start = time.time()

    solved_cp = tuple(range(8))
    solved_co = (0,) * 8

    table = {(solved_cp, solved_co): ""}
    queue = deque([(solved_cp, solved_co, "")])

    MOVE_SUFFIXES = [('', 1), ('2', 2), ("'", 3)]
    depth_counts = {0: 1}

    while queue:
        cp, co, path = queue.popleft()
        depth = len(path.split()) if path else 0
        if depth >= max_depth:
            continue

        for face in RUF_FACES:
            for suffix, turns in MOVE_SUFFIXES:
                new_cp, new_co = cp, co
                for _ in range(turns):
                    new_cp, new_co = _apply_cw(new_cp, new_co, face)

                ms = FACE_NAMES[face] + suffix
                new_path = (path + ' ' + ms).strip() if path else ms
                new_key = (new_cp, new_co)

                if new_key not in table:
                    table[new_key] = new_path
                    queue.append((new_cp, new_co, new_path))
                    d = depth + 1
                    depth_counts[d] = depth_counts.get(d, 0) + 1

    elapsed = time.time() - start
    print(f"Full BFS: {len(table)} states, {elapsed:.1f}s")
    for d in sorted(depth_counts.keys()):
        print(f"  depth {d}: {depth_counts[d]} states")

    return table


def load_eg_table():
    """加载 EG 表（co[4:8]=0 的状态），若无缓存则构建"""
    if os.path.exists(_EG_CACHE):
        with open(_EG_CACHE, 'rb') as f:
            return pickle.load(f)

    # 先构建全量 BFS
    full_table = _build_full_bfs()

    # 筛选 co[4:8]=0 → EG 表（正向路径，求解时 invert）
    eg_table = {k: v for k, v in full_table.items() if all(k[1][i] == 0 for i in range(4, 8))}

    pbl_count = sum(1 for (cp, co) in eg_table if all(c == 0 for c in co))
    print(f"EG table: {len(eg_table)} states (co[4:8]=0)")
    print(f"PBL subset: {pbl_count} states (co=[0]*8)")

    with open(_EG_CACHE, 'wb') as f:
        pickle.dump(eg_table, f)
    print(f"Saved to {_EG_CACHE}")

    return eg_table


if __name__ == '__main__':
    load_eg_table()
