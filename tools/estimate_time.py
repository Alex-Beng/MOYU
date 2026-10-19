"""单次复原耗时预估 —— 蒙特卡洛估算 recipe 下一次 solve 的固件下发耗时。

原理：
    - 生成 N 个 WCA 旧式随机打乱（25 步，含 180°，不含双层，去掉同面相邻）。
    - 每个打乱调用 CFOP 求解，得到各阶段步数（cross/f2l/oll/pll/alll）。
    - 复用 controller._build_phased_moves 生成与实机完全一致的下发 step 序列
      （含 F2L 组间停顿、净零废步、预判跳过 time）。
    - 按 gan-cube-emu 固件的实际时序模型累加耗时：
        * 90° 转动 (dir 0/1): + 当前 delay
        * 180° 转动 (dir 2) : + 2 × 当前 delay（HTTP 层拆成两条 90°）
        * {"delay": N}      : 仅更新当前 delay，不耗时
        * {"time": N}       : + round(N/10)*10 ms（固件按十进制取整到 10ms tick）
    - 汇总整体分布的均值/中位/分位及各阶段耗时占比。

用法：
    python -m tools.estimate_time --recipe rank.json --n 10000
    python -m tools.estimate_time --recipe rank.json --n 2000 --seed 0
"""
import argparse
import concurrent.futures
import os
import random
import statistics
import sys
from pathlib import Path
from types import SimpleNamespace

# 允许以脚本或 -m 方式运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recipe.loader import RECIPES_DIR  # noqa: E402
from recipe.schema import Recipe  # noqa: E402
from solve.solve import solve_cfop  # noqa: E402
from device.cube_api import parse_move_notation  # noqa: E402
import controller as _controller  # noqa: E402


FACES = ["U", "R", "F", "D", "L", "B"]
SUFFIXES = ["", "'", "2"]


def gen_wca_scramble(rng: random.Random, length: int = 25) -> str:
    """WCA 旧式随机打乱：六面 90°/180°，去掉同面相邻，不含双层。"""
    out = []
    last = None
    for _ in range(length):
        while True:
            f = rng.choice(FACES)
            if f != last:
                break
        last = f
        out.append(f + rng.choice(SUFFIXES))
    return " ".join(out)


def scramble_to_cube(cube_cls, apply_alg_str, moves: str):
    c = cube_cls.solved()
    return apply_alg_str(c, moves)


def resolve_recipe_path(name: str) -> Path:
    if not name.endswith(".json"):
        name += ".json"
    path = Path(name)
    if not path.is_absolute():
        path = RECIPES_DIR / path
    return path


def load_recipe(name: str) -> Recipe:
    path = resolve_recipe_path(name)
    import json
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return Recipe.from_dict(raw, base_dir=path.parent)


def build_stub(recipe: Recipe):
    """构造最小 controller stub，仅用于调用 _build_phased_moves。"""
    inst = SimpleNamespace()
    inst.recipe = SimpleNamespace(recipe=recipe)
    inst.state = "solve"
    return inst


def move_cost(step: dict, cur_delay: int) -> int:
    """单个 step 的固件耗时（ms）；同时返回是否更新了 delay（通过返回值之外处理）。"""
    if "delay" in step:
        return 0
    if "time" in step:
        return round(step["time"] / 10) * 10
    if "move" in step:
        parsed = parse_move_notation(step["move"])
        if not parsed:
            return 0
        return sum(cur_delay * (2 if p["dir"] == 2 else 1) for p in parsed)
    if "face" in step:
        return cur_delay * (2 if step["dir"] == 2 else 1)
    return 0


def simulate_time(steps: list, solve_delay: int | None) -> int:
    """按固件时序模型累加整批 steps 的耗时（ms）。"""
    return simulate_time_and_breakdown(steps, solve_delay)[0]


def simulate_time_breakdown(steps: list, solve_delay: int | None) -> dict:
    """累加耗时并按阶段归类，返回 {阶段: ms}。

    通过 step 来源标记（在构建时附加 _phase）归类；无标记归入 moves。
    """
    return simulate_time_and_breakdown(steps, solve_delay)[1]


