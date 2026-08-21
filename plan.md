QIYI = Quantized Inertial Yaw Inference

魔方姿态预测系统 — 技术方案文档

1. 项目概述
1.1 背景
魔方固件以 60ms 固定间隔 上报数据，每个 tick 包含：

事件信息（Move）：12 种面转动指令之一

陀螺仪数据（Gyro）：四元数姿态 + 3轴角速度（4-bit signed nibble，范围 -8 ~ +7）

1.2 目标
输入初始姿态 + 事件序列，预测未来每个 tick 的姿态四元数轨迹。

1.3 问题本质
这是一个 事件驱动的时序预测问题：

输入：离散事件序列 + 离散角速度信号

输出：连续姿态轨迹（6D 旋转表示 → 四元数）

关键挑战：事件与姿态变化之间存在未知延迟（机械响应时间），需由网络从数据中学习

2. 数据规格
2.1 采样特性
参数	规格
采样间隔	60ms（固定）
数据对齐	以 Gyro 时间戳为锚点构建 60ms 网格，Move 归到最近的 Gyro tick
上报规则	Gyro 每 ~60ms 独立推送；Move 为事件驱动，独立推送
2.2 输入数据
字段	类型	范围	说明
事件 ID	离散（整数）	0 = 无事件，1-12 = 12种面转动	每个 tick 至多一个事件。编码：face×2+dir+1
角速度 X	离散（整数）	-8 ~ +7	4-bit signed nibble，角速度原始值
角速度 Y	离散（整数）	-8 ~ +7	同上
角速度 Z	离散（整数）	-8 ~ +7	同上
初始姿态	四元数（连续）	模长 = 1	推理时由用户指定

事件编码表：
编码	含义
0	本 tick 无事件（仅 gyro，无 move）
1	U  (face=0, dir=0)
2	U' (face=0, dir=1)
3	R  (face=1, dir=0)
4	R' (face=1, dir=1)
5	F  (face=2, dir=0)
6	F' (face=2, dir=1)
7	D  (face=3, dir=0)
8	D' (face=3, dir=1)
9	L  (face=4, dir=0)
10	L' (face=4, dir=1)
11	B  (face=5, dir=0)
12	B' (face=5, dir=1)
2.3 输出数据
字段	类型	说明
姿态轨迹	四元数序列 [T, 4]	每个 tick 的绝对姿态，模长归一化
3. 方法
3.1 核心思路
采用 Action Chunking Transformer 范式，将问题建模为：

条件 → 一次性预测未来 T 个 tick 的姿态增量序列（Action Chunk）

条件（Condition）：历史事件序列 + 角速度序列

动作块（Action Chunk）：未来 T 个 tick 的姿态增量（6D 旋转表示）

递推方式：从初始姿态开始，逐步累乘增量得到绝对姿态轨迹

3.2 为什么采用 Action Chunk 方式？
对比项	逐帧预测	Action Chunk（本方案）
时序一致性	差（帧间抖动）	优（一次性生成完整块）
延迟影响	累积误差大	块内误差可相互补偿
平滑性	需额外强约束	Transformer 自注意力天然捕捉依赖
推理效率	逐帧前向传播	一次前向传播得到多帧
4. 模型架构
4.1 总体结构
输入层：

事件 ID (0-12) → Embedding(13 → d_model)

角速度 (-8~+7) → 归一化到 [-1,1] → Linear(3 → d_model)

相加 → 进入 Transformer

Decoder-Only Transformer：

Positional Encoding（可学习）

Transformer Decoder × N Layers

Causal Self-Attention（只看历史）

Feed-Forward Network

输出: [B, T, d_model]

输出层：

MLP Head: d_model → 128 → 64 → 6

6D 旋转表示 [B, T, 6]

Gram-Schmidt 正交化 → 旋转矩阵 [B, T, 3, 3]

四元数 [B, T, 4]（L2 归一化）

4.2 6D 旋转表示原理
为什么用 6D 而非四元数？

表示方式	维度	约束问题	训练稳定性
四元数	4	模长约束 + q/-q 二义性	低
欧拉角	3	万向锁 + 周期性	低
轴角	3	0°/360° 不连续	中
6D 表示	6	无约束，正交化可微	高
数学原理：

