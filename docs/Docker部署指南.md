# 牧民健康应用Docker部署指南

本文档提供了如何使用Docker和Docker Compose在本地部署牧民健康应用后端的详细步骤。

## 前提条件

在开始部署前，请确保你的系统已安装以下软件：

- [Docker](https://docs.docker.com/get-docker/) (20.10.0或更高版本)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0.0或更高版本)

你可以通过以下命令检查版本：

```bash
docker --version
docker-compose --version
```

## 部署步骤

### 1. 获取项目代码

将代码克隆到本地：

```bash
git clone https://github.com/yourusername/nomadcare-backend.git
cd nomadcare-backend
```

或者直接下载项目压缩包并解压。

### 2. 配置环境变量（可选）

在项目根目录创建`.env`文件，用于自定义配置。以下是一个示例：

```
# JWT密钥配置
JWT_SECRET_KEY=your-secret-key-here

# 讯飞语音识别API配置（如果有）
XUNFEI_API_KEY=your-xunfei-api-key
XUNFEI_API_SECRET=your-xunfei-api-secret

# 千问医疗模型API配置
# 如果需要使用真实的医疗模型（校园网内可用）
QWEN_API_URL=http://183.175.12.124:8000
USE_MOCK_MEDICAL_MODEL=false

# 或者使用模拟模式（校园网外使用）
# USE_MOCK_MEDICAL_MODEL=true
```

> **注意**：如果不创建`.env`文件，系统将使用docker-compose.yml中的默认值。

### 3. 构建和启动服务

在项目根目录执行以下命令：

```bash
# 构建镜像并启动所有服务
docker-compose up -d

# 查看容器日志
docker-compose logs -f
```

这将启动以下服务：
- **app**: 牧民健康应用后端API服务
- **db**: PostgreSQL数据库

首次启动时，Docker会：
1. 构建后端API镜像
2. 创建网络和数据卷
3. 启动所有服务

### 4. 验证部署

服务启动后，可通过以下方式验证部署是否成功：

```bash
# 检查容器状态
docker-compose ps

# 测试API是否可访问（应返回pong）
curl http://localhost:5000/api/health/ping
```

应用API现在应该可以通过 `http://localhost:5000/api` 访问。

### 5. 运行测试（可选）

如果你想验证API的功能，可以运行测试套件：

```bash
# 运行所有API测试
docker-compose --profile test up
```

## 常用操作

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 查看日志

```bash
# 查看所有服务的日志
docker-compose logs -f

# 只查看应用日志
docker-compose logs -f app
```

### 进入容器

```bash
# 进入应用容器
docker exec -it nomadcare-backend bash

# 进入数据库容器
docker exec -it nomadcare-db bash
```

### 数据库操作

连接到PostgreSQL数据库：

```bash
docker exec -it nomadcare-db psql -U postgres -d nomadcare
```

### 重新构建镜像

如果代码有更新，需要重新构建镜像：

```bash
docker-compose build
docker-compose up -d
```

## 数据持久化

系统使用Docker卷进行数据持久化：

- **postgres_data**: 存储PostgreSQL数据库文件
- **./static/uploads**: 存储用户上传的文件（头像、语音等）

这意味着即使容器被删除，数据也会保留。

## 生产环境部署注意事项

对于生产环境部署，请注意以下几点：

1. **安全性配置**:
   - 使用强密码和JWT密钥
   - 配置HTTPS
   - 限制数据库访问

2. **性能优化**:
   - 调整Gunicorn工作进程和线程数
   - 考虑使用Nginx作为反向代理
   - 配置适当的资源限制

3. **监控与日志**:
   - 集成监控工具
   - 配置集中式日志管理

## 故障排除

### 1. 服务无法启动

检查错误日志：

```bash
docker-compose logs app
```

常见问题：
- 端口冲突：确保5000和5432端口未被占用
- 权限问题：检查volumes挂载权限

### 2. 数据库连接失败

检查数据库状态和连接信息：

```bash
# 检查数据库容器是否运行
docker-compose ps db

# 检查数据库日志
docker-compose logs db
```

### 3. API无响应

检查应用是否正常运行：

```bash
# 检查应用日志
docker-compose logs app

# 检查应用健康状态
curl http://localhost:5000/api/health/ping
```

## 使用离线模式

如果你无法访问千问医疗模型API（校园网外），请确保`USE_MOCK_MEDICAL_MODEL`环境变量设置为`true`。这样系统将使用模拟响应代替实际调用医疗模型。 