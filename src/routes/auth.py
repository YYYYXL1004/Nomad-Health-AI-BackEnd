from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import logging

from src.models.user import User
from src.models.setting import UserSetting
from src.extensions.database import db
from src.utils.response import api_response

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    
    请求JSON参数:
    - account: 用户账号或手机号
    - password: 密码
    
    返回:
    - 成功: JWT令牌和用户信息
    - 失败: 错误信息
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('account') or not data.get('password'):
            return api_response(400, 'param_error')
        
        account = data.get('account')
        password = data.get('password')
        
        # 使用SQL查询用户
        from sqlalchemy import text
        from werkzeug.security import check_password_hash
        
        # 查询用户
        query_sql = text("""
            SELECT id, account, password_hash, nickname, phone
            FROM users 
            WHERE account = :account OR phone = :account
        """)
        
        user_result = db.session.execute(query_sql, {"account": account}).fetchone()
        
        if not user_result:
            return api_response(401, 'account_password_error')
        
        # 验证密码
        user_id, user_account, password_hash, nickname, phone = user_result
        
        if not check_password_hash(password_hash, password):
            return api_response(401, 'account_password_error')
        
        # 创建JWT令牌
        access_token = create_access_token(identity=str(user_id))
        
        # 返回用户信息和令牌
        return api_response(200, 'login_success', {
            'userId': user_id,
            'account': user_account,
            'nickname': nickname or "",
            'avatar': "",
            'token': access_token
        })
        
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        return api_response(500, 'server_error')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    
    请求JSON参数:
    - account: 用户账号
    - password: 密码
    - confirmPassword: 确认密码
    - nickname: 昵称
    - phone: 手机号
    
    返回:
    - 成功: JWT令牌和用户信息
    - 失败: 错误信息
    """
    try:
        logger.info("开始处理注册请求")
        data = request.get_json()
        logger.info(f"请求数据: {data}")
        
        # 验证必填参数
        required_fields = ['account', 'password', 'confirmPassword', 'nickname', 'phone']
        if not data or not all(field in data for field in required_fields):
            logger.error(f"缺少必填参数，当前数据: {data}")
            return api_response(400, 'param_error')
        
        # 验证密码
        if data['password'] != data['confirmPassword']:
            logger.error("密码不匹配")
            return api_response(400, 'password_mismatch')
        
        # 使用直接SQL查询检查账号是否已存在
        from sqlalchemy import text
        
        try:
            # 查询用户是否存在
            check_sql = text("SELECT id FROM users WHERE account = :account")
            result = db.session.execute(check_sql, {"account": data['account']}).fetchone()
            
            if result:
                logger.error(f"账号 {data['account']} 已存在")
                return api_response(409, 'account_exists')
                
            # 检查手机号是否已存在
            check_phone_sql = text("SELECT id FROM users WHERE phone = :phone")
            phone_result = db.session.execute(check_phone_sql, {"phone": data['phone']}).fetchone()
            
            if phone_result:
                logger.error(f"手机号 {data['phone']} 已存在")
                return api_response(409, 'phone_exists')
        except Exception as e:
            logger.error(f"检查用户是否存在时出错: {str(e)}")
            return api_response(500, 'server_error')
        
        # 创建用户
        try:
            # 执行SQL插入
            insert_sql = text("""
                INSERT INTO users (account, password_hash, nickname, phone)
                VALUES (:account, :password_hash, :nickname, :phone)
            """)
            
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(data['password'])
            
            db.session.execute(
                insert_sql, 
                {
                    "account": data['account'],
                    "password_hash": password_hash,
                    "nickname": data['nickname'],
                    "phone": data['phone']
                }
            )
            
            db.session.commit()
            logger.info(f"用户保存成功")
            
            # 获取插入的用户ID
            get_id_sql = text("SELECT id FROM users WHERE account = :account")
            user_id_result = db.session.execute(get_id_sql, {"account": data['account']}).fetchone()
            user_id = user_id_result[0] if user_id_result else None
            
            if not user_id:
                logger.error("创建用户成功但无法获取ID")
                return api_response(500, 'server_error')
            
            # 创建用户设置
            try:
                # 确保设置表存在
                create_settings_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS user_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        language TEXT DEFAULT 'zh-CN',
                        push_notification BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                db.session.execute(create_settings_table_sql)
                
                # 创建用户设置
                insert_settings_sql = text("""
                    INSERT INTO user_settings (user_id, language, push_notification)
                    VALUES (:user_id, 'zh-CN', 1)
                """)
                db.session.execute(insert_settings_sql, {"user_id": user_id})
                db.session.commit()
                logger.info(f"用户设置创建成功")
            except Exception as e:
                logger.warning(f"创建用户设置失败: {str(e)}")
                # 继续执行，不因设置创建失败而影响注册流程
            
            # 创建JWT令牌
            access_token = create_access_token(identity=str(user_id))
            logger.info("JWT令牌创建成功")
            
            # 返回用户信息和令牌
            return api_response(200, 'register_success', {
                'userId': user_id,
                'account': data['account'],
                'nickname': data['nickname'],
                'token': access_token
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建用户过程中发生错误: {str(e)}")
            import traceback
            logger.error(f"详细异常堆栈: {traceback.format_exc()}")
            return api_response(500, 'server_error')
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"注册异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error')

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    重置密码接口
    
    请求JSON参数:
    - phone: 手机号
    - verifyCode: 验证码（实际项目中需验证）
    - newPassword: 新密码
    
    返回:
    - 成功: 成功信息
    - 失败: 错误信息
    """
    try:
        data = request.get_json()
        
        # 验证必填参数
        if not data or not data.get('phone') or not data.get('verifyCode') or not data.get('newPassword'):
            return api_response(400, 'param_error')
        
        # 查询用户
        user = User.query.filter_by(phone=data['phone']).first()
        if not user:
            return api_response(404, 'phone_not_registered')
        
        # 验证码验证（实际项目中需实现）
        # 这里简化处理，假设验证码总是正确的
        verify_code = data.get('verifyCode')
        if not verify_code or verify_code != '1234':  # 测试验证码
            return api_response(400, 'param_error')
        
        # 更新密码
        user.password = data['newPassword']
        db.session.commit()
        
        return api_response(200, 'password_reset_success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"重置密码异常: {str(e)}")
        return api_response(500, 'server_error')

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    退出登录接口
    
    请求头:
    - Authorization: JWT令牌
    
    返回:
    - 成功: 成功信息
    """
    # JWT无状态，服务端不需要实际"退出"操作
    # 客户端需要自行删除令牌
    return api_response(200, 'logout_success')

@auth_bp.route('/register-test', methods=['POST'])
def register_test():
    """
    简化版用户注册接口，仅用于测试
    """
    try:
        data = request.get_json()
        logger.info(f"测试注册请求数据: {data}")
        
        # 验证必填参数
        if not data or not data.get('account') or not data.get('password'):
            return jsonify({"code": 400, "message": "参数错误", "data": None})
        
        # 简单验证，仅创建用户不做关联
        account = data.get('account')
        password = data.get('password')
        nickname = data.get('nickname', '')
        phone = data.get('phone', '')
        
        # 直接使用SQL
        from sqlalchemy import text
        
        # 检查账号是否已存在
        try:
            # 尝试创建用户表（如果不存在）
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nickname TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.session.execute(create_table_sql)
            db.session.commit()
            
            # 查询用户是否存在
            check_sql = text("SELECT id FROM users WHERE account = :account")
            result = db.session.execute(check_sql, {"account": account}).fetchone()
            
            if result:
                return jsonify({"code": 409, "message": "账号已存在", "data": None})
                
        except Exception as e:
            logger.error(f"检查用户出错: {str(e)}")
            return jsonify({"code": 500, "message": f"检查用户出错: {str(e)}", "data": None})
        
        # 创建用户
        try:
            # 执行SQL插入
            insert_sql = text("""
                INSERT INTO users (account, password_hash, nickname, phone)
                VALUES (:account, :password_hash, :nickname, :phone)
            """)
            
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash(password)
            
            db.session.execute(
                insert_sql, 
                {
                    "account": account,
                    "password_hash": password_hash,
                    "nickname": nickname,
                    "phone": phone
                }
            )
            
            db.session.commit()
            
            # 获取插入的用户ID
            get_id_sql = text("SELECT id FROM users WHERE account = :account")
            user_id_result = db.session.execute(get_id_sql, {"account": account}).fetchone()
            user_id = user_id_result[0] if user_id_result else None
            
            if not user_id:
                return jsonify({"code": 500, "message": "创建用户失败，无法获取用户ID", "data": None})
            
            # 创建用户设置
            try:
                # 确保设置表存在
                create_settings_table_sql = text("""
                    CREATE TABLE IF NOT EXISTS user_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        language TEXT DEFAULT 'zh-CN',
                        push_notification BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                db.session.execute(create_settings_table_sql)
                
                # 创建用户设置
                insert_settings_sql = text("""
                    INSERT INTO user_settings (user_id, language, push_notification)
                    VALUES (:user_id, 'zh-CN', 1)
                """)
                db.session.execute(insert_settings_sql, {"user_id": user_id})
                db.session.commit()
                logger.info(f"测试用户设置创建成功")
            except Exception as e:
                logger.warning(f"创建测试用户设置失败: {str(e)}")
                # 继续执行，不因设置创建失败而影响注册流程
            
            # 创建JWT令牌
            access_token = create_access_token(identity=str(user_id))
            
            # 返回简化信息
            return jsonify({
                "code": 200,
                "message": "注册成功",
                "data": {
                    "userId": user_id,
                    "account": account,
                    "token": access_token
                }
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建用户出错: {str(e)}")
            return jsonify({"code": 500, "message": f"创建用户出错: {str(e)}", "data": None})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"测试注册异常: {str(e)}")
        import traceback
        logger.error(f"测试注册异常堆栈: {traceback.format_exc()}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}", "data": None})

@auth_bp.route('/login-test', methods=['POST'])
def login_test():
    """
    简化版用户登录接口，仅用于测试
    """
    try:
        data = request.get_json()
        logger.info(f"测试登录请求数据: {data}")
        
        # 验证必填参数
        if not data or not data.get('account') or not data.get('password'):
            return jsonify({"code": 400, "message": "参数错误", "data": None})
        
        account = data.get('account')
        password = data.get('password')
        
        # 直接使用SQL查询用户
        from sqlalchemy import text
        from werkzeug.security import check_password_hash
        
        # 查询用户
        query_sql = text("""
            SELECT id, account, password_hash, nickname, phone
            FROM users 
            WHERE account = :account OR phone = :account
        """)
        
        user_result = db.session.execute(query_sql, {"account": account}).fetchone()
        
        if not user_result:
            return jsonify({"code": 401, "message": "账号或密码错误", "data": None})
        
        # 验证密码
        user_id, user_account, password_hash, nickname, phone = user_result
        
        if not check_password_hash(password_hash, password):
            return jsonify({"code": 401, "message": "账号或密码错误", "data": None})
        
        # 创建JWT令牌
        access_token = create_access_token(identity=str(user_id))
        
        # 返回简化信息
        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "userId": user_id,
                "account": user_account,
                "nickname": nickname or "",
                "token": access_token
            }
        })
        
    except Exception as e:
        logger.error(f"测试登录异常: {str(e)}")
        import traceback
        logger.error(f"测试登录异常堆栈: {traceback.format_exc()}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}", "data": None}) 