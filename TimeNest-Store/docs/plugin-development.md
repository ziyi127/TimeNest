# TimeNest 插件开发指南

本指南将帮助您创建功能完整的TimeNest插件。

## 快速开始

### 1. 插件结构

每个插件都应该包含以下基本文件：

```
your_plugin/
├── manifest.json    # 插件元数据（必需）
├── plugin.py       # 主插件代码（必需）
├── README.md       # 插件说明文档（推荐）
├── icon.png        # 插件图标，48x48px（可选）
└── screenshots/    # 截图目录（可选）
```

### 2. manifest.json 配置

```json
{
    "id": "your_plugin_id",
    "name": "插件显示名称",
    "version": "1.0.0",
    "description": "插件功能描述",
    "author": "作者名称",
    "plugin_class": "YourPluginClass",
    "plugin_type": "component|utility|theme|integration|notification",
    "api_version": "1.0.0",
    "min_app_version": "1.0.0",
    "max_app_version": "",
    "homepage": "https://your-plugin-homepage.com",
    "repository": "https://github.com/your/repo",
    "license": "Apache-2.0",
    "tags": ["tag1", "tag2", "tag3"],
    "dependencies": [],
    "permissions": [
        "network_access",
        "config_access",
        "notification_access"
    ],
    "settings": {
        "setting_name": {
            "type": "string|integer|boolean|choice",
            "default": "默认值",
            "description": "设置描述",
            "required": false
        }
    }
}
```

### 3. 插件主类

```python
from core.plugin_base import IPlugin, PluginStatus

class YourPluginClass(IPlugin):
    def __init__(self):
        super().__init__()
        self.status = PluginStatus.LOADED
        
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            # 初始化逻辑
            self.status = PluginStatus.INITIALIZED
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            # 激活逻辑
            self.status = PluginStatus.ENABLED
            return True
        except Exception as e:
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            # 停用逻辑
            self.status = PluginStatus.DISABLED
            return True
        except Exception as e:
            return False
    
    def cleanup(self) -> bool:
        """清理资源"""
        try:
            # 清理逻辑
            self.status = PluginStatus.UNLOADED
            return True
        except Exception as e:
            return False
```

## 插件类型

### Component 组件插件
用于在浮窗中显示信息的插件。

**特点：**
- 提供UI组件
- 实时数据更新
- 用户交互

**示例：** 天气插件、时钟插件

### Utility 工具插件
提供实用功能的插件。

**特点：**
- 独立功能模块
- 可能有独立界面
- 后台运行

**示例：** 番茄钟、截图工具

### Theme 主题插件
修改应用外观的插件。

**特点：**
- 样式表管理
- 颜色主题
- 界面美化

**示例：** 深色主题、节日主题

### Integration 集成插件
与第三方服务集成的插件。

**特点：**
- API调用
- 数据同步
- 外部服务

**示例：** 日历同步、邮件通知

### Notification 通知插件
扩展通知功能的插件。

**特点：**
- 通知渠道
- 提醒方式
- 消息处理

**示例：** 语音通知、邮件通知

## 设置系统

### 设置类型

#### string 字符串
```json
"api_key": {
    "type": "string",
    "default": "",
    "description": "API密钥",
    "required": false
}
```

#### integer 整数
```json
"update_interval": {
    "type": "integer",
    "default": 300,
    "min": 60,
    "max": 3600,
    "description": "更新间隔（秒）"
}
```

#### boolean 布尔值
```json
"enabled": {
    "type": "boolean",
    "default": true,
    "description": "启用功能"
}
```

#### choice 选择
```json
"theme": {
    "type": "choice",
    "default": "light",
    "choices": ["light", "dark", "auto"],
    "description": "主题选择"
}
```

### 设置管理

```python
def get_settings(self) -> Dict[str, Any]:
    """获取插件设置"""
    return self.settings.copy()

def update_settings(self, new_settings: Dict[str, Any]) -> bool:
    """更新插件设置"""
    try:
        self.settings.update(new_settings)
        # 应用新设置
        return True
    except Exception as e:
        return False
```

## UI组件开发

### 基本组件

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class YourWidget(QWidget):
    def __init__(self, plugin_instance):
        super().__init__()
        self.plugin = plugin_instance
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Hello, TimeNest!")
        layout.addWidget(self.label)
```

### 信号和槽

```python
from PyQt6.QtCore import pyqtSignal

class YourPlugin(IPlugin):
    # 定义信号
    data_updated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # 连接信号
        self.data_updated.connect(self.on_data_updated)
    
    def on_data_updated(self, data):
        """处理数据更新"""
        pass
```

## 权限系统

### 可用权限

- `network_access` - 网络访问权限
- `config_access` - 配置访问权限
- `notification_access` - 通知权限
- `file_access` - 文件访问权限
- `theme_access` - 主题修改权限

### 权限检查

```python
def check_permission(self, permission: str) -> bool:
    """检查权限"""
    if self.plugin_manager:
        return self.plugin_manager.check_permission(self.get_id(), permission)
    return False
```

## 最佳实践

### 1. 错误处理
```python
try:
    # 可能出错的代码
    pass
except Exception as e:
    self.logger.error(f"操作失败: {e}")
    return False
```

### 2. 资源管理
```python
def cleanup(self) -> bool:
    """清理资源"""
    try:
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
        
        if self.widget:
            self.widget.deleteLater()
        
        return True
    except Exception as e:
        return False
```

### 3. 日志记录
```python
import logging

class YourPlugin(IPlugin):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.YourPlugin')
        
    def some_method(self):
        self.logger.info("执行某个操作")
        self.logger.debug("调试信息")
        self.logger.error("错误信息")
```

### 4. 配置持久化
```python
def save_config(self):
    """保存配置"""
    if self.plugin_manager:
        self.plugin_manager.save_plugin_config(self.get_id(), self.settings)

def load_config(self):
    """加载配置"""
    if self.plugin_manager:
        config = self.plugin_manager.load_plugin_config(self.get_id())
        if config:
            self.settings.update(config)
```

## 测试和调试

### 单元测试
```python
import unittest
from your_plugin import YourPlugin

class TestYourPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = YourPlugin()
    
    def test_initialization(self):
        result = self.plugin.initialize(None)
        self.assertTrue(result)
    
    def test_settings(self):
        settings = self.plugin.get_settings()
        self.assertIsInstance(settings, dict)
```

### 调试模式
```python
if __name__ == "__main__":
    # 调试代码
    plugin = YourPlugin()
    plugin.initialize(None)
    plugin.activate()
```

## 发布流程

### 1. 准备发布
- 完善README文档
- 添加截图和图标
- 测试所有功能
- 更新版本号

### 2. 创建发布包
```bash
cd your_plugin
zip -r ../your_plugin_v1.0.0.zip .
```

### 3. 提交到仓库
- Fork TimeNest-Store仓库
- 添加插件到plugins目录
- 更新plugins.json
- 创建Pull Request

## 示例插件

参考仓库中的示例插件：
- `weather_enhanced` - 组件插件示例
- `pomodoro_timer` - 工具插件示例
- `dark_theme` - 主题插件示例
- `calendar_sync` - 集成插件示例

## 支持和帮助

- [GitHub Issues](https://github.com/ziyi127/TimeNest-Store/issues)
- [开发者论坛](https://github.com/ziyi127/TimeNest-Store/discussions)
- [API文档](api-reference.md)
