"""Decoder-Only Transformer 魔方姿态预测模型"""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from train.utils import gram_schmidt, quat_multiply, quat_conjugate


class QuatTransformer(nn.Module):
    """输入事件序列 + 角速度 + 面片 → 输出 6D 姿态增量（残差形式，初始化为 identity）"""

    def __init__(self, d_model: int = 128, nhead: int = 8,
                 num_layers: int = 6, seq_len: int = 128,
                 dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.seq_len = seq_len

        self.event_embed = nn.Embedding(13, d_model, padding_idx=0)
        self.gyro_proj = nn.Linear(3, d_model)
        self.facelet_embed = nn.Embedding(7, d_model, padding_idx=0)  # 0=未知, 1-6=URFDLB
        self.pos_embed = nn.Parameter(torch.randn(1, seq_len, d_model) * 0.02)

        layer = nn.TransformerDecoderLayer(
            d_model, nhead, dim_feedforward=d_model * 4,
            dropout=dropout, batch_first=True, norm_first=True,
        )
        self.decoder = nn.TransformerDecoder(layer, num_layers)

        self.head = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 6),
        )

        # 残差偏置：identity 6D 表示 [u1, u2] = [[1,0,0], [0,1,0]]
        self.register_buffer('identity_6d', torch.tensor([1.0, 0.0, 0.0, 0.0, 1.0, 0.0]))

        self._init_weights()

    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p, gain=0.5)
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, event_ids: torch.Tensor, gyros: torch.Tensor,
                facelets: torch.Tensor | None = None) -> torch.Tensor:
        B, T = event_ids.shape
        x = self.event_embed(event_ids)                     # [B, T, d_model]
        gyro_norm = gyros / 7.0
        x = x + self.gyro_proj(gyro_norm)                   # [B, T, d_model]
        if facelets is not None:
            fl = (facelets + 1).clamp(min=0, max=6)         # -1→0, 0→1, ..., 5→6
            fl_emb = self.facelet_embed(fl)                  # [B, T, 54, d_model]
            x = x + fl_emb.sum(dim=-2)                       # [B, T, d_model]
        x = x + self.pos_embed[:, :T, :]                    # [B, T, d_model]
        causal_mask = torch.triu(torch.full((T, T), float('-inf')), diagonal=1).to(x.device)
        x = self.decoder(x, x, tgt_mask=causal_mask)        # [B, T, d_model]
        residual = self.head(x)                              # [B, T, 6]
        delta_6d = self.identity_6d + residual               # [B, T, 6]
        return delta_6d


class QuatPredictor:
    """推理封装：从初始姿态 + 事件序列逐步预测姿态轨迹"""

    def __init__(self, model: QuatTransformer, device: str = "cuda"):
        self.model = model.to(device).eval()
        self.device = device

    @torch.no_grad()
    def predict(self, init_quat: torch.Tensor,
                event_ids: torch.Tensor,
                gyros: torch.Tensor) -> torch.Tensor:
        B, T = event_ids.shape
        delta_6d = self.model(event_ids.to(self.device), gyros.to(self.device))
        u1, u2 = delta_6d[..., :3], delta_6d[..., 3:]

        # 逐步累乘
        trajectory = []
        current = F.normalize(init_quat.to(self.device), dim=-1)
        for t in range(T):
            R = gram_schmidt(u1[:, t], u2[:, t])
            R_flat = R.reshape(-1, 9)
            # 从旋转矩阵提取四元数
            q_delta = self._rotm_to_quat_simple(R[:, t])
            current = F.normalize(quat_multiply(current, q_delta), dim=-1)
            trajectory.append(current)

        return torch.stack(trajectory, dim=1)  # [B, T, 4]

    @staticmethod
    def _rotm_to_quat_simple(R):
        trace = R[:, 0, 0] + R[:, 1, 1] + R[:, 2, 2]
        q = torch.zeros(R.shape[0], 4, device=R.device)
        s = torch.sqrt(trace.clamp(min=0) + 1.0) * 2
        q[:, 0] = 0.25 * s
        q[:, 1] = (R[:, 2, 1] - R[:, 1, 2]) / s
        q[:, 2] = (R[:, 0, 2] - R[:, 2, 0]) / s
        q[:, 3] = (R[:, 1, 0] - R[:, 0, 1]) / s
        return F.normalize(q, dim=-1)