"""推理脚本 —— 加载模型，滑窗预测姿态，对比 GT 并 3D 动画展示

用法：
    python -m train.infer --ckpt checkpoints/model.pt --csv data/proxy/20260822_0.csv
    python -m train.infer --ckpt checkpoints/pretrain.pt --csv data/proxy/20260822_0.csv --start 0 --end 500
    python -m train.infer --ckpt checkpoints/model.pt --csv data/proxy/20260822_0.csv --no-animate
"""
import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from train.model import QuatTransformer
from train.utils import (
    gram_schmidt, quat_multiply, quat_geodesic, rotm_to_quat,
)
from tools.viz_data import load_csv, tick_align, extract_arrays

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("infer")


def load_model(ckpt_path: str, device: str, d_model=128, nhead=8, num_layers=6, seq_len=128):
    model = QuatTransformer(d_model, nhead, num_layers, seq_len).to(device)
    state = torch.load(ckpt_path, map_location=device)
    if "model_state_dict" in state:
        state = state["model_state_dict"]
    model.load_state_dict(state, strict=False)
    model.eval()
    return model


def sliding_predict(model, event_ids, gyros, facelets, init_quat, device, context=128, chunk=8):
    """滑窗推理，返回预测四元数轨迹 [T, 4]
    
    chunk=8 -> 模型输出 8 个 delta，其中 delta[0]=identity, delta[1..7] 是实际增量
    滑窗步长 = chunk-1 = 7
    """
    T = event_ids.shape[0]
    step = chunk - 1  # 实际增量数
    trajectory = []
    current_q = F.normalize(init_quat.to(device), dim=-1)
    trajectory.append(current_q.cpu().numpy())

    for t in range(0, T - step, step):
        end = min(t + context, T)
        if end - t < context:
            break
        ctx = slice(t, end)
        ei = event_ids[ctx].unsqueeze(0).to(device)
        gy = gyros[ctx].unsqueeze(0).to(device)
        fl = facelets[ctx].unsqueeze(0).to(device) if facelets is not None else None

        with torch.no_grad():
            delta_6d = model(ei, gy, fl)  # [1, context, 6]
        # delta[0] = identity, delta[1..step] = 实际增量
        for d in range(1, step + 1):
            u1, u2 = delta_6d[0, d, :3], delta_6d[0, d, 3:]
            R = gram_schmidt(u1 + 1e-8, u2 + 1e-8)
            q_delta = rotm_to_quat(R.unsqueeze(0)).squeeze(0)
            current_q = F.normalize(quat_multiply(current_q, q_delta), dim=-1)
            trajectory.append(current_q.cpu().numpy())

    return np.array(trajectory)


