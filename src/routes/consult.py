from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime
import time

from src.models.consult import ConsultSession, ConsultMessage
from src.extensions.database import db
from src.utils.response import api_response
from src.utils.ai_service import xunfei_speech_to_text, query_qwen_medical_api
from src.utils.file_util import allowed_file, save_file, get_file_url

# 创建蓝图
consult_bp = Blueprint('consult', __name__)
logger = logging.getLogger(__name__)

@consult_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_consult_sessions():
    """
    获取用户问诊会话列表
    
    请求头:
    - Authorization: JWT令牌
    
    查询参数:
    - status: 会话状态（可选，如active/closed）
    
    返回:
    - 成功: 问诊会话列表
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取状态参数
        status = request.args.get('status')
        
        # 构建查询
        query = ConsultSession.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # 获取所有问诊会话
        sessions = query.order_by(ConsultSession.updated_at.desc()).all()
        
        # 转换为字典列表
        session_list = [session.to_dict() for session in sessions]
        
        return api_response(200, 'success', session_list)
        
    except Exception as e:
        logger.error(f"获取问诊会话列表异常: {str(e)}")
        return api_response(500, 'server_error')

@consult_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_consult_session_detail(session_id):
    """
    获取问诊会话详情
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - session_id: 会话ID
    
    返回:
    - 成功: 问诊会话详情，包括消息
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定会话
        session = ConsultSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return api_response(404, 'not_found', '问诊会话不存在')
        
        # 转换为字典，包括消息
        session_dict = session.to_dict(include_messages=True)
        
        return api_response(200, 'success', session_dict)
        
    except Exception as e:
        logger.error(f"获取问诊会话详情异常: {str(e)}")
        return api_response(500, 'server_error')

@consult_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_consult_session():
    """
    创建问诊会话
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - title: 会话标题
    - description: 会话描述
    
    返回:
    - 成功: 创建的问诊会话
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('title'):
            return api_response(400, 'param_error')
        
        # 创建问诊会话
        session = ConsultSession(
            user_id=user_id,
            title=data['title'],
            description=data.get('description', ''),
            status='active'
        )
        
        # 保存到数据库
        db.session.add(session)
        db.session.commit()
        
        # 添加系统欢迎消息
        welcome_message = ConsultMessage(
            session_id=session.id,
            sender_type='system',
            content='欢迎使用牧民健康智能问诊系统，请描述您的健康问题，我会尽力为您提供专业建议。',
            content_type='text'
        )
        db.session.add(welcome_message)
        db.session.commit()
        
        return api_response(200, 'success', session.to_dict(include_messages=True))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建问诊会话异常: {str(e)}")
        return api_response(500, 'server_error')

@consult_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_consult_session(session_id):
    """
    更新问诊会话
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - session_id: 会话ID
    
    请求JSON参数:
    - title: 会话标题
    - description: 会话描述
    - status: 会话状态（active/closed）
    
    返回:
    - 成功: 更新后的问诊会话
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定会话
        session = ConsultSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return api_response(404, 'not_found', '问诊会话不存在')
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(400, 'param_error')
        
        # 更新会话信息
        if 'title' in data:
            session.title = data['title']
        
        if 'description' in data:
            session.description = data['description']
        
        if 'status' in data:
            if data['status'] in ['active', 'closed']:
                session.status = data['status']
        
        # 保存更新
        db.session.commit()
        
        return api_response(200, 'update_success', session.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新问诊会话异常: {str(e)}")
        return api_response(500, 'server_error')

@consult_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
def send_message(session_id):
    """
    发送问诊消息
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - session_id: 会话ID
    
    请求JSON参数:
    - content: 消息内容
    - content_type: 消息类型（text/audio），默认为text
    - language: 语言（chinese/mongolian），默认为chinese
    - max_tokens: 回答的最大长度（可选，默认1024）
    - temperature: 控制回答的随机性（可选，默认0.7）
    
    返回:
    - 成功: 用户消息和AI回复消息
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定会话
        session = ConsultSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return api_response(404, 'not_found', '问诊会话不存在')
        
        # 检查会话状态
        if session.status != 'active':
            return api_response(400, 'param_error', '会话已关闭，无法发送消息')
        
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('content'):
            return api_response(400, 'param_error')
        
        # 创建用户消息
        user_message = ConsultMessage(
            session_id=session_id,
            sender_type='user',
            content=data['content'],
            content_type=data.get('content_type', 'text')
        )
        
        db.session.add(user_message)
        db.session.commit()
        
        # 更新会话时间
        session.updated_at = datetime.now()
        db.session.commit()
        
        # 查询医疗大模型
        language = data.get('language', 'chinese')
        max_tokens = data.get('max_tokens', 1024)
        temperature = data.get('temperature', 0.7)
        
        # 调用AI服务获取回复
        ai_response = query_qwen_medical_api(
            data['content'], 
            language=language,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # 创建AI回复消息
        ai_message = ConsultMessage(
            session_id=session_id,
            sender_type='ai',
            content=ai_response.get('response', '很抱歉，我暂时无法回答您的问题'),
            content_type='text'
        )
        
        db.session.add(ai_message)
        db.session.commit()
        
        # 更新会话时间
        session.updated_at = datetime.now()
        db.session.commit()
        
        # 返回对话结果
        return api_response(200, 'success', {
            'user_message': user_message.to_dict(),
            'ai_message': ai_message.to_dict(),
            'time_taken': ai_response.get('time_taken', 0)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"发送问诊消息异常: {str(e)}")
        return api_response(500, 'server_error')

@consult_bp.route('/sessions/<int:session_id>/audio', methods=['POST'])
@jwt_required()
def upload_audio(session_id):
    """
    上传语音文件并识别为文本
    
    请求头:
    - Authorization: JWT令牌
    
    路径参数:
    - session_id: 会话ID
    
    请求表单参数:
    - audio: 语音文件
    
    返回:
    - 成功: 识别后的文本
    - 失败: 错误信息
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取指定会话
        session = ConsultSession.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return api_response(404, 'not_found', '问诊会话不存在')
        
        # 检查会话状态
        if session.status != 'active':
            return api_response(400, 'param_error', '会话已关闭，无法发送消息')
        
        # 检查文件
        if 'audio' not in request.files:
            return api_response(400, 'no_file_selected')
        
        file = request.files['audio']
        if file.filename == '':
            return api_response(400, 'no_file_selected')
        
        if file and allowed_file(file.filename, {'mp3', 'wav'}):
            # 保存文件
            file_path = save_file(file, 'audio')
            file_url = get_file_url(file_path)
            
            # 读取文件内容用于语音识别
            file.seek(0)
            audio_data = file.read()
            
            # 调用语音识别服务
            recognition_result = xunfei_speech_to_text(audio_data, audio_format=file.filename.split('.')[-1].lower())
            
            if recognition_result['code'] == 0:
                recognized_text = recognition_result['text']
                
                # 创建音频消息
                audio_message = ConsultMessage(
                    session_id=session_id,
                    sender_type='user',
                    content=recognized_text,
                    content_type='audio',
                    media_url=file_url
                )
                
                db.session.add(audio_message)
                db.session.commit()
                
                # 更新会话时间
                session.updated_at = datetime.now()
                db.session.commit()
                
                return api_response(200, 'success', {
                    'text': recognized_text,
                    'audio_url': file_url,
                    'message': audio_message.to_dict()
                })
            else:
                return api_response(500, 'server_error', f"语音识别失败: {recognition_result.get('text')}")
        else:
            return api_response(400, 'unsupported_file_type')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"语音识别异常: {str(e)}")
        return api_response(500, 'server_error')

