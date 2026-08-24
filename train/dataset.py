"""数据集 —— 加载 CSV → tick 对齐 → 滑窗采样"""
import glob
import logging
import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from tools.viz_data import load_csv, tick_align, extract_arrays

logger = logging.getLogger(__name__)

EVENT_NAMES = {
    0: "·", 1: "U", 2: "U'", 3: "R", 4: "R'",
    5: "F", 6: "F'", 7: "D", 8: "D'",
    9: "L", 10: "L'", 11: "B", 12: "B'",
}


def load_trajectory(csv_path: str) -> dict:
    """加载单个 CSV 文件为 tick 对齐后的轨迹数组"""
    rows = load_csv(csv_path)
    tick_data, ticks = tick_align(rows)
    data = extract_arrays(tick_data, ticks)
    n = len(ticks)

    # 提取 facelets
    facelets = np.full((n, 54), -1, dtype=np.int64)
    facelet_rows = [r for r in rows if r["type"] == "facelets" and r.get("facelets")]
    tick_idx = 0
    for r in facelet_rows:
        ts = r["ts"]
        while tick_idx < len(ticks) - 1 and ts >= ticks[tick_idx + 1]:
            tick_idx += 1
        best = tick_idx
        if tick_idx + 1 < len(ticks):
            d1 = abs((ts - ticks[tick_idx]).total_seconds())
            d2 = abs((ts - ticks[tick_idx + 1]).total_seconds())
            if d2 < d1:
                best = tick_idx + 1
        fl = r["facelets"]
        if len(fl) == 54:
            from train.utils import facelets_to_idx
            facelets[best] = facelets_to_idx(fl)
    # forward-fill
    last = None
    for i in range(n):
        if facelets[i, 0] >= 0:
            last = facelets[i].copy()
        elif last is not None:
            facelets[i] = last

    return {
        "event_ids": data["event_ids"].astype(np.int64),
        "gyros": np.stack([data["vx"], data["vy"], data["vz"]], axis=1).astype(np.float32),
        "quats": np.stack([data["qw"], data["qx"], data["qy"], data["qz"]], axis=1).astype(np.float32),
        "facelets": facelets,  # [T, 54] int64, -1=unknown
        "n_ticks": len(ticks),
    }


