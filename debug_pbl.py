import sys
sys.path.insert(0, '.')
from collections import deque
from solve.pocket_solver import PocketCube, apply_alg_str, RUF_FACES, FACE_NAMES
from solve.cfop_solver import CubieCube

facelet = 'UUURUURLFURRFRBLFFBURLFRDDDFFFDDUDDULDDLLFLLRBBBRBBLBB'
full_cube = CubieCube.from_facelet(facelet)
cube = PocketCube(full_cube.cp, full_cube.co)
cube = apply_alg_str(cube, 'F R')
cube = apply_alg_str(cube, "R'")
key = (tuple(cube.cp), tuple(cube.co))

print("Target key:", key)

solved = PocketCube.solved()
table = {}
queue = deque()
table[(tuple(range(8)), (0,0,0,0,0,0,0,0))] = ''
queue.append((solved, ''))

found = False
while queue:
    state, path = queue.popleft()
    depth = len(path.split()) if path else 0
    if depth > 9:
        continue
    if (tuple(state.cp), tuple(state.co)) == key:
        print('FOUND at depth %d: %s' % (depth, path))
        found = True
        break
    for face in RUF_FACES:
        for times in [1, 2, 3]:
            ns = state.copy()
            ns.apply_move(face, times)
            ms = FACE_NAMES[face]
            if times == 2:
                ms += '2'
            elif times == 3:
                ms += "'"
            np = (path + ' ' + ms).strip()
            k = (tuple(ns.cp), tuple(ns.co))
            if k not in table:
                table[k] = np
                queue.append((ns, np))

if not found:
    print('NOT FOUND in table of %d states (max depth 9)' % len(table))
    # Check if co matches at all
    target_co = key[1]
    matching_co = [k for k in table if k[1] == target_co]
    print('States with matching co: %d' % len(matching_co))
    for mk in matching_co[:5]:
        print('  ', mk, '->', table[mk])
