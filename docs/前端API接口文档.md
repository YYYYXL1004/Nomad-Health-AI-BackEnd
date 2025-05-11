# 牧民健康应用API接口文档

本文档详细描述了牧民健康应用后端API的使用方法，供前端开发人员参考对接。

## 1. 通用说明

### 1.1 基础URL

所有API请求的基础URL为：`http://127.0.0.1:5000/api` 
或者     'http://10.102.45.184:5000'

### 1.2 认证方式

除了少数公开API外，大多数API需要身份验证。认证方式采用Bearer Token，在请求头中添加：

```
Authorization: Bearer [token值]
```

### 1.3 请求格式

- GET请求：查询参数使用URL参数
- POST/PUT请求：请求体使用JSON格式
- 文件上传：使用multipart/form-data格式

### 1.4 响应格式

所有API返回统一的JSON格式：

```json
{
  "code": 200,       // 状态码，200表示成功，其他值表示出错
  "message": "操作成功", // 状态描述
  "data": {          // 返回的数据，出错时可能为null
    // 具体数据
  }
}
```

### 1.5 错误码说明

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 2. 用户认证API

### 2.1 用户注册

- **URL**: `/auth/register`
- **方法**: POST
- **请求参数**:

```json
{
  "account": "用户名",       // 必填，长度5-20字符
  "password": "密码",        // 必填，长度8-20字符
  "confirmPassword": "确认密码", // 必填，与密码相同
  "nickname": "昵称",        // 可选
  "phone": "手机号"          // 必填，11位手机号
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "userId": 123,
    "account": "用户名",
    "nickname": "昵称",
    "token": "eyJhbGci..."  // JWT令牌
  }
}
```

### 2.2 用户登录

- **URL**: `/auth/login`
- **方法**: POST
- **请求参数**:

```json
{
  "account": "用户名或手机号", // 必填
  "password": "密码"         // 必填
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "userId": 123,
    "account": "用户名",
    "nickname": "昵称",
    "avatar": "头像URL",
    "token": "eyJhbGci..."  // JWT令牌
  }
}
```

### 2.3 找回密码

- **URL**: `/auth/reset-password`
- **方法**: POST
- **请求参数**:

```json
{
  "phone": "手机号",         // 必填
  "verifyCode": "验证码",    // 必填
  "newPassword": "新密码"    // 必填
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": null
}
```

### 2.4 获取短信验证码

- **URL**: `/auth/send-verify-code`
- **方法**: POST
- **请求参数**:

```json
{
  "phone": "手机号",       // 必填
  "type": "reset_password" // 验证码类型，可选值：register(注册)、reset_password(重置密码)
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "验证码发送成功",
  "data": {
    "expireTime": 300     // 验证码有效期(秒)
  }
}
```

### 2.5 退出登录

- **URL**: `/auth/logout`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "退出成功",
  "data": null
}
```

## 3. 用户信息API

### 3.1 获取用户资料

- **URL**: `/user/profile`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "userId": 123,
    "account": "用户名",
    "nickname": "昵称",
    "avatar": "头像URL",
    "gender": "male",      // male(男)、female(女)、unknown(未知)
    "birthday": "1990-01-01", // 出生日期，格式：YYYY-MM-DD
    "height": 175,          // 身高，单位：cm
    "weight": 65,           // 体重，单位：kg
    "phone": "13800138000",
    "registerTime": "2023-01-01 12:00:00"
  }
}
```

### 3.2 更新用户资料

- **URL**: `/user/profile`
- **方法**: PUT
- **请求头**: 需要包含Authorization令牌
- **请求参数**:

```json
{
  "nickname": "新昵称",    // 可选
  "gender": "male",       // 可选
  "birthday": "1990-01-01", // 可选
  "height": 175,          // 可选
  "weight": 65            // 可选
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    // 与3.1获取用户资料返回格式相同
  }
}
```

### 3.3 修改密码

- **URL**: `/user/change-password`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求参数**:

```json
{
  "oldPassword": "旧密码",    // 必填
  "newPassword": "新密码",    // 必填
  "confirmPassword": "确认新密码" // 必填
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

### 3.4 上传头像

- **URL**: `/user/avatar`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求体**: form-data格式，包含avatar图片文件
- **响应**:

```json
{
  "code": 200,
  "message": "头像上传成功",
  "data": {
    "avatarUrl": "https://example.com/uploads/avatar/123.jpg"
  }
}
```

## 4. 用户设置API

### 4.1 获取用户设置

- **URL**: `/settings`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "language": "zh-CN",       // 语言，可选值：zh-CN(中文)、mn-MN(蒙文)
    "push_notification": true,  // 是否开启推送通知
    "dark_mode": false         // 是否开启暗黑模式
  }
}
```

### 4.2 更新用户设置

- **URL**: `/settings`
- **方法**: PUT
- **请求头**: 需要包含Authorization令牌
- **请求参数**:

```json
{
  "language": "zh-CN",       // 可选
  "push_notification": true,  // 可选
  "dark_mode": false         // 可选
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    // 与4.1获取用户设置返回格式相同
  }
}
```

## 5. 健康服务API

### 5.1 获取健康报告列表

- **URL**: `/health/reports`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **查询参数**: 
  - page: 页码（默认1）
  - size: 每页数量（默认10）
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 25,
    "pages": 3,
    "page": 1,
    "size": 10,
    "list": [
      {
        "reportId": 1,
        "title": "2023年第一季度体检报告",
        "createTime": "2023-03-25 14:30:00",
        "status": "normal",    // normal(正常)、abnormal(异常)
        "hasRead": true
      },
      // ...更多报告
    ]
  }
}
```

### 5.2 获取健康报告详情

- **URL**: `/health/reports/{reportId}`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "reportId": 1,
    "title": "2023年第一季度体检报告",
    "createTime": "2023-03-25 14:30:00",
    "status": "normal",
    "examDate": "2023-03-20",
    "examLocation": "内蒙古自治区医院",
    "items": [
      {
        "name": "血压",
        "value": "120/80 mmHg",
        "reference": "90-139/60-89 mmHg",
        "status": "normal"
      },
      {
        "name": "血糖",
        "value": "5.8 mmol/L",
        "reference": "3.9-6.1 mmol/L",
        "status": "normal"
      },
      // ...更多检查项目
    ],
    "conclusion": "体检结果正常，请保持良好的生活习惯",
    "advice": "建议多运动，控制饮食，保持良好作息"
  }
}
```

### 5.3 获取健康建议

- **URL**: `/health/advice`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "generalAdvice": "根据您的健康状况，建议您：",
    "items": [
      {
        "title": "饮食建议",
        "content": "多吃蔬菜水果，减少油腻食物摄入"
      },
      {
        "title": "运动建议",
        "content": "每周至少进行3次中等强度运动，每次30分钟以上"
      },
      {
        "title": "作息建议",
        "content": "保持规律作息，每天睡眠7-8小时"
      }
    ]
  }
}
```

## 6. 在线问诊API

### 6.1 获取问诊会话列表

- **URL**: `/consult/sessions`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **查询参数**: 
  - page: 页码（默认1）
  - size: 每页数量（默认10）
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 5,
    "pages": 1,
    "page": 1,
    "size": 10,
    "list": [
      {
        "sessionId": 1,
        "title": "咨询高血压问题",
        "createTime": "2023-05-10 09:30:00",
        "lastMessageTime": "2023-05-10 10:15:00",
        "status": "active",    // active(进行中)、closed(已结束)
        "unreadCount": 2
      },
      // ...更多会话
    ]
  }
}
```

### 6.2 创建问诊会话

- **URL**: `/consult/sessions`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求参数**:

```json
{
  "title": "咨询高血压问题",    // 必填
  "description": "最近血压偏高，想咨询相关调理方法"  // 可选
}
```