def simulate_time_and_breakdown(steps: list, solve_delay: int | None):
    """单次遍历同时得到总耗时（ms）与分阶段累加，避免重复扫描。"""
    cur = max(solve_delay or 1, 1)
    total = 0
    acc = {"cross": 0, "f2l": 0, "oll": 0, "pll": 0, "alll": 0,
           "pause": 0, "scrap": 0}
    for s in steps:
        if "delay" in s:
            cur = max(s["delay"] or 1, 1)
            continue
        cost = move_cost(s, cur)
        total += cost
        phase = s.get("_phase", "f2l")
        if phase in ("pause",):
            acc["pause"] += cost
        elif phase in ("scrap",):
            acc["scrap"] += cost
        elif phase in acc:
            acc[phase] += cost
        else:
            acc["f2l"] += cost
    return total, acc


def build_phased_with_phase(controller_inst, result: dict, recipe: Recipe) -> list:
    """构造带 _phase 标记的 steps，逻辑与 controller._build_phased_moves 对齐。"""
    steps = []
    phase = {"cur": "cross"}

    def _parse(move_str):
        if recipe.move_format == "str":
            return [{"move": t} for t in move_str.split() if t]
        return parse_move_notation(move_str)

    def _tag(items):
        for it in items:
            it.setdefault("_phase", phase["cur"])
        return items

    scrap_prob = getattr(recipe, "scrap_prob", 0.0) or 0.0
    scrap_pause = getattr(recipe, "scrap_pause", None)
    predict_prob = getattr(recipe, "predict_prob", 0.0) or 0.0
    double_gap = getattr(recipe, "double_gap_ms", None)
    cur_delay = [getattr(recipe, "solve_delay", None)]

    def _predict():
        return predict_prob > 0 and random.random() < predict_prob

    def _time(ms):
        if ms and not _predict():
            steps.append({"time": ms, "_phase": "pause"})

    def _delay(ms):
        if ms:
            steps.append({"delay": ms, "_phase": phase["cur"]})
            cur_delay[0] = ms

    def _emit(move_str):
        """与 controller 一致：double_gap_ms 配置时把 180° 拆成两个 90°，
        中间插 {"delay": double_gap}，之后再恢复原持续 delay。"""
        parsed = _parse(move_str)
        if not double_gap:
            steps.extend(_tag(parsed))
            return
        for st in parsed:
            is_double = (st.get("dir") == 2) or (
                recipe.move_format == "str" and st.get("move", "").endswith("2"))
            if not is_double:
                steps.append(dict(st, _phase=phase["cur"]) if "_phase" not in st else st)
                continue
            if "face" in st:
                half = {"face": st["face"], "dir": 0}
            else:
                half = {"move": st["move"].rstrip("2")}
            steps.append(dict(half, _phase=phase["cur"]))
            steps.append({"delay": double_gap, "_phase": phase["cur"]})
            steps.append(dict(half, _phase=phase["cur"]))
            if cur_delay[0] is not None:
                steps.append({"delay": cur_delay[0], "_phase": phase["cur"]})

    def _scrap():
        """与 controller._build_phased_moves 一致：走 _parse 生成 face/dir。"""
        if not scrap_prob or random.random() >= scrap_prob:
            return
        pairs = [("U", "U'"), ("U'", "U"), ("U2", "U2")]
        a, b = random.choice(pairs)
        for t in (a, b):
            for it in _parse(t):
                it["_phase"] = "scrap"
                steps.append(it)
        if scrap_pause:
            steps.append({"time": scrap_pause, "_phase": "pause"})

    phase["cur"] = "cross"
    if result.get("cross"):
        _time(recipe.cross_time)
        _delay(recipe.cross_delay)
        _emit(result["cross"])

    f2l_groups = result.get("f2l_groups") or result.get("f2l") or []
    if isinstance(f2l_groups, str):
        f2l_groups = [f2l_groups] if f2l_groups else []
    f2l_groups = [g for g in f2l_groups if g]

    phase["cur"] = "f2l"
    if f2l_groups:
        _scrap()
        _time(recipe.f2l_time)
        _delay(recipe.f2l_delay)
        pause = getattr(recipe, "f2l_pair_pause", None)
        for gi, g in enumerate(f2l_groups):
            if gi > 0 and pause:
                lo, hi = pause[0], pause[1]
                _time(random.randint(lo, hi) if hi > lo else lo)
            _emit(g)

    if result.get("alll"):
        phase["cur"] = "alll"
        _scrap()
        _time(recipe.alll_time)
        _delay(recipe.alll_delay)
        _emit(result["alll"])
    else:
        if result.get("oll"):
            phase["cur"] = "oll"
            _scrap()
            _time(recipe.oll_time)
            _delay(recipe.oll_delay)
            _emit(result["oll"])
        if result.get("pll"):
            phase["cur"] = "pll"
            _time(recipe.pll_time)
            _delay(recipe.pll_delay)
            _emit(result["pll"])

    return steps


