import os
import datetime

class Config:
    """配置类，包含应用所需的所有配置"""
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///nomad_health.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = "nomad-health-jwt-secret-key-123456"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'} 
    
    # 讯飞语音识别API配置
    XUNFEI_API_KEY = os.getenv('XUNFEI_API_KEY', 'Your_API_KEY')
    XUNFEI_API_SECRET = os.getenv('XUNFEI_API_SECRET', 'Your_API_SECRET')
    
    # 千问医疗模型API配置
    QWEN_API_URL = os.getenv('QWEN_API_URL', 'http://183.175.12.124:8000')
    
    # API基础URL配置
    BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000/api')
    
    # 是否使用模拟医疗大模型响应
    USE_MOCK_MEDICAL_MODEL = os.getenv('USE_MOCK_MEDICAL_MODEL', 'false').lower() in ('true', '1', 'yes') 
