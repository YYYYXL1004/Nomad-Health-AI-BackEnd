#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database():
    """检查数据库中的表结构"""
    print("检查数据库结构...")
    
    # 数据库路径
    db_path = 'instance/nomad_health.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"数据库中的表:")
        for table in tables:
            table_name = table[0]
            print(f"\n表名: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("列结构:")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        
        # 关闭连接
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_database() 