class CubeDataset(Dataset):
    """滑窗采样数据集

    每个 epoch 随机采样窗口起始位置（验证集固定 stride 采样）。
    pretrain=True 时只采样包含事件的窗口。
    """

    def __init__(self, trajectories: list[dict], seq_len: int = 128,
                 stride: int = 32, is_train: bool = True,
                 augment: bool = True, pretrain: bool = False,
                 event_ratio: float = 0.5):
        self.trajectories = trajectories
        self.seq_len = seq_len
        self.stride = stride
        self.is_train = is_train
        self.augment = augment and is_train
        self.pretrain = pretrain
        self.event_ratio = event_ratio if pretrain else event_ratio
        # 预计算每个轨迹的窗口
        self._windows: list[tuple[int, int]] = []  # (traj_idx, start)
        self._event_windows: list[tuple[int, int]] = []
        self._static_windows: list[tuple[int, int]] = []
        for traj_idx, traj in enumerate(trajectories):
            n = traj["n_ticks"]
            if n < seq_len:
                continue
            event_ids = traj["event_ids"]
            if is_train:
                for s in range(0, max(1, n - seq_len + 1), max(1, stride // 4)):
                    if np.any(event_ids[s:s+seq_len] > 0):
                        self._event_windows.append((traj_idx, s))
                    else:
                        self._static_windows.append((traj_idx, s))
            else:
                for s in range(0, n - seq_len + 1, stride):
                    if pretrain and not np.any(event_ids[s:s+seq_len] > 0):
                        continue
                    self._windows.append((traj_idx, s))

        if pretrain and is_train:
            # 预训练模式：只采样包含事件的窗口
            self.event_ratio = 1.0
            if not self._event_windows:
                raise ValueError("预训练模式没有找到包含事件的窗口，请检查数据")
        elif is_train and not self._event_windows:
            # 训练但无事件窗口时退化为普通采样
            self.event_ratio = 0.0
            if not self._static_windows:
                raise ValueError("没有可用的训练窗口，请检查数据")
        elif not is_train and not self._windows:
            raise ValueError("没有可用的验证窗口，请检查数据")

    def __len__(self) -> int:
        if self.is_train and self._event_windows:
            return len(self._event_windows) + len(self._static_windows)
        return len(self._windows)

    def __getitem__(self, idx: int) -> dict:
        if self.is_train and self._event_windows:
            if random.random() < self.event_ratio:
                traj_idx, start = random.choice(self._event_windows)
            else:
                traj_idx, start = random.choice(self._static_windows or self._event_windows)
        else:
            traj_idx, start = self._windows[idx]
        traj = self.trajectories[traj_idx]
        end = start + self.seq_len

        event_ids = traj["event_ids"][start:end].copy()
        gyros = traj["gyros"][start:end].copy()
        quats = traj["quats"][start:end].copy()
        facelets = traj["facelets"][start:end].copy()

        # 数据增强
        if self.augment:
            event_ids, gyros, quats, facelets = self._augment(event_ids, gyros, quats, facelets)

        return {
            "event_ids": torch.from_numpy(event_ids).long(),       # [T]
            "gyros": torch.from_numpy(gyros).float(),               # [T, 3]
            "quats": torch.from_numpy(quats).float(),               # [T, 4]
            "facelets": torch.from_numpy(facelets).long(),          # [T, 54]
        }

    def _augment(self, event_ids, gyros, quats, facelets=None):
        # 时间反转 (50%)
        if random.random() < 0.5:
            event_ids = event_ids[::-1].copy()
            gyros = gyros[::-1].copy()
            quats = quats[::-1].copy()
            if facelets is not None:
                facelets = facelets[::-1].copy()
            # 反转事件: U↔U', R↔R', 即奇数↔偶数
            rev = event_ids.copy()
            for eid in range(1, 13, 2):
                rev[event_ids == eid] = eid + 1
                rev[event_ids == eid + 1] = eid
            event_ids = rev
            gyros = -gyros

        # 事件抖动 (±1 tick, 20%)
        if random.random() < 0.2:
            shift = random.choice([-1, 1])
            event_ids = np.roll(event_ids, shift)
            if shift == 1:
                event_ids[0] = 0
            else:
                event_ids[-1] = 0

        # 事件丢弃 (20%)
        if random.random() < 0.2:
            drop_mask = np.random.random(len(event_ids)) < 0.2
            event_ids[drop_mask] = 0

        # 角速度噪声 (±1, 30%)
        if random.random() < 0.3:
            gyros += np.random.randint(-1, 2, size=gyros.shape).astype(np.float32)
            gyros = gyros.clip(-8, 7)

        return event_ids, gyros, quats, facelets


def build_datasets(csv_pattern: str, seq_len: int = 128, stride: int = 32,
                   train_ratio: float = 0.7, val_ratio: float = 0.2,
                   augment: bool = True, pretrain: bool = False,
                   event_ratio: float = 0.5) -> tuple[CubeDataset, CubeDataset, CubeDataset]:
    """加载 CSV 文件，拆分训练/验证/测试集"""
    csv_paths = sorted(glob.glob(csv_pattern))
    if not csv_paths:
        raise FileNotFoundError(f"未找到 CSV 文件: {csv_pattern}")
    logger.info("加载 %d 个 CSV 文件: %s", len(csv_paths), csv_paths)

    trajectories = []
    for path in csv_paths:
        try:
            traj = load_trajectory(path)
            trajectories.append(traj)
            logger.info("  %s: %d ticks", Path(path).name, traj["n_ticks"])
        except Exception as e:
            logger.warning("  跳过 %s: %s", path, e)

    if not trajectories:
        raise ValueError("没有有效的轨迹数据")

    n = len(trajectories)
    n_train = max(1, int(n * train_ratio))
    n_val = max(1, int(n * val_ratio))
    n_test = max(0, n - n_train - n_val)

    # 按文件顺序拆分（保留时间顺序）
    train_trajs = trajectories[:n_train]
    val_trajs = trajectories[n_train:n_train + n_val]
    test_trajs = trajectories[n_train + n_val:] if n_test > 0 else []

    train_ds = CubeDataset(train_trajs, seq_len, stride, is_train=True, augment=augment, pretrain=pretrain, event_ratio=event_ratio)
    val_ds = CubeDataset(val_trajs, seq_len, stride, is_train=False, augment=False, pretrain=False) if val_trajs else None
    test_ds = CubeDataset(test_trajs, seq_len, stride, is_train=False, augment=False, pretrain=False) if test_trajs else None

    logger.info("训练: %d 轨迹, %d 样本", len(train_trajs), len(train_ds))
    if val_ds:
        logger.info("验证: %d 轨迹, %d 样本", len(val_trajs), len(val_ds))
    if test_ds:
        logger.info("测试: %d 轨迹, %d 样本", len(test_trajs), len(test_ds))

    return train_ds, val_ds, test_ds


def build_dataloaders(train_ds, val_ds, test_ds, batch_size: int = 32,
                      num_workers: int = 0):
    """构建 DataLoader"""
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            num_workers=num_workers, pin_memory=True) if val_ds else None
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                             num_workers=num_workers, pin_memory=True) if test_ds else None
    return train_loader, val_loader, test_loader