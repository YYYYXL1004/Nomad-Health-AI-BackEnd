# 医疗问答API调用文档

## 1. 基本说明

本API提供基于Qwen-7B微调模型的中文和传统蒙古文医疗问答服务。

**重要**: 此API仅在校园网环境下可访问，基础URL为 `http://183.175.12.124:8000`

## 2. API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/medical_qa` | POST | 医疗问答接口 |
| `/health` | GET | 服务健康检查 |

## 3. 调用方法

### 3.1 医疗问答接口

**端点**: `http://183.175.12.124:8000/api/medical_qa`

**方法**: POST

**请求头**:
```
Content-Type: application/json
```

**请求参数**:

```json
{
    "query": "医疗问题内容",
    "max_tokens": 1024,     // 可选，默认值: 2048
    "temperature": 0.7,     // 可选，默认值: 0.7
    "top_p": 0.95,          // 可选，默认值: 0.95
    "language": "chinese"   // 可选，默认值: "chinese"，可选值: "chinese"或"mongolian"
}
```

#### Python示例代码 (中文)

```python
import requests

url = "http://183.175.12.124:8000/api/medical_qa"
payload = {
    "query": "高血压患者日常应该注意什么？",
    "max_tokens": 1024,
    "temperature": 0.7,
    "language": "chinese"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"用时: {result['time_taken']:.2f}秒")
    print(f"回答: {result['response']}")
else:
    print(f"错误: {response.status_code}, {response.text}")
```

#### Python示例代码 (传统蒙古文)

```python
import requests

url = "http://183.175.12.124:8000/api/medical_qa"
payload = {
    "query": "ᠴᠢᠰᠦᠨ ᠦ ᠳᠠᠷᠤᠯᠲᠠ ᠥᠨᠳᠥᠷ ᠡᠪᠡᠳᠴᠢᠲᠡᠨ ᠥᠳᠥᠷ ᠲᠤᠲᠤᠮ ᠶᠠᠭᠤ ᠠᠩᠬᠠᠷᠬᠤ ᠪᠤᠢ",
    "max_tokens": 1024,
    "temperature": 0.7,
    "language": "mongolian"
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"用时: {result['time_taken']:.2f}秒")
    print(f"回答: {result['response']}")
else:
    print(f"错误: {response.status_code}, {response.text}")
```

#### cURL示例 (中文)

```bash
curl -X POST "http://183.175.12.124:8000/api/medical_qa" \
     -H "Content-Type: application/json" \
     -d '{
           "query": "高血压患者日常应该注意什么？",
           "max_tokens": 1024,
           "temperature": 0.7,
           "language": "chinese"
         }'
```

### 3.2 健康检查接口

**端点**: `http://183.175.12.124:8000/health`

**方法**: GET

#### Python示例代码

```python
import requests

url = "http://183.175.12.124:8000/health"
response = requests.get(url)

if response.status_code == 200:
    result = response.json()
    print(f"服务状态: {result['status']}")
    print(f"模型路径: {result['model_path']}")
else:
    print(f"错误: {response.status_code}, {response.text}")
```

#### cURL示例

```bash
curl -X GET "http://183.175.12.124:8000/health"
```

## 4. 响应格式

### 医疗问答接口响应

```json
{
    "response": "模型生成的回答内容...",
    "time_taken": 2.45
}
```

### 健康检查接口响应

```json
{
    "status": "healthy",
    "model_path": "/sda/data/yaoxianglin/Qwen_YIliao/models/qwen7b_lora_yiliao.gguf",
    "n_gpu_layers_configured": 29,
    "target_main_gpu_configured": 0
}
```

## 5. 错误处理

| 状态码 | 描述 | 处理方法 |
|--------|------|---------|
| 400 | 请求参数错误 | 检查请求参数格式和内容 |
| 500 | 服务器内部错误 | 联系管理员或稍后重试 |
| 503 | 服务不可用 | 模型可能未加载，稍后重试或联系管理员 |

## 6. 注意事项

- 此API仅在校园网环境下可使用
- 传统蒙古文请求需要使用正确的Unicode字符
- 返回结果可能需要几秒时间，请耐心等待
- 推荐设置较短的查询以获得更快的响应速度