旋转矩阵 R ∈ SO(3) 的前两列（6 个数值）唯一决定了整个旋转矩阵，第三列由叉积得到：

R = [a1, a2, a3], a3 = a1 × a2

网络输出 6 个数值 u1, u2，通过 Gram-Schmidt 正交化映射到合法旋转矩阵：

a1 = u1 / ||u1||
v = u2 - (a1 · u2) · a1
a2 = v / ||v||
a3 = a1 × a2

整个过程完全可微，梯度可正常回传。

4.3 输入特征融合
每个 tick 的输入特征构建：

事件 ID (0-12) → Embedding(d_model)
角速度 (-8~+7) → 归一化到 [-1,1] → Linear(d_model)
→ 相加 → 进入 Transformer

角速度归一化公式（范围 -8 ~ +7）：

gyro_norm = gyro_raw / 7.0（范围 ≈ [-1.14, +1.0]）

4.4 预测与姿态重建
推理输入: init_quat + event_ids [T] + gyros [T, 3]
→ 网络输出: delta_6d [T, 6]（每帧相对于上一帧的姿态增量）
→ 逐帧累乘:
current = init_quat
for t in 1..T:
delta_quat = 6D_to_quat(delta_6d[t])
current = quat_multiply(current, delta_quat)
trajectory[t] = current

5. 损失函数
5.1 损失组成
Total Loss = α · L_geodesic + β · L_6d_mse + γ · L_smooth + δ · L_event

5.2 各分量说明
5.2.1 Geodesic Loss（主损失）
计算预测姿态与真实姿态之间的角度差：

L_geodesic = arccos(|q_pred · q_gt|)

点积取绝对值解决 q/-q 二义性

物理意义明确（角度误差）

5.2.2 6D MSE Loss（辅助损失）
网络输出直接与 GT 的 6D 表示做 MSE：

L_6d_mse = MSE(pred_6d, gt_6d)

梯度直达输出层，加速收敛

给网络明确的数值目标

5.2.3 Smoothness Loss（平滑约束）
惩罚相邻帧之间的加速度（二阶差分），强制轨迹平滑：

L_smooth = mean(||(quat_{t+1} - quat_t) - (quat_t - quat_{t-1})||²)

5.2.4 Event-Weighted Loss（事件响应约束）
根据事件掩码动态调整约束：

L_event = mean(weight_t · smoothness_t)
where weight_t = 1.0 if event at t else 0.1

有事件时：允许姿态跳变

无事件时：强制姿态稳定

5.3 推荐权重
参数	推荐值
α (Geodesic)	1.0
β (6D MSE)	0.1
γ (Smoothness)	0.1
δ (Event)	0.2
6. 训练策略
6.1 数据预处理流程
原始日志 (timestamp, move_id, gyro_quat, gyro_xyz)
→ 以 Gyro 时间戳为锚点构建 60ms 网格，每个 Move 归到最近 Gyro tick
→ 构建滑动窗口样本 (seq_len = 100-200 ticks)
→ 训练/验证/测试拆分 (7:2:1)

6.2 数据增强
增强方法	说明
时间反转	将事件序列倒序，模拟反向转动
事件抖动	事件时间戳 ±1 tick，模拟时间同步误差
事件丢弃	随机删除 20% 事件，模拟漏检
角速度噪声	添加 ±1 量化噪声，增强鲁棒性
6.3 超参数
参数	建议值	说明
seq_len	100-200	每个样本的 tick 数
d_model	128	Transformer 隐藏维度
nhead	8	注意力头数
num_layers	6	Decoder 层数
batch_size	32-64	根据 GPU 内存调整
learning_rate	1e-3	AdamW 优化器
weight_decay	0.01	正则化
grad_clip	1.0	梯度裁剪阈值
6.4 训练监控指标
指标	说明
Geodesic Loss	主损失，持续下降
平均角度误差	验证集上的姿态精度
事件响应延迟	事件发生后姿态开始变化的帧数
平滑度	无事件段的抖动幅度
7. 推理部署
7.1 输入输出接口
推理输入:

init_quat: [4] float32，初始姿态四元数

event_ids: [T] int，事件 ID 序列

gyros: [T, 3] int，角速度原始值 (-8 ~ +7)

推理输出:

quat_trajectory: [T, 4] float32，预测的姿态轨迹

7.2 流式推理流程
初始化:

