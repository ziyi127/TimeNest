# TimeNest 插件开发指南

## 概述

TimeNest 提供了一套完整的插件接口系统，允许开发者扩展应用程序的功能。通过这些接口，插件可以在托盘菜单、悬浮窗和设置窗口中添加自定义功能和内容。

## 插件架构

TimeNest 插件系统基于 Qt 的信号槽机制和面向对象设计。插件可以通过应用程序实例访问核心组件，并通过预定义的接口与用户界面进行交互。

### 核心组件

TimeNest 插件系统提供了以下核心组件的访问接口：

1. **托盘图标 (TrayIcon)**: 允许插件添加自定义菜单项到系统托盘菜单
2. **悬浮窗 (FloatingWindow)**: 允许插件在悬浮窗中添加自定义内容
3. **设置窗口 (SettingsWindow)**: 允许插件添加自定义设置页面
4. **主窗口 (MainWindow)**: 提供对主应用程序窗口的访问
5. **课程服务 (LessonsService)**: 提供对课程数据和服务的访问
6. **时间服务 (TimeService)**: 提供对时间相关功能的访问
7. **主题管理器 (ThemeManager)**: 提供对应用程序主题和样式的访问

### 接口设计原则

TimeNest 插件接口遵循以下设计原则：

1. **简洁性**: 接口设计简单明了，易于理解和使用
2. **一致性**: 所有接口遵循统一的命名和使用规范
3. **安全性**: 接口提供了适当的错误处理和资源管理机制
4. **可扩展性**: 接口设计考虑了未来功能的扩展需求
5. **稳定性**: 接口保持向后兼容性，避免破坏性变更

## 插件开发基础

### 插件类结构

插件应该实现一个包含以下方法的类：

```python
class TimeNestPlugin:
    def initialize(self, app):
        """
        插件初始化方法
        :param app: TimeNestApplication 实例
        """
        pass
    
    def cleanup(self):
        """
        插件清理方法，在插件注销时调用
        """
        pass
```

### 插件注册和管理

插件需要通过应用程序实例进行注册：

```python
# 注册插件
app.register_plugin("插件名称", plugin_instance)

# 注销插件
app.unregister_plugin("插件名称")
```

## 核心组件访问接口

### 托盘图标接口

托盘图标组件提供了以下接口：

```python
# 获取托盘图标实例
tray_icon = app.get_tray_icon()

# 添加菜单项
tray_icon.plugin_menu_item_added.emit("菜单项名称", callback_function)

# 移除菜单项
tray_icon.plugin_menu_item_removed.emit("菜单项名称")
```

### 悬浮窗接口

悬浮窗组件提供了以下接口：

```python
# 获取悬浮窗实例
floating_window = app.get_floating_window()

# 添加内容
floating_window.plugin_content_added.emit("内容标识符", widget)

# 移除内容
floating_window.plugin_content_removed.emit("内容标识符")
```

### 设置窗口接口

设置窗口组件提供了以下接口：

```python
# 获取设置窗口实例
settings_window = app.get_settings_window()

# 添加设置页面
settings_window.plugin_page_added.emit("页面名称", widget)

# 移除设置页面
settings_window.plugin_page_removed.emit("页面名称")
```

### 其他核心组件接口

```python
# 获取主窗口实例
main_window = app.get_main_window()

# 获取课程服务实例
lessons_service = app.get_lessons_service()

# 获取时间服务实例
time_service = app.get_time_service()

# 获取主题管理器实例
theme_manager = app.get_theme_manager()
```

## 托盘图标插件接口

### 添加菜单项

```python
def add_menu_item(self, name, callback):
    """
    添加托盘菜单项
    :param name: 菜单项名称
    :param callback: 回调函数
    """
    tray_icon = self.app.get_tray_icon()
    if tray_icon:
        tray_icon.plugin_menu_item_added.emit(name, callback)

# 使用示例
def my_callback():
    print("插件菜单项被点击")

add_menu_item("我的插件功能", my_callback)
```

### 移除菜单项

```python
def remove_menu_item(self, name):
    """
    移除托盘菜单项
    :param name: 菜单项名称
    """
    tray_icon = self.app.get_tray_icon()
    if tray_icon:
        tray_icon.plugin_menu_item_removed.emit(name)

# 使用示例
remove_menu_item("我的插件功能")
```

## 悬浮窗插件接口

### 添加内容

```python
def add_floating_content(self, identifier, widget):
    """
    添加悬浮窗内容
    :param identifier: 内容标识符
    :param widget: Qt 控件
    """
    floating_window = self.app.get_floating_window()
    if floating_window:
        floating_window.plugin_content_added.emit(identifier, widget)

# 使用示例
from PySide6.QtWidgets import QLabel

label = QLabel("插件内容")
add_floating_content("my_plugin_content", label)
```

### 移除内容

```python
def remove_floating_content(self, identifier):
    """
    移除悬浮窗内容
    :param identifier: 内容标识符
    """
    floating_window = self.app.get_floating_window()
    if floating_window:
        floating_window.plugin_content_removed.emit(identifier)

# 使用示例
remove_floating_content("my_plugin_content")
```

## 设置窗口插件接口

### 添加设置页面

```python
def add_settings_page(self, name, widget):
    """
    添加设置页面
    :param name: 页面名称
    :param widget: Qt 控件（页面内容）
    """
    settings_window = self.app.get_settings_window()
    if settings_window:
        settings_window.plugin_page_added.emit(name, widget)

# 使用示例
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

page = QWidget()
layout = QVBoxLayout(page)
layout.addWidget(QLabel("这是插件设置页面"))
page.setLayout(layout)

add_settings_page("我的插件设置", page)
```