def percentile(sorted_vals, q):
    if not sorted_vals:
        return 0
    import math
    idx = (len(sorted_vals) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return sorted_vals[int(idx)]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


# ---------------------------------------------------------------------------
# 并行 worker：每个子进程首次启动时预加载 tables 与 xcross 表，避免逐样本重复。
# 所有 worker 均为模块级函数，保证在 Windows(spawn) 下可 pickle。
# ---------------------------------------------------------------------------

_W = {
    "recipe": None,
    "stub": None,
    "cubie_cls": None,
    "apply_alg_str": None,
    "base_seed": None,
    "scramble_length": 25,
}


def _worker_init(recipe_name: str, seed, scramble_length: int):
    """子进程初始化：加载 recipe、预建所有搜索表、缓存常量。"""
    global _W
    recipe = load_recipe(recipe_name)

    from solve import cfop_solver
    from solve.cfop_solver import CubieCube, apply_alg_str

    cfop_solver.init_tables()
    cfop_solver.build_xcross_pair_move_tables()

    _W["recipe"] = recipe
    _W["stub"] = build_stub(recipe)
    _W["cubie_cls"] = CubieCube
    _W["apply_alg_str"] = apply_alg_str
    _W["base_seed"] = seed
    _W["scramble_length"] = scramble_length


def _run_sample(index: int):
    """求解单个样本并返回 (time_ms, breakdown, stage_counts) 或 None（跳过）。"""
    recipe = _W["recipe"]
    stub = _W["stub"]
    CubieCube = _W["cubie_cls"]

    # 种子派生：保证 (seed, index) -> 确定性 rng，与并行/串行、worker 数无关。
    if _W["base_seed"] is None:
        rng = random.Random()
    else:
        rng = random.Random(_W["base_seed"] * 1000003 + index)
        random.seed(_W["base_seed"] * 1000003 + index)  # build_phased 内部用全局 random

    scr = gen_wca_scramble(rng, _W["scramble_length"])
    c = scramble_to_cube(CubieCube, _W["apply_alg_str"], scr)
    facelets = c.to_facelet()
    try:
        result = solve_cfop(facelets, rotation=recipe.rotation,
                            alll_prob=recipe.alll_prob)
    except Exception:
        return None

    stage = {
        "cross": len(result["cross"].split()) if result["cross"] else 0,
        "f2l": sum(len(g.split()) for g in (result.get("f2l_groups") or [])),
        "oll": 0,
        "pll": 0,
        "alll": 0,
    }
    if result.get("alll"):
        stage["alll"] = len(result["alll"].split())
    else:
        stage["oll"] = len(result["oll"].split()) if result.get("oll") else 0
        stage["pll"] = len(result["pll"].split()) if result.get("pll") else 0

    steps = build_phased_with_phase(stub, result, recipe)
    total, bd = simulate_time_and_breakdown(steps, recipe.solve_delay)
    return total, bd, stage


def main():
    ap = argparse.ArgumentParser(description="蒙特卡洛估算 recipe 单次复原的固件下发耗时")
    ap.add_argument("--recipe", default="example.json", help="recipe 名称或路径（默认 example.json）")
    ap.add_argument("--n", type=int, default=2000, help="蒙特卡洛样本数（默认 2000）")
    ap.add_argument("--seed", type=int, default=None, help="随机种子（可选；并行下按样本索引派生）")
    ap.add_argument("--scramble-length", type=int, default=25, help="打乱步数（默认 25）")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1,
                    help="并行进程数（默认 CPU 核数；设为 1 则串行）")
    ap.add_argument("--chunksize", type=int, default=None,
                    help="ProcessPoolExecutor.map 的分块大小（默认自动）")
    args = ap.parse_args()

    recipe_name = args.recipe
    recipe = load_recipe(recipe_name)

    print(f"recipe: {recipe.name}  (cube={recipe.cube}, rotation={recipe.rotation}, "
          f"alll_prob={recipe.alll_prob})")
    print(f"样本数: {args.n}, 打乱: WCA 旧式 {args.scramble_length} 步（含 180°，去同面相邻）")
    print(f"solve_delay={recipe.solve_delay}, f2l_pair_pause={recipe.f2l_pair_pause}, "
          f"scrap_prob={recipe.scrap_prob}, predict_prob={recipe.predict_prob}")
    print(f"workers={args.workers}")
    print()

    times = []
    breakdown_sum = {"cross": 0, "f2l": 0, "oll": 0, "pll": 0, "alll": 0,
                     "pause": 0, "scrap": 0}
    stage_moves = {"cross": [], "f2l": [], "oll": [], "pll": [], "alll": []}
    skipped = 0

    # 单样本耗时波动大，用较小的 chunksize 以减少 straggler 造成的空等。
    chunksize = args.chunksize or max(1, args.n // (args.workers * 16) or 1)
    done = 0
    report_every = max(1, args.n // 20)

    def _consume(sample):
        nonlocal skipped, done
        done += 1
        if done % report_every == 0:
            print(f"  进度 {done}/{args.n}", file=sys.stderr)
        if sample is None:
            skipped += 1
            return
        t, bd, stage = sample
        times.append(t)
        for k in breakdown_sum:
            breakdown_sum[k] += bd[k]
        for k in ("cross", "f2l", "oll", "pll", "alll"):
            stage_moves[k].append(stage[k])

    if args.workers <= 1:
        _worker_init(recipe_name, args.seed, args.scramble_length)
        for i in range(args.n):
            _consume(_run_sample(i))
    else:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=_worker_init,
            initargs=(recipe_name, args.seed, args.scramble_length),
        ) as ex:
            for sample in ex.map(_run_sample, range(args.n), chunksize=chunksize):
                _consume(sample)

    if not times:
        print("无有效样本")
        return

    times.sort()
    n = len(times)
    mean = sum(times) / n
    median = statistics.median(times)
    p90 = percentile(times, 0.90)
    p99 = percentile(times, 0.99)
    print("=" * 52)
    print("单次复原固件下发耗时（ms）")
    print("=" * 52)
    print(f"  样本数   : {n}" + (f"  (跳过 {skipped})" if skipped else ""))
    print(f"  均值     : {mean:.0f}")
    print(f"  中位数   : {median:.0f}")
    print(f"  P50      : {percentile(times, 0.50):.0f}")
    print(f"  P90      : {p90:.0f}")
    print(f"  P99      : {p99:.0f}")
    print(f"  最大     : {times[-1]:.0f}")
    print(f"  最小     : {times[0]:.0f}")
    print()
    print("各阶段平均步数:")
    for k in ("cross", "f2l", "oll", "pll", "alll"):
        arr = stage_moves[k]
        if arr:
            print(f"  {k:6s}: {sum(arr)/len(arr):.2f}  (n={len(arr)})")
    print()
    total_bd = sum(breakdown_sum.values()) or 1
    print("各阶段耗时占比（按总耗时累计）:")
    for k in ("cross", "f2l", "oll", "pll", "alll", "pause", "scrap"):
        v = breakdown_sum[k]
        print(f"  {k:6s}: {v/1e3:9.1f} s  ({v/total_bd*100:5.1f}%)")
    print(f"  平均单次: {mean/1000:.2f} s")


if __name__ == "__main__":
    main()
