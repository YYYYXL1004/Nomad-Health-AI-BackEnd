from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions.database import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    gender = db.Column(db.String(10), default="unknown")
    birthday = db.Column(db.Date, nullable=True)
    height = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    avatar = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 用户设置关联
    settings = db.relationship("UserSetting", backref="user", uselist=False)
    
    # 健康报告关联
    health_reports = db.relationship("HealthReport", backref="user", lazy=True)
    
    # 问诊会话关联
    consult_sessions = db.relationship("ConsultSession", backref="user", lazy=True)
    
    @property
    def password(self):
        raise AttributeError('密码不可读')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'userId': self.id,
            'account': self.account,
            'nickname': self.nickname or "",
            'phone': self.phone or "",
            'gender': self.gender or "unknown",
            'birthday': self.birthday.strftime('%Y-%m-%d') if self.birthday else None,
            'height': self.height or 0,
            'weight': self.weight or 0,
            'avatar': self.avatar or "",
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        } 