def main():
    parser = argparse.ArgumentParser(description="魔方姿态预测推理")
    parser.add_argument("--ckpt", default="checkpoints/model.pt", help="模型 checkpoint 路径")
    parser.add_argument("--csv", default=None, help="CSV 数据文件路径")
    parser.add_argument("--start", type=int, default=0, help="起始 tick")
    parser.add_argument("--end", type=int, default=None, help="结束 tick")
    parser.add_argument("--no-animate", action="store_true", help="不显示 3D 动画")
    parser.add_argument("--d-model", type=int, default=128, help="模型维度")
    parser.add_argument("--nhead", type=int, default=8, help="注意力头数")
    parser.add_argument("--num-layers", type=int, default=6, help="Decoder 层数")
    parser.add_argument("--seq-len", type=int, default=128, help="上下文长度")
    parser.add_argument("--chunk-size", type=int, default=8, help="预测步数")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("设备: %s", device)

    # 加载模型
    model = load_model(args.ckpt, device, args.d_model, args.nhead, args.num_layers, args.seq_len)
    logger.info("模型加载完成: %s", args.ckpt)

    if not args.csv:
        logger.error("需要 --csv 数据文件")
        sys.exit(1)

    # 加载 CSV
    rows = load_csv(args.csv)
    tick_data, ticks = tick_align(rows)
    data = extract_arrays(tick_data, ticks)
    n = len(data["event_ids"])
    logger.info("数据: %d ticks", n)

    # 提取 facelets
    from train.dataset import build_datasets
    ds, _, _ = build_datasets(args.csv, seq_len=args.seq_len, stride=args.seq_len, pretrain=False)
    # 用第一个样本的 facelets 作为参考
    facelets = None
    if ds.trajectories:
        traj = ds.trajectories[0]
        facelets = traj["facelets"]  # [T, 54], -1=unknown

    # 切片
    start = args.start
    end = args.end or n
    sl = slice(start, end)
    event_ids = data["event_ids"][sl]
    gyros = np.stack([data["vx"][sl], data["vy"][sl], data["vz"][sl]], axis=1)
    gt_quats = np.stack([data["qw"][sl], data["qx"][sl], data["qy"][sl], data["qz"][sl]], axis=1)
    fl = facelets[sl] if facelets is not None else None

    T = len(event_ids)
    logger.info("推理窗口: %d ~ %d (%d ticks)", start, end, T)

    # 滑窗推理
    init_quat = torch.from_numpy(gt_quats[0]).float()
    pred_quats = sliding_predict(
        model, torch.from_numpy(event_ids).long(),
        torch.from_numpy(gyros).float(),
        torch.from_numpy(fl).long() if fl is not None else None,
        init_quat, device, args.seq_len, args.chunk_size,
    )

    # 对齐长度
    min_len = min(len(pred_quats), len(gt_quats))
    pred_quats = pred_quats[:min_len]
    gt_quats = gt_quats[:min_len]

    # 计算角度误差
    pq = torch.from_numpy(pred_quats).float()
    gq = torch.from_numpy(gt_quats).float()
    errors = quat_geodesic(pq, gq).numpy()  # 弧度
    errors_deg = np.degrees(errors)
    logger.info("")
    logger.info("=== 预测 vs 真实 角度误差 ===")
    logger.info("  mean:   %.2f deg", np.mean(errors_deg))
    logger.info("  median: %.2f deg", np.median(errors_deg))
    logger.info("  p90:    %.2f deg", np.percentile(errors_deg, 90))
    logger.info("  min:    %.2f deg", np.min(errors_deg))
    logger.info("  max:    %.2f deg", np.max(errors_deg))

    # 3D 动画对比
    if not args.no_animate:
        import cv2
        from tools.gan_proxy import _render_cube, _quat_to_gravity

        cv2.namedWindow("预测 vs 真实", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("预测 vs 真实", 900, 500)
        yaw = 0.0
        idx = 0
        paused = False
        while idx < min_len:
            img_p = _render_cube(float(pred_quats[idx][0]), float(pred_quats[idx][1]),
                                 float(pred_quats[idx][2]), float(pred_quats[idx][3]),
                                 size=500, view_yaw=yaw)
            img_g = _render_cube(float(gt_quats[idx][0]), float(gt_quats[idx][1]),
                                 float(gt_quats[idx][2]), float(gt_quats[idx][3]),
                                 size=500, view_yaw=yaw)
            # 拼接
            img = np.concatenate([img_p, img_g], axis=1)
            cv2.putText(img, f"预测", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"真实", (510, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"error={errors_deg[idx]:.1f}deg  tick={idx+start}", (10, 470),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
            if paused:
                cv2.putText(img, "PAUSED", (400, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow("预测 vs 真实", img)
            key = cv2.waitKeyEx(60 if not paused else 100)
            if key == ord("q") or key == 27:
                break
            elif key == 2555904:  # →
                yaw += 0.15
            elif key == 2424832:  # ←
                yaw -= 0.15
            elif key == ord(" "):
                paused = not paused
            if not paused:
                idx += 1
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()