- **响应**:

```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "sessionId": 1,
    "title": "咨询高血压问题",
    "description": "最近血压偏高，想咨询相关调理方法",
    "createTime": "2023-05-10 09:30:00",
    "status": "active"
  }
}
```

### 6.3 获取会话详情

- **URL**: `/consult/sessions/{sessionId}`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "sessionId": 1,
    "title": "咨询高血压问题",
    "description": "最近血压偏高，想咨询相关调理方法",
    "createTime": "2023-05-10 09:30:00",
    "lastMessageTime": "2023-05-10 10:15:00",
    "status": "active"
  }
}
```

### 6.4 获取问诊消息记录

- **URL**: `/consult/sessions/{sessionId}/messages`
- **方法**: GET
- **请求头**: 需要包含Authorization令牌
- **查询参数**: 
  - page: 页码（默认1）
  - size: 每页数量（默认20）
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 10,
    "pages": 1,
    "page": 1,
    "size": 20,
    "list": [
      {
        "messageId": 1,
        "sessionId": 1,
        "sender": "user",      // user(用户)、ai(AI助手)
        "contentType": "text", // text(文本)、image(图片)、audio(音频)
        "content": "最近我的血压偏高，有什么建议吗？",
        "time": "2023-05-10 09:35:00"
      },
      {
        "messageId": 2,
        "sessionId": 1,
        "sender": "ai",
        "contentType": "text",
        "content": "高血压需要从饮食、运动和作息等多方面调理...",
        "time": "2023-05-10 09:36:12"
      }
      // ...更多消息
    ]
  }
}
```

### 6.5 发送问诊消息

- **URL**: `/consult/sessions/{sessionId}/messages`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求参数**:

```json
{
  "content": "我想详细了解一下高血压患者的饮食注意事项",
  "content_type": "text",
  "language": "chinese",
  "max_tokens": 1024,
  "temperature": 0.7
}
```

**参数说明**:
- `content`: 消息内容（必填）
- `content_type`: 消息类型，默认为"text"
- `language`: 语言，支持"chinese"或"mongolian"（可选，默认chinese）
- `max_tokens`: 回答的最大长度（可选，默认1024）
- `temperature`: 控制回答的随机性，越高越有创意（可选，默认0.7）

- **响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_message": {
      "id": 3,
      "session_id": 1,
      "sender_type": "user",
      "content": "我想详细了解一下高血压患者的饮食注意事项",
      "content_type": "text",
      "created_at": "2023-05-10 10:15:00"
    },
    "ai_message": {
      "id": 4,
      "session_id": 1,
      "sender_type": "ai",
      "content": "高血压患者在饮食方面应注意以下几点：\n\n1. 控制钠盐摄入：每天食盐摄入量应控制在5克以下...",
      "content_type": "text",
      "created_at": "2023-05-10 10:15:05"
    },
    "time_taken": 1.25
  }
}
```

### 6.6 上传问诊图片

- **URL**: `/consult/upload-image`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求体**: form-data格式，包含image图片文件
- **响应**:

```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "imageUrl": "https://example.com/uploads/consult/123.jpg"
  }
}
```

### 6.7 语音转文字

- **URL**: `/consult/speech-to-text`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求体**: form-data格式，包含audio音频文件
- **响应**:

```json
{
  "code": 200,
  "message": "转换成功",
  "data": {
    "text": "转换后的文本内容"
  }
}
```

### 6.8 医疗问答

- **URL**: `/consult/medical-qa`
- **方法**: POST
- **请求头**: 需要包含Authorization令牌
- **请求参数**:

```json
{
  "query": "高血压患者日常应该注意什么？",
  "language": "chinese",
  "max_tokens": 1024,
  "temperature": 0.7
}
```

**参数说明**:
- `query`: 用户的医疗问题（必需）
- `language`: 语言，支持"chinese"或"mongolian"（可选，默认chinese）
- `max_tokens`: 回答的最大长度（可选，默认1024）
- `temperature`: 控制回答的随机性，越高越有创意（可选，默认0.7）

- **响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "response": "高血压患者日常应注意以下几点：\n1. 定期监测血压，保持血压稳定\n2. 合理饮食，减少盐分和脂肪摄入...",
    "time_taken": 3.21
  }
}
```

