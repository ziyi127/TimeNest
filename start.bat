@echo off

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Python。请先安装Python 3.8或更高版本。
    pause
    exit /b 1
)

:: 检查是否已创建虚拟环境
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 错误: 创建虚拟环境失败。
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 安装依赖项
 echo 安装依赖项...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 安装依赖项失败。
    pause
    exit /b 1
)

:: 启动应用程序
 echo 启动TimeNest课表软件...
python main.py

:: 退出虚拟环境
deactivate

pause