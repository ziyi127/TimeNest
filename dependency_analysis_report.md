# TimeNest 依赖关系分析报告

生成时间: 2025年 07月 11日 星期五 13:07:40 CST

## 循环依赖检测结果

✅ **未发现循环依赖**

## 模块依赖关系

### components.schedule_component

- models.schedule

### core.app_manager

- core.config_manager
- core.schedule_manager
- core.notification_manager
- core.time_manager
- core.component_system
- core.theme_system
- core.plugin_system
- core.weather_service
- core.floating_manager

### core.component_manager

- core.config_manager

### core.data_import_export

- models.schedule
- utils.excel_exporter

### core.floating_manager

- ui.floating_widget
- models.schedule
- core.config_manager
- core.theme_system

### core.notification_manager

- models.schedule
- core.config_manager
- utils.text_to_speech
- core.notification_service

### core.preview_manager

- core.theme_manager
- core.notification_system_v2
- core.plugin_system

### core.schedule_manager

- models.schedule
- core.config_manager
- core.attached_settings
- core.notification_service
- utils.excel_exporter_v2

### core.time_manager

- core.config_manager

### demo_refactored_systems

- core.notification_manager
- core.floating_manager

### main

- core.app_manager
- ui.main_window

### run_timenest

- core.config_manager
- core.notification_manager
- core.floating_manager
- ui.system_tray

### test_module_imports

- core.floating_manager

### test_refactored_components

- core.notification_manager
- core.floating_manager
- ui.system_tray

### tests.test_floating_system

- ui.floating_widget
- core.floating_manager
- ui.system_tray
- ui.floating_settings_tab
- models.schedule

### tests.test_notification_system

- core.notification_manager
- core.config_manager
- core.notification_service
- models.schedule

### ui.__init__

- ui.main_window

### ui.floating_settings_tab

- ui.floating_widget

### ui.floating_widget

- models.schedule

### ui.main_window

- core.app_manager
- core.config_manager
- core.theme_system
- ui.settings_dialog
- ui.about_dialog
- ui.weather_widget
- ui.notification_widget

### ui.notification_widget

- core.notification_service

### ui.settings_dialog

- core.config_manager
- core.theme_system
- core.notification_manager
- core.notification_system_v2
- core.plugin_system
- core.preview_manager
- ui.floating_settings_tab
- core.notification_system_v2

### ui.system_tray

- core.floating_manager

### ui.weather_widget

- core.weather_service

### utils.excel_exporter_v2

- models.schedule

## 修复建议

1. **使用依赖注入**: 通过构造函数传递依赖，而非直接导入
2. **接口抽象**: 创建抽象基类，减少具体类之间的依赖
3. **延迟导入**: 将导入语句移到函数内部
4. **事件系统**: 使用信号槽机制替代直接方法调用
5. **重构架构**: 调整模块职责，提取共同依赖
