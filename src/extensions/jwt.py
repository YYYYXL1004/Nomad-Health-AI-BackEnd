from flask_jwt_extended import JWTManager
from flask import jsonify

# 初始化JWTManager实例
jwt = JWTManager()

# JWT错误处理
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """过期令牌回调"""
    return jsonify({
        'code': 401,
        'message': '令牌已过期',
        'data': None
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """无效令牌回调"""
    return jsonify({
        'code': 401,
        'message': '无效的令牌',
        'data': None
    }), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    """未认证回调"""
    return jsonify({
        'code': 401,
        'message': '请求未包含访问令牌',
        'data': None
    }), 401

@jwt.token_verification_failed_loader
def token_verification_failed_callback():
    """令牌验证失败回调"""
    return jsonify({
        'code': 401,
        'message': '令牌验证失败',
        'data': None
    }), 401 