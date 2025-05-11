from datetime import datetime
from src.extensions.database import db

# 文章标签关联表
article_tags = db.Table('article_tags',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class ArticleCategory(db.Model):
    """文章分类模型"""
    __tablename__ = 'article_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    name_mn = db.Column(db.String(50))  # 蒙古语名称
    
    # 文章关联
    articles = db.relationship("Article", backref="category", lazy=True)
    
    def to_dict(self):
        """将文章分类对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'name_mn': self.name_mn
        }


class Tag(db.Model):
    """标签模型"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    
    def to_dict(self):
        """将标签对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name
        }


class Article(db.Model):
    """文章模型"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    title_mn = db.Column(db.String(100))
    summary = db.Column(db.String(200))
    summary_mn = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    content_mn = db.Column(db.Text)
    cover_image = db.Column(db.String(200))
    author = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('article_categories.id'))
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 标签关联
    tags = db.relationship('Tag', secondary=article_tags, lazy='subquery',
                           backref=db.backref('articles', lazy=True))
    
    def to_dict(self, include_content=True):
        """将文章对象转换为字典"""
        result = {
            'id': self.id,
            'title': self.title,
            'title_mn': self.title_mn,
            'summary': self.summary,
            'summary_mn': self.summary_mn,
            'cover_image': self.cover_image,
            'author': self.author,
            'category_id': self.category_id,
            'view_count': self.view_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'tags': [tag.to_dict() for tag in self.tags]
        }
        
        if self.category:
            result['category'] = self.category.to_dict()
            
        if include_content:
            result['content'] = self.content
            result['content_mn'] = self.content_mn
            
        return result
    
    def increment_view_count(self):
        """增加文章浏览次数"""
        self.view_count += 1
        db.session.commit() 