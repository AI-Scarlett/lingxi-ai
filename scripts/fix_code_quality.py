#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀代码质量修复工具
自动修复裸 except 问题

作者：斯嘉丽 Scarlett
日期：2026-03-08
"""

import re
import os
from pathlib import Path


def fix_bare_except(file_path: Path) -> tuple[int, int]:
    """
    修复文件中的裸 except 问题
    
    Returns:
        (修复数量，总问题数)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 统计问题数量
        bare_except_pattern = r'\n(\s*)except\s*:\s*\n'
        matches = list(re.finditer(bare_except_pattern, content))
        total_issues = len(matches)
        
        if total_issues == 0:
            return 0, 0
        
        # 修复：except: → except Exception as e:
        fixed_count = 0
        for match in reversed(matches):  # 从后向前替换，保持索引正确
            indent = match.group(1)
            start = match.start()
            end = match.end()
            
            # 检查下一行是否是 pass 或简单的日志
            next_line_start = end
            next_line_end = content.find('\n', next_line_start)
            if next_line_end == -1:
                next_line_end = len(content)
            
            next_line = content[next_line_start:next_line_end]
            
            # 如果是简单的 except: pass 或 except: + 日志
            if 'pass' in next_line or 'print' in next_line.lower():
                # 替换为 except Exception as e:
                replacement = f'\n{indent}except Exception as e:\n'
                content = content[:start] + replacement + content[end:]
                fixed_count += 1
            else:
                # 复杂情况，添加日志
                replacement = f'\n{indent}except Exception as e:\n{indent}    # 容错处理\n'
                content = content[:start] + replacement + content[end:]
                fixed_count += 1
        
        # 保存修复后的文件
        if fixed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return fixed_count, total_issues
        
    except Exception as e:
        print(f"  ❌ 修复失败：{e}")
        return 0, 0


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🔧 灵犀代码质量修复工具")
    print("="*60 + "\n")
    
    # 灵犀脚本目录
    script_dir = Path(__file__).parent
    
    # 跳过测试和示例文件
    skip_patterns = ['test_', 'benchmark', 'demo', 'fix_']
    
    # 查找所有 Python 文件
    py_files = [f for f in script_dir.glob('*.py') 
                if not any(p in f.name for p in skip_patterns)]
    
    # 递归查找子目录
    for subdir in script_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            py_files.extend([f for f in subdir.glob('*.py')
                            if not any(p in f.name for p in skip_patterns)])
    
    print(f"📁 检查目录：{script_dir}")
    print(f"📄 找到 {len(py_files)} 个 Python 文件\n")
    
    # 修复统计
    total_fixed = 0
    total_issues = 0
    fixed_files = []
    
    # 逐个修复
    for py_file in sorted(py_files):
        fixed, issues = fix_bare_except(py_file)
        
        if issues > 0:
            total_issues += issues
            if fixed > 0:
                total_fixed += fixed
                fixed_files.append((py_file, fixed, issues))
                print(f"✅ {py_file.name}: 修复 {fixed}/{issues} 个问题")
    
    # 输出汇总
    print("\n" + "="*60)
    print("📊 修复汇总")
    print("="*60)
    print(f"总问题数：{total_issues}")
    print(f"已修复：{total_fixed}")
    print(f"修复率：{total_fixed/total_issues*100:.1f}%" if total_issues > 0 else "N/A")
    print(f"修复文件数：{len(fixed_files)}")
    
    if fixed_files:
        print("\n📝 修复详情:")
        for file_path, fixed, issues in fixed_files:
            rel_path = file_path.relative_to(script_dir)
            print(f"  - {rel_path}: {fixed}/{issues}")
    
    print("\n✅ 修复完成!\n")


if __name__ == "__main__":
    main()
