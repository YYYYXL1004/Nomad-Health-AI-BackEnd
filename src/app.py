from flask import Flask
import os
import logging
from flask_cors import CORS

from src.config import Config
from src.extensions.database import db
from src.extensions.jwt import jwt
from src.routes import get_blueprints

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 从配置对象加载配置
    app.config.from_object(Config)
    
    # 设置数据库连接为SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nomad_health.db'
    
    # 启用CORS，允许所有跨域请求
    CORS(app, 
         supports_credentials=True, 
         resources={r"/*": {"origins": ["http://localhost:8080"]}},
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Content-Disposition", "Accept",
                       "X-Requested-With", "Access-Control-Allow-Origin"])
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 设置JWT密钥和过期时间
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES
    
    # 注册蓝图
    register_blueprints(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """注册所有蓝图"""
    blueprints = get_blueprints()
    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True) 