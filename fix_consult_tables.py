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
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_consult_tables():
    """修复问诊相关的数据库表结构"""
    logger.info("开始修复问诊相关的数据库表结构...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 检查consult_sessions表结构
            check_table = text("""
                PRAGMA table_info(consult_sessions)
            """)
            columns = db.session.execute(check_table).fetchall()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if not columns:
                logger.info("consult_sessions表不存在，创建新表")
                create_table(db)
            else:
                column_names = [col[1] for col in columns]
                logger.info(f"consult_sessions表现有列: {column_names}")
                
                # 检查是否为旧表结构，如果是完全不同的结构，重新创建表
                if 'user_id' not in column_names or ('symptoms' in column_names and 'title' not in column_names):
                    logger.info("表结构不匹配，将重新创建表")
                    
                    # 备份旧表数据
                    backup_table(db, "consult_sessions")
                    
                    # 删除旧表
                    drop_table = text("DROP TABLE IF EXISTS consult_sessions")
                    db.session.execute(drop_table)
                    db.session.commit()
                    
                    # 创建新表
                    create_table(db)
                else:
                    # 只添加缺少的列
                    if 'title' not in column_names:
                        logger.info("添加缺失的title列")
                        add_column = text("""
                            ALTER TABLE consult_sessions ADD COLUMN title TEXT DEFAULT '问诊会话'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加title列")
                    
                    # 添加其他缺失列
                    if 'description' not in column_names:
                        logger.info("添加缺失的description列")
                        add_column = text("""
                            ALTER TABLE consult_sessions ADD COLUMN description TEXT DEFAULT ''
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加description列")
                    
                    if 'status' not in column_names:
                        logger.info("添加缺失的status列")
                        add_column = text("""
                            ALTER TABLE consult_sessions ADD COLUMN status TEXT DEFAULT 'active'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加status列")
                    
                    # 对于时间戳列，使用固定值而不是CURRENT_TIMESTAMP
                    if 'created_at' not in column_names:
                        logger.info("添加缺失的created_at列")
                        add_column = text(f"""
                            ALTER TABLE consult_sessions ADD COLUMN created_at TEXT DEFAULT '{current_time}'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加created_at列")
                    
                    if 'updated_at' not in column_names:
                        logger.info("添加缺失的updated_at列")
                        add_column = text(f"""
                            ALTER TABLE consult_sessions ADD COLUMN updated_at TEXT DEFAULT '{current_time}'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加updated_at列")
            
            # 检查consult_messages表结构
            check_table = text("""
                PRAGMA table_info(consult_messages)
            """)
            columns = db.session.execute(check_table).fetchall()
            
            if not columns:
                logger.info("consult_messages表不存在，创建新表")
                create_messages_table(db)
            else:
                column_names = [col[1] for col in columns]
                logger.info(f"consult_messages表现有列: {column_names}")
                
                # 检查必需列是否存在
                if 'session_id' not in column_names or len(column_names) < 5:
                    logger.info("consult_messages表结构不匹配，将重新创建表")
                    
                    # 备份旧表数据
                    backup_table(db, "consult_messages")
                    
                    # 删除旧表
                    drop_table = text("DROP TABLE IF EXISTS consult_messages")
                    db.session.execute(drop_table)
                    db.session.commit()
                    
                    # 创建新表
                    create_messages_table(db)
                else:
                    # 只添加缺少的列
                    if 'sender_type' not in column_names:
                        logger.info("添加缺失的sender_type列")
                        add_column = text("""
                            ALTER TABLE consult_messages ADD COLUMN sender_type TEXT DEFAULT 'system'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加sender_type列")
                    
                    if 'content' not in column_names:
                        logger.info("添加缺失的content列")
                        add_column = text("""
                            ALTER TABLE consult_messages ADD COLUMN content TEXT DEFAULT ''
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加content列")
                    
                    if 'content_type' not in column_names:
                        logger.info("添加缺失的content_type列")
                        add_column = text("""
                            ALTER TABLE consult_messages ADD COLUMN content_type TEXT DEFAULT 'text'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加content_type列")
                    
                    if 'media_url' not in column_names:
                        logger.info("添加缺失的media_url列")
                        add_column = text("""
                            ALTER TABLE consult_messages ADD COLUMN media_url TEXT DEFAULT ''
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加media_url列")
                    
                    if 'created_at' not in column_names:
                        logger.info("添加缺失的created_at列")
                        add_column = text(f"""
                            ALTER TABLE consult_messages ADD COLUMN created_at TEXT DEFAULT '{current_time}'
                        """)
                        db.session.execute(add_column)
                        db.session.commit()
                        logger.info("成功添加created_at列")
            
            logger.info("数据库表修复完成！")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"修复数据库表时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

def backup_table(db, table_name):
    """备份表数据"""
    backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(f"备份 {table_name} 表数据到 {backup_name}")
    
    try:
        # 创建备份表
        create_backup = text(f"""
            CREATE TABLE {backup_name} AS SELECT * FROM {table_name}
        """)
        db.session.execute(create_backup)
        db.session.commit()
        logger.info(f"表 {table_name} 备份成功")
    except Exception as e:
        logger.error(f"备份表 {table_name} 失败: {str(e)}")

def create_table(db):
    """创建问诊会话表"""
    create_consult_sessions_table = text("""
        CREATE TABLE IF NOT EXISTS consult_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '问诊会话',
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.session.execute(create_consult_sessions_table)
    db.session.commit()
    logger.info("问诊会话表创建成功")

def create_messages_table(db):
    """创建问诊消息表"""
    create_consult_messages_table = text("""
        CREATE TABLE IF NOT EXISTS consult_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            sender_type TEXT NOT NULL DEFAULT 'system',
            content TEXT NOT NULL DEFAULT '',
            content_type TEXT DEFAULT 'text',
            media_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.session.execute(create_consult_messages_table)
    db.session.commit()
    logger.info("问诊消息表创建成功")

if __name__ == "__main__":
    fix_consult_tables() 