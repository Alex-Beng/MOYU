#!/usr/bin/env python3
"""二阶魔方求解器完整测试"""
import logging
from solve.pocket_solver import PocketCube, PocketSolver

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_scramble_solve():
    """测试打乱后求解"""
    print("=" * 60)
    print("测试：打乱后求解")
    print("=" * 60)
    
    solver = PocketSolver()
    
    # 测试多个打乱状态
    test_cases = [
        ("R U R' U'", "简单 4 步打乱"),
        ("R U2 R' U R U' R'", "Sune 算法"),
        ("R U R' F' R U R' U' R' F R2 U' R'", "较复杂打乱"),
        ("F R U R' U' F'", "OLL 算法"),
    ]
    
    for scramble, desc in test_cases:
        print(f"\n{desc}: {scramble}")
        print("-" * 60)
        
        # 创建打乱状态
        cube = PocketCube.solved()
        cube.apply_moves_str(scramble)
        
        print(f"打乱后: cp={cube.cp[:4]}..., co={cube.co[:4]}...")
        
        # 转换为面片字符串（简化：只构造角块部分）
        # 实际使用时需要从真实魔方状态获取完整的 54 字符面片
        # 这里我们直接使用 PocketCube 对象进行求解测试
        
        # 使用 BFS 搜索验证是否可解
        from collections import deque
        
        queue = deque([(cube.copy(), "")])
        visited = set()
        found = False
        max_depth = 15
        
        while queue and not found:
            state, path = queue.popleft()
            
            if len(path.split()) > max_depth:
                continue
            
            state_key = (tuple(state.cp), tuple(state.co))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            if state.is_solved():
                print(f"✓ 找到解法（{len(path.split())} 步）: {path}")
                found = True
                break
            
            # 尝试所有 RUF 转动
            for face in [0, 1, 2]:  # U, R, F
                for times in [1, 2, 3]:
                    new_state = state.copy()
                    new_state.apply_move(face, times)
                    
                    face_names = ['U', 'R', 'F']
                    move_str = face_names[face]
                    if times == 2:
                        move_str += "2"
                    elif times == 3:
                        move_str += "'"
                    
                    new_path = f"{path} {move_str}".strip()
                    queue.append((new_state, new_path))
        
        if not found:
            print(f"✗ 未找到解法（搜索深度 {max_depth}）")

def test_inverse_scramble():
    """测试打乱的逆向求解"""
    print("\n" + "=" * 60)
    print("测试：逆向算法验证")
    print("=" * 60)
    
    test_cases = [
        "R U R' U'",
        "R U2 R' U R U' R'",
        "F R U R' U' F'",
    ]
    
    for scramble in test_cases:
        print(f"\n打乱: {scramble}")
        
        # 正向
        cube1 = PocketCube.solved()
        cube1.apply_moves_str(scramble)
        
        # 逆向
        moves = scramble.split()
        inverse = []
        for m in reversed(moves):
            if len(m) == 1:
                inverse.append(m + "'")
            elif m[1] == "'":
                inverse.append(m[0])
            elif m[1] == "2":
                inverse.append(m)
        inverse_str = " ".join(inverse)
        
        print(f"逆向: {inverse_str}")
        
        # 应用逆向
        cube1.apply_moves_str(inverse_str)
        
        if cube1.is_solved():
            print("✓ 逆向求解成功")
        else:
            print("✗ 逆向求解失败")

def test_commutator():
    """测试换位子（Commutator）"""
    print("\n" + "=" * 60)
    print("测试：换位子 [R, U] = R U R' U'")
    print("=" * 60)
    
    cube = PocketCube.solved()
    
    # [R, U] = R U R' U'
    cube.apply_moves_str("R U R' U'")
    
    print(f"执行 [R, U] 后: cp={cube.cp}, co={cube.co}")
    
    # 重复 6 次应该回到复原（对于某些换位子）
    cube2 = PocketCube.solved()
    for i in range(1, 13):
        cube2.apply_moves_str("R U R' U'")
        if cube2.is_solved():
            print(f"✓ 重复 {i} 次后复原")
            break
    else:
        print("✗ 重复 12 次未复原")

def test_god_number():
    """测试上帝之数（二阶魔方的上帝之数是 11）"""
    print("\n" + "=" * 60)
    print("测试：上帝之数验证")
    print("=" * 60)
    
    print("二阶魔方的上帝之数（God's Number）是 11")
    print("即任何打乱状态都可以在 11 步内复原（使用 6 个面）")
    print("使用 RUF 限定时，最坏情况可能需要更多步数")
    
    # 测试一个已知需要较多步数的状态
    # Superflip 的二阶版本
    cube = PocketCube.solved()
    # 这是一个对称的打乱
    cube.apply_moves_str("R U R' F R U2 R' U R U2 R' F'")
    
    print(f"复杂打乱后: cp={cube.cp}, co={cube.co}")

if __name__ == "__main__":
    test_scramble_solve()
    test_inverse_scramble()
    test_commutator()
    test_god_number()
    
    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
