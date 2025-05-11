import base64
import hashlib
import hmac
import json
import time
import urllib.parse
import requests
import logging
import websocket
import traceback
from datetime import datetime
from flask import current_app

# 配置日志
logger = logging.getLogger(__name__)

def xunfei_iat_auth(api_key, api_secret):
    """
    生成讯飞语音识别API的鉴权参数
    
    Args:
        api_key: 讯飞API Key
        api_secret: 讯飞API Secret
        
    Returns:
        dict: 鉴权参数
    """
    # 获取当前GMT时间
    now = datetime.utcnow()
    date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 构建signature_origin
    signature_origin = f"host: iat.cn-huabei-1.xf-yun.com\ndate: {date}\nGET /v1 HTTP/1.1"
    
    # 使用hmac-sha256计算签名
    signature_sha = hmac.new(api_secret.encode('utf-8'), 
                              signature_origin.encode('utf-8'),
                              digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    # 构建authorization_origin
    authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    return {
        "authorization": authorization,
        "date": date,
        "host": "iat.cn-huabei-1.xf-yun.com"
    }

def xunfei_speech_to_text(audio_data, audio_format="mp3"):
    """
    讯飞语音识别API，将音频转换为文本
    
    Args:
        audio_data (bytes): 音频数据
        audio_format (str): 音频格式，支持pcm/mp3
        
    Returns:
        dict: 识别结果，包含code和text字段
    """
    try:
        api_key = current_app.config.get('XUNFEI_API_KEY')
        api_secret = current_app.config.get('XUNFEI_API_SECRET')
        
        if not api_key or not api_secret:
            logger.error("缺少讯飞API配置")
            return {"code": -1, "text": "讯飞API配置错误"}
            
        # 获取鉴权参数
        auth_params = xunfei_iat_auth(api_key, api_secret)
        
        # 构建WebSocket URL
        url = "wss://iat.cn-huabei-1.xf-yun.com/v1?" + urllib.parse.urlencode({
            "authorization": auth_params["authorization"],
            "date": auth_params["date"],
            "host": auth_params["host"]
        })
        
        # 使用WebSocket客户端连接并发送数据
        recognition_result = ""
        
        def on_message(ws, message):
            nonlocal recognition_result
            response = json.loads(message)
            if response.get("code") == 0:
                data = response.get("data", {})
                if data.get("status") == 2:  # 识别结束
                    result = data.get("result", {})
                    recognition_result = result.get("text", "")
        
        def on_error(ws, error):
            logger.error(f"WebSocket错误: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.info(f"WebSocket连接关闭: {close_status_code}, {close_msg}")
        
        def on_open(ws):
            # 组装发送的数据
            data = {
                "common": {
                    "app_id": api_key
                },
                "business": {
                    "language": "zh_cn",
                    "domain": "iat",
                    "accent": "mandarin",
                    "format": audio_format
                },
                "data": {
                    "status": 0,  # 0：第一帧音频；1：中间帧；2：最后一帧
                    "format": audio_format,
                    "audio": base64.b64encode(audio_data).decode('utf-8'),
                    "encoding": "raw"
                }
            }
            ws.send(json.dumps(data))
            
            # 发送结束帧
            data["data"]["status"] = 2
            data["data"]["audio"] = ""
            ws.send(json.dumps(data))
        
        # 建立WebSocket连接
        ws = websocket.WebSocketApp(url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(ping_interval=10)
        
        if recognition_result:
            return {"code": 0, "text": recognition_result}
        else:
            return {"code": -1, "text": "语音识别失败"}
            
    except Exception as e:
        logger.error(f"语音识别异常: {str(e)}")
        logger.error(traceback.format_exc())
        return {"code": -1, "text": f"语音识别异常: {str(e)}"}

def query_qwen_medical_api(query, language="chinese", max_tokens=1024, temperature=0.7):
    """
    查询千问医疗大模型API
    
    Args:
        query (str): 用户查询内容
        language (str): 语言，支持chinese和mongolian
        max_tokens (int): 最大生成token数
        temperature (float): 温度参数，控制生成的随机性
        
    Returns:
        dict: 查询结果
    """
    try:
        # 关键点：这里决定是否使用模拟数据
        use_mock = current_app.config.get('USE_MOCK_MEDICAL_MODEL', False)
        if use_mock:
            return generate_mock_response(query, language)
        
        # 真实API调用部分
        api_url = current_app.config.get('QWEN_API_URL')
        if not api_url:
            logger.error("缺少千问API配置")
            return {"code": -1, "response": "千问API配置错误"}
        
        # 构建请求数据
        payload = {
            "query": query,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "language": language
        }
        
        # 发送请求到千问API
        start_time = time.time()
        response = requests.post(
            f"{api_url}/api/medical_qa",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        time_taken = time.time() - start_time
        
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            return {
                "code": 0, 
                "response": result.get("response", ""),
                "time_taken": result.get("time_taken", round(time_taken, 2))
            }
        else:
            return {"code": response.status_code, "response": f"医疗咨询服务暂时不可用"}
    
    except Exception as e:
        return {"code": -1, "response": f"医疗咨询服务异常: {str(e)}"}

def generate_mock_response(query, language="chinese"):
    """
    生成模拟的医疗大模型响应（用于测试或离线环境）
    
    Args:
        query (str): 用户查询内容
        language (str): 语言，支持chinese和mongolian
        
    Returns:
        dict: 模拟的查询结果
    """
    time.sleep(1)  # 模拟网络延迟
    
    mock_responses = {
        "chinese": {
            "高血压": "高血压是常见的慢性疾病，日常应注意：\n1. 限制钠盐摄入\n2. 规律测量血压\n3. 保持适当运动\n4. 避免情绪激动\n5. 按时服药\n6. 戒烟限酒",
            "糖尿病": "糖尿病患者日常管理建议：\n1. 控制碳水化合物摄入\n2. 规律监测血糖\n3. 坚持适量运动\n4. 按医嘱服药\n5. 定期进行并发症筛查",
            "感冒": "普通感冒建议：\n1. 多休息，保证充足睡眠\n2. 多饮水\n3. 可服用对症药物缓解症状\n4. 如症状持续超过一周或出现高热应及时就医"
        },
        "mongolian": {
            "高血压": "ᠴᠢᠰᠦᠨ ᠦ ᠳᠠᠷᠤᠯᠲᠠ ᠥᠨᠳᠥᠷ ᠡᠪᠡᠳᠴᠢᠲᠡᠨ ᠦ ᠡᠳᠦᠷ ᠲᠤᠲᠤᠮ ᠤᠨ ᠠᠩᠬᠠᠷᠬᠤ ᠵᠦᠢᠯ᠄\n1. ᠳᠠᠪᠤᠰᠤ ᠢᠳᠡᠬᠦ ᠶᠢ ᠬᠢᠵᠠᠭᠠᠷᠯᠠᠬᠤ\n2. ᠴᠢᠰᠦᠨ ᠦ ᠳᠠᠷᠤᠯᠲᠠ ᠪᠠᠨ ᠲᠣᠭᠲᠠᠮᠠᠯ ᠬᠡᠮᠵᠢᠬᠦ\n3. ᠵᠣᠬᠢᠰᠲᠠᠢ ᠳᠠᠰᠬᠠᠯ ᠬᠥᠳᠡᠯᠭᠡᠭᠡᠨ ᠬᠢᠬᠦ\n4. ᠰᠡᠳᠬᠢᠯ ᠬᠥᠳᠡᠯᠦᠯ ᠡᠴᠡ ᠵᠠᠢᠯᠠᠰᠬᠢᠬᠦ\n5. ᠡᠮ ᠢᠶᠠᠨ ᠴᠠᠭ ᠲᠤᠬᠠᠢ ᠳᠤᠨᠢ ᠤᠤᠭᠤᠬᠤ\n6. ᠲᠠᠮᠠᠬᠢ ᠲᠠᠲᠠᠬᠤ ᠦᠭᠡᠢ᠂ ᠠᠷᠢᠬᠢ ᠤᠤᠭᠤᠬᠤ ᠦᠭᠡᠢ ᠪᠠᠢᠬᠤ",
            "糖尿病": "ᠴᠢᠬᠢᠷ ᠰᠢᠵᠢᠩ ᠡᠪᠡᠳᠴᠢᠲᠡᠨ ᠳᠦ ᠡᠳᠦᠷ ᠲᠤᠲᠤᠮ ᠤᠨ ᠵᠥᠪᠯᠡᠭᠡ᠄\n1. ᠨᠢᠭᠦᠷᠰᠦ ᠤᠰᠤᠨ ᠤ ᠬᠡᠷᠡᠭᠯᠡᠭᠡ ᠶᠢ ᠬᠢᠨᠠᠬᠤ\n2. ᠴᠢᠰᠦᠨ ᠳᠠᠬᠢ ᠴᠢᠬᠢᠷ ᠢ ᠲᠣᠭᠲᠠᠮᠠᠯ ᠬᠢᠨᠠᠬᠤ\n3. ᠲᠣᠬᠢᠷᠠᠭᠰᠠᠨ ᠳᠠᠰᠬᠠᠯ ᠬᠥᠳᠡᠯᠭᠡᠭᠡᠨ ᠬᠢᠬᠦ\n4. ᠡᠮᠴᠢ ᠶᠢᠨ ᠵᠢᠭᠠᠪᠤᠷᠢ ᠶᠢᠨ ᠳᠠᠭᠠᠤ ᠡᠮ ᠤᠤᠭᠤᠬᠤ\n5. ᠬᠦᠨᠳᠦᠷᠡᠯ ᠦᠨ ᠰᠢᠨᠵᠢᠯᠡᠭᠡ ᠶᠢ ᠲᠣᠭᠲᠠᠮᠠᠯ ᠬᠢᠯᠭᠡᠬᠦ",
            "感冒": "ᠡᠩ ᠦᠨ ᠬᠠᠨᠢᠶᠠᠳᠤᠨ ᠵᠥᠪᠯᠡᠭᠡ᠄\n1. ᠠᠮᠠᠷᠠᠬᠤ᠂ ᠬᠠᠩᠭᠠᠯᠲᠠᠢ ᠤᠨᠲᠠᠬᠤ\n2. ᠢᠬᠡ ᠬᠡᠮᠵᠢᠶᠡᠨ ᠦ ᠰᠢᠩᠭᠡᠨ ᠤᠤᠭᠤᠬᠤ\n3. ᠰᠢᠨᠵᠢ ᠲᠡᠮᠳᠡᠭ ᠢ ᠨᠠᠮᠳᠠᠭᠠᠬᠤ ᠡᠮ ᠤᠤᠭᠤᠬᠤ\n4. ᠬᠡᠷᠪᠡ ᠰᠢᠨᠵᠢ ᠲᠡᠮᠳᠡᠭ ᠳᠣᠯᠣᠭᠠᠨ ᠬᠣᠨᠣᠭ ᠠᠴᠠ ᠳᠡᠭᠡᠷᠡ ᠦᠷᠭᠦᠯᠵᠢᠯᠡᠭᠰᠡᠨ ᠡᠰᠡᠬᠦᠯᠡ ᠥᠨᠳᠥᠷ ᠬᠠᠯᠠᠭᠤᠷᠠᠭᠰᠠᠨ ᠪᠣᠯ ᠡᠮᠴᠢ ᠳᠦ ᠶᠠᠭᠠᠷᠠᠯᠲᠠᠢ ᠦᠵᠡᠭᠦᠯᠬᠦ"
        }
    }
    
    # 选择语言
    lang = language.lower()
    if lang not in mock_responses:
        lang = "chinese"
    
    # 查找匹配的关键词
    response_text = "很抱歉，我无法理解您的问题。请提供更多信息，或咨询其他健康问题。"
    if lang == "mongolian":
        response_text = "ᠤᠴᠢᠷ ᠤᠨ ᠤᠴᠢᠷ᠂ ᠪᠢ ᠲᠠᠨ ᠤ ᠠᠰᠠᠭᠤᠯᠲᠠ ᠶᠢ ᠣᠢᠢᠯᠠᠭᠠᠬᠤ ᠦᠭᠡᠢ ᠪᠠᠢᠨᠠ᠃ ᠲᠠ ᠨᠡᠩ ᠣᠯᠠᠨ ᠮᠡᠳᠡᠭᠡᠯᠡᠯ ᠥᠭᠬᠦ ᠡᠰᠡᠬᠦᠯᠡ ᠥᠭᠡᠷᠡ ᠡᠷᠡᠭᠦᠯ ᠮᠡᠨᠳᠦ ᠶᠢᠨ ᠠᠰᠠᠭᠤᠯᠲᠠ ᠠᠰᠠᠭᠤᠨᠠ ᠤᠤ᠃"
    
    for keyword, resp in mock_responses[lang].items():
        if keyword in query:
            response_text = resp
            break
    
    return {
        "code": 0,
        "response": response_text,
        "time_taken": round(time.time() % 3 + 0.5, 2),  # 随机生成0.5-3.5秒的响应时间
        "is_mock": True
    } 