### 移除设置页面

```python
def remove_settings_page(self, name):
    """
    移除设置页面
    :param name: 页面名称
    """
    settings_window = self.app.get_settings_window()
    if settings_window:
        settings_window.plugin_page_removed.emit(name)

# 使用示例
remove_settings_page("我的插件设置")
```

## 完整插件示例

以下是一个完整的插件示例，演示了如何使用所有接口：

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import logging

logger = logging.getLogger(__name__)


class ExamplePlugin:
    def __init__(self):
        self.app = None
        self.button = None
        
    def initialize(self, app):
        """
        插件初始化
        :param app: TimeNestApplication 实例
        """
        self.app = app
        logger.info("示例插件初始化")
        
        # 添加托盘菜单项
        self._add_tray_menu_item()
        
        # 添加悬浮窗内容
        self._add_floating_content()
        
        # 添加设置页面
        self._add_settings_page()
        
    def cleanup(self):
        """
        插件清理
        """
        logger.info("示例插件清理")
        
        # 移除托盘菜单项
        self._remove_tray_menu_item()
        
        # 移除悬浮窗内容
        self._remove_floating_content()
        
        # 移除设置页面
        self._remove_settings_page()
        
    def _add_tray_menu_item(self):
        """添加托盘菜单项"""
        def menu_callback():
            logger.info("插件菜单项被点击")
            # 可以在这里实现具体功能
            
        tray_icon = self.app.get_tray_icon()
        if tray_icon:
            tray_icon.plugin_menu_item_added.emit("示例插件功能", menu_callback)
            
    def _remove_tray_menu_item(self):
        """移除托盘菜单项"""
        tray_icon = self.app.get_tray_icon()
        if tray_icon:
            tray_icon.plugin_menu_item_removed.emit("示例插件功能")
            
    def _add_floating_content(self):
        """添加悬浮窗内容"""
        self.button = QPushButton("插件按钮")
        self.button.clicked.connect(lambda: logger.info("插件按钮被点击"))
        
        floating_window = self.app.get_floating_window()
        if floating_window:
            floating_window.plugin_content_added.emit("example_plugin_button", self.button)
            
    def _remove_floating_content(self):
        """移除悬浮窗内容"""
        floating_window = self.app.get_floating_window()
        if floating_window:
            floating_window.plugin_content_removed.emit("example_plugin_button")
            
    def _add_settings_page(self):
        """添加设置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel("示例插件设置")
        layout.addWidget(label)
        
        button = QPushButton("插件设置按钮")
        button.clicked.connect(lambda: logger.info("插件设置按钮被点击"))
        layout.addWidget(button)
        
        page.setLayout(layout)
        
        settings_window = self.app.get_settings_window()
        if settings_window:
            settings_window.plugin_page_added.emit("示例插件", page)
            
    def _remove_settings_page(self):
        """移除设置页面"""
        settings_window = self.app.get_settings_window()
        if settings_window:
            settings_window.plugin_page_removed.emit("示例插件")


# 注册插件
def register_plugin(app):
    plugin = ExamplePlugin()
    app.register_plugin("example_plugin", plugin)
```

## 最佳实践

### 1. 错误处理

在插件开发中，应该始终包含适当的错误处理：

```python
def initialize(self, app):
    try:
        self.app = app
        # 插件初始化代码
    except Exception as e:
        logger.error(f"插件初始化失败: {e}")
```

### 2. 资源管理

确保在插件注销时正确清理所有资源：

```python
def cleanup(self):
    # 清理资源
    if self.timer:
        self.timer.stop()
        self.timer = None
        
    if self.widget:
        self.widget.deleteLater()
        self.widget = None
```

### 3. 用户体验

- 为插件功能提供清晰的用户界面
- 使用一致的设计语言和主题
- 提供适当的用户反馈

## 常见问题

### 1. 插件接口不可用

确保在应用程序完全初始化后再注册插件。

### 2. 内存泄漏

确保在插件注销时正确删除所有 Qt 对象。

### 3. 线程安全

避免在非 UI 线程中直接操作 UI 组件。

## API 参考

### TimeNestApplication

| 方法 | 描述 |
|------|------|
| `get_tray_icon()` | 获取托盘图标实例 |
| `get_floating_window()` | 获取悬浮窗实例 |
| `get_settings_window()` | 获取设置窗口实例 |
| `get_main_window()` | 获取主窗口实例 |
| `get_lessons_service()` | 获取课程服务实例 |
| `get_time_service()` | 获取时间服务实例 |
| `get_theme_manager()` | 获取主题管理器实例 |
| `register_plugin(name, plugin)` | 注册插件 |
| `unregister_plugin(name)` | 注销插件 |

### TrayIcon

| 信号 | 描述 |
|------|------|
| `plugin_menu_item_added(name, callback)` | 添加插件菜单项 |
| `plugin_menu_item_removed(name)` | 移除插件菜单项 |

### FloatingWindow

| 信号 | 描述 |
|------|------|
| `plugin_content_added(identifier, widget)` | 添加插件内容 |
| `plugin_content_removed(identifier)` | 移除插件内容 |

### SettingsWindow

| 信号 | 描述 |
|------|------|
| `plugin_page_added(name, widget)` | 添加插件页面 |
| `plugin_page_removed(name)` | 移除插件页面 |