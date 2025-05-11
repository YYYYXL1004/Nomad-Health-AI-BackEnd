#!/bin/bash 
. bin/activate 

# 创建数据库表并启动应用
python -c "from app import create_app; app = create_app()"
gunicorn --bind 0.0.0.0:5000 "app:create_app()" 