姿态缓存 current_quat = init_quat

历史窗口缓存（保存最近 N 个 tick 的事件和角速度）

每个 Tick:

接收当前 tick 的事件 ID 和角速度

更新历史窗口

如果窗口已满：
a. 构造输入张量 [1, N] 事件ID + [1, N, 3] 角速度
b. 模型前向推理，得到 [1, T, 6] 增量
c. 取第一个增量，累乘到 current_quat
d. 输出 current_quat

否则：等待窗口填满

7.3 性能要求
指标	目标值
单 tick 推理延迟	< 50ms（60ms 间隔内完成）
模型参数量	< 10M
姿态精度	平均角度误差 < 5°
7.4 加速优化
KV Cache：缓存历史帧的 Key/Value，增量推理时只需计算新帧

模型量化：INT8 量化减小模型体积和延迟

ONNX 导出：便于跨平台部署

8. 风险与应对
风险	影响	应对措施
数据量不足	模型欠拟合	增加数据增强；使用更小模型
事件过于稀疏	模型只会预测"保持不变"	平衡数据集中的事件密度分布
延迟不一致	模型混乱	确保数据采集时机械状态一致；加入时间抖动增强
过拟合到特定操作者	泛化差	收集多用户数据；增加操作模式增强
角速度 4-bit 量化噪声	精度受限	使用平滑滤波；Embedding 方式可能比数值归一化更好
9. 数据可视化工具

9.1 工具：tools/viz_data.py

读取 CSV 数据，按 Gyro 锚点对齐到 60ms tick 网格，绘制时序图或播放 3D 动画。

用法：
    python -m tools.viz_data data/proxy/20260816_10.csv                # 静态时序图
    python -m tools.viz_data data/proxy/20260816_10.csv --animate       # 3D 立方体动画
    python -m tools.viz_data data/proxy/20260816_10.csv --start 0 --end 500  # 切片
    python -m tools.viz_data data/proxy/20260816_10.csv --no-tick       # 原始数据，不 tick 对齐

9.2 静态时序图（matplotlib）

双轴图：
- 上图：四元数 qw/qx/qy/qz 时序曲线，move 事件以竖线标记
- 下图：角速度 vx/vy/vz 时序曲线

9.3 3D 动画（OpenCV）

复用 tools/gan_proxy.py 的 _render_cube + _quat_to_rotm，逐帧播放。
窗口底部显示当前 tick 的 move 事件和角速度值。

9.4 依赖

- matplotlib（已有）
- numpy（已有）
- opencv-python（已有）
10. 后续优化方向
Diffusion Policy：用扩散模型替代 Transformer，处理多模态动作分布

MoE 结构：针对不同转动阶段使用不同专家网络

物理约束嵌入：在 Loss 中加入角速度/角加速度物理上限约束

在线微调：部署后根据真实观测值持续微调模型

11. 参考文献
Zhao et al., "Action Chunking Transformer for Imitation Learning", 2023

Zhou et al., "On the Continuity of Rotation Representations in Neural Networks", CVPR 2019

Chi et al., "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion", RSS 2023

Radosavovic et al., "Real-World Robot Learning with Masked Visual Pre-training", CoRL 2023

12. 数据规模与采集建议

12.1 当前数据量

指标	数值
有效 CSV 文件	9 个
总 tick 数	~43,000
事件 tick 数	~8,678（20%）
训练样本（seq=128）	915
模型参数	1.63M
参数/样本比	~1,780:1

12.2 建议数据量

训练样本	事件 tick	预计采集时间
2,000	~20,000	~2 小时 solve
5,000	~50,000	~5 小时 solve
10,000	~100,000	~10 小时 solve

12.3 采集方法

使用 tools/gan_proxy.py 收集数据：

    python -m tools.gan_proxy --host 192.168.50.246

将魔方连接至 ESP32 并正常进行 solve 操作，脚本会自动记录转动和陀螺仪到 CSV。

12.4 数据多样性建议

- 不同操作者：多人操作，增加操作风格多样性
- 不同转速：有快有慢，覆盖不同角速度范围
- 不同解法：CFOP、ZZ、Roux 等不同解法（不同事件序列模式）
- 不同魔方：如果可能，用不同魔方型号采集

文档版本: 1.2
最后更新: 2026-08-17

