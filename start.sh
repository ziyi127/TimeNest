#!/bin/bash

# TimeNest 启动脚本

echo "启动 TimeNest 应用程序..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 运行应用程序
echo "运行 TimeNest..."
python main.py

echo "TimeNest 已退出"
