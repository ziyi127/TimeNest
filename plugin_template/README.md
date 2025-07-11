# TimeNest 插件模板

这是一个 TimeNest 插件开发模板，提供了插件开发的基础结构和示例代码。

## 📋 功能特性

- ✅ 完整的插件生命周期管理
- ✅ 事件系统集成
- ✅ 配置管理
- ✅ 日志记录
- ✅ 错误处理
- ✅ 资源管理

## 🚀 快速开始

### 1. 复制模板

```bash
cp -r plugin_template my_awesome_plugin
cd my_awesome_plugin
```

### 2. 修改插件信息

编辑 `plugin.json` 文件：

```json
{
  "id": "my_awesome_plugin",
  "name": "我的超棒插件",
  "version": "1.0.0",
  "description": "这是一个超棒的插件",
  "author": "Your Name"
}
```

### 3. 实现插件功能

编辑 `main.py` 文件，在相应的方法中实现您的插件功能：

- `_start_plugin_functionality()`: 启动插件功能
- `_register_ui_components()`: 注册 UI 组件
- `_start_background_tasks()`: 启动后台任务

### 4. 测试插件

```bash
# 将插件复制到 TimeNest 插件目录
cp -r my_awesome_plugin ~/.timenest/plugins/

# 启动 TimeNest 并在插件管理器中启用插件
```

## 📁 文件结构

```
plugin_template/
├── plugin.json          # 插件清单文件
├── main.py              # 主模块文件
├── README.md            # 说明文档
├── CHANGELOG.md         # 更新日志
├── requirements.txt     # Python 依赖
└── tests/               # 测试文件
    └── test_main.py
```

## 🔧 开发指南

### 插件配置

插件支持以下配置项：

- `enabled`: 是否启用插件
- `example_setting`: 示例设置项

您可以通过以下方式访问配置：

```python
# 获取配置
value = self.get_setting('example_setting', '默认值')

# 设置配置
self.set_setting('example_setting', '新值')
```

### 事件处理

插件会自动订阅以下系统事件：

- `app_started`: 应用启动
- `app_closing`: 应用关闭
- `schedule_changed`: 课程表变更

您可以在相应的事件处理方法中添加自己的逻辑。

### 数据存储

插件提供了便捷的数据存储方法：

```python
# 获取数据文件路径
data_file = self.get_data_file_path('my_data.json')

# 保存数据
import json
with open(data_file, 'w') as f:
    json.dump(data, f)
```

## 🧪 测试

运行插件测试：

```bash
python -m pytest tests/
```

## 📦 打包

使用提供的构建脚本打包插件：

```bash
python build.py
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如果您在开发过程中遇到问题，可以：

- 查看 [插件开发指南](../PLUGIN_DEVELOPMENT_GUIDE.md)
- 提交 [GitHub Issue](https://github.com/ziyi127/TimeNest/issues)
- 发送邮件到 [ziyihed@outlook.com](mailto:ziyihed@outlook.com)
