from datetime import datetime
from src.extensions.database import db

class HealthReport(db.Model):
    """健康报告模型"""
    __tablename__ = 'health_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(200))
    doctor = db.Column(db.String(50))
    hospital = db.Column(db.String(100))
    suggestion = db.Column(db.Text)
    status = db.Column(db.String(20), default='normal')
    has_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 健康报告项目关联
    items = db.relationship("HealthReportItem", backref="report", lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self, include_items=False):
        """将健康报告对象转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'summary': self.summary,
            'doctor': self.doctor,
            'hospital': self.hospital,
            'suggestion': self.suggestion,
            'status': self.status,
            'has_read': self.has_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
        
        if include_items:
            result['items'] = [item.to_dict() for item in self.items]
            
        return result


class HealthReportItem(db.Model):
    """健康报告项目模型"""
    __tablename__ = 'health_report_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50))
    reference = db.Column(db.String(50))
    status = db.Column(db.String(20), default='normal')
    report_id = db.Column(db.Integer, db.ForeignKey('health_reports.id'), nullable=False)
    
    def to_dict(self):
        """将健康报告项目对象转换为字典"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'name': self.name,
            'value': self.value,
            'reference': self.reference,
            'status': self.status
        }


class HealthAdvice(db.Model):
    """健康建议模型"""
    __tablename__ = 'health_advices'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50))
    category = db.Column(db.String(20), default='general')
    has_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        """将健康建议对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'summary': self.summary, 
            'content': self.content,
            'author': self.author,
            'category': self.category,
            'has_read': self.has_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        } 