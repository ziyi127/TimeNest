@echo off
echo ========================================
echo TimeNest Release Builder
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt
pip install pyinstaller

REM 清理旧的构建文件
echo 清理旧文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "TimeNest-portable" rmdir /s /q "TimeNest-portable"
if exist "*.zip" del "*.zip"

REM 构建可执行文件
echo 构建可执行文件...
pyinstaller TimeNest.spec --clean --noconfirm

if not exist "dist\TimeNest.exe" (
    echo 错误: 构建失败
    pause
    exit /b 1
)

REM 创建便携版目录
echo 创建便携版包...
mkdir "TimeNest-portable"
copy "dist\TimeNest.exe" "TimeNest-portable\"
copy "README.md" "TimeNest-portable\"
copy "LICENSE" "TimeNest-portable\"
xcopy /E /I "config" "TimeNest-portable\config"
xcopy /E /I "resources" "TimeNest-portable\resources"
xcopy /E /I "plugin_template" "TimeNest-portable\plugin_template"

REM 创建ZIP包
echo 创建ZIP包...
powershell -Command "Compress-Archive -Path 'TimeNest-portable\*' -DestinationPath 'TimeNest-portable.zip' -Force"

echo.
echo ========================================
echo 构建完成!
echo 可执行文件: dist\TimeNest.exe
echo 便携版包: TimeNest-portable.zip
echo ========================================
pause