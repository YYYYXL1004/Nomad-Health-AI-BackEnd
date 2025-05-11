from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
import os
from datetime import datetime
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from src.models.user import User
from src.extensions.database import db
from src.utils.response import api_response
from src.utils.file_util import allowed_file, save_file, get_file_url

# 创建蓝图
user_bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    获取用户个人信息
    
    请求头:
    - Authorization: JWT令牌
    
    返回:
    - 成功: 用户信息
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()  # 使用字符串形式的用户ID
        
        # 使用SQL查询用户
        # 查询用户
        query_sql = text("""
            SELECT id, account, nickname, phone, gender, avatar, created_at
            FROM users 
            WHERE id = :user_id
        """)
        
        user_result = db.session.execute(query_sql, {"user_id": user_id}).fetchone()
        
        if not user_result:
            return api_response(404, 'user_not_found')
        
        # 构建用户资料
        user_dict = {
            'userId': user_result[0],
            'account': user_result[1],
            'nickname': user_result[2] or "",
            'phone': user_result[3] or "",
            'gender': user_result[4] or "unknown",
            'birthday': None,  # 暂不支持
            'height': 0,  # 暂不支持
            'weight': 0,  # 暂不支持
            'avatar': user_result[5] or "",
            'created_at': user_result[6]
        }
        
        # 返回用户信息
        return api_response(200, 'success', user_dict)
        
    except Exception as e:
        logger.error(f"获取用户信息异常: {str(e)}")
        return api_response(500, 'server_error')

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """
    更新用户个人信息
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - nickname: 昵称
    - gender: 性别
    - avatar: 头像URL
    - phone: 手机号
    
    返回:
    - 成功: 更新后的用户信息
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 使用SQL查询用户是否存在
        query_sql = text("""
            SELECT id FROM users WHERE id = :user_id
        """)
        
        user_exists = db.session.execute(query_sql, {"user_id": user_id}).fetchone()
        
        if not user_exists:
            return api_response(404, 'user_not_found')
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(400, 'param_error')
        
        # 构建更新字段
        update_fields = []
        params = {"user_id": user_id}
        
        if 'nickname' in data:
            update_fields.append("nickname = :nickname")
            params['nickname'] = data['nickname']
        
        if 'gender' in data:
            update_fields.append("gender = :gender")
            params['gender'] = data['gender']
        
        if 'avatar' in data:
            update_fields.append("avatar = :avatar")
            params['avatar'] = data['avatar']
        
        # 新增：支持手机号更新
        if 'phone' in data:
            update_fields.append("phone = :phone")
            params['phone'] = data['phone']
        
        # 如果没有更新字段，直接返回
        if not update_fields:
            return api_response(400, 'no_update_fields')
        
        # 构建更新SQL
        update_sql = text(f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = :user_id
        """)
        
        # 执行更新
        db.session.execute(update_sql, params)
        db.session.commit()
        
        # 查询更新后的用户
        query_updated_sql = text("""
            SELECT id, account, nickname, phone, gender, avatar, created_at
            FROM users 
            WHERE id = :user_id
        """)
        
        updated_user = db.session.execute(query_updated_sql, {"user_id": user_id}).fetchone()
        
        # 构建用户资料
        user_dict = {
            'userId': updated_user[0],
            'account': updated_user[1],
            'nickname': updated_user[2] or "",
            'phone': updated_user[3] or "",
            'gender': updated_user[4] or "unknown",
            'birthday': None,  # 暂不支持
            'height': 0,  # 暂不支持
            'weight': 0,  # 暂不支持
            'avatar': updated_user[5] or "",
            'created_at': updated_user[6]
        }
        
        # 返回更新后的用户信息
        return api_response(200, 'update_success', user_dict)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户信息异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error')

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    修改密码
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - oldPassword: 旧密码
    - newPassword: 新密码
    - confirmPassword: 确认新密码
    
    返回:
    - 成功: 成功消息
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()  # 使用字符串形式的用户ID
        
        # 使用SQL查询用户
        # 查询用户
        query_sql = text("""
            SELECT password_hash FROM users WHERE id = :user_id
        """)
        
        user_result = db.session.execute(query_sql, {"user_id": user_id}).fetchone()
        
        if not user_result:
            return api_response(404, 'user_not_found')
        
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('oldPassword') or not data.get('newPassword') or not data.get('confirmPassword'):
            return api_response(400, 'param_error')
        
        # 验证旧密码
        if not check_password_hash(user_result[0], data['oldPassword']):
            return api_response(400, 'old_password_error')
        
        # 验证新密码和确认密码
        if data['newPassword'] != data['confirmPassword']:
            return api_response(400, 'password_mismatch')
        
        # 更新密码
        update_sql = text("""
            UPDATE users 
            SET password_hash = :password_hash
            WHERE id = :user_id
        """)
        
        db.session.execute(
            update_sql, 
            {
                "user_id": user_id,
                "password_hash": generate_password_hash(data['newPassword'])
            }
        )
        
        db.session.commit()
        
        return api_response(200, 'password_update_success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"修改密码异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return api_response(500, 'server_error')

@user_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """
    上传用户头像
    
    请求头:
    - Authorization: JWT令牌
    
    请求表单参数:
    - avatar: 头像文件
    
    返回:
    - 成功: 头像URL
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()  # 使用字符串形式的用户ID
        
        # 查询用户
        user = User.query.get(user_id)
        if not user:
            return api_response(404, 'user_not_found')
        
        # 检查文件
        if 'avatar' not in request.files:
            return api_response(400, 'no_avatar_file')
        
        file = request.files['avatar']
        if file.filename == '':
            return api_response(400, 'no_file_selected')
        
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
            # 保存文件
            file_path = save_file(file, 'avatars')
            
            # 获取文件URL
            file_url = get_file_url(file_path)
            
            # 更新用户头像
            user.avatar = file_url
            db.session.commit()
            
            return api_response(200, 'avatar_upload_success', {'avatar': file_url})
        else:
            return api_response(400, 'unsupported_file_type')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"上传头像异常: {str(e)}")
        return api_response(500, 'server_error') 