## 7. 健康文章API

### 7.1 获取文章分类

- **URL**: `/articles/categories`
- **方法**: GET
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "categoryId": 1,
      "name": "心脑血管",
      "icon": "heart.png"
    },
    {
      "categoryId": 2,
      "name": "糖尿病",
      "icon": "diabetes.png"
    },
    // ...更多分类
  ]
}
```

### 7.2 获取文章列表

- **URL**: `/articles`
- **方法**: GET
- **查询参数**: 
  - category: 分类ID（可选）
  - page: 页码（默认1）
  - size: 每页数量（默认10）
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 50,
    "pages": 5,
    "page": 1,
    "size": 10,
    "list": [
      {
        "articleId": 1,
        "title": "高血压患者的日常饮食指南",
        "summary": "介绍高血压患者的饮食禁忌和推荐食物...",
        "coverImage": "https://example.com/images/article1.jpg",
        "author": "张医生",
        "publishTime": "2023-04-15 08:30:00",
        "viewCount": 1250,
        "categoryId": 1,
        "categoryName": "心脑血管"
      },
      // ...更多文章
    ]
  }
}
```

### 7.3 获取文章详情

- **URL**: `/articles/{articleId}`
- **方法**: GET
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "articleId": 1,
    "title": "高血压患者的日常饮食指南",
    "content": "# 高血压患者的日常饮食指南\n\n高血压是一种常见的慢性疾病...",
    "contentFormat": "markdown",  // markdown或html
    "coverImage": "https://example.com/images/article1.jpg",
    "author": "张医生",
    "authorTitle": "心内科主任医师",
    "publishTime": "2023-04-15 08:30:00",
    "updateTime": "2023-04-16 10:15:00",
    "viewCount": 1250,
    "categoryId": 1,
    "categoryName": "心脑血管",
    "tags": ["高血压", "饮食", "健康管理"]
  }
}
```

## 8. 系统API

### 8.1 健康检查

- **URL**: `/health/ping`
- **方法**: GET
- **请求参数**: 无
- **响应**:

```json
{
  "code": 200,
  "message": "服务正常",
  "data": {
    "version": "1.0.0",
    "timestamp": 1683702285
  }
}
```

## 9. 状态码和错误信息

| 状态码 | 消息 | 说明 |
|-------|------|------|
| 200 | 操作成功 | 请求已成功处理 |
| 400 | 请求参数错误 | 请求参数不符合要求 |
| 401 | 未授权访问 | 未登录或令牌已过期 |
| 403 | 权限不足 | 没有权限执行该操作 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 服务器内部错误 | 服务器处理请求时发生错误 |

## 10. 最佳实践

### 10.1 错误处理

前端应捕获所有API请求可能的错误，并给用户友好提示：

```javascript
fetch('/api/user/profile')
  .then(response => response.json())
  .then(result => {
    if (result.code !== 200) {
      // 显示错误提示
      showError(result.message);
      return;
    }
    // 处理成功结果
    processData(result.data);
  })
  .catch(error => {
    // 处理网络错误
    showError('网络请求失败，请检查网络连接');
  });
```

### 10.2 认证处理

对于需要认证的API，应处理认证失败的情况：

```javascript
// 检查认证状态
function checkAuth(result) {
  if (result.code === 401) {
    // 清除本地token
    localStorage.removeItem('token');
    // 跳转到登录页
    window.location.href = '/login';
    return false;
  }
  return true;
}
```

### 10.3 请求拦截器

建议使用请求拦截器统一处理认证信息：

```javascript
// axios拦截器示例
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
``` 