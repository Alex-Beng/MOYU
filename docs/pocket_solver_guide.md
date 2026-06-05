# 二阶魔方求解器使用指南

## 概述

二阶魔方（Pocket Cube）求解器专门针对仅使用 R、U、F 三个面转动的场景设计，适用于三轴机械臂控制的二阶魔方。

## 特性

- **RUF 限定**：仅使用 R（右）、U（上）、F（前）三个面的转动
- **求解方法**：简化版 Ortega 方法
  - 第一层（First Layer）：使底层同色
  - 定向顶层（OLL）：使顶层同色
  - 排列顶层（PBL）：完成求解
- **搜索算法**：BFS + 预定义算法库

## 使用方法

### 1. Python API

```python
from solve import solve_pocket

# facelet_str 为 54 字符的三阶魔方格式面片字符串
# 格式：UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB
facelet_str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

result = solve_pocket(facelet_str)

if result:
    print(f"完整解法: {result['solution']}")
    print(f"第一层: {result['first_layer']}")
    print(f"OLL: {result['oll']}")
    print(f"PBL: {result['pbl']}")
else:
    print("求解失败")
```

### 2. 命令行

```bash
# 从 ESP32 获取魔方状态并求解
python3 solve/solve.py 192.168.4.1 --method pocket

# 求解并发送到设备执行
python3 solve/solve.py 192.168.4.1 --method pocket --send
```

### 3. 直接使用 PocketCube 类

```python
from solve.pocket_solver import PocketCube, PocketSolver

# 创建已复原状态
cube = PocketCube.solved()

# 应用打乱
cube.apply_moves_str("R U R' U' F R U R' U' F'")

# 检查状态
print(f"是否复原: {cube.is_solved()}")
print(f"角块位置: {cube.cp}")
print(f"角块方向: {cube.co}")

# 求解
solver = PocketSolver()
# 注意：solver.solve() 需要 54 字符的面片字符串
# 这里展示的是直接操作 PocketCube 对象
```

## 算法示例

### 常用算法

```python
# Sune（右手公式）
"R U R' U R U2 R'"

# Anti-Sune
"R U2 R' U' R U' R'"

# T-Perm（相邻交换）
"R U R' U' R' F R2 U' R' U' R U R' F'"

# Y-Perm（对角交换）
"F R U' R' U' R U R' F' R U R' U' R' F R F'"
```

### 测试打乱

```python
from solve.pocket_solver import PocketCube

# 简单打乱
cube = PocketCube.solved()
cube.apply_moves_str("R U R' U'")
print(f"打乱后: {cube.cp}, {cube.co}")

# 应用逆向复原
cube.apply_moves_str("U R U' R'")
print(f"是否复原: {cube.is_solved()}")  # True
```

## 性能

- **搜索深度**：最大 11 步（可配置）
- **状态空间**：二阶魔方有 3,674,160 种状态
- **RUF 限定**：相比使用全部 6 个面，可能需要更多步数
- **平均求解时间**：< 1 秒（简单打乱）

## 限制

1. **仅支持 RUF 转动**：不使用 D、L、B 面
2. **最优性**：不保证找到最短解法，但保证在合理步数内求解
3. **输入格式**：需要 54 字符的三阶魔方面片字符串（仅使用角块信息）

## 与三阶 CFOP 求解器的区别

| 特性 | 二阶求解器 | 三阶 CFOP |
|------|-----------|-----------|
| 魔方类型 | 2x2x2（仅角块） | 3x3x3（角块+棱块） |
| 转动限制 | RUF 限定 | 全部 6 面 |
| 求解方法 | Ortega 简化版 | CFOP（Cross+F2L+OLL+PLL） |
| 平均步数 | 10-15 步 | 50-60 步 |
| 适用场景 | 三轴机械臂 | 六轴机械臂 |

## 故障排除

### 问题：求解失败返回 None

**可能原因**：
1. 输入的面片字符串不合法
2. 魔方状态无法用 RUF 转动复原（理论上不应该发生）
3. 搜索深度不足

**解决方法**：
```python
# 增加搜索深度
solver = PocketSolver()
solver.max_depth = 15  # 默认 11
result = solver.solve(facelet_str)
```

### 问题：求解步数过多

**可能原因**：
- RUF 限定导致需要更多步数
- 使用的是 BFS 而非最优搜索

**解决方法**：
- 这是正常现象，RUF 限定会增加步数
- 如需最优解，可以考虑实现 IDA* 搜索

## 开发与测试

```bash
# 运行基础测试
python3 test_pocket.py

# 运行高级测试
python3 test_pocket_advanced.py

# 测试特定打乱
python3 -c "
from solve.pocket_solver import PocketCube, PocketSolver
cube = PocketCube.solved()
cube.apply_moves_str('R U R\\' U\\'')
print(f'打乱后: {cube.cp}, {cube.co}')
"
```

## 参考资料

- [二阶魔方维基百科](https://en.wikipedia.org/wiki/Pocket_Cube)
- [Ortega 方法](https://www.speedsolving.com/wiki/index.php/Ortega_Method)
- [二阶魔方上帝之数](https://www.cube20.org/) - 11 步（使用全部 6 面）
