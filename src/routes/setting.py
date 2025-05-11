from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from src.models.user import User
from src.models.setting import UserSetting
from src.extensions.database import db
from src.utils.response import api_response

# 创建蓝图
setting_bp = Blueprint('setting', __name__)
logger = logging.getLogger(__name__)

@setting_bp.route('', methods=['GET'])
@jwt_required()
def get_user_settings():
    """
    获取用户设置
    
    请求头:
    - Authorization: JWT令牌
    
    返回:
    - 成功: 用户设置
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()  # 使用字符串形式的用户ID
        logger.info(f"获取用户设置 - 用户ID: {user_id}")
        
        # 使用SQL查询用户设置
        from sqlalchemy import text
        
        # 查询用户是否存在
        user_exists_sql = text("""
            SELECT id FROM users WHERE id = :user_id
        """)
        
        user_exists = db.session.execute(user_exists_sql, {"user_id": user_id}).fetchone()
        
        if not user_exists:
            logger.error(f"用户不存在 - ID: {user_id}")
            return api_response(404, 'user_not_found')
        
        logger.info(f"用户存在，继续查询设置")
        
        # 尝试创建设置表
        try:
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    language TEXT DEFAULT 'zh-CN',
                    push_notification BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            db.session.execute(create_table_sql)
            db.session.commit()
            logger.info("成功创建或确认设置表存在")
        except Exception as e:
            logger.error(f"创建设置表失败: {str(e)}")
            db.session.rollback()
            raise
        
        # 查询用户设置
        try:
            settings_sql = text("""
                SELECT id, user_id, language, push_notification
                FROM user_settings 
                WHERE user_id = :user_id
            """)
            
            setting_result = db.session.execute(settings_sql, {"user_id": user_id}).fetchone()
            logger.info(f"查询设置结果: {setting_result}")
        except Exception as e:
            logger.error(f"查询设置失败: {str(e)}")
            raise
        
        # 如果设置不存在，创建默认设置
        if not setting_result:
            logger.info(f"设置不存在，为用户 {user_id} 创建默认设置")
            try:
                insert_sql = text("""
                    INSERT INTO user_settings (user_id, language, push_notification)
                    VALUES (:user_id, 'zh-CN', 1)
                """)
                
                db.session.execute(insert_sql, {"user_id": user_id})
                db.session.commit()
                logger.info("成功创建默认设置")
                
                # 再次查询
                setting_result = db.session.execute(settings_sql, {"user_id": user_id}).fetchone()
                logger.info(f"创建后的设置结果: {setting_result}")
            except Exception as e:
                logger.error(f"创建默认设置失败: {str(e)}")
                db.session.rollback()
                raise
        
        # 返回设置
        settings_dict = {
            'language': setting_result[2],
            'push_notification': bool(setting_result[3])
        }
        
        logger.info(f"返回设置数据: {settings_dict}")
        return api_response(200, 'success', settings_dict)
        
    except Exception as e:
        logger.error(f"获取用户设置异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error')

@setting_bp.route('', methods=['PUT'])
@jwt_required()
def update_user_settings():
    """
    更新用户设置
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - language: 语言设置，如zh-CN，mn-MN
    - push_notification: 是否启用推送通知
    
    返回:
    - 成功: 更新后的用户设置
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()  # 使用字符串形式的用户ID
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(400, 'param_error')
        
        # 使用SQL查询和更新
        from sqlalchemy import text
        
        # 查询用户设置是否存在
        check_setting_sql = text("""
            SELECT id FROM user_settings WHERE user_id = :user_id
        """)
        
        setting_exists = db.session.execute(check_setting_sql, {"user_id": user_id}).fetchone()
        
        # 构建更新或插入
        params = {"user_id": user_id}
        
        if 'language' in data:
            params['language'] = data['language']
        
        if 'push_notification' in data:
            params['push_notification'] = 1 if data['push_notification'] else 0
        
        # 如果没有参数，直接返回
        if len(params) <= 1:  # 只有user_id
            return api_response(400, 'no_update_fields')
        
        # 如果设置存在，更新；否则插入
        if setting_exists:
            # 构建更新字段
            update_fields = []
            
            if 'language' in params:
                update_fields.append("language = :language")
            
            if 'push_notification' in params:
                update_fields.append("push_notification = :push_notification")
            
            # 构建更新SQL
            update_sql = text(f"""
                UPDATE user_settings 
                SET {', '.join(update_fields)}
                WHERE user_id = :user_id
            """)
            
            db.session.execute(update_sql, params)
        else:
            # 插入默认值
            if 'language' not in params:
                params['language'] = 'zh-CN'
            
            if 'push_notification' not in params:
                params['push_notification'] = 1
            
            # 构建插入SQL
            insert_sql = text("""
                INSERT INTO user_settings (user_id, language, push_notification)
                VALUES (:user_id, :language, :push_notification)
            """)
            
            db.session.execute(insert_sql, params)
        
        # 提交事务
        db.session.commit()
        
        # 查询更新后的设置
        query_sql = text("""
            SELECT language, push_notification
            FROM user_settings 
            WHERE user_id = :user_id
        """)
        
        updated_setting = db.session.execute(query_sql, {"user_id": user_id}).fetchone()
        
        # 返回更新后的设置
        settings_dict = {
            'language': updated_setting[0],
            'push_notification': bool(updated_setting[1])
        }
        
        return api_response(200, 'update_success', settings_dict)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户设置异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error')

@setting_bp.route('/test', methods=['GET'])
@jwt_required()
def get_test_settings():
    """测试版获取用户设置"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        logger.info(f"测试获取用户设置 - 用户ID: {user_id}")
        
        # 返回固定的测试设置
        settings_dict = {
            'language': 'zh-CN',
            'push_notification': True
        }
        
        logger.info(f"返回测试设置数据: {settings_dict}")
        return api_response(200, 'success', settings_dict)
        
    except Exception as e:
        logger.error(f"测试获取用户设置异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error')

@setting_bp.route('/test', methods=['PUT'])
@jwt_required()
def update_test_settings():
    """测试版更新用户设置"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        logger.info(f"测试更新用户设置 - 用户ID: {user_id}")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(400, 'param_error')
        
        logger.info(f"接收到的更新数据: {data}")
        
        # 处理更新
        updated_dict = {
            'language': data.get('language', 'zh-CN'),
            'push_notification': data.get('push_notification', True)
        }
        
        logger.info(f"返回更新后的测试设置数据: {updated_dict}")
        return api_response(200, 'update_success', updated_dict)
        
    except Exception as e:
        logger.error(f"测试更新用户设置异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error') 