# 构建和发布系统说明

## 概述

TimeNest使用GitHub Actions实现自动构建和发布系统。当推送新的git标签时，系统会自动为Windows、Linux和macOS平台构建可执行文件，并创建GitHub Release发布版本。

## 触发条件

### 自动触发
- 当推送符合`v*`格式的git标签时（例如`v1.0.0`）
- 仅在main分支上推送标签时触发

### 手动触发
- 项目维护者可以通过GitHub Actions界面手动触发构建

## 支持的平台和发行版

### Windows
- 构建环境: Windows Server 2019 (windows-latest)
- 架构: x64
- 输出格式: ZIP便携包

### Linux
- 构建环境: Ubuntu 20.04 (ubuntu-latest)
- 架构: x86_64
- 支持的发行版系列:
  - **Debian系**: Ubuntu, Debian (输出DEB包)
  - **Red Hat系**: Fedora, CentOS (输出RPM包)
  - **Arch系**: Arch Linux (输出PKG包)
  - **通用**: 适用于所有Linux发行版的TAR.GZ便携包

### macOS
- 构建环境: macOS最新版本 (macos-latest)
- 架构: x86_64, arm64
- 输出格式: ZIP包

## 构建流程

### 1. 代码检出
- 使用`actions/checkout@v4`检出代码

### 2. Python环境设置
- 使用`actions/setup-python@v5`设置Python 3.11环境

### 3. 依赖安装
- 安装项目依赖: `pip install -r requirements.txt`
- 安装构建工具: `pip install pyinstaller`

### 4. 可执行文件构建
- 使用PyInstaller构建单文件可执行程序
- Windows: `pyinstaller --onefile --windowed --name TimeNest main.py`
- Linux: `pyinstaller --onefile --windowed --name TimeNest main.py`
- macOS: `pyinstaller --onefile --windowed --name TimeNest main.py`

### 5. 包装和分发
- 将可执行文件和必要的资源文件打包
- 为不同平台创建相应的安装包格式
- 上传到GitHub Release

## 创建新版本

### 1. 更新版本号
1. 更新代码中的版本号
2. 提交更改到main分支

### 2. 创建和推送标签
```bash
# 创建标签
git tag v1.0.0

# 推送标签
git push origin v1.0.0
```

### 3. 等待构建完成
- GitHub Actions会自动开始构建流程
- 可以在Actions选项卡中查看构建进度

### 4. 检查发布
- 构建完成后会自动创建GitHub Release
- 所有平台的构建产物会自动上传到Release中

## 手动触发构建

项目维护者可以手动触发构建流程：

1. 进入GitHub仓库的"Actions"选项卡
2. 选择"Build and Release"工作流
3. 点击"Run workflow"按钮
4. 选择要构建的分支（通常是main）
5. 点击"Run workflow"确认

## 故障排除

### 构建失败
- 检查Actions日志以获取详细错误信息
- 确保所有依赖项都能正确安装
- 验证PyInstaller构建命令是否正确

### 依赖问题
- 确保`requirements.txt`包含所有必要的依赖项
- 对于PySide6等大型依赖，可能需要增加构建超时时间

### 平台特定问题
- Windows: 确保正确设置图标和资源文件路径
- Linux: 确保所有必要的系统库都已安装
- macOS: 确保正确设置应用 bundle 信息

## 自定义构建

### 修改构建配置
- 编辑`.github/workflows/release.yml`文件
- 调整构建矩阵以支持更多平台或架构
- 修改PyInstaller参数以优化构建输出

### 添加新平台
1. 在工作流文件中添加新的job
2. 配置适当的构建环境
3. 实现平台特定的打包逻辑
4. 更新文档说明

## 最佳实践

### 版本控制
- 使用语义化版本控制（SemVer）
- 在标签推送前确保代码稳定

### 依赖管理
- 定期更新`requirements.txt`
- 锁定关键依赖的版本以确保构建一致性

### 构建优化
- 使用`.spec`文件优化PyInstaller构建
- 排除不必要的模块以减小文件大小
- 启用UPX压缩以进一步减小文件大小