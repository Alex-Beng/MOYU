"""数据可视化工具 —— 读取 CSV，绘制四元数+角速度时序图或播放 3D 动画

用法：
    python -m tools.viz_data data/proxy/20260816_10.csv                # 静态时序图
    python -m tools.viz_data data/proxy/20260816_10.csv --animate       # 3D 立方体动画
    python -m tools.viz_data data/proxy/20260816_10.csv --start 0 --end 500  # 切片
    python -m tools.viz_data data/proxy/20260816_10.csv --no-tick       # 原始数据，不 tick 对齐
"""
import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from tools.gan_proxy import _render_cube, _quat_to_rotm, _quat_to_gravity

EVENT_NAMES = {
    0: "·",
    1: "U", 2: "U'", 3: "R", 4: "R'",
    5: "F", 6: "F'", 7: "D", 8: "D'",
    9: "L", 10: "L'", 11: "B", 12: "B'",
}


def load_csv(path: str) -> dict:
    """加载 CSV，返回结构化数据"""
    rows = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    # 解析时间戳
    for r in rows:
        r["ts"] = datetime.fromisoformat(r["timestamp"])
    # 按时间排序
    rows.sort(key=lambda r: r["ts"])
    return rows


def tick_align(rows, start_ts=None, tick_ms=60):
    """以 gyro 为锚点构建 60ms tick 网格，每个 move 归到最近 gyro tick"""
    # 提取所有 gyro 时间戳
    gyro_rows = [r for r in rows if r["type"] == "gyro"]
    if not gyro_rows:
        return rows
    if start_ts is None:
        start_ts = gyro_rows[0]["ts"]
    # 构建 tick 网格
    end_ts = gyro_rows[-1]["ts"]
    tick_delta = timedelta(milliseconds=tick_ms)
    ticks = []
    ts = start_ts
    while ts <= end_ts:
        ticks.append(ts)
        ts += tick_delta
    # 双指针分配：每个 move 归到最近 gyro tick
    tick_idx = 0
    tick_data = {t: {"gyro": None, "move": None} for t in ticks}
    for r in rows:
        ts = r["ts"]
        # 推进 tick_idx 直到 ts 在当前 tick 和下一个 tick 之间
        while tick_idx < len(ticks) - 1 and ts >= ticks[tick_idx + 1]:
            tick_idx += 1
        # 比较当前 tick 和下一个 tick，选更近的
        best = tick_idx
        if tick_idx + 1 < len(ticks):
            d1 = abs((ts - ticks[tick_idx]).total_seconds())
            d2 = abs((ts - ticks[tick_idx + 1]).total_seconds())
            if d2 < d1:
                best = tick_idx + 1
        if r["type"] == "gyro":
            tick_data[ticks[best]]["gyro"] = r
        elif r["type"] == "move":
            tick_data[ticks[best]]["move"] = r
    return tick_data, ticks


def extract_arrays(tick_data, ticks):
    """从 tick 数据中提取数组用于绘图"""
    n = len(ticks)
    qw = np.zeros(n)
    qx = np.zeros(n)
    qy = np.zeros(n)
    qz = np.zeros(n)
    vx = np.zeros(n)
    vy = np.zeros(n)
    vz = np.zeros(n)
    event_ids = np.zeros(n, dtype=int)
    move_ticks = []
    move_labels = []
    last_q = [0.0, 0.0, 0.0, 1.0]
    for i, t in enumerate(ticks):
        d = tick_data[t]
        if d["gyro"]:
            r = d["gyro"]
            qw[i] = float(r["qw"]) if r["qw"] else last_q[0]
            qx[i] = float(r["qx"]) if r["qx"] else last_q[1]
            qy[i] = float(r["qy"]) if r["qy"] else last_q[2]
            qz[i] = float(r["qz"]) if r["qz"] else last_q[3]
            last_q = [qw[i], qx[i], qy[i], qz[i]]
            vx[i] = int(r["vx"]) if r["vx"] else 0
            vy[i] = int(r["vy"]) if r["vy"] else 0
            vz[i] = int(r["vz"]) if r["vz"] else 0
        else:
            qw[i], qx[i], qy[i], qz[i] = last_q
        if d["move"]:
            face = int(d["move"]["face"])
            direction = int(d["move"]["dir"])
            event_ids[i] = face * 2 + direction + 1
            move_ticks.append(i)
            move_labels.append(EVENT_NAMES.get(event_ids[i], "?"))
    return {
        "ticks": np.arange(n),
        "qw": qw, "qx": qx, "qy": qy, "qz": qz,
        "vx": vx, "vy": vy, "vz": vz,
        "event_ids": event_ids,
        "move_ticks": move_ticks,
        "move_labels": move_labels,
        "timestamps": ticks,
    }


