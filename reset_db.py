#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入应用
from src.app import create_app
from src.extensions.database import db

def reset_database():
    """重置数据库"""
    print("开始重置数据库...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 删除数据库文件
        db_path = os.path.join(app.instance_path, 'nomad_health.db')
        if os.path.exists(db_path):
            print(f"删除数据库文件: {db_path}")
            os.remove(db_path)
        
        # 创建数据库表
        print("创建新的数据库表...")
        db.create_all()
        
        print("数据库重置完成！")

if __name__ == "__main__":
    reset_database() 