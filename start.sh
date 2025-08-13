#!/bin/bash

# TimeNest 启动脚本

echo "启动 TimeNest 应用程序..."

# 检查是否在WSL环境中运行
is_wsl() {
    if [[ -f /proc/version ]] && grep -q Microsoft /proc/version; then
        return 0
    else
        return 1
    fi
}

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    # 检查可用的Python命令
    PYTHON_CMD=""
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        echo "错误: 未找到Python命令"
        exit 1
    fi
    
    # 创建虚拟环境
    if ! $PYTHON_CMD -m venv venv; then
        echo "错误: 无法创建虚拟环境"
        exit 1
    fi
    
    echo "激活虚拟环境并安装依赖..."
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo "错误: 未找到虚拟环境激活脚本"
        exit 1
    fi
    
    # 检查pip是否可用
    if ! command -v pip >/dev/null 2>&1; then
        echo "错误: pip不可用"
        exit 1
    fi
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        if ! pip install -r requirements.txt; then
            echo "错误: 无法安装依赖"
            exit 1
        fi
    else
        echo "警告: 未找到requirements.txt文件"
    fi
else
    echo "激活虚拟环境..."
    # 激活虚拟环境
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo "错误: 未找到虚拟环境激活脚本"
        exit 1
    fi
fi

# 运行应用程序
echo "运行 TimeNest..."
if ! python main.py; then
    echo "错误: TimeNest运行失败"
    exit 1
fi

echo "TimeNest 已退出"