from src.extensions.database import db

class UserSetting(db.Model):
    """用户设置模型"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    language = db.Column(db.String(10), default='zh-CN')  # 语言设置: zh-CN, mn-MN
    push_notification = db.Column(db.Boolean, default=True)  # 推送通知
    
    def to_dict(self):
        """将设置对象转换为字典"""
        return {
            'language': self.language,
            'push_notification': self.push_notification
        } 