from datetime import datetime
from src.extensions.database import db

class ConsultSession(db.Model):
    """问诊会话模型"""
    __tablename__ = 'consult_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, closed
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 问诊消息关联
    messages = db.relationship("ConsultMessage", backref="session", lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self, include_messages=False):
        """将问诊会话对象转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if include_messages:
            result['messages'] = [message.to_dict() for message in self.messages]
            
        return result


class ConsultMessage(db.Model):
    """问诊消息模型"""
    __tablename__ = 'consult_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('consult_sessions.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # user, ai, system
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), default='text')  # text, image, audio
    media_url = db.Column(db.String(200))  # 媒体文件URL
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        """将问诊消息对象转换为字典"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_type': self.sender_type,
            'content': self.content,
            'content_type': self.content_type,
            'media_url': self.media_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } 