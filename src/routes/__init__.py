from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.health import health_bp
from src.routes.consult import consult_bp
from src.routes.article import article_bp
from src.routes.setting import setting_bp

def get_blueprints():
    """获取所有蓝图及其URL前缀"""
    return [
        (auth_bp, '/api/auth'),
        (user_bp, '/api/user'),
        (health_bp, '/api/health'),
        (consult_bp, '/api/consult'),
        (article_bp, '/api/articles'),
        (setting_bp, '/api/settings')
    ]

__all__ = [
    'auth_bp',
    'user_bp',
    'health_bp',
    'consult_bp',
    'article_bp',
    'setting_bp',
    'get_blueprints'
] 