"""训练入口 —— 训练/评估/可视化魔方姿态预测模型

用法：
    python -m train.train --data "data/proxy/20260816_*.csv"              # 训练
    python -m train.train --data "data/proxy/20260816_*.csv" --resume     # 续训
    python -m train.train --eval --ckpt checkpoints/model.pt              # 评估
    python -m train.train --data "data/proxy/20260816_*.csv" --viz-data  # 训练后可视化
"""
import argparse
import logging
import math
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from train.dataset import build_datasets, build_dataloaders
from train.model import QuatTransformer
from train.loss import compute_losses

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("train")


def train_epoch(model, loader, optimizer, scheduler, device, epoch, chunk_size=8):
    model.train()
    total_loss = 0.0
    total_angle = 0.0
    n_batches = 0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        delta_6d = model(batch["event_ids"], batch["gyros"], batch.get("facelets"))
        losses = compute_losses(delta_6d, batch, event_weight=3.0, proximity_radius=8, chunk_size=chunk_size)
        optimizer.zero_grad()
        losses["loss"].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += losses["loss"].item()
        total_angle += losses["angle_error"].item()
        n_batches += 1
    if scheduler:
        scheduler.step()
    avg_loss = total_loss / n_batches
    avg_angle = total_angle / n_batches
    logger.info("Epoch %d: train loss=%.4f  angle=%.2f°",
                epoch, avg_loss, avg_angle)
    return avg_loss, avg_angle


@torch.no_grad()
def eval_epoch(model, loader, device, epoch, chunk_size=8):
    model.eval()
    total_loss = 0.0
    total_angle = 0.0
    n_batches = 0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        delta_6d = model(batch["event_ids"], batch["gyros"], batch.get("facelets"))
        losses = compute_losses(delta_6d, batch, event_weight=3.0, proximity_radius=8, chunk_size=chunk_size)
        total_loss += losses["loss"].item()
        total_angle += losses["angle_error"].item()
        n_batches += 1
    avg_loss = total_loss / n_batches
    avg_angle = total_angle / n_batches
    logger.info("Epoch %d: val loss=%.4f  angle=%.2f°",
                epoch, avg_loss, avg_angle)
    return avg_loss, avg_angle


def main():
    parser = argparse.ArgumentParser(description="魔方姿态预测训练")
    parser.add_argument("--data", default="data/proxy/20260816_*.csv",
                        help="CSV 文件 glob 模式")
    parser.add_argument("--seq-len", type=int, default=128,
                        help="序列长度 (默认 128)")
    parser.add_argument("--stride", type=int, default=32,
                        help="验证集采样步长 (默认 32)")
    parser.add_argument("--batch-size", type=int, default=32,
                        help="批次大小 (默认 32)")
    parser.add_argument("--epochs", type=int, default=200,
                        help="训练轮数 (默认 200)")
    parser.add_argument("--lr", type=float, default=1e-4,
                        help="学习率 (默认 1e-4)")
    parser.add_argument("--d-model", type=int, default=128,
                        help="模型维度 (默认 128)")
    parser.add_argument("--nhead", type=int, default=8,
                        help="注意力头数 (默认 8)")
    parser.add_argument("--num-layers", type=int, default=6,
                        help="Decoder 层数 (默认 6)")
    parser.add_argument("--checkpoint-dir", default="checkpoints",
                        help="模型保存目录 (默认 checkpoints)")
    parser.add_argument("--resume", action="store_true",
                        help="从 checkpoint 续训")
    parser.add_argument("--eval", action="store_true",
                        help="评估模式")
    parser.add_argument("--ckpt", default=None,
                        help="评估/可视化用的 checkpoint 路径")
    parser.add_argument("--viz-data", action="store_true",
                        help="训练后可视化预测结果")
    parser.add_argument("--no-augment", action="store_true",
                        help="禁用数据增强")
    parser.add_argument("--pretrain-epochs", type=int, default=20,
                        help="预训练轮数（只含事件窗口，默认 20）")
    parser.add_argument("--chunk-size", type=int, default=8,
                        help="Action chunk 大小（默认 8）")
    parser.add_argument("--event-ratio", type=float, default=0.5,
                        help="训练时事件窗口采样比例（默认 0.5）")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("设备: %s", device)

    # 加载数据
    logger.info("加载数据: %s", args.data)
    total_epochs = args.epochs
    pretrain_epochs = args.pretrain_epochs

    # Stage 1: 预训练（只含事件窗口）
    if pretrain_epochs > 0:
        logger.info("=== Stage 1: 预训练（仅事件窗口）===")
        pt_train_ds, pt_val_ds, _ = build_datasets(
            args.data, seq_len=args.seq_len, stride=args.stride,
            augment=not args.no_augment, pretrain=True, event_ratio=args.event_ratio,
        )
        pt_train_loader, pt_val_loader, _ = build_dataloaders(
            pt_train_ds, pt_val_ds, None, batch_size=args.batch_size,
        )
        logger.info("预训练样本数: %d", len(pt_train_ds))

        model = QuatTransformer(
            d_model=args.d_model, nhead=args.nhead,
            num_layers=args.num_layers, seq_len=args.seq_len,
        ).to(device)
        param_count = sum(p.numel() for p in model.parameters())
        logger.info("模型参数量: %.2fM", param_count / 1e6)

        optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=pretrain_epochs, eta_min=1e-5,
        )

        for epoch in range(pretrain_epochs):
            t0 = time.time()
            train_loss, train_angle = train_epoch(
                model, pt_train_loader, optimizer, scheduler, device, epoch, chunk_size=args.chunk_size)
            if pt_val_loader:
                val_loss, val_angle = eval_epoch(
                    model, pt_val_loader, device, epoch, chunk_size=args.chunk_size)
            logger.info("  time=%.1fs  lr=%.2e", time.time() - t0, optimizer.param_groups[0]["lr"])

        # 保存预训练模型
        ckpt_dir = Path(args.checkpoint_dir)
        ckpt_dir.mkdir(exist_ok=True)
        torch.save(model.state_dict(), ckpt_dir / "pretrain.pt")
        logger.info("预训练完成，模型已保存")

    # Stage 2: 微调（全量数据）
    logger.info("=== Stage 2: 微调（全量数据）===")
    train_ds, val_ds, test_ds = build_datasets(
        args.data, seq_len=args.seq_len, stride=args.stride,
        augment=not args.no_augment, pretrain=False, event_ratio=args.event_ratio,
    )
    train_loader, val_loader, _ = build_dataloaders(
        train_ds, val_ds, test_ds, batch_size=args.batch_size,
    )
    logger.info("微调样本数: %d", len(train_ds))

    if pretrain_epochs == 0:
        model = QuatTransformer(
            d_model=args.d_model, nhead=args.nhead,
            num_layers=args.num_layers, seq_len=args.seq_len,
        ).to(device)
        param_count = sum(p.numel() for p in model.parameters())
        logger.info("模型参数量: %.2fM", param_count / 1e6)

    ckpt_dir = Path(args.checkpoint_dir)
    ckpt_dir.mkdir(exist_ok=True)
    ckpt_path = ckpt_dir / "model.pt"

    start_epoch = 0
    best_val_loss = float("inf")

    if args.resume and ckpt_path.exists():
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        logger.info("已恢复 checkpoint: %s", ckpt_path)
        # 尝试加载训练状态
        state_path = ckpt_dir / "train_state.pt"
        if state_path.exists():
            state = torch.load(state_path, map_location=device)
            start_epoch = state.get("epoch", 0) + 1
            best_val_loss = state.get("best_val_loss", float("inf"))
            logger.info("从 epoch %d 续训", start_epoch)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=1e-5,
    )

    logger.info("开始训练, %d epochs", args.epochs)
    for epoch in range(start_epoch, args.epochs):
        t0 = time.time()
        train_loss, train_angle = train_epoch(
            model, train_loader, optimizer, scheduler, device, epoch, chunk_size=args.chunk_size)

        val_loss, val_angle = eval_epoch(
            model, val_loader, device, epoch, chunk_size=args.chunk_size) if val_loader else (0, 0)

        elapsed = time.time() - t0
        logger.info("  time=%.1fs  lr=%.2e", elapsed, optimizer.param_groups[0]["lr"])

        # 保存最佳模型
        if val_loader and val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), ckpt_path)
            torch.save({
                "epoch": epoch,
                "best_val_loss": best_val_loss,
            }, ckpt_dir / "train_state.pt")
            logger.info("  ✓ 保存最佳模型 (val_loss=%.4f)", val_loss)

    # 最终保存
    if not val_loader:
        torch.save(model.state_dict(), ckpt_path)
        logger.info("训练完成，模型已保存: %s", ckpt_path)

    if args.viz_data:
        visualize_prediction(model, train_ds, device, args)


