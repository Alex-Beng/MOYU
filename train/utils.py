"""旋转工具函数 —— 6D 表示 ↔ 四元数 ↔ 旋转矩阵"""
import torch
import torch.nn.functional as F


def gram_schmidt(u1: torch.Tensor, u2: torch.Tensor) -> torch.Tensor:
    """6D → 旋转矩阵 [B, T, 3, 3]"""
    a1 = F.normalize(u1, dim=-1)
    v = u2 - (a1 * u2).sum(dim=-1, keepdim=True) * a1
    a2 = F.normalize(v, dim=-1)
    a3 = torch.cross(a1, a2, dim=-1)
    return torch.stack([a1, a2, a3], dim=-1)


def rotm_to_quat(R: torch.Tensor) -> torch.Tensor:
    """旋转矩阵 [B, T, 3, 3] → 四元数 [B, T, 4] (w, x, y, z)"""
    orig_shape = R.shape
    R = R.reshape(-1, 3, 3)
    N = R.shape[0]
    q = torch.zeros(N, 4, device=R.device, dtype=R.dtype)

    trace = R[:, 0, 0] + R[:, 1, 1] + R[:, 2, 2]
    s = torch.sqrt((trace + 1.0).clamp(min=1e-8)) * 2
    q[:, 0] = 0.25 * s
    q[:, 1] = (R[:, 2, 1] - R[:, 1, 2]) / s
    q[:, 2] = (R[:, 0, 2] - R[:, 2, 0]) / s
    q[:, 3] = (R[:, 1, 0] - R[:, 0, 1]) / s

    return F.normalize(q.reshape(*orig_shape[:-2], 4), dim=-1)


def quat_to_rotm(q: torch.Tensor) -> torch.Tensor:
    """四元数 [B, T, 4] → 旋转矩阵 [B, T, 3, 3]"""
    q = F.normalize(q, dim=-1)
    w, x, y, z = q.unbind(-1)
    x2, y2, z2 = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    R = torch.stack([
        torch.stack([1 - 2*(y2 + z2), 2*(xy - wz), 2*(xz + wy)], dim=-1),
        torch.stack([2*(xy + wz), 1 - 2*(x2 + z2), 2*(yz - wx)], dim=-1),
        torch.stack([2*(xz - wy), 2*(yz + wx), 1 - 2*(x2 + y2)], dim=-1),
    ], dim=-2)
    return R


def quat_to_6d(q: torch.Tensor) -> torch.Tensor:
    """四元数 [B, T, 4] → 6D 旋转表示 [B, T, 6]"""
    R = quat_to_rotm(q)
    return torch.cat([R[..., 0], R[..., 1]], dim=-1)


def quat_multiply(q1: torch.Tensor, q2: torch.Tensor) -> torch.Tensor:
    """四元数乘法 q1 * q2 [B, T, 4]"""
    w1, x1, y1, z1 = q1.unbind(-1)
    w2, x2, y2, z2 = q2.unbind(-1)
    return torch.stack([
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ], dim=-1)


def quat_conjugate(q: torch.Tensor) -> torch.Tensor:
    """四元数共轭 [B, T, 4]"""
    return q * torch.tensor([1, -1, -1, -1], device=q.device, dtype=q.dtype)


def quat_delta(q_from: torch.Tensor, q_to: torch.Tensor) -> torch.Tensor:
    """计算相对旋转: q_from → q_to 的增量四元数 [B, T, 4]"""
    return quat_multiply(q_to, quat_conjugate(q_from))


def quat_geodesic(q_pred: torch.Tensor, q_gt: torch.Tensor) -> torch.Tensor:
    """计算角度误差 (弧度) [B, T]"""
    dot = (q_pred * q_gt).sum(dim=-1).abs().clamp(max=1.0)
    return 2 * torch.acos(dot)


def sixd_to_quat(u1: torch.Tensor, u2: torch.Tensor) -> torch.Tensor:
    """6D 表示 → 四元数 [B, T, 4]"""
    R = gram_schmidt(u1, u2)
    return rotm_to_quat(R)