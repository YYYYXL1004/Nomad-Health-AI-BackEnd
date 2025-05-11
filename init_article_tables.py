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

def init_article_tables():
    """初始化文章相关的数据库表"""
    print("开始初始化文章相关的数据库表...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 创建文章分类表
            create_article_categories_table = text("""
                CREATE TABLE IF NOT EXISTS article_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL,
                    name_mn VARCHAR(50)
                )
            """)
            
            db.session.execute(create_article_categories_table)
            print("文章分类表创建成功")
            
            # 创建标签表
            create_tags_table = text("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE
                )
            """)
            
            db.session.execute(create_tags_table)
            print("标签表创建成功")
            
            # 创建文章表
            create_articles_table = text("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    summary VARCHAR(500),
                    cover_image VARCHAR(200),
                    author VARCHAR(50),
                    category_id INTEGER,
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES article_categories (id)
                )
            """)
            
            db.session.execute(create_articles_table)
            print("文章表创建成功")
            
            # 创建文章标签关联表
            create_article_tags_table = text("""
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (article_id, tag_id),
                    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
            """)
            
            db.session.execute(create_article_tags_table)
            print("文章标签关联表创建成功")
            
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
            # 插入文章分类
            insert_categories = text("""
                INSERT INTO article_categories (name, name_mn)
                VALUES 
                ('健康知识', '健康知识(蒙文)'),
                ('疾病预防', '疾病预防(蒙文)'),
                ('医疗咨询', '医疗咨询(蒙文)')
            """)
            
            db.session.execute(insert_categories)
            print("文章分类测试数据插入成功")
            
            # 插入标签
            insert_tags = text("""
                INSERT INTO tags (name)
                VALUES 
                ('高血压'),
                ('糖尿病'),
                ('心脏健康'),
                ('饮食'),
                ('运动'),
                ('睡眠')
            """)
            
            db.session.execute(insert_tags)
            print("标签测试数据插入成功")
            
            # 插入文章
            insert_articles = text("""
                INSERT INTO articles (title, content, summary, author, category_id, created_at, updated_at)
                VALUES 
                (
                    '高血压的预防与控制', 
                    '<p>高血压是常见的慢性疾病，本文介绍高血压的预防和控制方法。</p><p>1. 合理饮食：减少钠盐摄入，增加钾的摄入，多吃蔬菜水果。</p><p>2. 适量运动：每周至少进行150分钟中等强度有氧运动。</p><p>3. 戒烟限酒：吸烟和过量饮酒都会增加血压。</p><p>4. 保持心理平衡：避免长期处于紧张状态。</p><p>5. 按时服药：如已确诊高血压，应遵医嘱按时服药。</p><p>6. 定期检查：定期监测血压，及时了解自己的血压变化。</p>',
                    '高血压是影响全球大量人口的慢性疾病，本文介绍了高血压的预防和控制方法，包括饮食、运动、生活方式等方面的建议。',
                    '张医生',
                    1,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                ),
                (
                    '糖尿病患者的饮食指南', 
                    '<p>糖尿病患者的饮食管理非常重要，本文提供了详细的饮食指南。</p><p>1. 控制总热量：根据个人情况制定合理的热量摄入计划。</p><p>2. 均衡饮食：合理搭配碳水化合物、蛋白质和脂肪。</p><p>3. 选择低升糖指数食物：如粗粮、豆类、大部分蔬菜等。</p><p>4. 规律进餐：保持每日三餐定时定量，可增加少量加餐。</p><p>5. 限制糖分摄入：减少单糖和双糖的摄入。</p><p>6. 增加膳食纤维：有助于控制血糖波动。</p>',
                    '糖尿病患者需要特别关注饮食管理，本文提供了糖尿病患者的饮食指南，帮助患者科学合理地安排日常饮食。',
                    '李医生',
                    2,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                ),
                (
                    '健康生活方式的重要性', 
                    '<p>健康的生活方式对预防疾病至关重要，本文详细介绍了健康生活的各个方面。</p><p>1. 均衡饮食：摄入多样化的食物，保证营养均衡。</p><p>2. 适量运动：根据个人情况选择适合的运动方式和强度。</p><p>3. 充足睡眠：保证每天7-8小时的高质量睡眠。</p><p>4. 心理健康：保持积极乐观的心态，学会减压。</p><p>5. 社交活动：维持良好的社交关系，避免孤独。</p><p>6. 戒烟限酒：避免烟草和酒精的危害。</p>',
                    '健康的生活方式是预防疾病、提高生活质量的基础，本文从饮食、运动、睡眠等多个方面介绍了如何保持健康的生活方式。',
                    '王医生',
                    3,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
            """)
            
            db.session.execute(insert_articles)
            print("文章测试数据插入成功")
            
            # 插入文章标签关联
            insert_article_tags = text("""
                INSERT INTO article_tags (article_id, tag_id)
                VALUES 
                (1, 1), -- 高血压的预防与控制 - 高血压
                (1, 4), -- 高血压的预防与控制 - 饮食
                (1, 5), -- 高血压的预防与控制 - 运动
                (2, 2), -- 糖尿病患者的饮食指南 - 糖尿病
                (2, 4), -- 糖尿病患者的饮食指南 - 饮食
                (3, 4), -- 健康生活方式的重要性 - 饮食
                (3, 5), -- 健康生活方式的重要性 - 运动
                (3, 6)  -- 健康生活方式的重要性 - 睡眠
            """)
            
            db.session.execute(insert_article_tags)
            print("文章标签关联测试数据插入成功")
            
            # 提交事务
            db.session.commit()
            print("测试数据插入完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"插入测试数据时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    init_article_tables() 