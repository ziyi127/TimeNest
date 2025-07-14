# TimeNest 安装指南

## 概述

TimeNest 提供了两种安装程序：

1. **标准安装程序** (`install.py`) - 基础安装功能

2. **增强版增安装程序** (`install_enhanced.py`) - 包含自动故障处理和多环境支持

## 增强版增安装程序特性

### 🚀 自动环境检测
- 自动检测操作系统类型（Windows、Linux、macOS）
- 识别特殊环境（WSL、Docker、Conda）
- 智能选择最适合的安装策略

### 🛠️ 自动故障处理
- **pip安装失败恢复**：自动尝试不同镜像源、清理缓存
- **虚拟环境创建失败恢复**：自动清理并重试、使用virtualenv备选方案
- **权限问题恢复**：自动使用--user参数重试
- **网络错误恢复**：等待网络恢复并重试
- **依赖冲突恢复**：强制重新安装冲突包

### 🎯 多环境预设

#### Windows 标准环境
- 适用于标准Windows Python环境
- 自动处理权限问题
- 建议使用--user参数安装

#### Windows Conda环境
- 专为Anaconda/Miniconda优化
- 自动更新conda和pip
- 使用conda channels

#### Linux 标准环境
- 支持Ubuntu、CentOS、Debian等
- 自动安装系统依赖
- 配置Qt环境变量

#### WSL环境
- Windows Subsystem for Linux专用
- 自动配置X11转发
- 安装必要的系统包

#### macOS环境
- 支持Homebrew Python
- 处理Xcode命令行工具依赖
- 兼容Apple Silicon

#### Docker环境
- 容器化部署优化
- 无头模式运行
- 最小化镜像大小

## 使用方法

### 方法1：GUI模式（推荐）

```bash
python install_enhanced.py
```

GUI界面包含三个标签页：

1. **基本选项**
   - 创建虚拟环境
   - 升级pip
   - 选择依赖文件

2. **高级选项**
   - 环境信息显示
   - 安装策略配置
   - 镜像源选择

3. **故障排除**
   - 环境诊断工具
   - 缓存清理
   - 网络连接测试

### 方法2：命令行模式

如果PyQt6不可用，程序会自动切换到命令行模式：

```bash
python install_enhanced.py
```

### 方法3：标准安装程序

```bash
python install.py
```

## 故障排除

### 常见问题及解决方案

#### 1. PyQt6安装失败
**症状**：`ImportError: No module named 'PyQt6'`

**解决方案**：
```bash
# 方法1：升级pip
python -m pip install --upgrade pip
python -m pip install PyQt6

# 方法2：使用国内镜像
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ PyQt6

# 方法3：使用conda
conda install pyqt
```

#### 2. 权限拒绝错误
**症状**：`PermissionError: [Errno 13] Permission denied`

**解决方案**：
```bash
# Windows：使用--user参数
python -m pip install --user package_name

# Linux/macOS：使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

#### 3. 网络连接问题
**症状**：`Could not fetch URL` 或连接超时

**解决方案**：
```bash
# 使用国内镜像源
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name

# 或配置pip.conf
mkdir ~/.pip
echo "[global]" > ~/.pip/pip.conf
echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple/" >> ~/.pip/pip.conf
echo "trusted-host = pypi.tuna.tsinghua.edu.cn" >> ~/.pip/pip.conf
```

#### 4. 虚拟环境创建失败
**症状**：`Error: Unable to create virtual environment`

**解决方案**：
```bash
# 方法1：使用virtualenv
python -m pip install virtualenv
python -m virtualenv venv

# 方法2：检查Python安装
python --version
python -m venv --help

# 方法3：清理现有目录
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

#### 5. 依赖冲突
**症状**：`ERROR: pip's dependency resolver does not currently consider all the packages`

**解决方案**：
```bash
# 强制重新安装
python -m pip install --force-reinstall package_name

# 或使用--no-deps跳过依赖检查
python -m pip install --no-deps package_name
```

### 环境特定问题

#### WSL环境
```bash
# 安装X11服务器支持
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
sudo apt-get install -y qt6-base-dev

# 配置显示
export DISPLAY=:0
```

#### Docker环境
```bash
# 使用无头模式
export QT_QPA_PLATFORM=offscreen

# 或安装虚拟显示
apt-get install -y xvfb
xvfb-run -a python main.py
```

#### macOS环境
```bash
# 安装Xcode命令行工具
xcode-select --install

# 使用Homebrew安装Python
brew install python
```

## 高级配置

### 自定义镜像源
创建 `pip.conf` 文件：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 60
retries = 3
```

### 环境变量配置
```bash
# Linux/macOS
export QT_QPA_PLATFORM=xcb
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Windows
set QT_QPA_PLATFORM=windows
set PYTHONPATH=%PYTHONPATH%;%CD%
```

### 虚拟环境最佳实践
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
python -m pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

## 技术支持

如果遇到安装问题：

1. 查看安装日志文件 `install.log`
2. 运行环境诊断工具
3. 查看故障排除标签页
4. 提交Issue到GitHub仓库

## 更新日志

### v1.1.2 Preview
- 新增增强版安装程序
- 添加自动故障处理功能
- 支持多种环境预设
- 改进错误恢复机制
- 优化用户界面体验
