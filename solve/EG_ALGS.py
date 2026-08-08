"""EG 方法算法库（二阶魔方）

EG (Erik-Gunnar) 方法是二阶魔方的高级求解方法：
1. 第一面（First Face）：使底层同色
2. EG 算法：一步完成剩余部分（OLL + PBL）

EG 方法分为两个阶段：
- EG0 (CLL): 第一面颜色对齐，顶层角块需要定向和排列
- EG1: 第一面颜色对齐，但有一个角块方向错误
- EG2: 第一面颜色未完全对齐

参考：https://www.speedsolving.com/wiki/index.php/EG_method
"""

# EG 算法表
# key: (case_name, auf) -> alg
# case_name 根据底层和顶层的状态分类

EG_ALGS = {}

def update_eg(prefix, algs_str):
    """更新 EG 算法表"""
    global EG_ALGS
    algs = algs_str.strip().splitlines()
    for i, alg in enumerate(algs):
        alg = alg.strip()
        if alg:
            EG_ALGS[f"{prefix}_{i+1}"] = alg


# ===== EG0 (CLL) 算法 =====
# 第一面颜色对齐，需要解决顶层

# T perm case
EG0_T = """
R U R' U' R' F R2 U' R' U' R U R' F'
"""

# Y perm case
EG0_Y = """
F R U' R' U' R U R' F' R U R' U' R' F R F'
"""

# Ua perm case
EG0_UA = """
R U R' U R U2 R'
"""

# Ub perm case
EG0_UB = """
R' U R' U' R' U' R' U R U R2
"""

# H perm case (RUF version)
EG0_H = """
R2 U2 R U2 R2 U2 R2 U2 R U2 R2
"""

# Z perm case (RUF version)
EG0_Z = """
R U R' U R U2 R' F R U R' U' R' F R2 U' R' U2 R U' R' U' R U' R'
"""

# Aa perm case
EG0_AA = """
R' F R F' R U2 R' U' R U2 R' U' R' F R F' R'
"""

# Ab perm case
EG0_AB = """
R' F R F' R' F R F' R U2 R' U' R U2 R' U' R' F R F' R'
"""

# E perm case (RUF version)
EG0_E = """
R U R' U' R' F R2 U' R' U' R U R' F' R U R' U' R' F R F'
"""

# F perm case
EG0_F = """
R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R
"""

# Ja perm case (RUF version)
EG0_JA = """
R U R' F' R U R' U' R' F R2 U' R'
"""

# Jb perm case
EG0_JB = """
R U R' F' R U R' U' R' F R2 U' R'
"""

# Na perm case
EG0_NA = """
R U R' U R U R' F' R U R' U' R' F R2 U' R' U2 R U' R'
"""

# Nb perm case
EG0_NB = """
R' U R U' R' F' U' F R U R' F R' F' R U' R
"""

# Ra perm case
EG0_RA = """
R U R' F' R U2 R' U2 R' F R U R U2 R'
"""

# Rb perm case
EG0_RB = """
R' U2 R U2 R' F R U R' U' R' F' R2
"""

# V perm case (RUF version)
EG0_V = """
R' U R' U' R' F R2 U' R' U' R U R' U R F' R U R' U'
"""

# Ga perm case (RUF version)
EG0_GA = """
R2 U R' U R' U' R U' R2 U R' U R U' R U' R2
"""

# Gb perm case (RUF version)
EG0_GB = """
R' U' R U R2 U R' U R U' R U' R2 U' R U' R
"""

# Gc perm case (RUF version)
EG0_GC = """
R2 U' R U' R U R' U R2 U' R U' R' U R U R2
"""

# Gd perm case (RUF version)
EG0_GD = """
R U R' U' R2 U' R U' R' U R' U R2 U R' U R'
"""

update_eg("EG0_T", EG0_T)
update_eg("EG0_Y", EG0_Y)
update_eg("EG0_UA", EG0_UA)
update_eg("EG0_UB", EG0_UB)
update_eg("EG0_H", EG0_H)
update_eg("EG0_Z", EG0_Z)
update_eg("EG0_AA", EG0_AA)
update_eg("EG0_AB", EG0_AB)
update_eg("EG0_E", EG0_E)
update_eg("EG0_F", EG0_F)
update_eg("EG0_JA", EG0_JA)
update_eg("EG0_JB", EG0_JB)
update_eg("EG0_NA", EG0_NA)
update_eg("EG0_NB", EG0_NB)
update_eg("EG0_RA", EG0_RA)
update_eg("EG0_RB", EG0_RB)
update_eg("EG0_V", EG0_V)
update_eg("EG0_GA", EG0_GA)
update_eg("EG0_GB", EG0_GB)
update_eg("EG0_GC", EG0_GC)
update_eg("EG0_GD", EG0_GD)


# ===== EG1 算法 =====
# 第一面颜色对齐，但有一个角块方向错误

EG1_SUNE = """
R U R' U R U2 R'
"""

EG1_ANTISUNE = """
R U2 R' U' R U' R'
"""

EG1_H = """
F R U R' U' F' U F R U R' U' F'
"""

EG1_PI = """
F R U R' U' R U R' U' F'
"""

EG1_U = """
F R U R' U' F'
"""

EG1_T = """
R U R' U' R' F R F'
"""

EG1_L = """
F R' F' R U R U' R'
"""

EG1_CAR = """
R U R' U' R' F R2 U R' U' F'
"""

EG1_SQUUNE = """
R U R' U R U' R' U R U2 R'
"""

update_eg("EG1_SUNE", EG1_SUNE)
update_eg("EG1_ANTISUNE", EG1_ANTISUNE)
update_eg("EG1_H", EG1_H)
update_eg("EG1_PI", EG1_PI)
update_eg("EG1_U", EG1_U)
update_eg("EG1_T", EG1_T)
update_eg("EG1_L", EG1_L)
update_eg("EG1_CAR", EG1_CAR)
update_eg("EG1_SQUUNE", EG1_SQUUNE)


# ===== EG2 算法 =====
# 第一面颜色未完全对齐

EG2_SUNE = """
R U R' U R U2 R'
"""

EG2_ANTISUNE = """
R U2 R' U' R U' R'
"""

EG2_H = """
F R U R' U' F' U F R U R' U' F'
"""

EG2_PI = """
F R U R' U' R U R' U' F'
"""

EG2_U = """
F R U R' U' F'
"""

EG2_T = """
R U R' U' R' F R F'
"""

EG2_L = """
F R' F' R U R U' R'
"""

EG2_CAR = """
R U R' U' R' F R2 U R' U' F'
"""

update_eg("EG2_SUNE", EG2_SUNE)
update_eg("EG2_ANTISUNE", EG2_ANTISUNE)
update_eg("EG2_H", EG2_H)
update_eg("EG2_PI", EG2_PI)
update_eg("EG2_U", EG2_U)
update_eg("EG2_T", EG2_T)
update_eg("EG2_L", EG2_L)
update_eg("EG2_CAR", EG2_CAR)


def get_eg_algs():
    """获取所有 EG 算法"""
    return EG_ALGS.copy()


def get_eg_alg_count():
    """获取 EG 算法数量"""
    return len(EG_ALGS)
