from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

from src.models.health import HealthReport, HealthReportItem, HealthAdvice
from src.extensions.database import db
from src.utils.response import api_response
from src.utils.ai_service import query_qwen_medical_api

# 创建蓝图
health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

@health_bp.route('/ping', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    返回:
    - 服务器状态
    """
    return api_response(200, 'ok', {'status': 'running'})

@health_bp.route('/medical-qa-test', methods=['POST'])
def test_medical_qa():
    """
    测试医疗问答接口，无需认证
    
    请求JSON参数:
    - query: 查询内容
    - language: 语言(chinese/mongolian)
    
    返回:
    - 医疗问答结果
    """
    try:
        data = request.get_json()
        if not data or not data.get('query'):
            return api_response(400, 'param_error')
            
        query = data['query']
        language = data.get('language', 'chinese')
        
        # 调用医疗问答服务
        result = query_qwen_medical_api(query, language)
        
        return api_response(200, 'success', result)
        
    except Exception as e:
        logger.error(f"测试医疗问答异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/reports', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_health_reports():
    """
    获取用户健康报告列表
    
    请求头:
    - Authorization: JWT令牌
    
    返回:
    - 成功: 健康报告列表
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取所有健康报告
        reports = HealthReport.query.filter_by(user_id=user_id).order_by(HealthReport.created_at.desc()).all()
        
        # 转换为字典列表
        report_list = [report.to_dict() for report in reports]
        
        return api_response(200, 'success', report_list)
        
    except Exception as e:
        logger.error(f"获取健康报告列表异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/reports/<int:report_id>', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_health_report_detail(report_id):
    """
    获取健康报告详情
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - report_id: 报告ID
    
    返回:
    - 成功: 健康报告详情
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定报告
        report = HealthReport.query.filter_by(id=report_id, user_id=user_id).first()
        
        if not report:
            return api_response(404, 'not_found', '健康报告不存在')
        
        # 转换为字典，包括报告项目
        report_dict = report.to_dict(include_items=True)
        
        return api_response(200, 'success', report_dict)
        
    except Exception as e:
        logger.error(f"获取健康报告详情异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/reports', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def create_health_report():
    """
    创建健康报告
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - title: 报告标题
    - summary: 报告摘要
    - doctor: 医生姓名
    - hospital: 医院名称
    - suggestion: 医生建议
    - items: 报告项目列表
      - name: 项目名称
      - value: 项目值
      - reference: 参考范围
      - status: 状态
    
    返回:
    - 成功: 创建的健康报告
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('title'):
            return api_response(400, 'param_error')
        
        # 创建健康报告
        report = HealthReport(
            user_id=user_id,
            title=data['title'],
            summary=data.get('summary', ''),
            doctor=data.get('doctor', ''),
            hospital=data.get('hospital', ''),
            suggestion=data.get('suggestion', ''),
            status=data.get('status', 'normal')
        )
        
        # 添加报告项目
        items = data.get('items', [])
        for item_data in items:
            item = HealthReportItem(
                name=item_data.get('name', ''),
                value=item_data.get('value', ''),
                reference=item_data.get('reference', ''),
                status=item_data.get('status', 'normal')
            )
            report.items.append(item)
        
        # 保存到数据库
        db.session.add(report)
        db.session.commit()
        
        return api_response(200, 'success', report.to_dict(include_items=True))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建健康报告异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/reports/<int:report_id>', methods=['PUT', 'OPTIONS'])
@jwt_required(optional=True)
def update_health_report(report_id):
    """
    更新健康报告
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - report_id: 报告ID
    
    请求JSON参数:
    - title: 报告标题
    - summary: 报告摘要
    - doctor: 医生姓名
    - hospital: 医院名称
    - suggestion: 医生建议
    - status: 状态
    
    返回:
    - 成功: 更新后的健康报告
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定报告
        report = HealthReport.query.filter_by(id=report_id, user_id=user_id).first()
        
        if not report:
            return api_response(404, 'not_found', '健康报告不存在')
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(400, 'param_error')
        
        # 更新报告信息
        if 'title' in data:
            report.title = data['title']
        
        if 'summary' in data:
            report.summary = data['summary']
            
        if 'doctor' in data:
            report.doctor = data['doctor']
            
        if 'hospital' in data:
            report.hospital = data['hospital']
            
        if 'suggestion' in data:
            report.suggestion = data['suggestion']
            
        if 'status' in data:
            report.status = data['status']
        
        # 保存更新
        db.session.commit()
        
        return api_response(200, 'update_success', report.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新健康报告异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/reports/<int:report_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required(optional=True)
def delete_health_report(report_id):
    """
    删除健康报告
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - report_id: 报告ID
    
    返回:
    - 成功: 成功信息
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定报告
        report = HealthReport.query.filter_by(id=report_id, user_id=user_id).first()
        
        if not report:
            return api_response(404, 'not_found', '健康报告不存在')
        
        # 删除报告及其关联的项目
        db.session.delete(report)
        db.session.commit()
        
        return api_response(200, 'delete_success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除健康报告异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/advice', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_health_advice():
    """
    获取健康建议列表
    
    请求头:
    - Authorization: JWT令牌
    
    返回:
    - 成功: 健康建议列表
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取所有健康建议
        advice_list = HealthAdvice.query.filter_by(user_id=user_id).order_by(HealthAdvice.created_at.desc()).all()
        
        # 转换为字典列表
        result = [advice.to_dict() for advice in advice_list]
        
        return api_response(200, 'success', result)
        
    except Exception as e:
        logger.error(f"获取健康建议列表异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/advice', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def create_health_advice():
    """
    创建健康建议
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - title: 建议标题
    - content: 建议内容
    - summary: 建议摘要
    - author: 作者
    - category: 建议类型
    
    返回:
    - 成功: 创建的健康建议
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('title') or not data.get('content'):
            return api_response(400, 'param_error')
        
        # 创建健康建议
        advice = HealthAdvice(
            user_id=user_id,
            title=data['title'],
            content=data['content'],
            summary=data.get('summary', ''),
            author=data.get('author', ''),
            category=data.get('category', 'general')
        )
        
        # 保存到数据库
        db.session.add(advice)
        db.session.commit()
        
        return api_response(200, 'success', advice.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建健康建议异常: {str(e)}")
        return api_response(500, 'server_error')

@health_bp.route('/datapoints', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_health_datapoints():
    """
    获取健康数据点（体重、血压等）
    
    请求头:
    - Authorization: JWT令牌
    
    返回:
    - 成功: 健康数据点
    - 失败: 错误信息
    """
    if request.method == 'OPTIONS':
        # 处理OPTIONS请求，返回CORS需要的头信息
        return '', 200
        
    # 模拟数据
    data = {
        "weight": [
            {"date": "2023-01-01", "value": 70.5},
            {"date": "2023-01-08", "value": 70.2},
            {"date": "2023-01-15", "value": 69.8},
            {"date": "2023-01-22", "value": 69.5},
            {"date": "2023-01-29", "value": 69.0}
        ],
        "blood_pressure": [
            {"date": "2023-01-01", "systolic": 130, "diastolic": 85},
            {"date": "2023-01-08", "systolic": 128, "diastolic": 83},
            {"date": "2023-01-15", "systolic": 126, "diastolic": 82},
            {"date": "2023-01-22", "systolic": 125, "diastolic": 80},
            {"date": "2023-01-29", "systolic": 122, "diastolic": 78}
        ],
        "blood_sugar": [
            {"date": "2023-01-01", "value": 5.6},
            {"date": "2023-01-08", "value": 5.5},
            {"date": "2023-01-15", "value": 5.4},
            {"date": "2023-01-22", "value": 5.3},
            {"date": "2023-01-29", "value": 5.2}
        ]
    }
    
    return api_response(200, 'success', data) 