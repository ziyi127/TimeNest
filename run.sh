#!/bin/bash

# TimeNest 课程表桌面应用启动脚本

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否已安装
if [ ! -f "venv/installed" ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
    touch venv/installed
fi

# 运行程序
echo "正在启动 TimeNest 课程表应用..."
python main.py