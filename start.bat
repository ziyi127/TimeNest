@echo off
REM TimeNest 启动脚本 (Windows)

echo 启动 TimeNest 应用程序...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    echo 激活虚拟环境并安装依赖...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 运行应用程序
echo 运行 TimeNest...
python main.py

echo TimeNest 已退出
pause