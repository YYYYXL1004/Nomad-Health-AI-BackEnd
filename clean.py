#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
清理仓库中的无关文件，使其适合上传到GitHub
"""

import os
import shutil
import sys

# 需要保留的文件和目录
KEEP_FILES = [
    'README.md',
    'requirements.txt',
    'run.py',
    'src',
    '.gitignore',
    'openapi.json',
    'entrypoint.sh',
    'docs',
    'docker',
    'init_health_tables.py',
    'init_article_tables.py',
    'init_consult_tables.py',
    'reset_db.py',
    'clean_repo.py',  # 保留这个脚本本身
    'static',  # 静态资源目录
    'test_consult_api.py',  # 核心测试文件
    'test_register.py',    # 核心测试文件
    'api_test.py',         # 核心测试文件
    'LICENSE',             # 如果存在许可证文件
]

def clean_repo():
    """清理仓库中的无关文件"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取所有文件和目录
    all_items = os.listdir(current_dir)
    
    # 筛选出需要删除的文件和目录
    items_to_delete = [item for item in all_items if item not in KEEP_FILES and not item.startswith('.git')]
    
    if not items_to_delete:
        print("没有需要清理的文件。")
        return
    
    print("以下文件/目录将被删除:")
    for item in items_to_delete:
        print(f" - {item}")
    
    confirmation = input("\n确认删除这些文件? (y/n): ").strip().lower()
    if confirmation != 'y':
        print("操作已取消。")
        return
    
    # 删除文件和目录
    for item in items_to_delete:
        item_path = os.path.join(current_dir, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"已删除文件: {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"已删除目录: {item}")
        except Exception as e:
            print(f"删除 {item} 时出错: {e}")
    
    print("\n清理完成！仓库现在已准备好上传到GitHub。")
    print("注意：.git 目录和隐藏文件已保留。")

if __name__ == "__main__":
    print("敕勒云诊后端 - 仓库清理工具")
    print("=" * 40)
    clean_repo()