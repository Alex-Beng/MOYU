"""打乱状态统计分析 —— 从 controller.log 提取每次 solve 对应的打乱状态（54 面片串）

原理：
    solver 只记录解法，不记录状态。真正的打乱状态由 device.cube_api 记录：
        [device.cube_api] INFO: ... GET .../api/facelets  resp=<54字符>
    一次 solve 周期会抓取一次面片（可能在 solve 前多次重试），
    因此把每个 `*/solve: <解法> (*步)` 行之前最近一次抓取的面片串归属为该次打乱的
    状态。同一时刻连续相同的抓取视为同一次。

用法：
    python -m tools.analyze_states                          # 分析 log/controller.log
    python -m tools.analyze_states --log log/controller.log
    python -m tools.analyze_states --mode rank              # 只看某模式
    python -m tools.analyze_states --top 50                 # 重复状态显示条数
    python -m tools.analyze_states --plot                   # 弹窗显示重复随时间分布图
"""
import argparse
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

DEFAULT_LOG = "log/controller.log"
SOLVED = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

FX_RE = re.compile(r"\[device\.cube_api\] INFO:.*api/facelets\s+resp=([URFDLB]{54})")
SOLVE_START_RE = re.compile(r"\[__main__\] INFO: (\w+)/solve: 求解")
SOLVE_DONE_RE = re.compile(r"\[__main__\] INFO: (\w+)/solve: .* \((\d+)步\)")


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        return None


