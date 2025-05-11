from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

from src.models.article import Article, ArticleCategory, Tag
from src.extensions.database import db
from src.utils.response import api_response

# 创建蓝图
article_bp = Blueprint('article', __name__)
logger = logging.getLogger(__name__)

@article_bp.route('', methods=['GET', 'OPTIONS'])
def get_articles():
    """
    获取文章列表
    
    查询参数:
    - category_id: 分类ID（可选）
    - tag: 标签名称（可选）
    - page: 页码，默认1
    - per_page: 每页数量，默认10
    
    返回:
    - 成功: 文章列表和分页信息
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取查询参数
        category_id = request.args.get('category_id', type=int)
        tag = request.args.get('tag')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建查询
        query = Article.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if tag:
            query = query.join(Article.tags).filter(Tag.name == tag)
        
        # 分页查询
        pagination = query.order_by(Article.created_at.desc()).paginate(page=page, per_page=per_page)
        
        # 转换为字典列表，不包含内容
        articles = [article.to_dict(include_content=False) for article in pagination.items]
        
        return api_response(200, 'success', {
            'articles': articles,
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"获取文章列表异常: {str(e)}")
        return api_response(500, 'server_error')

@article_bp.route('/<int:article_id>', methods=['GET', 'OPTIONS'])
def get_article_detail(article_id):
    """
    获取文章详情
    
    路径参数:
    - article_id: 文章ID
    
    返回:
    - 成功: 文章详情
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        article = Article.query.get(article_id)
        
        if not article:
            return api_response(404, 'not_found', '文章不存在')
        
        # 增加浏览次数
        article.increment_view_count()
        
        # 转换为字典，包含内容
        article_dict = article.to_dict(include_content=True)
        
        return api_response(200, 'success', article_dict)
        
    except Exception as e:
        logger.error(f"获取文章详情异常: {str(e)}")
        return api_response(500, 'server_error')

@article_bp.route('/categories', methods=['GET', 'OPTIONS'])
def get_article_categories():
    """
    获取文章分类列表
    
    返回:
    - 成功: 分类列表
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        categories = ArticleCategory.query.all()
        
        # 转换为字典列表
        category_list = [category.to_dict() for category in categories]
        
        return api_response(200, 'success', category_list)
        
    except Exception as e:
        logger.error(f"获取文章分类列表异常: {str(e)}")
        return api_response(500, 'server_error')

@article_bp.route('/tags', methods=['GET', 'OPTIONS'])
def get_tags():
    """
    获取标签列表
    
    返回:
    - 成功: 标签列表
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        tags = Tag.query.all()
        
        # 转换为字典列表
        tag_list = [tag.to_dict() for tag in tags]
        
        return api_response(200, 'success', tag_list)
        
    except Exception as e:
        logger.error(f"获取标签列表异常: {str(e)}")
        return api_response(500, 'server_error')

@article_bp.route('/hot', methods=['GET', 'OPTIONS'])
def get_hot_articles():
    """
    获取热门文章列表
    
    查询参数:
    - limit: 数量限制，默认5
    
    返回:
    - 成功: 热门文章列表
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        limit = request.args.get('limit', 5, type=int)
        
        # 按浏览次数排序
        articles = Article.query.order_by(Article.view_count.desc()).limit(limit).all()
        
        # 转换为字典列表，不包含内容
        article_list = [article.to_dict(include_content=False) for article in articles]
        
        return api_response(200, 'success', article_list)
        
    except Exception as e:
        logger.error(f"获取热门文章列表异常: {str(e)}")
        return api_response(500, 'server_error') 