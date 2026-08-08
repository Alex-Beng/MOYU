#!/usr/bin/env python3
"""测试二阶魔方求解器"""
import logging
from solve.pocket_solver import PocketCube, PocketSolver
from solve.cfop_solver import CubieCube

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_basic():
    """测试基本功能"""
    print("=" * 60)
    print("测试 1: 已复原状态")
    print("=" * 60)
    
    cube = PocketCube.solved()
    print(f"初始状态: cp={cube.cp}, co={cube.co}")
    print(f"是否复原: {cube.is_solved()}")
    
    print("\n" + "=" * 60)
    print("测试 2: 应用转动")
    print("=" * 60)
    
    cube = PocketCube.solved()
    cube.apply_moves_str("R U R' U'")
    print(f"执行 'R U R' U'' 后: cp={cube.cp}, co={cube.co}")
    print(f"是否复原: {cube.is_solved()}")
    
    print("\n" + "=" * 60)
    print("测试 3: Sune 算法（应回到复原状态）")
    print("=" * 60)
    
    cube = PocketCube.solved()
    sune = "R U R' U R U2 R'"
    for _ in range(6):  # Sune 重复 6 次应回到复原
        cube.apply_moves_str(sune)
    print(f"执行 6 次 Sune 后: {cube.is_solved()}")
    
    print("\n" + "=" * 60)
    print("测试 4: 简单打乱求解")
    print("=" * 60)
    
    # 创建一个简单的打乱状态
    cube = PocketCube.solved()
    scramble = "R U R' U'"
    cube.apply_moves_str(scramble)
    print(f"打乱: {scramble}")
    print(f"打乱后状态: cp={cube.cp}, co={cube.co}")
    
    # 手动逆向求解（应该是 U R U' R'）
    cube.apply_moves_str("U R U' R'")
    print(f"执行逆向后: {cube.is_solved()}")

def test_solver():
    """测试求解器"""
    print("\n" + "=" * 60)
    print("测试 5: 求解器测试")
    print("=" * 60)
    
    # 创建一个已知的打乱状态（使用三阶魔方格式）
    # 这里使用一个简单的打乱：R U R' U'
    # 对应的三阶魔方面片字符串需要手动构造
    
    solver = PocketSolver()
    
    # 测试已复原状态
    # U2 R U F2 F R U F' U' R U F'
    solved_facelet = "UUURUURLFURRFRBLFFBURLFRDDDFFFDDUDDULDDLLFLLRBBBRBBLBB"
    result = solver.solve(solved_facelet)
    
    if result:
        print(f"已复原状态求解结果: {result['solution']}")
        print(f"  第一层: {result['first_layer']}")
        print(f"  OLL: {result['oll']}")
        print(f"  PBL: {result['pbl']}")
    else:
        print("求解失败")

def test_from_facelet():
    """测试从面片字符串提取角块"""
    print("\n" + "=" * 60)
    print("测试 6: 从面片字符串提取角块")
    print("=" * 60)
    
    # 已复原状态
    solved_facelet = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    full_cube = CubieCube.from_facelet(solved_facelet)
    cube = PocketCube(full_cube.cp, full_cube.co)
    
    print(f"已复原面片 -> cp={cube.cp}, co={cube.co}")
    print(f"是否复原: {cube.is_solved()}")
    
    # 执行 R U R' U' 后的状态
    cube2 = PocketCube.solved()
    cube2.apply_moves_str("R U R' U'")
    print(f"\n执行 'R U R' U'' 后: cp={cube2.cp}, co={cube2.co}")

if __name__ == "__main__":
    test_basic()
    test_solver()
    test_from_facelet()
    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
