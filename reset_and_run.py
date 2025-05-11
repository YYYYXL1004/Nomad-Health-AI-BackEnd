#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入应用
from src.app import create_app
from src.extensions.database import db

def reset_database():
    """重置数据库"""
    print("开始重置数据库...")
    
    # 创建应用实例但不运行
    app = create_app()
    
    with app.app_context():
        # 检查并重命名数据库文件
        db_path = 'instance/nomad_health.db'
        if os.path.exists(db_path):
            print(f"重命名旧数据库文件")
            backup_path = 'instance/nomad_health.db.bak'
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.move(db_path, backup_path)
        
        # 创建数据库表
        print("创建新的数据库表...")
        db.create_all()
        
        print("数据库重置完成！")
    
    return app

if __name__ == "__main__":
    app = reset_database()
    print("启动应用服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True) 