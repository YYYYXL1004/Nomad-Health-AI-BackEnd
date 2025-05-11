# 敕勒云诊后端服务

## 项目介绍

敕勒云诊是一个基于Vue3+Flask实现的跨平台应用，旨在为内蒙古地区的牧民提供便捷的医疗健康服务。平台支持中蒙双语，实现了健康咨询、在线问诊、健康报告查看等核心功能。本仓库为项目的后端部分。

## 技术栈

- **Web框架**: Flask 2.3.3
- **ORM**: SQLAlchemy 2.0.20, Flask-SQLAlchemy 3.1.1
- **认证**: Flask-JWT-Extended 4.5.3
- **数据库**: SQLite (开发环境), PostgreSQL (生产环境)
- **其他**: Flask-CORS, Gunicorn, Pillow, pytest等

## 功能模块

项目后端主要包含以下功能模块：

- **用户认证模块**：用户注册、登录、密码重置等功能
- **用户信息模块**：用户个人资料管理
- **健康咨询模块**：提供在线问诊、医生咨询等功能
- **健康报告模块**：健康数据记录与查询功能
- **文章管理模块**：健康资讯与知识库管理
- **系统设置模块**：平台配置与参数设置

## 目录结构

```
├── src/                # 源代码目录
│   ├── config/         # 配置文件
│   ├── extensions/     # Flask扩展
│   ├── models/         # 数据模型
│   ├── routes/         # API路由
│   ├── utils/          # 工具函数
│   └── app.py          # 应用入口
├── instance/           # 实例文件夹（包含本地配置和数据库文件）
├── docs/               # 项目文档
├── docker/             # Docker相关文件
├── tests/              # 测试文件
├── requirements.txt    # 依赖包列表
├── run.py              # 应用启动脚本
└── entrypoint.sh       # Docker入口脚本
```

## 安装与部署

### 环境要求

- Python 3.8+
- pip 包管理工具

### 本地开发环境部署

1. 克隆代码仓库

```bash
git clone <仓库地址>
cd 敕勒云诊后端
```

2. 创建并激活虚拟环境

```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/MacOS
source env/bin/activate
```

3. 安装依赖包

```bash
# 使用国内镜像源安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

4. 初始化数据库

```bash
python reset_db.py  # 重置数据库
python init_consult_tables.py  # 初始化咨询相关表
python init_health_tables.py  # 初始化健康相关表
python init_article_tables.py  # 初始化文章相关表
```

5. 启动应用

```bash
python run.py
```

应用将在 http://localhost:5000 上运行。

### Docker部署

1. 构建Docker镜像

```bash
docker build -t chileer-health-backend .
```

2. 运行容器

```bash
docker run -d -p 5000:5000 chileer-health-backend
```

## API文档

API文档请参考项目中的 `openapi.json` 文件或 `docs` 目录下的相关文档。

## 单元测试

运行单元测试：

```bash
pytest test_consult_api.py
pytest test_register.py
pytest api_test.py
```

## 多语言支持

系统支持中文和蒙古语双语界面，通过用户设置的语言偏好提供相应的内容。

## 项目贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 [MIT 许可证](LICENSE)

## 联系方式

项目维护者: 您的名字 - 邮箱地址

---

© 2023 敕勒云诊. 保留所有权利. 