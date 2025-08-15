#!/bin/bash

# 检查Python是否安装
if ! command -v python3 &> /dev/null
then
    echo "错误: 未找到Python。请先安装Python 3.8或更高版本�?
    read -p "按Enter键退�?.."
    exit 1
fi

# 检查是否已创建虚拟环境
if [ ! -d "venv" ]
then
    echo "创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]
    then
        echo "错误: 创建虚拟环境失败�?
        read -p "按Enter键退�?.."
        exit 1
    fi
fi

# 激活虚拟环�?echo "激活虚拟环�?.."
source venv/bin/activate

# 安装依赖�?echo "安装依赖�?.."
pip install -r requirements.txt
if [ $? -ne 0 ]
then
    echo "错误: 安装依赖项失败�?
    read -p "按Enter键退�?.."
    exit 1
fi

# 启动应用程序
echo "启动TimeNest课表软件..."
python main.py

# 退出虚拟环�?deactivate

read -p "按Enter键退�?.."
