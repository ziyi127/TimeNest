# TimeNest 安装指南

## 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Linux (主流发行版)
- **内存**: 建议 4GB 以上
- **存储**: 至少 500MB 可用空间

## 安装方式

### 1. 标准安装（推荐）

```bash
# 克隆项目
git clone https://github.com/ziyi127/TimeNest.git
cd TimeNest

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 最小安装

如果只需要基本功能，可以使用最小依赖：

```bash
pip install -r requirements-minimal.txt
```

**注意**: 最小安装将缺少以下功能：
- Excel 导入导出
- 数据分析功能
- 性能监控
- 错误监控
- 图像处理
- 彩色日志

### 3. 开发环境安装

如果需要进行开发或贡献代码：

```bash
# 安装核心依赖 + 开发工具
pip install -r requirements-dev.txt

# 或者使用 setup.py
pip install -e .[dev]
```

### 4. 生产环境安装

生产环境推荐使用固定版本：

```bash
pip install -r requirements-prod.txt
```

### 5. 使用 setup.py 安装

```bash
# 基础安装
pip install .

# 包含开发工具
pip install .[dev]

# 包含构建工具
pip install .[build]

# 包含文档工具
pip install .[docs]

# 完整安装
pip install .[dev,build,docs,security]
```

## 依赖文件说明

| 文件 | 用途 | 包含内容 |
|------|------|----------|
| `requirements.txt` | 核心运行时依赖 | 应用运行必需的包 |
| `requirements-minimal.txt` | 最小依赖 | 仅核心功能所需 |
| `requirements-dev.txt` | 开发依赖 | 开发、测试、构建工具 |
| `requirements-prod.txt` | 生产依赖 | 固定版本的生产环境依赖 |

## 验证安装

```bash
# 检查依赖
python -c "import PyQt6, yaml, requests; print('核心依赖正常')"

# 运行应用
python main.py

# 运行测试（如果安装了开发依赖）
pytest tests/
```

## 常见问题

### Q: PyQt6 安装失败
A: 
```bash
# 尝试更新 pip
pip install --upgrade pip

# 或使用 conda
conda install pyqt
```

### Q: 在 Linux 上缺少系统依赖
A:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6 python3-pyqt6.qtmultimedia

# CentOS/RHEL
sudo yum install python3-qt6

# Arch Linux
sudo pacman -S python-pyqt6
```

### Q: macOS 上权限问题
A:
```bash
# 使用 --user 安装
pip install --user -r requirements.txt

# 或使用 Homebrew Python
brew install python
```

## 更新依赖

```bash
# 更新到最新版本
pip install --upgrade -r requirements.txt

# 检查过时的包
pip list --outdated

# 使用 pip-tools 管理依赖（如果安装了开发依赖）
pip-compile requirements.in
pip-sync requirements.txt
```

## 卸载

```bash
# 如果使用虚拟环境，直接删除环境目录
rm -rf venv

# 或者卸载包
pip uninstall TimeNest

# 清理配置文件（可选）
rm -rf ~/.timenest
```
