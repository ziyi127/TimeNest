# TimeNest 课程表软件部署文档

## 1. 系统要求说明

### 1.1 操作系统要求
TimeNest 可以在以下操作系统上运行：
- Windows 10 或更高版本
- macOS 10.15 (Catalina) 或更高版本
- Linux (Ubuntu 20.04 LTS 或更高版本，CentOS 8 或更高版本)

### 1.2 Python 版本要求
- Python 3.8 或更高版本

### 1.3 依赖库
TimeNest 使用以下 Python 标准库和第三方库：
- `json` (Python 标准库) - JSON 数据处理
- `os`, `pathlib` (Python 标准库) - 文件系统操作
- `logging` (Python 标准库) - 日志记录
- `datetime` (Python 标准库) - 日期时间处理
- `shutil` (Python 标准库) - 高级文件操作
- `re` (Python 标准库) - 正则表达式处理

## 2. 安装步骤

### 2.1 从源码安装

1. 克隆或下载 TimeNest 源码到本地目录
2. 确保系统已安装 Python 3.8 或更高版本
3. 进入项目根目录
4. 创建虚拟环境（可选但推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows
   ```
5. 安装依赖（如果项目有 requirements.txt 文件）：
   ```bash
   pip install -r requirements.txt
   ```

### 2.2 从包安装

目前 TimeNest 不提供预编译的安装包，建议直接从源码安装。

## 3. 环境配置

### 3.1 环境变量
TimeNest 支持以下环境变量配置：
- `TIMENEST_DATA_DIR`：数据存储目录，默认为 `./data`
- `TIMENEST_LOG_LEVEL`：日志级别，默认为 `INFO`

### 3.2 配置文件
TimeNest 使用 JSON 文件作为配置文件，配置文件位于 `data/` 目录下：
- `user_settings.json`：用户设置配置
- `class_plans.json`：课程表数据
- `plugins.json`：插件配置

## 4. 启动和停止应用的步骤

### 4.1 启动应用
在项目根目录下执行以下命令启动应用：
```bash
python launcher.py
```

如果是 Web 应用，可能需要启动 Flask 服务器：
```bash
python app.py
```

### 4.2 停止应用
- 在终端中按 `Ctrl+C` 停止应用
- 如果应用在后台运行，可以使用 `kill` 命令停止进程

## 5. 故障排除指南

### 5.1 常见问题及解决方案

#### 问题1：Python 版本不兼容
**错误信息**：`SyntaxError` 或 `ImportError`
**解决方案**：确保使用 Python 3.8 或更高版本运行应用。

#### 问题2：缺少依赖库
**错误信息**：`ModuleNotFoundError`
**解决方案**：安装缺失的依赖库：
```bash
pip install -r requirements.txt
```

#### 问题3：数据目录权限问题
**错误信息**：`PermissionError`
**解决方案**：确保应用有权限读写数据目录，可以修改 `data/` 目录的权限或更改 `TIMENEST_DATA_DIR` 环境变量指向有权限的目录。

#### 问题4：JSON 文件格式错误
**错误信息**：`json.JSONDecodeError`
**解决方案**：检查对应的 JSON 配置文件格式是否正确，确保使用有效的 JSON 格式。

### 5.2 日志查看
TimeNest 会将日志记录到 `logs/` 目录下，可以通过查看日志文件来诊断问题：
- `logs/course_service.log`：课程服务日志
- `logs/schedule_service.log`：课程表服务日志
- `logs/temp_change_service.log`：临时换课服务日志
- `logs/cycle_schedule_service.log`：循环课程表服务日志
- `logs/business_coordinator.log`：业务协调器日志
- `logs/PluginManager.log`：插件管理器日志

### 5.3 数据备份和恢复
如果遇到数据损坏问题，可以从备份文件恢复：
1. 查找备份文件：在 `data/backups/` 目录下查找最新的备份文件
2. 将备份文件复制到 `data/` 目录下替换原文件