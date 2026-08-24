"""CSV 数据清理 —— 去除前 10s 脏陀螺仪数据，用初始 facelet + move 推演校准期状态

用法：
    python -m tools.clean_csv data/proxy/20260822_0.csv --dry-run      # 预览
    python -m tools.clean_csv data/proxy/20260822_0.csv --in-place     # 覆盖原文件
    python -m tools.clean_csv data/proxy/v1/*.csv --in-place           # 批量清理旧数据
"""
import argparse
import csv
import glob
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from device.ble_cube import apply_move_state, cp_co_ep_eo_to_facelets

CALIB_SEC = 10.0

# 54 面片串的转动置换（Kociemba 顺序 URFDLB）
# 用 solve 状态 + apply_move_state 自动生成各面的置换表
def _build_perm_tables():
    solved_cp = list(range(8))
    solved_co = [0] * 8
    solved_ep = list(range(12))
    solved_eo = [0] * 12
    labels = [chr(65 + i) for i in range(54)]
    solved_str = "".join(labels)

    def cp_co_ep_eo_labels(cp, co, ep, eo, labels):
        CORNER_FACELET = [[8,9,20],[6,18,38],[0,36,47],[2,45,11],[29,26,15],[27,44,24],[33,53,42],[35,17,51]]
        CORNER_COLOR = [[0,1,2],[0,2,4],[0,4,5],[0,5,1],[3,2,1],[3,4,2],[3,5,4],[3,1,5]]
        EDGE_FACELET = [[5,10],[7,19],[3,37],[1,46],[32,16],[28,25],[30,43],[34,52],[23,12],[21,41],[50,39],[48,14]]
        EDGE_COLOR = [[0,1],[0,2],[0,4],[0,5],[3,1],[3,2],[3,4],[3,5],[2,1],[2,4],[5,4],[5,1]]
        CENTER_FACELET = [4,13,22,31,40,49]
        f = [""] * 54
        for i in range(6):
            f[CENTER_FACELET[i]] = labels[i * 9 + 4]
        for i in range(8):
            j = cp[i]; ori = co[i]
            for k in range(3):
                # 在 moved 状态中，cubie i 的 sticker k 位于位置 p
                p = CORNER_FACELET[j][(k + ori) % 3]
                # 在 solved 状态中，cubie i 的 sticker k 位于位置 CORNER_FACELET[i][k]
                # 其标签为 labels[CORNER_COLOR[i][k] * 9 + (CORNER_FACELET[i][k] % 9)]
                src = CORNER_FACELET[i][k]
                fi = CORNER_COLOR[i][k]
                f[p] = labels[fi * 9 + (src % 9)]
        for i in range(12):
            j = ep[i]; ori = eo[i]
            for k in range(2):
                p = EDGE_FACELET[j][(k + ori) % 2]
                src = EDGE_FACELET[i][k]
                fi = EDGE_COLOR[i][k]
                f[p] = labels[fi * 9 + (src % 9)]
        return "".join(f)

    tables = {}
    for face in range(6):
        for dir in [0, 1]:
            cp, co, ep, eo = apply_move_state(solved_cp, solved_co, solved_ep, solved_eo, face, dir)
            moved = cp_co_ep_eo_labels(cp, co, ep, eo, labels)
            perm = [solved_str.index(moved[i]) for i in range(54)]
            tables[(face, dir)] = perm
    return tables

_PERM = _build_perm_tables()


def apply_move_facelets(fl: str, face: int, dir: int) -> str:
    perm = _PERM[(face, dir)]
    return "".join(fl[perm[i]] for i in range(54))


def clean_file(path: str, dry_run: bool = False) -> int:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for r in reader:
            rows.append(r)

    if not rows:
        return 0

    t0 = datetime.fromisoformat(rows[0]["timestamp"])
    t_calib = t0 + timedelta(seconds=CALIB_SEC)

    # 找到第一个 facelets 行初始化状态，然后用 move 推演
    fl_state = None
    for r in rows:
        if r["type"] == "facelets" and r.get("facelets") and len(r["facelets"]) == 54:
            fl_state = r["facelets"]
            break

    # 校准期内的 move 推演
    if fl_state is not None:
        for r in rows:
            ts = datetime.fromisoformat(r["timestamp"])
            if ts >= t_calib:
                break
            if r["type"] == "move":
                face = int(r["face"])
                direction = int(r["dir"])
                fl_state = apply_move_facelets(fl_state, face, direction)

    cleaned = []
    skipped = 0
    facelet_written = False
    for r in rows:
        ts = datetime.fromisoformat(r["timestamp"])
        if r["type"] == "gyro" and ts < t_calib:
            skipped += 1
            continue
        # 在校准结束时刻插入一个正确的 facelets 行
        if not facelet_written and fl_state is not None and ts >= t_calib:
            facelet_row = {
                "timestamp": t_calib.isoformat(timespec="microseconds"),
                "type": "facelets",
                "face": "", "dir": "", "qw": "", "qx": "", "qy": "", "qz": "",
                "vx": "", "vy": "", "vz": "", "facelets": fl_state,
            }
            cleaned.append(facelet_row)
            facelet_written = True
        cleaned.append(r)

    if dry_run:
        print(f"  {Path(path).name}: {len(rows)}行 → {len(cleaned)}行 (跳过{skipped}个gyro, 插入facelets)")
        return 0

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(cleaned)
    print(f"  {Path(path).name}: {len(rows)}行 → {len(cleaned)}行 (跳过{skipped}个gyro, 插入facelets)")
    return len(cleaned)


def main():
    parser = argparse.ArgumentParser(description="清理 CSV 前 10s 脏陀螺仪数据")
    parser.add_argument("path", help="CSV 文件路径或 glob 模式")
    parser.add_argument("--dry-run", action="store_true", help="预览，不修改文件")
    parser.add_argument("--in-place", action="store_true", help="覆盖原文件")
    args = parser.parse_args()

    paths = sorted(glob.glob(args.path, recursive=True))
    if not paths:
        print(f"未找到文件: {args.path}")
        sys.exit(1)

    total = 0
    for p in paths:
        total += clean_file(p, dry_run=args.dry_run or not args.in_place)

    mode = "预览" if (args.dry_run or not args.in_place) else "已清理"
    print(f"\n{mode} {len(paths)} 个文件, {total} 行")


if __name__ == "__main__":
    main()