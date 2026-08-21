"""损失函数 —— 姿态预测损失 + 事件近邻加权"""
import torch
import torch.nn.functional as F

from train.utils import quat_geodesic, quat_to_6d, quat_delta, quat_multiply, quat_conjugate, gram_schmidt


def _proximity_mask(event_ids: torch.Tensor, radius: int) -> torch.Tensor:
    """事件附近 radius 个 tick 置 1，其余 0，用 1D 卷积膨胀"""
    B, T = event_ids.shape
    if radius <= 0:
        return event_ids.float()
    kernel = torch.ones(1, 1, 2 * radius + 1, device=event_ids.device, dtype=torch.float32)
    expanded = F.conv1d(event_ids.float().unsqueeze(1), kernel, padding=radius).squeeze(1)
    return (expanded > 0).float()


def compute_losses(pred_delta_6d: torch.Tensor, batch: dict,
                   alpha: float = 1.0, beta: float = 0.1,
                   event_weight: float = 3.0, proximity_radius: int = 8) -> dict:
    B, T = batch["quats"].shape[:2]
    gt_quats = batch["quats"]
    event_ids = batch["event_ids"]

    # GT 增量四元数
    gt_delta_q = quat_delta(gt_quats[:, :-1], gt_quats[:, 1:])
    identity = torch.zeros_like(gt_quats[:, :1])
    identity[..., 0] = 1.0
    gt_delta_q = torch.cat([identity, gt_delta_q], dim=1)

    # 预测 6D → 四元数
    u1, u2 = pred_delta_6d[..., :3], pred_delta_6d[..., 3:]
    u1 = u1 + 1e-8
    u2 = u2 + 1e-8
    R_pred = gram_schmidt(u1, u2)
    from train.utils import rotm_to_quat
    pred_delta_q = rotm_to_quat(R_pred)

    # 重建绝对姿态
    pred_quats = [F.normalize(gt_quats[:, 0], dim=-1)]
    for t in range(1, T):
        q = F.normalize(quat_multiply(pred_quats[-1], pred_delta_q[:, t]), dim=-1)
        pred_quats.append(q)
    pred_quats = torch.stack(pred_quats, dim=1)

    # 事件近邻权重
    mask = _proximity_mask(event_ids, proximity_radius)  # [B, T]
    weight = 1.0 + event_weight * mask                   # [B, T]

    # 1. Geodesic Loss（加权）
    dot = (pred_quats * gt_quats).sum(dim=-1).abs().clamp(max=1.0 - 1e-7)
    geo_per_tick = 2 * torch.acos(dot)                   # [B, T]
    L_geo = (geo_per_tick * weight).sum() / weight.sum()

    # 2. 6D MSE Loss（加权）
    gt_delta_6d = quat_to_6d(gt_delta_q)
    mse_per_tick = (pred_delta_6d - gt_delta_6d).pow(2).mean(dim=-1)  # [B, T]
    L_6d = (mse_per_tick * weight).sum() / weight.sum()

    total = alpha * L_geo + beta * L_6d

    return {
        "loss": total,
        "L_geo": L_geo.detach(),
        "L_6d": L_6d.detach(),
        "angle_error": (L_geo.detach() * 180.0 / 3.14159),
    }