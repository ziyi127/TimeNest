@echo off
REM TimeNest 启动脚本 (Windows)

echo 启动 TimeNest 应用程序...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 无法创建虚拟环境
        pause
        exit /b 1
    )
    
    echo 激活虚拟环境并安装依赖...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo 错误: 无法激活虚拟环境
        pause
        exit /b 1
    )
    
    if exist requirements.txt (
        pip install -r requirements.txt
        if errorlevel 1 (
            echo 错误: 无法安装依赖
            pause
            exit /b 1
        )
    ) else (
        echo 警告: 未找到requirements.txt文件
    )
) else (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo 错误: 无法激活虚拟环境
        pause
        exit /b 1
    )
)

REM 运行应用程序
echo 运行 TimeNest...
python main.py
if errorlevel 1 (
    echo 错误: TimeNest运行失败
    pause
    exit /b 1
)

echo TimeNest 已退出
pause