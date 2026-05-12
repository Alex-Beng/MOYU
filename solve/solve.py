import argparse
import logging
import random
import sys

FACE_MAP = {'U':0,'R':1,'F':2,'D':3,'L':4,'B':5}
COLOR_MAP = {'U':'W','R':'R','F':'G','D':'Y','L':'O','B':'B'}
SOLVED = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

logger = logging.getLogger(__name__)
# GBBWWBGRYYOYGOYOOORWORGGWYYBWWWRORGRRROYBRGOWGBBGYYBBW

ROTATION_EQUIV = {
    'y': ["U'", "D", "F'", "B", "L'", "R'"],
    "y'": ["U", "D'", "F", "B'", "L", "R"],
    'x': ["U'", "D'", "F", "B'", "L'", "R"],
    "x'": ["U", "D", "F'", "B", "L", "R'"],
    'z': ["U'", "D", "R", "L'", "F", "B'"],
    "z'": ["U", "D'", "R'", "L", "F'", "B"],
}

ZERO_MOVES = [
    "R U R' F' R U R' U' R' F R2 U' R' U' R U2 R' U' R U2 L' U R' U' L",
    "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R    U' R' U R U' R2 F' U' F U R F R' F' R2 ",
    # "R2 U R' U R' U' R U' R2 D U' R' U R D' U R2 U R' U R' U' R U' R2 D U' R' U R D' U R2 U R' U R' U' R U' R2 D U' R' U R D' U"
]

def expand_rotations(tokens):
    result = []
    for t in tokens:
        key = t.rstrip('2')
        if key in ROTATION_EQUIV:
            n = 2 if t.endswith('2') else 1
            equiv = ROTATION_EQUIV[key]
            for _ in range(n):
                result.extend(equiv)
        else:
            result.append(t)
    return result

def get_facelets(base):
    import requests
    r = requests.get(f"{base}/api/facelets")
    r.raise_for_status()
    return r.text.strip()

def kociemba_to_rubik_solver(k_facelets):
    faces = [k_facelets[i*9:(i+1)*9] for i in range(6)]
    reordered = faces[0] + faces[4] + faces[2] + faces[1] + faces[5] + faces[3]
    return ''.join(COLOR_MAP[c] for c in reordered)

def kociemba_to_rubik_cube(k_facelets):
    faces = [k_facelets[i*9:(i+1)*9] for i in range(6)]
    u, r, f, d, l, b = faces
    cross = [None] * 54
    cross[0:9] = u
    cross[9:12] = l[0:3]
    cross[12:15] = f[0:3]
    cross[15:18] = r[0:3]
    cross[18:21] = b[0:3]
    cross[21:24] = l[3:6]
    cross[24:27] = f[3:6]
    cross[27:30] = r[3:6]
    cross[30:33] = b[3:6]
    cross[33:36] = l[6:9]
    cross[36:39] = f[6:9]
    cross[39:42] = r[6:9]
    cross[42:45] = b[6:9]
    cross[45:54] = d
    return ''.join(COLOR_MAP[c] for c in cross)

def solve_cfop(facelets, debug=False):
    try:
        from solve import cfop_solver
        from solve.cfop_solver import CFOPSolver
    except ImportError:
        raise RuntimeError("cfop_solver.py not found in solve/")
    cfop_solver.DEBUG = debug
    solver = CFOPSolver()
    result = solver.solve(facelets)
    if result is None:
        raise RuntimeError("No CFOP solution found")
    cross_n = len(result['cross'].split()) if result['cross'] else 0
    f2l_n   = len(result['f2l'].split())   if result['f2l']   else 0
    oll_n   = len(result['oll'].split())   if result['oll']   else 0
    pll_n   = len(result['pll'].split())   if result['pll']   else 0
    alll_n  = len(result['alll'].split())  if result['alll']  else 0
    total_n = cross_n + f2l_n + oll_n + pll_n + alll_n
    logger.info("  Cross (%d): %s", cross_n, result['cross'])
    logger.info("  F2L   (%d): %s", f2l_n, result['f2l'])
    logger.info("  OLL   (%d): %s", oll_n, result['oll'])
    logger.info("  PLL   (%d): %s", pll_n, result['pll'])
    logger.info("  ALLL  (%d): %s", alll_n, result['alll'])
    logger.info("  Total : %d moves", total_n)
    return {"solution": result['solution']}

def solve_kociemba(facelets):
    try:
        import kociemba
    except ImportError:
        print("kociemba not installed. Run: pip install kociemba")
        sys.exit(1)
    return kociemba.solve(facelets)

DEFAULT_JAVA_DIR = "E:/Dev/Cube/Rubik-s-Cube-Robot/min2phase-dev-min"

def solve_min2phase(facelets, java_dir=None):
    import subprocess
    java_dir = java_dir or DEFAULT_JAVA_DIR
    result = subprocess.run(
        ["java", "demo", facelets],
        capture_output=True, text=True, cwd=java_dir
    )
    if result.returncode != 0:
        print(f"Java solver error: {result.stderr.strip()}")
        sys.exit(1)
    output = result.stdout.strip()
    return output
    return random.choice(ZERO_MOVES) + ' ' + output


def parse_moves(solution):
    if isinstance(solution, str):
        tokens = solution.strip().split()
    else:
        tokens = [str(m) for m in solution]
    tokens = expand_rotations(tokens)
    moves = []
    for t in tokens:
        face = FACE_MAP.get(t[0])
        if face is None:
            continue
        if len(t) == 1:
            moves.append({"face": face, "dir": 0})
        elif t[1] == "'":
            moves.append({"face": face, "dir": 1})
        elif t[1] == "2":
            moves.append({"face": face, "dir": 2})
    return moves

def send_moves(base, moves):
    import requests
    if not moves:
        print("No moves to send")
        return
    r = requests.post(f"{base}/api/moves", json=moves)
    print(f"-> {r.text}")

def main():
    parser = argparse.ArgumentParser(description='GAN Cube Solver')
    parser.add_argument('host', nargs='?', default='192.168.50.246', help='Device IP address')
    parser.add_argument('--method', choices=['cfop', 'kociemba', 'min2phase'], default='cfop', help='Solving method (default: cfop)')
    parser.add_argument('--send', action='store_true', help='Send solution to device')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    base = f"http://{args.host}"

    facelets = get_facelets(base)
    print(f"Facelets: {facelets}")
    if len(facelets) != 54 or not all(c in 'URFDLB' for c in facelets):
        print("Invalid facelet string from device")
        sys.exit(1)
    if facelets == SOLVED:
        print("Already solved!")
        return

    print(f"Solving with {args.method.upper()}...")
    if args.method == 'cfop':
        solution = solve_cfop(facelets, debug=args.debug)
    elif args.method == 'kociemba':
        solution = solve_kociemba(facelets)
    else:
        solution = solve_min2phase(facelets)

    if isinstance(solution, str):
        print(f"Solution: {solution}")
        moves = parse_moves(solution)
    else:
        move_str = solution.get("solution", "")
        print(f"Solution: {move_str}")
        moves = parse_moves(move_str)

    names = ['U','R','F','D','L','B']
    move_strs = [names[m['face']] + ({0: '', 1: "'", 2: '2'}[m['dir']]) for m in moves]
    print("Moves (%d quarter-turns): %s" % (len(moves), ' '.join(move_strs)))

    if args.send:
        send_moves(base, moves)
    else:
        print("Add --send to execute solution on device")

if __name__ == '__main__':
    main()
