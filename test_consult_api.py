import os
import json
import time
from src.app import create_app
from flask_jwt_extended import create_access_token

# 强制使用真实API
os.environ['USE_MOCK_MEDICAL_MODEL'] = 'false'

# 创建应用实例
app = create_app()

# 测试函数
def test_consult_api():
    # 在应用上下文中创建测试客户端
    with app.app_context():
        # 创建测试客户端
        client = app.test_client()
        
        # 创建测试用户令牌
        test_user_id = "test_user_123"
        access_token = create_access_token(identity=test_user_id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("=== 测试consult路由问诊功能 (修复后) ===")
        
        # 测试正常会话创建路由
        print("\n1. 创建问诊会话...")
        session_data = {
            'title': '测试问诊会话',
            'description': '测试千问医疗API'
        }
        
        response = client.post(
            '/api/consult/sessions',
            headers=headers,
            json=session_data
        )
        
        result = response.get_json()
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if response.status_code != 200 or not result.get('data', {}).get('id'):
            print("尝试使用测试路由创建会话...")
            response = client.post(
                '/api/consult/test/sessions',
                headers=headers,
                json=session_data
            )
            
            result = response.get_json()
            print(f"测试路由状态码: {response.status_code}")
            print(f"测试路由响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if response.status_code != 200 or not result.get('data', {}).get('id'):
                print("创建会话失败，无法继续测试")
                return
        
        session_id = result['data']['id']
        print(f"成功创建会话，ID: {session_id}")
        
        # 2. 发送问诊消息
        print("\n2. 发送问诊消息...")
        message_data = {
            'content': '我感冒了，有什么建议？',
            'content_type': 'text',
            'language': 'chinese'
        }
        
        start_time = time.time()
        response = client.post(
            f'/api/consult/sessions/{session_id}/messages',
            headers=headers,
            json=message_data
        )
        
        # 如果主路由失败，尝试测试路由
        if response.status_code != 200:
            print("主路由失败，尝试使用测试路由发送消息...")
            start_time = time.time()
            response = client.post(
                f'/api/consult/test/sessions/{session_id}/messages',
                headers=headers,
                json=message_data
            )
        
        result = response.get_json()
        total_time = time.time() - start_time
        
        print(f"状态码: {response.status_code}")
        print(f"总耗时: {round(total_time, 2)}秒")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 检查AI回复内容
        if result.get('data', {}).get('ai_message', {}).get('content'):
            ai_response = result['data']['ai_message']['content']
            print(f"\nAI回复内容:\n{ai_response}")
            
            # 检查是否使用了模拟数据（基于固定回复的特征判断）
            mock_responses = [
                "感谢您的咨询。根据您描述的症状，这可能是由多种原因引起的。建议您保持良好的作息习惯，适当休息，如症状持续，请及时就医。",
                "普通感冒建议：\n1. 多休息，保证充足睡眠\n2. 多饮水\n3. 可服用对症药物缓解症状\n4. 如症状持续超过一周或出现高热应及时就医"
            ]
            
            is_mock = any(mock_text in ai_response for mock_text in mock_responses)
            if is_mock:
                print("\n警告：返回结果与模拟数据模板匹配，可能使用了模拟回答")
            else:
                print("\n成功：返回结果看起来是由真实API生成的")
            
            # 检查响应时间
            api_time = result.get('data', {}).get('time_taken', 0)
            if api_time > 0:
                print(f"API响应时间: {api_time}秒")

        # 3. 直接测试API
        print("\n3. 直接测试医疗问答API...")
        
        # 导入AI服务函数
        from src.utils.ai_service import query_qwen_medical_api
        
        # 直接调用AI服务
        query = "我感冒了，有什么建议？"
        start_time = time.time()
        result = query_qwen_medical_api(query, language="chinese")
        total_time = time.time() - start_time
        
        print(f"直接API调用耗时: {round(total_time, 2)}秒")
        print(f"API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 检查是否为模拟数据
        if "is_mock" in str(result):
            print("\n警告：这是模拟数据，未调用真实API")
        else:
            print("\n成功：调用了真实的医疗问答API")
        
        # 4. 打印环境配置
        from flask import current_app
        print(f"\n当前USE_MOCK_MEDICAL_MODEL配置: {current_app.config.get('USE_MOCK_MEDICAL_MODEL', '未设置')}")

# 执行测试
if __name__ == "__main__":
    test_consult_api() 