def visualize_prediction(model, dataset, device, args):
    """可视化预测结果与真实轨迹对比"""
    try:
        import matplotlib.pyplot as plt
        from tools.viz_data import animate_3d
    except ImportError as e:
        logger.error("可视化需要 matplotlib: %s", e)
        return

    model.eval()
    # 从验证集取一个样本
    sample = dataset[0]
    batch = {k: v.unsqueeze(0).to(device) for k, v in sample.items()}

    with torch.no_grad():
        delta_6d = model(batch["event_ids"], batch["gyros"], batch.get("facelets"))

    # 重建预测姿态
    from train.utils import rotm_to_quat, quat_multiply, gram_schmidt
    B, T = delta_6d.shape[:2]
    u1, u2 = delta_6d[..., :3], delta_6d[..., 3:]
    R_pred = gram_schmidt(u1, u2)
    pred_delta_q = rotm_to_quat(R_pred)
    gt_quats = batch["quats"].cpu()
    pred_quats = [F.normalize(gt_quats[:, 0], dim=-1)]
    for t in range(1, T):
        q = F.normalize(quat_multiply(pred_quats[-1].to(device), pred_delta_q[:, t]), dim=-1)
        pred_quats.append(q)
    pred_quats = torch.stack(pred_quats, dim=1).cpu().squeeze(0).numpy()

    gt = gt_quats.squeeze(0).numpy()
    n = min(T, 500)
    ticks = np.arange(n)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    ax1.plot(ticks, gt[:n, 0], label="gt_qw", linewidth=0.8)
    ax1.plot(ticks, gt[:n, 1], label="gt_qx", linewidth=0.8)
    ax1.plot(ticks, gt[:n, 2], label="gt_qy", linewidth=0.8)
    ax1.plot(ticks, gt[:n, 3], label="gt_qz", linewidth=0.8, linestyle="--")
    ax1.set_title("Ground Truth Quaternion")
    ax1.legend(ncol=4, fontsize=8)
    ax1.grid(True, alpha=0.3)

    ax2.plot(ticks, pred_quats[:n, 0], label="pred_qw", linewidth=0.8)
    ax2.plot(ticks, pred_quats[:n, 1], label="pred_qx", linewidth=0.8)
    ax2.plot(ticks, pred_quats[:n, 2], label="pred_qy", linewidth=0.8)
    ax2.plot(ticks, pred_quats[:n, 3], label="pred_qz", linewidth=0.8, linestyle="--")
    ax2.set_title("Predicted Quaternion")
    ax2.legend(ncol=4, fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()