def parse(log_path: Path):
    """流式解析日志，返回每次 solve 的记录列表。

    record = {
        "mode": str, "facelets": str | None, "steps": int,
        "line": int, "ts": str,
    }
    """
    records = []
    pending_mode = None          # 当前处于“求解中”的模式
    last_facelets = None         # solve 前最近抓取的面片串
    last_ts = None

    with open(log_path, encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            if line[:4].isdigit() and "-" in line[:8]:
                last_ts = line[:23]

            m = SOLVE_START_RE.search(line)
            if m:
                pending_mode = m.group(1)
                last_facelets = None
                continue

            m = FX_RE.search(line)
            if m and pending_mode is not None:
                last_facelets = m.group(1)
                continue

            m = SOLVE_DONE_RE.search(line)
            if m:
                mode, steps = m.group(1), int(m.group(2))
                if pending_mode is None:
                    pending_mode = mode
                records.append({
                    "mode": mode,
                    "facelets": last_facelets,
                    "steps": steps,
                    "line": lineno,
                    "ts": last_ts,
                })
                pending_mode = None
                last_facelets = None
                continue

    return records


def report(records, mode_filter=None, top=30):
    if mode_filter:
        records = [r for r in records if r["mode"] == mode_filter]

    total = len(records)
    with_state = [r for r in records if r["facelets"]]
    missing = total - len(with_state)

    print("=" * 72)
    print("打乱状态统计分析")
    print("=" * 72)
    if mode_filter:
        print(f"模式过滤: {mode_filter}")
    print(f"solve 事件总数      : {total}")
    print(f"含状态(solve 前抓到) : {len(with_state)}")
    print(f"缺失状态            : {missing}")

    # 各模式统计
    by_mode = Counter(r["mode"] for r in records)
    print("\n-- 各模式 solve 次数 --")
    for mode, cnt in by_mode.most_common():
        print(f"  {mode:<10} {cnt}")

    if not with_state:
        return

    # 状态去重
    state_first = {}
    state_records = defaultdict(list)
    for r in with_state:
        fl = r["facelets"]
        state_records[fl].append(r)
        if fl not in state_first:
            state_first[fl] = r

    unique = len(state_records)
    solved_recs = state_records.get(SOLVED, [])
    print("\n-- 唯一性 --")
    print(f"不同状态数          : {unique}")
    print(f"唯一率              : {unique / len(with_state):.2%}")
    print(f"已复原状态(solved)  : {len(solved_recs)} 次")

    dup_states = {s: rs for s, rs in state_records.items() if len(rs) > 1}
    dup_total = sum(len(rs) for rs in dup_states.values())
    print(f"重复状态(出现≥2次)  : {len(dup_states)} 种，共 {dup_total} 次")

    # 按天汇总（重复次数 = 当日属于“重复状态”的 solve 总次数）
    day_stat = defaultdict(lambda: {"total": 0, "dup": 0, "states": set()})
    skipped = 0
    for r in with_state:
        dt = _parse_ts(r["ts"])
        if dt is None:
            skipped += 1
            continue
        key = dt.strftime("%Y-%m-%d")
        d = day_stat[key]
        d["total"] += 1
        d["states"].add(r["facelets"])
        if r["facelets"] in dup_states:
            d["dup"] += 1

    if day_stat:
        print("\n-- 按天重复汇总（按日期升序）--")
        print(f"  {'日期':<12}{'总solve':>8}{'重复次数':>10}{'重复率':>9}{'不同状态':>10}")
        tot_all = tot_dup = 0
        for day in sorted(day_stat):
            d = day_stat[day]
            rate = d["dup"] / d["total"] if d["total"] else 0.0
            print(f"  {day:<12}{d['total']:>8}{d['dup']:>10}{rate:>8.1%}{len(d['states']):>10}")
            tot_all += d["total"]
            tot_dup += d["dup"]
        overall = tot_dup / tot_all if tot_all else 0.0
        print(f"  {'合计':<12}{tot_all:>8}{tot_dup:>10}{overall:>8.1%}")
        if skipped:
            print(f"  （跳过无时间戳记录 {skipped} 条，未计入上表）")

    if dup_states:
        print(f"\n-- 重复最多的状态 TOP {top} --")
        for s, rs in sorted(dup_states.items(), key=lambda kv: -len(kv[1]))[:top]:
            modes = Counter(r["mode"] for r in rs)
            steps = sorted({r["steps"] for r in rs})
            tag = " [SOLVED]" if s == SOLVED else ""
            print(f"  x{len(rs):<3} steps={steps} modes={dict(modes)}{tag}")
            print(f"       {s}")
            for r in rs[:3]:
                print(f"       - {r['ts']} line={r['line']} ({r['mode']})")
            if len(rs) > 3:
                print(f"       - ... 其余 {len(rs) - 3} 次")

    # 步数分布
    steps_all = [r["steps"] for r in with_state]
    print("\n-- 解法步数分布 --")
    print(f"  最小 {min(steps_all)} / 最大 {max(steps_all)} / 平均 {sum(steps_all)/len(steps_all):.1f}")
    hist = Counter(steps_all)
    for lo in range(0, max(steps_all) + 1, 10):
        chunk = sum(v for k, v in hist.items() if lo <= k < lo + 10)
        if chunk:
            bar = "#" * min(chunk // max(1, len(steps_all) // 60), 60)
            print(f"  {lo:>3}-{lo+9:<3}: {chunk:>5} {bar}")


def plot_repeats(records, mode_filter=None, bucket="day"):
    """弹窗显示“重复现象”随时间的分布（不区分具体是哪种状态）。

    三张子图：
      1. 重复散点时间线：每个 solve 一个点，重复状态红色高亮、唯一状态灰色。
      2. 单位时间重复率曲线：每桶内“重复状态 solve 数 / 总 solve 数”。
      3. 重复间隔直方图：同一状态相邻两次出现的时间间隔分布（对数 X 轴）。
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np

    # 中文字体（Windows 常见 CJK 字体）
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei", "SimHei", "SimSun", "Microsoft JhengHei", "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False

    if mode_filter:
        records = [r for r in records if r["mode"] == mode_filter]

    # 附加解析时间
    have = []
    for r in records:
        dt = _parse_ts(r["ts"])
        if dt is not None and r["facelets"]:
            r["_dt"] = dt
            have.append(r)
    if not have:
        print("无可用带时间戳的记录，跳过绘图。")
        return
    have.sort(key=lambda r: r["_dt"])

    # 判定重复：该状态在全量中出现 >= 2 次
    state_cnt = Counter(r["facelets"] for r in have)
    for r in have:
        r["_dup"] = state_cnt[r["facelets"]] >= 2

    n = len(have)
    dts = np.array([mdates.date2num(r["_dt"]) for r in have])
    dup_mask = np.array([r["_dup"] for r in have])

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12))

    # ---- 图 1：重复散点时间线 ----
    uniq_idx = np.where(~dup_mask)[0]
    dup_idx = np.where(dup_mask)[0]
    ax1.scatter(dts[uniq_idx], uniq_idx, s=3, c="lightgray", label="唯一状态", rasterized=True)
    ax1.scatter(dts[dup_idx], dup_idx, s=4, c="crimson", label="重复状态", rasterized=True)
    ax1.set_title(f"重复现象时间线（红=该状态在全程出现≥2次）  共 {n} 次 solve，重复 {int(dup_mask.sum())} 次")
    ax1.set_ylabel("solve 序号")
    ax1.legend(loc="upper left", markerscale=3)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate(rotation=30, ha="right")

    # ---- 图 2：单位时间重复率曲线 ----
    fmt = "%Y-%m-%d" if bucket == "day" else "%Y-%m-%d %H"
    buckets = defaultdict(lambda: [0, 0])
    for r in have:
        key = r["_dt"].strftime(fmt)
        buckets[key][0] += 1
        if r["_dup"]:
            buckets[key][1] += 1
    keys = sorted(buckets)
    bk_dt = [datetime.strptime(k, fmt) for k in keys]
    totals = np.array([buckets[k][0] for k in keys])
    dups = np.array([buckets[k][1] for k in keys])
    rates = dups / np.maximum(totals, 1)
    ax2.plot(bk_dt, rates, "-o", markersize=3, color="darkorange")
    ax2.scatter(bk_dt, rates, s=totals * 2, color="darkorange", alpha=0.3)
    ax2.set_title(f"单位时间重复率曲线（点大小=该桶 solve 总数，桶粒度={bucket}）")
    ax2.set_ylabel("重复率")
    ax2.set_ylim(0, 1.05)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    if bucket == "hour":
        ax2.xaxis.set_major_locator(mdates.DayLocator())
    fig.autofmt_xdate(rotation=30, ha="right")

    # ---- 图 3：重复间隔直方图 ----
    seen = defaultdict(list)
    for r in have:
        seen[r["facelets"]].append(r["_dt"])
    gaps_min = []
    for s, ts_list in seen.items():
        if len(ts_list) < 2:
            continue
        for a, b in zip(ts_list, ts_list[1:]):
            gaps_min.append((b - a).total_seconds() / 60.0)
    if gaps_min:
        gaps_min = np.array(gaps_min)
        bins = np.logspace(np.log10(max(gaps_min.min(), 1e-2)), np.log10(gaps_min.max()), 40)
        ax3.hist(gaps_min, bins=bins, color="steelblue", alpha=0.8)
        ax3.set_xscale("log")
        ax3.set_title(f"同一状态相邻两次出现的时间间隔分布（共 {len(gaps_min)} 对相邻重复）")
        ax3.set_xlabel("间隔（分钟，对数轴）")
        ax3.set_ylabel("频次")
        ax3.grid(True, alpha=0.3, which="both")
        med = np.median(gaps_min)
        ax3.axvline(med, color="crimson", linestyle="--", label=f"中位数 {med:.1f} min")
        ax3.legend()
    else:
        ax3.set_title("无相邻重复（每个状态仅出现一次）")

    plt.tight_layout()
    plt.show()


def main():
    ap = argparse.ArgumentParser(description="从 controller.log 统计打乱状态")
    ap.add_argument("--log", default=DEFAULT_LOG, help="日志路径")
    ap.add_argument("--mode", default=None, help="只统计某模式 (rank/team/week/holder/remote)")
    ap.add_argument("--top", type=int, default=30, help="重复状态显示条数")
    ap.add_argument("--plot", action="store_true", help="弹窗显示重复随时间分布图")
    ap.add_argument("--bucket", choices=["day", "hour"], default="day", help="重复率时间桶粒度")
    args = ap.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        raise SystemExit(f"日志不存在: {log_path}")

    records = parse(log_path)
    report(records, mode_filter=args.mode, top=args.top)
    if args.plot:
        plot_repeats(records, mode_filter=args.mode, bucket=args.bucket)


if __name__ == "__main__":
    main()