def plot_static(data, start=0, end=None):
    """绘制静态时序图（matplotlib）"""
    import matplotlib.pyplot as plt

    n = len(data["ticks"])
    if end is None:
        end = n
    sl = slice(start, end)
    ticks = data["ticks"][sl]
    qw = data["qw"][sl]
    qx = data["qx"][sl]
    qy = data["qy"][sl]
    qz = data["qz"][sl]
    vx = data["vx"][sl]
    vy = data["vy"][sl]
    vz = data["vz"][sl]
    move_ticks = [i - start for i in data["move_ticks"] if start <= i < end]
    move_labels = [data["move_labels"][j] for j, i in enumerate(data["move_ticks"]) if start <= i < end]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # 上图：四元数
    ax1.plot(ticks, qw, label="qw", linewidth=0.8)
    ax1.plot(ticks, qx, label="qx", linewidth=0.8)
    ax1.plot(ticks, qy, label="qy", linewidth=0.8)
    ax1.plot(ticks, qz, label="qz", linewidth=0.8)
    for mt, ml in zip(move_ticks, move_labels):
        ax1.axvline(x=ticks[mt] if isinstance(ticks, np.ndarray) else mt,
                    color="red", linestyle="--", alpha=0.5, linewidth=0.8)
        ax1.text(ticks[mt] if isinstance(ticks, np.ndarray) else mt,
                 ax1.get_ylim()[1], ml, fontsize=8, color="red",
                 ha="center", va="bottom")
    ax1.set_ylabel("Quaternion")
    ax1.legend(loc="upper right", ncol=4, fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Quaternion & Angular Velocity Timeline")

    # 下图：角速度
    ax2.plot(ticks, vx, label="vx", linewidth=0.8)
    ax2.plot(ticks, vy, label="vy", linewidth=0.8)
    ax2.plot(ticks, vz, label="vz", linewidth=0.8)
    for mt in move_ticks:
        ax2.axvline(x=ticks[mt] if isinstance(ticks, np.ndarray) else mt,
                    color="red", linestyle="--", alpha=0.5, linewidth=0.8)
    ax2.set_xlabel("Tick")
    ax2.set_ylabel("Angular Velocity")
    ax2.legend(loc="upper right", ncol=3, fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def animate_3d(data, start=0, end=None, tick_ms=60):
    """3D 立方体动画（OpenCV）"""
    n = len(data["ticks"])
    if end is None:
        end = n
    sl = slice(start, end)
    qw = data["qw"][sl]
    qx = data["qx"][sl]
    qy = data["qy"][sl]
    qz = data["qz"][sl]
    event_ids = data["event_ids"][sl]
    move_ticks = [i - start for i in data["move_ticks"] if start <= i < end]
    move_labels = [data["move_labels"][j] for j, i in enumerate(data["move_ticks"]) if start <= i < end]

    import cv2
    cv2.namedWindow("Data Animation", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Data Animation", 500, 500)
    idx = 0
    paused = False
    while idx < len(qw):
        if not paused:
            img = _render_cube(qw[idx], qx[idx], qy[idx], qz[idx], size=500)
            # 显示事件信息
            eid = event_ids[idx]
            if eid > 0:
                label = EVENT_NAMES.get(eid, "?")
                cv2.putText(img, f"Move: {label}", (8, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(img, f"Tick {idx + start}/{end - 1}", (8, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
            cv2.imshow("Data Animation", img)
            key = cv2.waitKey(tick_ms) & 0xFF
            if key == ord("q") or key == 27:
                break
            elif key == ord(" "):
                paused = not paused
            idx += 1
        else:
            key = cv2.waitKey(100) & 0xFF
            if key == ord(" "):
                paused = not paused
            elif key == ord("q") or key == 27:
                break
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="CSV 数据可视化")
    parser.add_argument("csv", help="CSV 文件路径")
    parser.add_argument("--animate", action="store_true", help="3D 立方体动画")
    parser.add_argument("--start", type=int, default=0, help="起始 tick")
    parser.add_argument("--end", type=int, default=None, help="结束 tick")
    parser.add_argument("--no-tick", action="store_true", help="不按 tick 对齐，直接显示原始数据")
    args = parser.parse_args()

    path = Path(args.csv)
    if not path.exists():
        print(f"文件不存在: {args.csv}")
        sys.exit(1)

    print(f"加载数据: {args.csv}")
    rows = load_csv(str(path))
    print(f"总行数: {len(rows)}")

    if args.no_tick:
        # 原始数据模式：直接按行索引绘图
        # 构建简单数组
        n = len(rows)
        data = {
            "ticks": np.arange(n),
            "qw": np.zeros(n), "qx": np.zeros(n), "qy": np.zeros(n), "qz": np.zeros(n),
            "vx": np.zeros(n), "vy": np.zeros(n), "vz": np.zeros(n),
            "event_ids": np.zeros(n, dtype=int),
            "move_ticks": [], "move_labels": [],
            "timestamps": [r["ts"] for r in rows],
        }
        for i, r in enumerate(rows):
            if r["type"] == "gyro":
                data["qw"][i] = float(r["qw"]) if r["qw"] else 0
                data["qx"][i] = float(r["qx"]) if r["qx"] else 0
                data["qy"][i] = float(r["qy"]) if r["qy"] else 0
                data["qz"][i] = float(r["qz"]) if r["qz"] else 0
                data["vx"][i] = int(r["vx"]) if r["vx"] else 0
                data["vy"][i] = int(r["vy"]) if r["vy"] else 0
                data["vz"][i] = int(r["vz"]) if r["vz"] else 0
            elif r["type"] == "move":
                face = int(r["face"])
                direction = int(r["dir"])
                eid = face * 2 + direction + 1
                data["event_ids"][i] = eid
                data["move_ticks"].append(i)
                data["move_labels"].append(EVENT_NAMES.get(eid, "?"))
        print(f"  move: {len(data['move_ticks'])}  gyro: {n - len(data['move_ticks'])}")
    else:
        tick_data, ticks = tick_align(rows)
        data = extract_arrays(tick_data, ticks)
        print(f"  tick 数: {len(ticks)}")
        print(f"  move: {len(data['move_ticks'])}  gyro: {len(ticks)}")

    if args.animate:
        animate_3d(data, start=args.start, end=args.end)
    else:
        plot_static(data, start=args.start, end=args.end)


if __name__ == "__main__":
    main()