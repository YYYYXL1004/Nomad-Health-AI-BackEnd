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

def init_health_tables():
    """初始化健康相关的数据库表"""
    print("开始初始化健康相关的数据库表...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 创建健康报告表
            create_health_reports_table = text("""
                CREATE TABLE IF NOT EXISTS health_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    summary VARCHAR(200),
                    doctor VARCHAR(50),
                    hospital VARCHAR(100),
                    suggestion TEXT,
                    status VARCHAR(20) DEFAULT 'normal',
                    has_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            db.session.execute(create_health_reports_table)
            print("健康报告表创建成功")
            
            # 创建健康报告项目表
            create_health_report_items_table = text("""
                CREATE TABLE IF NOT EXISTS health_report_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    value VARCHAR(50),
                    reference VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'normal',
                    FOREIGN KEY (report_id) REFERENCES health_reports (id) ON DELETE CASCADE
                )
            """)
            
            db.session.execute(create_health_report_items_table)
            print("健康报告项目表创建成功")
            
            # 创建健康建议表
            create_health_advices_table = text("""
                CREATE TABLE IF NOT EXISTS health_advices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    summary VARCHAR(200),
                    content TEXT NOT NULL,
                    author VARCHAR(50),
                    category VARCHAR(20) DEFAULT 'general',
                    has_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            db.session.execute(create_health_advices_table)
            print("健康建议表创建成功")
            
            # 提交事务
            db.session.commit()
            print("数据库表初始化完成！")
            
            # 添加测试数据
            insert_test_data()
            
        except Exception as e:
            db.session.rollback()
            print(f"初始化数据库表时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())

def insert_test_data():
    """插入测试数据"""
    print("开始插入测试数据...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 获取第一个用户ID用于测试
            get_user_id = text("SELECT id FROM users LIMIT 1")
            user_id_result = db.session.execute(get_user_id).fetchone()
            
            if not user_id_result:
                print("找不到用户，无法插入测试数据")
                return
                
            user_id = user_id_result[0]
            
            # 插入健康报告
            insert_health_report = text("""
                INSERT INTO health_reports (user_id, title, summary, doctor, hospital, suggestion, status, has_read, created_at)
                VALUES 
                (
                    :user_id, 
                    '年度体检报告', 
                    '年度常规体检报告，包含各项检查指标', 
                    '张医生',
                    '北京协和医院',
                    '总体健康状况良好，需要注意血压轻度偏高，建议适当调整饮食结构，增加运动',
                    'normal',
                    0,
                    CURRENT_TIMESTAMP
                )
            """)
            
            result = db.session.execute(insert_health_report, {"user_id": user_id})
            print("健康报告测试数据插入成功")
            
            # 获取插入的报告ID
            get_report_id = text("SELECT last_insert_rowid()")
            report_id_result = db.session.execute(get_report_id).fetchone()
            report_id = report_id_result[0] if report_id_result else None
            
            if not report_id:
                print("无法获取报告ID，跳过插入报告项目")
            else:
                # 插入健康报告项目
                insert_report_items = text("""
                    INSERT INTO health_report_items (report_id, name, value, reference, status)
                    VALUES 
                    (:report_id, '血压', '135/85', '90-140/60-90', 'abnormal'),
                    (:report_id, '血糖', '5.6', '3.9-6.1', 'normal'),
                    (:report_id, '总胆固醇', '4.8', '2.8-5.2', 'normal'),
                    (:report_id, '甘油三酯', '1.5', '0.56-1.7', 'normal'),
                    (:report_id, '尿酸', '420', '149-416', 'abnormal')
                """)
                
                db.session.execute(insert_report_items, {"report_id": report_id})
                print("健康报告项目测试数据插入成功")
            
            # 插入健康建议
            insert_health_advice = text("""
                INSERT INTO health_advices (user_id, title, summary, content, author, category, has_read, created_at)
                VALUES 
                (:user_id, '血压管理建议', '针对轻度高血压的日常管理建议', '建议限制盐分摄入，每天摄入量不超过6克；增加体育锻炼，每周至少进行150分钟中等强度有氧运动；保持良好的作息习惯，避免熬夜和过度紧张。', '李医生', 'diet', 0, CURRENT_TIMESTAMP),
                (:user_id, '睡眠质量改善建议', '改善睡眠质量的方法', '建议保持规律作息，每晚10-11点入睡；睡前避免使用电子设备；睡前可以泡脚或热水浴放松身心；营造安静、舒适的睡眠环境。', '王医生', 'lifestyle', 0, CURRENT_TIMESTAMP),
                (:user_id, '季节性健康提示', '春季健康注意事项', '近期天气变化较大，注意适时增减衣物；外出注意防晒；多喝水，保持充分的水分摄入；避免长时间在高温环境下活动。', '赵医生', 'seasonal', 0, CURRENT_TIMESTAMP)
            """)
            
            db.session.execute(insert_health_advice, {"user_id": user_id})
            print("健康建议测试数据插入成功")
            
            # 提交事务
            db.session.commit()
            print("测试数据插入完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"插入测试数据时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    init_health_tables() 