@consult_bp.route('/test/sessions', methods=['POST'])
@jwt_required()
def create_test_session():
    """
    简化版创建问诊会话，用于测试
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        logger.info(f"测试创建问诊会话 - 用户ID: {user_id}")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"code": 400, "message": "参数错误", "data": None})
        
        # 使用SQL直接创建会话
        from sqlalchemy import text
        
        try:
            # 确保表存在
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS consult_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.session.execute(create_table_sql)
            db.session.commit()
            logger.info("问诊会话表创建或确认成功")
            
            # 插入会话数据
            insert_sql = text("""
                INSERT INTO consult_sessions (user_id, title, description, status)
                VALUES (:user_id, :title, :description, 'active')
            """)
            
            result = db.session.execute(
                insert_sql, 
                {
                    "user_id": user_id,
                    "title": data.get('title', '测试会话'),
                    "description": data.get('description', '')
                }
            )
            db.session.commit()
            
            # 获取插入的会话ID
            get_id_sql = text("SELECT last_insert_rowid()")
            session_id_result = db.session.execute(get_id_sql).fetchone()
            session_id = session_id_result[0] if session_id_result else None
            
            if not session_id:
                logger.error("创建会话成功但无法获取ID")
                return jsonify({"code": 500, "message": "服务器错误", "data": None})
            
            # 创建欢迎消息
            create_message_table_sql = text("""
                CREATE TABLE IF NOT EXISTS consult_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    sender_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    media_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.session.execute(create_message_table_sql)
            db.session.commit()
            
            # 插入欢迎消息
            insert_message_sql = text("""
                INSERT INTO consult_messages (session_id, sender_type, content, content_type)
                VALUES (:session_id, 'system', '欢迎使用牧民健康智能问诊系统，请描述您的健康问题，我会尽力为您提供专业建议。', 'text')
            """)
            
            db.session.execute(insert_message_sql, {"session_id": session_id})
            db.session.commit()
            
            # 返回会话信息
            return jsonify({
                "code": 200,
                "message": "创建成功",
                "data": {
                    "id": session_id,
                    "user_id": user_id,
                    "title": data.get('title', '测试会话'),
                    "description": data.get('description', ''),
                    "status": "active",
                    "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "updated_at": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建测试会话出错: {str(e)}")
            import traceback
            logger.error(f"详细异常堆栈: {traceback.format_exc()}")
            return jsonify({"code": 500, "message": f"服务器错误: {str(e)}", "data": None})
            
    except Exception as e:
        logger.error(f"测试创建会话异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}", "data": None})

@consult_bp.route('/test/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
def send_test_message(session_id):
    """
    简化版发送问诊消息，用于测试
    """
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        logger.info(f"测试发送问诊消息 - 用户ID: {user_id}, 会话ID: {session_id}")
        
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({"code": 400, "message": "参数错误", "data": None})
        
        # 使用SQL直接操作
        from sqlalchemy import text
        
        try:
            # 检查会话是否存在且属于当前用户
            check_session_sql = text("""
                SELECT id FROM consult_sessions 
                WHERE id = :session_id AND user_id = :user_id
            """)
            
            session_result = db.session.execute(check_session_sql, {
                "session_id": session_id,
                "user_id": user_id
            }).fetchone()
            
            if not session_result:
                logger.error(f"会话不存在或不属于当前用户 - 会话ID: {session_id}, 用户ID: {user_id}")
                return jsonify({"code": 404, "message": "会话不存在", "data": None})
            
            # 插入用户消息
            insert_message_sql = text("""
                INSERT INTO consult_messages (session_id, sender_type, content, content_type)
                VALUES (:session_id, 'user', :content, :content_type)
            """)
            
            db.session.execute(insert_message_sql, {
                "session_id": session_id,
                "content": data.get('content'),
                "content_type": data.get('content_type', 'text')
            })
            db.session.commit()
            
            # 获取插入的消息ID
            get_id_sql = text("SELECT last_insert_rowid()")
            message_id_result = db.session.execute(get_id_sql).fetchone()
            user_message_id = message_id_result[0] if message_id_result else None
            
            # 更新会话时间
            update_session_sql = text("""
                UPDATE consult_sessions 
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = :session_id
            """)
            db.session.execute(update_session_sql, {"session_id": session_id})
            db.session.commit()
            
            # 生成AI回复
            ai_response = "感谢您的咨询。根据您描述的症状，这可能是由多种原因引起的。建议您保持良好的作息习惯，适当休息，如症状持续，请及时就医。"
            
            # 插入AI回复
            insert_ai_message_sql = text("""
                INSERT INTO consult_messages (session_id, sender_type, content, content_type)
                VALUES (:session_id, 'ai', :content, 'text')
            """)
            
            db.session.execute(insert_ai_message_sql, {
                "session_id": session_id,
                "content": ai_response
            })
            db.session.commit()
            
            # 获取插入的AI消息ID
            ai_message_id_result = db.session.execute(get_id_sql).fetchone()
            ai_message_id = ai_message_id_result[0] if ai_message_id_result else None
            
            # 更新会话时间
            db.session.execute(update_session_sql, {"session_id": session_id})
            db.session.commit()
            
            # 返回消息结果
            return jsonify({
                "code": 200,
                "message": "发送成功",
                "data": {
                    "user_message": {
                        "id": user_message_id,
                        "session_id": session_id,
                        "sender_type": "user",
                        "content": data.get('content'),
                        "content_type": data.get('content_type', 'text'),
                        "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    "ai_message": {
                        "id": ai_message_id,
                        "session_id": session_id,
                        "sender_type": "ai",
                        "content": ai_response,
                        "content_type": "text",
                        "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
                    },
                    "time_taken": 0.1
                }
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"发送测试消息出错: {str(e)}")
            import traceback
            logger.error(f"详细异常堆栈: {traceback.format_exc()}")
            return jsonify({"code": 500, "message": f"服务器错误: {str(e)}", "data": None})
            
    except Exception as e:
        logger.error(f"测试发送消息异常: {str(e)}")
        import traceback
        logger.error(f"详细异常堆栈: {traceback.format_exc()}")
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}", "data": None})

@consult_bp.route('/medical-qa', methods=['POST'])
@jwt_required()
def medical_qa():
    """
    医疗问答API，无需创建会话即可直接咨询
    
    请求头:
    - Authorization: JWT令牌
    
    请求JSON参数:
    - query: 用户的医疗问题
    - language: 语言（chinese/mongolian），默认为chinese
    - max_tokens: 回答的最大长度（可选，默认1024）
    - temperature: 控制回答的随机性（可选，默认0.7）
    
    返回:
    - 成功: AI的回复内容
    - 失败: 错误信息
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or not data.get('query'):
            return api_response(400, 'param_error', '缺少必要的查询参数')
        
        # 提取参数
        query = data['query']
        language = data.get('language', 'chinese')
        max_tokens = data.get('max_tokens', 1024)
        temperature = data.get('temperature', 0.7)
        
        # 调用医疗大模型API
        start_time = time.time()
        ai_response = query_qwen_medical_api(
            query, 
            language=language, 
            max_tokens=max_tokens, 
            temperature=temperature
        )
        
        if ai_response.get('code', -1) != 0:
            return api_response(500, 'ai_service_error', ai_response.get('response', '医疗咨询服务暂时不可用'))
        
        # 返回结果
        return api_response(200, 'success', {
            'response': ai_response.get('response', ''),
            'time_taken': ai_response.get('time_taken', time.time() - start_time)
        })
        
    except Exception as e:
        logger.error(f"医疗问答API异常: {str(e)}")
        return api_response(500, 'server_error') 