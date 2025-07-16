@echo off
chcp 65001 >nul
echo TimeNest Release Creator
echo ========================================
echo.

REM 检查是否在 Git 仓库中
git status >nul 2>&1
if errorlevel 1 (
    echo 错误: 当前目录不是 Git 仓库
    pause
    exit /b 1
)

REM 检查工作目录状态
for /f %%i in ('git status --porcelain') do (
    echo 警告: 工作目录有未提交的更改
    echo 请先提交所有更改后再创建发布
    pause
    exit /b 1
)

REM 获取当前版本
set "version="
if exist "app_info.json" (
    for /f "tokens=2 delims=:" %%a in ('findstr "number" app_info.json') do (
        set "line=%%a"
        setlocal enabledelayedexpansion
        set "version=!line:"=!"
        set "version=!version: =!"
        set "version=!version:,=!"
        endlocal & set "version=!version!"
    )
)

if defined version (
    echo 当前版本: %version%
    set /p "use_current=使用当前版本 %version% 创建发布? (y/n): "
    if /i "!use_current!"=="y" (
        set "new_version=%version%"
    ) else (
        set /p "new_version=请输入新版本号 (例如: 2.1.0): "
    )
) else (
    set /p "new_version=请输入版本号 (例如: 2.1.0): "
)

REM 验证版本号格式
echo %new_version% | findstr /r "^[0-9]\+\.[0-9]\+\.[0-9]\+\(-[a-zA-Z0-9]\+\)\?$" >nul
if errorlevel 1 (
    echo 错误: 版本号格式无效
    echo 正确格式: x.y.z 或 x.y.z-suffix (例如: 2.1.0 或 2.1.0-Preview)
    pause
    exit /b 1
)

set "tag_name=v%new_version%"

echo.
echo 即将创建发布:
echo 版本: %new_version%
echo 标签: %tag_name%
echo.

set /p "confirm=确认创建? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b 0
)

REM 检查标签是否已存在
git tag -l %tag_name% | findstr %tag_name% >nul
if not errorlevel 1 (
    echo 错误: 标签 %tag_name% 已存在
    pause
    exit /b 1
)

REM 创建标签
echo 创建标签 %tag_name%...
git tag -a %tag_name% -m "Release %new_version%"
if errorlevel 1 (
    echo 错误: 创建标签失败
    pause
    exit /b 1
)

REM 推送标签
echo 推送标签到远程仓库...
git push origin %tag_name%
if errorlevel 1 (
    echo 错误: 推送标签失败
    pause
    exit /b 1
)

echo.
echo ✅ 发布创建成功!
echo GitHub Actions 将自动构建并发布 TimeNest %new_version%
echo 请访问 GitHub 仓库查看构建进度
echo.
pause
