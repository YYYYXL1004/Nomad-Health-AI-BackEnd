#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入应用
from src.app import create_app
from src.extensions.database import db
from sqlalchemy import text

def init_consult_tables():
    """初始化问诊相关的数据库表"""
    print("开始初始化问诊相关的数据库表...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 创建问诊会话表
            create_consult_sessions_table = text("""
                CREATE TABLE IF NOT EXISTS consult_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            db.session.execute(create_consult_sessions_table)
            print("问诊会话表创建成功")
            
            # 创建问诊消息表
            create_consult_messages_table = text("""
                CREATE TABLE IF NOT EXISTS consult_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    sender_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    media_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES consult_sessions (id)
                )
            """)
            
            db.session.execute(create_consult_messages_table)
            print("问诊消息表创建成功")
            
            # 提交事务
            db.session.commit()
            print("数据库表初始化完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"初始化数据库表时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    init_consult_tables() 