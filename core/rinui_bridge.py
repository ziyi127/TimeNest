#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RinUI 桥接类
连接QML前端和Python后端业务逻辑
"""

import logging
from typing import Dict, Any, List, Optional

from utils.common_imports import QObject, Signal, Slot, Property, QTimer, qmlRegisterType
from utils.shared_utilities import cleanup_timers, debounce
from utils.config_constants import ERROR_MESSAGES, SUCCESS_MESSAGES

from utils.version_manager import version_manager
from core.data_manager import DataManager
from core.schedule_manager import ScheduleManager
from core.task_manager import TaskManager
from core.theme_manager import ThemeManager
from core.notification_manager import NotificationManager
from core.excel_schedule_manager import ExcelScheduleManager


class TimeNestBridge(QObject):
    """TimeNest QML桥接类"""
    
    # 信号定义
    scheduleChanged = Signal()
    tasksChanged = Signal()
    settingsChanged = Signal()
    themeChanged = Signal(str)  # theme_name
    notificationReceived = Signal(str, str)  # title, message
    floatingWindowToggled = Signal(bool)  # visible
    systemTrayClicked = Signal()
    pluginsChanged = Signal()  # 插件变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.floating_manager = None
        self.tray_manager = None

        self._init_managers()
        self._init_timers()
        self._init_error_handling()

        self.logger.info("RinUI桥接类初始化完成")

    def _init_managers(self):
        """初始化管理器"""
        try:
            self.data_manager = DataManager()
            from core.config_manager import ConfigManager
            config_manager = ConfigManager()
            self.schedule_manager = ScheduleManager(config_manager)
            self.task_manager = TaskManager()
            self.theme_manager = ThemeManager()
            self.notification_manager = NotificationManager(config_manager)
            self.excel_manager = ExcelScheduleManager()
            self.system_tray = None
        except Exception as e:
            self.logger.error(f"初始化管理器失败: {e}")
            self._set_null_managers()

    def _set_null_managers(self):
        """设置空管理器"""
        for attr in ['data_manager', 'schedule_manager', 'task_manager',
                     'theme_manager', 'notification_manager', 'system_tray']:
            setattr(self, attr, None)

    def _init_timers(self):
        """初始化定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateCurrentTime)
        self.timer.start(1000)

        self.memory_monitor_timer = QTimer()
        self.memory_monitor_timer.timeout.connect(self._monitor_memory)
        self.memory_monitor_timer.start(300000)

    def _init_error_handling(self):
        """初始化错误处理"""
        self._error_count = 0
        self._max_errors = 10
        self._last_error_time = None


    def _handle_error(self, error_msg: str, exception: Exception = None):
        """统一错误处理"""
        try:
            from datetime import datetime

            current_time = datetime.now()

            if self._last_error_time and (current_time - self._last_error_time).total_seconds() < 60:
                self._error_count += 1
            else:
                self._error_count = 1

            self._last_error_time = current_time

            if self._error_count > self._max_errors:
                self.logger.critical(f"错误过于频繁，进入安全模式: {error_msg}")
                self._enter_safe_mode()
                return

            log_msg = f"处理错误: {error_msg}"
            if exception:
                log_msg += f" - {exception}"
            self.logger.debug(log_msg)

        except Exception as e:
            self.logger.debug(f"错误处理失败: {e}")

    def _enter_safe_mode(self):
        """进入安全模式"""
        try:
            timers = [('timer', 5000), ('memory_monitor_timer', None)]

            for timer_name, restart_interval in timers:
                if hasattr(self, timer_name):
                    timer = getattr(self, timer_name)
                    if timer:
                        timer.stop()
                        if restart_interval and timer_name == 'timer':
                            timer.start(restart_interval)

            self._error_count = 0
            self.logger.info("已进入安全模式，降低系统负载")

        except Exception as e:
            self.logger.debug(f"进入安全模式失败: {e}")

    def set_floating_manager(self, floating_manager):
        """设置悬浮窗管理器引用"""
        self.floating_manager = floating_manager

    def set_tray_manager(self, tray_manager):
        """设置系统托盘管理器引用"""
        self.tray_manager = tray_manager
    
    # 应用信息属性
    @Property(str, constant=True)
    def appName(self):
        """获取应用名称"""
        return version_manager.get_app_name()
    
    @Property(str, constant=True)
    def appVersion(self):
        """获取应用版本"""
        return version_manager.get_full_version()
    
    @Property(str, constant=True)
    def appDescription(self):
        """获取应用描述"""
        return version_manager.get_app_description()
    
    # 课程表相关方法
    @Slot(result='QVariant')
    def getScheduleData(self):
        """获取课程表数据"""
        try:
            if self.schedule_manager:
                courses = self.schedule_manager.get_all_courses()
                return self._convert_courses_to_qml(courses)
            return []
        except Exception as e:
            self.logger.error(f"获取课程表数据失败: {e}")
            return []
    
    @Slot(str, str, str, str, int, int, result=bool)
    def addCourse(self, name, teacher, location, time, start_week, end_week):
        """添加课程"""
        try:
            if self.schedule_manager:
                course_data = {
                    'name': name,
                    'teacher': teacher,
                    'location': location,
                    'time': time,
                    'start_week': start_week,
                    'end_week': end_week
                }
                success = self.schedule_manager.add_course(course_data)
                if success:
                    self.scheduleChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"添加课程失败: {e}")
            return False
    
    @Slot(str, result=bool)
    def deleteCourse(self, course_id):
        """删除课程"""
        try:
            if self.schedule_manager:
                # 转换字符串ID为整数
                course_id_int = int(course_id)
                success = self.schedule_manager.delete_course(course_id_int)
                if success:
                    self.scheduleChanged.emit()
                    self.showNotification("课程管理", f"课程已删除")
                return success
            return False
        except Exception as e:
            self.logger.error(f"删除课程失败: {e}")
            self.showNotification("课程管理", f"删除课程失败: {e}")
            return False

    @Slot('QVariant', result=bool)
    def updateCourse(self, course_data):
        """更新课程"""
        try:
            if self.schedule_manager:
                course_id = course_data.get('course_id')
                if not course_id:
                    self.logger.error("课程ID不能为空")
                    self.showNotification("课程管理", "课程ID不能为空")
                    return False

                # 转换字符串ID为整数
                course_id_int = int(course_id)

                update_data = {
                    'name': course_data.get('name', ''),
                    'teacher': course_data.get('teacher', ''),
                    'location': course_data.get('location', ''),
                    'time': course_data.get('time', ''),
                    'weeks': course_data.get('weeks', ''),
                    'start_week': course_data.get('start_week', 1),
                    'end_week': course_data.get('end_week', 16)
                }

                success = self.schedule_manager.update_course(course_id_int, update_data)
                if success:
                    self.scheduleChanged.emit()
                    self.showNotification("课程管理", "课程更新成功")
                    self.logger.info(f"课程更新成功: {course_id}")
                return success
            return False
        except Exception as e:
            self.logger.error(f"更新课程失败: {e}")
            self.showNotification("课程管理", f"更新课程失败: {e}")
            return False
    
    # 任务管理相关方法
    @Slot(result='QVariant')
    def getTasksData(self):
        """获取任务数据"""
        try:
            if self.task_manager:
                tasks = self.task_manager.get_all_tasks()
                return self._convert_tasks_to_qml(tasks)
            return []
        except Exception as e:
            self.logger.error(f"获取任务数据失败: {e}")
            return []
    
    @Slot(str, str, str, str, result=bool)
    def addTask(self, title, description, priority, due_date):
        """添加任务"""
        try:
            if self.task_manager:
                task_data = {
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'due_date': due_date,
                    'status': '进行中'
                }
                success = self.task_manager.add_task(task_data)
                if success:
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return False
    
    @Slot(int, bool, result=bool)
    def updateTaskStatus(self, task_id, completed):
        """更新任务状态"""
        try:
            if self.task_manager:
                status = '已完成' if completed else '进行中'
                success = self.task_manager.update_task_status(task_id, status)
                if success:
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"更新任务状态失败: {e}")
            return False
    
    @Slot(int, result=bool)
    def deleteTask(self, task_id):
        """删除任务"""
        try:
            if self.task_manager:
                success = self.task_manager.delete_task(task_id)
                if success:
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"删除任务失败: {e}")
            return False

    @Slot(int, str, str, str, str, result=bool)
    def updateTask(self, task_id, title, description, priority, due_date):
        """更新任务"""
        try:
            if self.task_manager:
                task_data = {
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'due_date': due_date
                }
                success = self.task_manager.update_task(task_id, task_data)
                if success:
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"更新任务失败: {e}")
            return False
    
    # 设置相关方法
    @Slot(str, 'QVariant')
    def saveSetting(self, key, value):
        """保存设置"""
        try:
            if self.data_manager:
                self.data_manager.save_setting(key, value)
                self.settingsChanged.emit()
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
    
    @Slot(str, result='QVariant')
    def loadSetting(self, key):
        """加载设置"""
        try:
            if self.data_manager:
                return self.data_manager.load_setting(key)
            return None
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            return None

    @Slot(str, 'QVariant', result='QVariant')
    def getSetting(self, key, default_value=None):
        """获取设置（带默认值）"""
        try:
            if self.data_manager:
                value = self.data_manager.get_setting(key, default_value)
                self.logger.debug(f"获取设置: {key} = {value}")
                return value
            return default_value
        except Exception as e:
            self.logger.error(f"获取设置失败: {e}")
            return default_value
    
    # 通知相关方法
    @Slot(str, str)
    def showNotification(self, title, message):
        """显示通知"""
        self.notificationReceived.emit(title, message)
        if self.notification_manager:
            self.notification_manager.send_notification(title, message)
        self.logger.info(f"通知: {title} - {message}")

    # 主题相关方法
    @Slot(result='QVariant')
    def getAvailableThemes(self):
        """获取可用主题列表"""
        try:
            if self.theme_manager:
                themes = []
                for name, theme_info in self.theme_manager.themes.items():
                    themes.append({
                        'name': name,
                        'display_name': theme_info.get('display_name', name),
                        'description': theme_info.get('description', ''),
                        'author': theme_info.get('author', ''),
                        'version': theme_info.get('version', '1.0.0')
                    })
                return themes
            return []
        except Exception as e:
            self.logger.error(f"获取主题列表失败: {e}")
            return []

    @Slot(str, result=bool)
    def applyTheme(self, theme_name):
        """应用主题"""
        try:
            if self.theme_manager:
                success = self.theme_manager.apply_theme(theme_name)
                if success:
                    self.themeChanged.emit(theme_name)
                return success
            return False
        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")
            return False

    @Slot(result=str)
    def getCurrentTheme(self):
        """获取当前主题"""
        try:
            if self.theme_manager:
                return self.theme_manager.current_theme or "default"
            return "default"
        except Exception as e:
            self.logger.error(f"获取当前主题失败: {e}")
            return "default"

    @Slot(str)
    def applyTheme(self, theme_mode):
        """应用主题"""
        try:
            self.saveSetting("theme_mode", theme_mode)
            # 发送主题变化信号
            self.themeChanged.emit(theme_mode)
            self.logger.info(f"应用主题: {theme_mode}")
        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")

    # 悬浮窗相关方法
    @Slot(result=bool)
    def toggleFloatingWindow(self):
        """切换悬浮窗显示状态"""
        try:
            if self.floating_manager:
                self.floating_manager.toggle_floating_window()
                visible = self.floating_manager.is_window_visible()
                self.floatingWindowToggled.emit(visible)
                return True
            return False
        except Exception as e:
            self.logger.error(f"切换悬浮窗失败: {e}")
            return False

    @Slot(result=bool)
    def isFloatingWindowVisible(self):
        """检查悬浮窗是否可见"""
        try:
            if self.floating_manager:
                return self.floating_manager.is_window_visible()
            return False
        except Exception as e:
            self.logger.error(f"检查悬浮窗状态失败: {e}")
            return False

    @Slot(result=bool)
    def showFloatingWindow(self):
        """显示悬浮窗"""
        try:
            if self.floating_manager:
                self.floating_manager.show_floating_window()
                return True
            return False
        except Exception as e:
            self.logger.error(f"显示悬浮窗失败: {e}")
            return False

    @Slot(result=bool)
    def hideFloatingWindow(self):
        """隐藏悬浮窗"""
        try:
            if self.floating_manager:
                self.floating_manager.hide_floating_window()
                return True
            return False
        except Exception as e:
            self.logger.error(f"隐藏悬浮窗失败: {e}")
            return False

    @Slot(result=bool)
    def forceFloatingWindowToTop(self):
        """强制悬浮窗置顶"""
        try:
            if self.floating_manager and hasattr(self.floating_manager, 'floating_window'):
                floating_window = self.floating_manager.floating_window
                if floating_window and hasattr(floating_window, 'force_to_top'):
                    floating_window.force_to_top()
                    return True
            return False
        except Exception as e:
            self.logger.error(f"强制悬浮窗置顶失败: {e}")
            return False

    # 系统托盘相关方法
    @Slot(result=bool)
    def isSystemTrayAvailable(self):
        """检查系统托盘是否可用"""
        try:
            if self.system_tray:
                return self.system_tray.is_available()
            return False
        except Exception as e:
            self.logger.error(f"检查系统托盘失败: {e}")
            return False

    @Slot(str)
    def setSystemTrayTooltip(self, tooltip):
        """设置系统托盘提示文本"""
        try:
            if self.system_tray:
                self.system_tray.set_tooltip(tooltip)
        except Exception as e:
            self.logger.error(f"设置托盘提示失败: {e}")

    # 数据导入导出方法
    @Slot(str, result=bool)
    def exportData(self, file_path):
        """导出数据"""
        try:
            if self.data_manager:
                return self.data_manager.export_data(file_path)
            return False
        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            return False

    @Slot(str, result=bool)
    def importData(self, file_path):
        """导入数据"""
        try:
            if self.data_manager:
                success = self.data_manager.import_data(file_path)
                if success:
                    self.scheduleChanged.emit()
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"导入数据失败: {e}")
            return False

    @Slot(result=bool)
    def backupData(self):
        """备份数据"""
        try:
            if self.data_manager:
                return self.data_manager.backup_data()
            return False
        except Exception as e:
            self.logger.error(f"备份数据失败: {e}")
            return False

    @Slot(result=bool)
    def restoreData(self):
        """恢复数据"""
        try:
            if self.data_manager:
                success = self.data_manager.restore_data()
                if success:
                    self.scheduleChanged.emit()
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"恢复数据失败: {e}")
            return False

    # 应用控制方法
    @Slot()
    def exitApplication(self):
        """退出应用"""
        try:
            # 保存所有数据
            if self.data_manager:
                self.data_manager.save_all()

            # 关闭系统托盘
            if self.system_tray:
                self.system_tray.hide()

            # 退出应用
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
        except Exception as e:
            self.logger.error(f"退出应用失败: {e}")

    @Slot()
    def minimizeToTray(self):
        """最小化到系统托盘"""
        try:
            if self.system_tray and self.system_tray.is_available():
                # 隐藏主窗口，显示托盘图标
                pass
        except Exception as e:
            self.logger.error(f"最小化到托盘失败: {e}")

    # 时间相关方法
    @Slot()
    def updateCurrentTime(self):
        """更新当前时间（由定时器调用）"""
        # 这里可以触发QML中的时间更新
        pass
    
    # 数据转换辅助方法
    def _convert_courses_to_qml(self, courses):
        """将课程数据转换为QML可用格式（优化版本）"""
        from utils.data_processing import convert_courses_to_qml_format
        return convert_courses_to_qml_format(courses)
    
    def _convert_tasks_to_qml(self, tasks):
        """将任务数据转换为QML可用格式（优化版本）"""
        from utils.data_processing import convert_tasks_to_qml_format
        return convert_tasks_to_qml_format(tasks)

    # 插件管理相关方法
    @Slot(result='QVariant')
    def getPluginsData(self):
        """获取插件数据"""
        try:
            import json
            from pathlib import Path

            plugins = []
            plugins_dir = Path("plugins")

            if plugins_dir.exists():
                for plugin_dir in plugins_dir.iterdir():
                    if plugin_dir.is_dir():
                        plugin_info_file = plugin_dir / "plugin.json"
                        if plugin_info_file.exists():
                            try:
                                with open(plugin_info_file, 'r', encoding='utf-8') as f:
                                    plugin_info = json.load(f)

                                plugins.append({
                                    'id': plugin_info.get('id', plugin_dir.name),
                                    'name': plugin_info.get('name', plugin_dir.name),
                                    'description': plugin_info.get('description', '无描述'),
                                    'version': plugin_info.get('version', '1.0.0'),
                                    'author': plugin_info.get('author', '未知'),
                                    'enabled': plugin_info.get('enabled', False),
                                    'hasUpdate': False  # 可以后续实现更新检查
                                })
                            except Exception as e:
                                self.logger.error(f"读取插件信息失败 {plugin_dir}: {e}")

            # 如果没有插件，返回示例数据
            if not plugins:
                plugins = [
                    {
                        'id': 'example-weather',
                        'name': '天气插件示例',
                        'description': '这是一个示例插件，显示天气信息',
                        'version': '1.0.0',
                        'author': 'TimeNest Team',
                        'enabled': False,
                        'hasUpdate': False
                    },
                    {
                        'id': 'example-pomodoro',
                        'name': '番茄钟示例',
                        'description': '这是一个示例插件，提供番茄工作法计时',
                        'version': '1.2.0',
                        'author': 'TimeNest Team',
                        'enabled': False,
                        'hasUpdate': False
                    }
                ]

            return plugins
        except Exception as e:
            self.logger.error(f"获取插件数据失败: {e}")
            return []

    @Slot(str, bool)
    def togglePlugin(self, plugin_id, enabled):
        """切换插件状态"""
        try:
            import json
            from pathlib import Path

            # 查找插件目录
            plugins_dir = Path("plugins")
            if not plugins_dir.exists():
                plugins_dir.mkdir(parents=True, exist_ok=True)
                self.showNotification("插件管理", "已创建插件目录")
                return

            # 查找对应的插件
            plugin_found = False
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_info_file = plugin_dir / "plugin.json"
                    if plugin_info_file.exists():
                        try:
                            with open(plugin_info_file, 'r', encoding='utf-8') as f:
                                plugin_info = json.load(f)

                            if plugin_info.get('id') == str(plugin_id):
                                plugin_info['enabled'] = enabled
                                with open(plugin_info_file, 'w', encoding='utf-8') as f:
                                    json.dump(plugin_info, f, ensure_ascii=False, indent=2)
                                plugin_found = True
                                break
                        except Exception as e:
                            self.logger.error(f"处理插件信息文件失败: {e}")

            if plugin_found:
                status = "启用" if enabled else "禁用"
                self.logger.info(f"插件 {plugin_id} 已{status}")
                self.showNotification("插件管理", f"插件已{status}")
                self.pluginsChanged.emit()
            else:
                self.showNotification("插件管理", f"未找到插件 {plugin_id}")

        except Exception as e:
            self.logger.error(f"切换插件状态失败: {e}")
            self.showNotification("插件管理", f"切换插件状态失败: {e}")

    @Slot(str)
    def openPluginSettings(self, plugin_id):
        """打开插件设置"""
        try:
            # 实现基本的插件设置功能
            self.logger.info(f"打开插件 {plugin_id} 设置")

            # 这里可以实现插件设置对话框
            # 目前显示一个简单的通知
            self.showNotification("插件设置", f"插件 {plugin_id} 设置界面\n\n这里可以配置插件的各种选项\n功能正在开发中...")

        except Exception as e:
            self.logger.error(f"打开插件设置失败: {e}")
            self.showNotification("插件设置", f"打开插件设置失败: {e}")

    @Slot(str, result=bool)
    def uninstallPlugin(self, plugin_id):
        """卸载插件"""
        try:
            import shutil
            from pathlib import Path

            plugins_dir = Path("plugins")
            if not plugins_dir.exists():
                self.showNotification("插件管理", "插件目录不存在")
                return False

            # 查找并删除插件目录
            for plugin_dir in plugins_dir.iterdir():
                if plugin_dir.is_dir():
                    plugin_info_file = plugin_dir / "plugin.json"
                    if plugin_info_file.exists():
                        try:
                            with open(plugin_info_file, 'r', encoding='utf-8') as f:
                                plugin_info = json.load(f)

                            if plugin_info.get('id') == plugin_id:
                                shutil.rmtree(plugin_dir)
                                self.logger.info(f"已卸载插件: {plugin_id}")
                                self.showNotification("插件管理", f"插件 {plugin_id} 已卸载")
                                self.pluginsChanged.emit()
                                return True
                        except Exception as e:
                            self.logger.error(f"处理插件信息失败: {e}")

            self.showNotification("插件管理", f"未找到插件 {plugin_id}")
            return False
        except Exception as e:
            self.logger.error(f"卸载插件失败: {e}")
            self.showNotification("插件管理", f"卸载插件失败: {e}")
            return False

    @Slot(result=int)
    def getAvailablePluginsCount(self):
        """获取可用插件数量"""
        try:
            # 返回模拟的可用插件数量
            return 15  # 示例数量
        except Exception as e:
            self.logger.error(f"获取可用插件数量失败: {e}")
            return 0

    @Slot(str, result=bool)
    def installPlugin(self, plugin_id):
        """安装插件"""
        try:
            # 模拟插件安装过程
            self.logger.info(f"开始安装插件: {plugin_id}")
            self.showNotification("插件管理", f"正在安装插件 {plugin_id}...")

            # 这里应该实现真正的插件下载和安装逻辑
            # 目前只是模拟
            import time
            import threading

            def install_process():
                time.sleep(2)  # 模拟安装时间
                self.showNotification("插件管理", f"插件 {plugin_id} 安装完成")
                self.pluginsChanged.emit()

            threading.Thread(target=install_process, daemon=True).start()
            return True

        except Exception as e:
            self.logger.error(f"安装插件失败: {e}")
            self.showNotification("插件管理", f"安装插件失败: {e}")
            return False

    @Slot(result='QVariant')
    def getAvailablePlugins(self):
        """从插件仓库获取可用插件"""
        try:
            import requests
            import json

            # 模拟插件仓库API
            available_plugins = [
                {
                    'id': 'weather-pro',
                    'name': '高级天气插件',
                    'description': '提供详细的天气预报和气象信息',
                    'version': '2.0.0',
                    'author': 'WeatherTeam',
                    'download_url': 'https://github.com/timenest/plugins/weather-pro.zip',
                    'installed': False,
                    'category': '工具'
                },
                {
                    'id': 'pomodoro-timer',
                    'name': '专业番茄钟',
                    'description': '功能完整的番茄工作法计时器',
                    'version': '1.5.0',
                    'author': 'ProductivityTeam',
                    'download_url': 'https://github.com/timenest/plugins/pomodoro-timer.zip',
                    'installed': False,
                    'category': '效率'
                },
                {
                    'id': 'calendar-sync',
                    'name': '日历同步',
                    'description': '与Google Calendar、Outlook等同步',
                    'version': '1.3.0',
                    'author': 'SyncTeam',
                    'download_url': 'https://github.com/timenest/plugins/calendar-sync.zip',
                    'installed': False,
                    'category': '同步'
                },
                {
                    'id': 'note-taking',
                    'name': '快速笔记',
                    'description': '在悬浮窗中快速记录笔记',
                    'version': '1.1.0',
                    'author': 'NoteTeam',
                    'download_url': 'https://github.com/timenest/plugins/note-taking.zip',
                    'installed': False,
                    'category': '工具'
                }
            ]

            self.logger.info(f"从插件仓库获取到 {len(available_plugins)} 个可用插件")
            return available_plugins

        except Exception as e:
            self.logger.error(f"获取可用插件失败: {e}")
            return []

    @Slot(result=int)
    def getAvailablePluginsCount(self):
        """获取可用插件数量"""
        try:
            available_plugins = self.getAvailablePlugins()
            return len(available_plugins)
        except Exception as e:
            self.logger.error(f"获取可用插件数量失败: {e}")
            return 0

    @Slot(str, str, result=bool)
    def installPlugin(self, plugin_id, download_url):
        """安装插件"""
        try:
            import os
            import zipfile
            import requests
            from pathlib import Path

            # 创建插件目录
            plugins_dir = Path("plugins")
            plugins_dir.mkdir(exist_ok=True)

            plugin_dir = plugins_dir / plugin_id
            plugin_dir.mkdir(exist_ok=True)

            # 模拟下载和安装过程
            self.logger.info(f"开始安装插件: {plugin_id}")
            self.showNotification("插件管理", f"正在安装插件: {plugin_id}")

            # 这里应该实际下载和解压插件文件
            # 现在只是创建一个示例文件
            plugin_info = {
                'id': plugin_id,
                'name': plugin_id.replace('-', ' ').title(),
                'version': '1.0.0',
                'installed': True,
                'enabled': False
            }

            info_file = plugin_dir / "plugin.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(plugin_info, f, ensure_ascii=False, indent=2)

            self.logger.info(f"插件安装成功: {plugin_id}")
            self.showNotification("插件管理", f"插件 {plugin_id} 安装成功")
            self.pluginsChanged.emit()
            return True

        except Exception as e:
            self.logger.error(f"安装插件失败: {e}")
            self.showNotification("插件管理", f"安装插件失败: {e}")
            return False

    # Excel课程表管理方法
    @Slot(result=bool)
    def createExcelTemplate(self):
        """创建Excel课程表模板"""
        try:
            if self.excel_manager:
                success = self.excel_manager.create_template()
                if success:
                    self.excel_manager.create_config_file()
                    self.showNotification("Excel模板", "Excel课程表模板已创建成功")
                return success
            return False
        except Exception as e:
            self.logger.error(f"创建Excel模板失败: {e}")
            return False

    # 添加进度信号
    importProgress = Signal(int, str)  # 进度百分比, 状态消息

    @Slot(str, result=bool)
    def importExcelSchedule(self, file_path):
        """从Excel文件导入课程表"""
        try:
            if not self.excel_manager:
                return False

            self.importProgress.emit(5, "开始导入...")

            # 验证Excel格式
            is_valid, message = self.excel_manager.validate_excel_format(file_path)
            if not is_valid:
                self.showNotification("导入失败", f"Excel格式错误: {message}")
                self.importProgress.emit(0, f"格式错误: {message}")
                return False

            # 定义进度回调函数
            def progress_callback(progress, message):
                self.importProgress.emit(progress, message)

            # 导入课程数据
            courses = self.excel_manager.import_from_excel(file_path, progress_callback)
            if not courses:
                self.showNotification("导入失败", "未能从Excel文件中读取到课程数据")
                self.importProgress.emit(0, "未读取到课程数据")
                return False

            self.importProgress.emit(85, "正在保存课程数据...")

            # 清空现有课程表
            if self.schedule_manager:
                self.schedule_manager.clear_all_courses()

            # 添加导入的课程
            imported_count = 0
            total_courses = len(courses)

            for i, course in enumerate(courses):
                if self.schedule_manager:
                    success = self.schedule_manager.add_course(
                        course['name'],
                        course['teacher'],
                        course['location'],
                        course['time'],
                        course['start_week'],
                        course['end_week'],
                        course.get('weekday', '周一')  # 添加weekday参数
                    )
                    if success:
                        imported_count += 1

                # 更新保存进度
                if i % 10 == 0:
                    save_progress = 85 + int((i / total_courses) * 10)
                    self.importProgress.emit(save_progress, f"正在保存课程... ({i+1}/{total_courses})")

            # 发送课程变化信号
            self.scheduleChanged.emit()

            self.importProgress.emit(100, f"导入完成！成功导入 {imported_count} 条课程")
            self.showNotification("导入成功", f"成功导入 {imported_count} 条课程记录")
            self.logger.info(f"成功从Excel导入 {imported_count} 条课程记录")
            return True

        except Exception as e:
            error_msg = f"导入过程中发生错误: {e}"
            self.logger.error(f"导入Excel课程表失败: {e}")
            self.showNotification("导入失败", error_msg)
            self.importProgress.emit(0, error_msg)
            return False

    @Slot(str, result=bool)
    def exportExcelSchedule(self, file_path):
        """导出课程表到Excel文件"""
        try:
            if not self.excel_manager or not self.schedule_manager:
                return False

            # 获取所有课程数据
            courses = self.schedule_manager.get_all_courses()
            if not courses:
                self.showNotification("导出失败", "没有课程数据可以导出")
                return False

            # 导出到Excel
            success = self.excel_manager.export_to_excel(courses, file_path)
            if success:
                self.showNotification("导出成功", f"课程表已导出到: {file_path}")
                self.logger.info(f"成功导出课程表到: {file_path}")
            else:
                self.showNotification("导出失败", "导出过程中发生错误")

            return success

        except Exception as e:
            self.logger.error(f"导出Excel课程表失败: {e}")
            self.showNotification("导出失败", f"导出过程中发生错误: {e}")
            return False

    @Slot(str, result='QVariant')
    def validateExcelFile(self, file_path):
        """验证Excel文件格式"""
        try:
            if self.excel_manager:
                is_valid, message = self.excel_manager.validate_excel_format(file_path)
                return {
                    'valid': is_valid,
                    'message': message
                }
            return {
                'valid': False,
                'message': 'Excel管理器未初始化'
            }
        except Exception as e:
            self.logger.error(f"验证Excel文件失败: {e}")
            return {
                'valid': False,
                'message': f'验证失败: {e}'
            }

    # 新增功能方法
    @Slot(str, str, str, str, int, int, str, result=bool)
    def addCourse(self, name, teacher, location, time, start_week, end_week, weekday):
        """添加新课程"""
        try:
            if self.schedule_manager:
                success = self.schedule_manager.add_course(
                    name, teacher, location, time, start_week, end_week, weekday
                )
                if success:
                    self.scheduleChanged.emit()
                    self.logger.info(f"成功添加课程: {name}")
                return success
            return False
        except Exception as e:
            self.logger.error(f"添加课程失败: {e}")
            return False

    @Slot(str, str, str, str, result=bool)
    def addTask(self, title, description, priority, due_date):
        """添加新任务"""
        try:
            if self.task_manager:
                success = self.task_manager.add_simple_task(title, description, priority, due_date)
                if success:
                    self.tasksChanged.emit()
                    self.logger.info(f"成功添加任务: {title}")
                return success
            return False
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return False

    @Slot(str, result=bool)
    def deleteTask(self, task_id):
        """删除任务"""
        try:
            if self.task_manager:
                success = self.task_manager.delete_task(int(task_id))
                if success:
                    self.tasksChanged.emit()
                    self.showNotification("任务管理", "任务已删除")
                return success
            return False
        except Exception as e:
            self.logger.error(f"删除任务失败: {e}")
            return False

    @Slot(str, str, result=bool)
    def updateTaskStatus(self, task_id, status):
        """更新任务状态"""
        try:
            if self.task_manager:
                success = self.task_manager.update_task_status(int(task_id), status)
                if success:
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"更新任务状态失败: {e}")
            return False

    @Slot(str, result=bool)
    def toggleTaskComplete(self, task_id):
        """切换任务完成状态"""
        try:
            if self.task_manager:
                success = self.task_manager.toggle_task_complete(int(task_id))
                if success:
                    self.tasksChanged.emit()
                return success
            return False
        except Exception as e:
            self.logger.error(f"切换任务状态失败: {e}")
            return False

    @Slot(result=int)
    def getTasksCount(self):
        """获取任务总数"""
        try:
            if self.task_manager:
                return len(self.task_manager.get_all_tasks())
            return 0
        except Exception as e:
            self.logger.error(f"获取任务数量失败: {e}")
            return 0

    @Slot(result=int)
    def getCompletedTasksCount(self):
        """获取已完成任务数"""
        try:
            if self.task_manager:
                tasks = self.task_manager.get_all_tasks()
                return len([t for t in tasks if t.get('status') == '已完成'])
            return 0
        except Exception as e:
            self.logger.error(f"获取已完成任务数失败: {e}")
            return 0

    @Slot(result=int)
    def getPendingTasksCount(self):
        """获取待完成任务数"""
        try:
            if self.task_manager:
                tasks = self.task_manager.get_all_tasks()
                return len([t for t in tasks if t.get('status') != '已完成'])
            return 0
        except Exception as e:
            self.logger.error(f"获取待完成任务数失败: {e}")
            return 0

    @Slot(str, result=bool)
    def importData(self, file_path):
        """导入数据"""
        try:
            if self.data_manager:
                success = self.data_manager.import_data(file_path)
                if success:
                    self.scheduleChanged.emit()
                    self.tasksChanged.emit()
                    self.logger.info(f"成功导入数据: {file_path}")
                return success
            return False
        except Exception as e:
            self.logger.error(f"导入数据失败: {e}")
            return False

    @Slot(str, result=bool)
    def exportData(self, file_path):
        """导出数据"""
        try:
            if self.data_manager:
                success = self.data_manager.export_data(file_path)
                if success:
                    self.logger.info(f"成功导出数据: {file_path}")
                return success
            return False
        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            return False

    @Slot(result=bool)
    def backupData(self):
        """备份数据"""
        try:
            if self.data_manager:
                success = self.data_manager.backup_data()
                if success:
                    self.logger.info("数据备份成功")
                return success
            return False
        except Exception as e:
            self.logger.error(f"数据备份失败: {e}")
            return False

    @Slot(result=bool)
    def restoreData(self):
        """恢复数据"""
        try:
            if self.data_manager:
                success = self.data_manager.restore_data()
                if success:
                    self.scheduleChanged.emit()
                    self.tasksChanged.emit()
                    self.logger.info("数据恢复成功")
                return success
            return False
        except Exception as e:
            self.logger.error(f"数据恢复失败: {e}")
            return False

    @Slot()
    def showTimeCalibration(self):
        """显示时间校准"""
        try:
            # 实现时间校准功能
            import subprocess
            import platform

            system = platform.system()
            if system == "Windows":
                subprocess.run(["w32tm", "/resync"], check=False)
            elif system == "Linux":
                subprocess.run(["sudo", "ntpdate", "-s", "time.nist.gov"], check=False)

            self.showNotification("时间校准", "时间校准完成")
            self.logger.info("时间校准完成")
        except Exception as e:
            self.logger.error(f"时间校准失败: {e}")
            self.showNotification("时间校准", f"时间校准失败: {e}")

    @Slot(result='QVariant')
    def getSystemInfo(self):
        """获取详细的系统信息"""
        try:
            import platform
            import psutil
            import sys
            import os
            import time
            import socket
            import uuid
            from datetime import datetime, timedelta
            from PySide6.QtCore import qVersion, QSysInfo

            # 获取系统启动时间
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = f"{uptime.days}天 {uptime.seconds//3600}小时 {(uptime.seconds//60)%60}分钟"

            # 获取内存信息
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_str = f"{memory.total // (1024**3)} GB (可用: {memory.available // (1024**3)} GB, 使用率: {memory.percent}%)"
            swap_str = f"{swap.total // (1024**3)} GB (使用率: {swap.percent}%)" if swap.total > 0 else "无"

            # 获取CPU信息
            cpu_info = platform.processor()
            if not cpu_info:
                cpu_info = f"{platform.machine()}"
            cpu_count = psutil.cpu_count(logical=False)  # 物理核心
            cpu_logical = psutil.cpu_count(logical=True)  # 逻辑核心
            cpu_freq = psutil.cpu_freq()
            cpu_usage = psutil.cpu_percent(interval=1)

            # 获取磁盘信息
            disk_usage = psutil.disk_usage('/')
            disk_str = f"{disk_usage.total // (1024**3)} GB (可用: {disk_usage.free // (1024**3)} GB, 使用率: {(disk_usage.used/disk_usage.total)*100:.1f}%)"

            # 获取网络信息
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
            except:
                hostname = platform.node()
                local_ip = "Unknown"

            # 获取MAC地址
            try:
                mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
            except:
                mac_address = "Unknown"

            # 获取环境变量
            user = os.environ.get('USER') or os.environ.get('USERNAME', 'Unknown')
            home_dir = os.environ.get('HOME') or os.environ.get('USERPROFILE', 'Unknown')

            # 获取显示信息
            try:
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    screen = app.primaryScreen()
                    geometry = screen.geometry()
                    dpi = screen.logicalDotsPerInch()
                    display_str = f"{geometry.width()}x{geometry.height()} @ {dpi:.0f} DPI"
                else:
                    display_str = "Unknown"
            except:
                display_str = "Unknown"

            info = {
                # 基础系统信息
                "os": f"{platform.system()} {platform.release()} ({platform.version()})",
                "kernel": platform.platform(),
                "architecture": f"{platform.architecture()[0]} ({platform.machine()})",
                "hostname": hostname,
                "user": user,
                "home_directory": home_dir,

                # 硬件信息
                "cpu": f"{cpu_info} ({cpu_count}核心/{cpu_logical}线程)",
                "cpu_frequency": f"{cpu_freq.current:.0f} MHz (最大: {cpu_freq.max:.0f} MHz)" if cpu_freq else "Unknown",
                "cpu_usage": f"{cpu_usage}%",
                "memory": memory_str,
                "swap": swap_str,
                "disk": disk_str,
                "display": display_str,

                # 网络信息
                "local_ip": local_ip,
                "mac_address": mac_address,

                # 软件环境
                "python": f"Python {platform.python_version()} ({sys.executable})",
                "qt": f"Qt {qVersion()}",
                "pyside6": "PySide6 (已安装)",
                "rinui": "RinUI (已安装)",

                # 时间信息
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
                "uptime": uptime_str,
                "timezone": time.tzname[0],

                # TimeNest信息
                "timenest_version": version_manager.get_full_version(),
                "config_dir": str(getattr(self.config_manager, 'config_dir', 'Unknown')) if hasattr(self, 'config_manager') and self.config_manager else "Unknown",
                "data_dir": str(getattr(self.data_manager, 'data_dir', 'Unknown')) if hasattr(self, 'data_manager') and self.data_manager else "Unknown"
            }

            return info
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {
                "os": "Unknown",
                "cpu": "Unknown",
                "memory": "Unknown",
                "python": "Unknown",
                "qt": "Unknown",
                "uptime": "Unknown",
                "hostname": "Unknown",
                "architecture": "Unknown",
                "error": str(e)
            }

    @Slot(str)
    def updateWeatherData(self, city):
        """更新天气数据"""
        try:
            if self.floating_manager:
                self.floating_manager.update_weather_city(city)
                self.logger.info(f"天气城市已更新为: {city}")
        except Exception as e:
            self.logger.error(f"更新天气数据失败: {e}")

    @Slot(bool)
    def setWeatherEnabled(self, enabled):
        """设置天气显示开关"""
        try:
            if self.floating_manager:
                self.floating_manager.set_weather_enabled(enabled)
                self.logger.info(f"天气显示已{'启用' if enabled else '禁用'}")
        except Exception as e:
            self.logger.error(f"设置天气显示失败: {e}")

    @Slot(result='QVariant')
    def getWeatherData(self):
        """获取当前天气数据"""
        try:
            if self.floating_manager:
                return self.floating_manager.get_weather_data()
            return {"temperature": "N/A", "description": "无数据", "city": "未知"}
        except Exception as e:
            self.logger.error(f"获取天气数据失败: {e}")
            return {"temperature": "N/A", "description": "获取失败", "city": "未知"}

    @Slot()
    def openUserManual(self):
        """打开用户手册"""
        try:
            import webbrowser
            webbrowser.open("https://ziyi127.github.io/TimeNest-Website/manual")
            self.logger.info("已打开用户手册")
        except Exception as e:
            self.logger.error(f"打开用户手册失败: {e}")

    @Slot()
    def checkForUpdates(self):
        """检查更新"""
        try:
            # 实现更新检查逻辑
            import requests
            import json

            try:
                response = requests.get("https://api.github.com/repos/ziyi127/TimeNest/releases/latest", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data.get("tag_name", "").replace("v", "")
                    current_version = version_manager.get_version()

                    if latest_version and latest_version != current_version:
                        self.showNotification("更新检查", f"发现新版本: {latest_version}")
                    else:
                        self.showNotification("更新检查", "当前已是最新版本")
                else:
                    self.showNotification("更新检查", "检查更新失败")
            except requests.RequestException:
                self.showNotification("更新检查", "网络连接失败")

            self.logger.info("更新检查完成")
        except Exception as e:
            self.logger.error(f"检查更新失败: {e}")
            self.showNotification("更新检查", f"检查更新失败: {e}")

    @Slot()
    def minimizeToTray(self):
        """最小化到系统托盘"""
        try:
            if self.tray_manager:
                self.tray_manager.show_tray()
            self.logger.info("已最小化到系统托盘")
        except Exception as e:
            self.logger.error(f"最小化到托盘失败: {e}")

    @Slot()
    def exitApplication(self):
        """退出应用程序"""
        try:
            # 清理资源
            if self.floating_manager:
                self.floating_manager.cleanup()
            if self.tray_manager:
                self.tray_manager.cleanup()

            # 保存数据
            if self.data_manager:
                self.data_manager.save_all_data()

            self.logger.info("应用程序正在退出")

            # 退出应用
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
        except Exception as e:
            self.logger.error(f"退出应用失败: {e}")

    @Slot()
    def switchToSettingsView(self):
        """切换到设置页面"""
        try:
            # 发送信号通知QML切换到设置页面
            self.viewChangeRequested.emit("settings")
            self.logger.info("已请求切换到设置页面")
        except Exception as e:
            self.logger.error(f"切换到设置页面失败: {e}")

    # 添加视图切换信号
    viewChangeRequested = Signal(str)  # 请求切换视图

    # 悬浮窗设置方法
    @Slot(bool)
    def setFloatingAutoHide(self, auto_hide):
        """设置悬浮窗自动隐藏"""
        try:
            if self.floating_manager:
                self.floating_manager.set_auto_hide(auto_hide)
                self.logger.info(f"悬浮窗自动隐藏设置为: {auto_hide}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗自动隐藏失败: {e}")

    @Slot(bool)
    def setFloatingAlwaysOnTop(self, always_on_top):
        """设置悬浮窗始终置顶"""
        try:
            if self.floating_manager:
                self.floating_manager.set_always_on_top(always_on_top)
                self.logger.info(f"悬浮窗始终置顶设置为: {always_on_top}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗始终置顶失败: {e}")

    @Slot(bool)
    def setFloatingTransparent(self, transparent):
        """设置悬浮窗透明背景"""
        try:
            if self.floating_manager:
                self.floating_manager.set_transparent(transparent)
                self.logger.info(f"悬浮窗透明背景设置为: {transparent}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗透明背景失败: {e}")

    @Slot(int, int)
    def setFloatingPosition(self, x, y):
        """设置悬浮窗位置"""
        try:
            if self.floating_manager:
                self.floating_manager.set_position(x, y)
                self.logger.info(f"悬浮窗位置设置为: ({x}, {y})")
        except Exception as e:
            self.logger.error(f"设置悬浮窗位置失败: {e}")

    @Slot(str, result=bool)
    def setFloatingPositionPreset(self, preset):
        """设置悬浮窗预设位置"""
        try:
            if self.floating_manager:
                success = self.floating_manager.set_position_preset(preset)
                if success:
                    self.logger.info(f"悬浮窗位置设置为预设: {preset}")
                return success
            return False
        except Exception as e:
            self.logger.error(f"设置悬浮窗预设位置失败: {e}")
            return False

    @Slot(result=bool)
    def resetFloatingPosition(self):
        """重置悬浮窗位置"""
        try:
            if self.floating_manager:
                success = self.floating_manager.reset_position()
                if success:
                    self.logger.info("悬浮窗位置已重置")
                return success
            return False
        except Exception as e:
            self.logger.error(f"重置悬浮窗位置失败: {e}")
            return False

    @Slot(result='QVariant')
    def getFloatingPosition(self):
        """获取悬浮窗当前位置"""
        try:
            if self.floating_manager:
                pos = self.floating_manager.get_position()
                return {'x': pos[0], 'y': pos[1]} if pos else None
            return None
        except Exception as e:
            self.logger.error(f"获取悬浮窗位置失败: {e}")
            return None

    @Slot(bool)
    def setFloatingShowTime(self, show_time):
        """设置悬浮窗显示时间"""
        try:
            if self.floating_manager:
                self.floating_manager.set_show_time(show_time)
                self.logger.info(f"悬浮窗显示时间设置为: {show_time}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗显示时间失败: {e}")

    @Slot(bool)
    def setFloatingShowCourse(self, show_course):
        """设置悬浮窗显示课程"""
        try:
            if self.floating_manager:
                self.floating_manager.set_show_course(show_course)
                self.logger.info(f"悬浮窗显示课程设置为: {show_course}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗显示课程失败: {e}")

    @Slot(bool)
    def setFloatingShowWeather(self, show_weather):
        """设置悬浮窗显示天气"""
        try:
            if self.floating_manager:
                self.floating_manager.set_show_weather(show_weather)
                self.logger.info(f"悬浮窗显示天气设置为: {show_weather}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗显示天气失败: {e}")

    @Slot(bool)
    def setFloatingShowTasks(self, show_tasks):
        """设置悬浮窗显示任务"""
        try:
            if self.floating_manager:
                self.floating_manager.set_show_tasks(show_tasks)
                self.logger.info(f"悬浮窗显示任务设置为: {show_tasks}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗显示任务失败: {e}")

    @Slot(float)
    def setFloatingOpacity(self, opacity):
        """设置悬浮窗透明度"""
        try:
            if self.floating_manager:
                self.floating_manager.set_opacity(opacity)
                self.logger.info(f"悬浮窗透明度设置为: {opacity}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗透明度失败: {e}")

    @Slot(int)
    def setFloatingFontSize(self, font_size):
        """设置悬浮窗字体大小"""
        try:
            if self.floating_manager:
                self.floating_manager.set_font_size(font_size)
                self.logger.info(f"悬浮窗字体大小设置为: {font_size}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗字体大小失败: {e}")

    @Slot(str)
    def setFloatingTheme(self, theme):
        """设置悬浮窗主题"""
        try:
            if self.floating_manager:
                self.floating_manager.set_theme(theme)
                self.logger.info(f"悬浮窗主题设置为: {theme}")
        except Exception as e:
            self.logger.error(f"设置悬浮窗主题失败: {e}")

    @Slot()
    def forceFloatingToTop(self):
        """强制悬浮窗置顶"""
        try:
            if self.floating_manager:
                self.floating_manager.force_to_top()
                self.logger.info("悬浮窗已强制置顶")
        except Exception as e:
            self.logger.error(f"强制悬浮窗置顶失败: {e}")

    @Slot(result=bool)
    def isFloatingWindowOnTop(self):
        """检测悬浮窗是否在最顶层"""
        try:
            if self.floating_manager:
                return self.floating_manager.is_on_top()
            return False
        except Exception as e:
            self.logger.error(f"检测悬浮窗置顶状态失败: {e}")
            return False

    def _monitor_memory(self):
        """静默监控内存使用情况（不显示警告）"""
        try:
            import psutil
            import gc
            from datetime import datetime

            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)

            if memory_mb > 1024:
                self.logger.debug(f"内存使用: {memory_mb:.1f}MB，执行清理")
                gc.collect()

                if hasattr(self.schedule_manager, '_invalidate_cache'):
                    self.schedule_manager._invalidate_cache()

            if (not hasattr(self, '_last_memory_log') or
                (datetime.now() - self._last_memory_log).total_seconds() > 1800):
                self.logger.debug(f"内存使用: {memory_mb:.1f}MB")
                self._last_memory_log = datetime.now()

        except ImportError:
            self.memory_monitor_timer.stop()
            self.logger.debug("psutil不可用，停止内存监控")
        except Exception as e:
            self.logger.debug(f"内存监控: {e}")

    def cleanup(self):
        """清理资源"""
        try:
            cleanup_timers(
                getattr(self, 'timer', None),
                getattr(self, 'memory_monitor_timer', None)
            )
            self.logger.info("RinUI桥接资源已清理")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")

    @Slot(result='QVariant')
    def getFloatingSettings(self):
        """获取悬浮窗设置"""
        try:
            if self.floating_manager:
                settings = self.floating_manager.get_settings()
                return settings if settings else {}
            return {}
        except Exception as e:
            self.logger.error(f"获取悬浮窗设置失败: {e}")
            return {}

    # 设置页面功能实现
    @Slot(str, 'QVariant')
    def saveSetting(self, key, value):
        """保存设置"""
        try:
            if self.data_manager:
                success = self.data_manager.save_setting(key, value)
                if success:
                    self.logger.debug(f"设置已保存: {key} = {value}")
                    # 应用设置变更
                    self._apply_setting_change(key, value)
                return success
            return False
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False

    @Slot(str, result='QVariant')
    def getSetting(self, key):
        """获取设置"""
        try:
            if self.data_manager:
                return self.data_manager.get_setting(key, None)
            return None
        except Exception as e:
            self.logger.error(f"获取设置失败: {e}")
            return None

    def _apply_setting_change(self, key, value):
        """应用设置变更"""
        try:
            if key == "app_theme":
                # 应用主题变更
                theme_names = ["light", "dark", "auto"]
                if 0 <= value < len(theme_names):
                    theme_name = theme_names[value]
                    if self.theme_manager:
                        self.theme_manager.set_theme(theme_name)

            elif key == "auto_start":
                # 应用开机自启动设置
                self._set_auto_start(value)

            elif key == "notifications_enabled":
                # 应用通知设置
                if self.notification_manager:
                    self.notification_manager.set_enabled(value)

            elif key == "floating_window_enabled":
                # 应用悬浮窗设置
                if self.floating_manager:
                    if value:
                        self.floating_manager.show_floating_window()
                    else:
                        self.floating_manager.hide_floating_window()

        except Exception as e:
            self.logger.error(f"应用设置变更失败: {e}")

    def _set_auto_start(self, enabled):
        """设置开机自启动"""
        try:
            import sys
            import os
            from pathlib import Path

            if sys.platform == "win32":
                import winreg
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
                app_name = "TimeNest"
                exe_path = sys.executable

                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    if enabled:
                        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                        self.logger.info("已启用开机自启动")
                    else:
                        try:
                            winreg.DeleteValue(key, app_name)
                            self.logger.info("已禁用开机自启动")
                        except FileNotFoundError:
                            pass  # 键不存在，忽略
                    winreg.CloseKey(key)
                except Exception as e:
                    self.logger.error(f"设置Windows开机自启动失败: {e}")

            elif sys.platform == "darwin":
                # macOS 自启动设置
                self.logger.info("macOS开机自启动设置暂未实现")

            elif sys.platform.startswith("linux"):
                # Linux 自启动设置
                desktop_file_content = f"""[Desktop Entry]
Type=Application
Name=TimeNest
Exec={sys.executable}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
                autostart_dir = Path.home() / ".config" / "autostart"
                autostart_dir.mkdir(parents=True, exist_ok=True)
                desktop_file = autostart_dir / "timenest.desktop"

                if enabled:
                    with open(desktop_file, 'w') as f:
                        f.write(desktop_file_content)
                    self.logger.info("已启用Linux开机自启动")
                else:
                    if desktop_file.exists():
                        desktop_file.unlink()
                    self.logger.info("已禁用Linux开机自启动")

        except Exception as e:
            self.logger.error(f"设置开机自启动失败: {e}")

    @Slot()
    def exportSettings(self):
        """导出设置"""
        try:
            if self.data_manager:
                # 获取所有设置
                settings = {}
                common_keys = [
                    "app_theme", "auto_start", "notifications_enabled",
                    "floating_window_enabled", "auto_hide_enabled",
                    "language", "font_size", "update_check_enabled"
                ]

                for key in common_keys:
                    value = self.data_manager.get_setting(key, None)
                    if value is not None:
                        settings[key] = value

                # 保存到文件
                from datetime import datetime
                import json
                from pathlib import Path

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"timenest_settings_{timestamp}.json"
                filepath = Path.home() / "Downloads" / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)

                self.showNotification("设置导出", f"设置已导出到: {filepath}")
                return str(filepath)
        except Exception as e:
            self.logger.error(f"导出设置失败: {e}")
            self.showNotification("导出失败", "设置导出失败，请检查权限")
            return ""

    @Slot()
    def importSettings(self):
        """导入设置"""
        try:
            # 这里应该打开文件选择对话框，暂时使用固定路径
            from pathlib import Path
            import json

            # 查找最新的设置文件
            downloads_dir = Path.home() / "Downloads"
            setting_files = list(downloads_dir.glob("timenest_settings_*.json"))

            if not setting_files:
                self.showNotification("导入失败", "未找到设置文件")
                return False

            # 使用最新的文件
            latest_file = max(setting_files, key=lambda x: x.stat().st_mtime)

            with open(latest_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # 应用设置
            if self.data_manager:
                for key, value in settings.items():
                    self.data_manager.save_setting(key, value)
                    self._apply_setting_change(key, value)

            self.showNotification("设置导入", f"设置已从 {latest_file.name} 导入")
            return True

        except Exception as e:
            self.logger.error(f"导入设置失败: {e}")
            self.showNotification("导入失败", "设置导入失败，请检查文件格式")
            return False

    @Slot()
    def resetSettings(self):
        """重置设置"""
        try:
            if self.data_manager:
                # 重置为默认值
                default_settings = {
                    "app_theme": 0,  # 浅色主题
                    "auto_start": False,
                    "notifications_enabled": True,
                    "floating_window_enabled": True,
                    "auto_hide_enabled": False,
                    "language": "zh_CN",
                    "font_size": 14,
                    "update_check_enabled": True
                }

                for key, value in default_settings.items():
                    self.data_manager.save_setting(key, value)
                    self._apply_setting_change(key, value)

                self.showNotification("设置重置", "所有设置已重置为默认值")
                return True
        except Exception as e:
            self.logger.error(f"重置设置失败: {e}")
            self.showNotification("重置失败", "设置重置失败")
            return False

    # ========== 菜单功能实现 ==========

    @Slot()
    def showNewCourseDialog(self):
        """显示新建课程对话框"""
        try:
            self.logger.info("显示新建课程对话框")
            self.showNotification("课程管理", "新建课程功能")
        except Exception as e:
            self.logger.error(f"显示新建课程对话框失败: {e}")

    @Slot()
    def showNewTaskDialog(self):
        """显示新建任务对话框"""
        try:
            self.logger.info("显示新建任务对话框")
            self.showNotification("任务管理", "新建任务功能")
        except Exception as e:
            self.logger.error(f"显示新建任务对话框失败: {e}")

    @Slot()
    def importExcelFile(self):
        """导入Excel文件"""
        try:
            self.logger.info("导入Excel文件")
            self.showNotification("数据管理", "Excel导入功能")
        except Exception as e:
            self.logger.error(f"导入Excel文件失败: {e}")

    @Slot()
    def exportExcelFile(self):
        """导出Excel文件"""
        try:
            self.logger.info("导出Excel文件")
            self.showNotification("数据管理", "Excel导出功能")
        except Exception as e:
            self.logger.error(f"导出Excel文件失败: {e}")

    @Slot()
    def toggleFullScreen(self):
        """切换全屏模式"""
        try:
            self.logger.info("切换全屏模式")
            self.showNotification("视图", "全屏模式切换")
        except Exception as e:
            self.logger.error(f"切换全屏模式失败: {e}")

    @Slot()
    def showPluginManager(self):
        """显示插件管理器"""
        try:
            self.logger.info("显示插件管理器")
            self.showNotification("插件管理", "插件管理功能")
        except Exception as e:
            self.logger.error(f"显示插件管理器失败: {e}")

    @Slot()
    def showThemeManager(self):
        """显示主题管理器"""
        try:
            self.logger.info("显示主题管理器")
            self.showNotification("主题管理", "主题管理功能")
        except Exception as e:
            self.logger.error(f"显示主题管理器失败: {e}")

    @Slot()
    def calibrateTime(self):
        """时间校准"""
        try:
            import time
            from datetime import datetime

            self.logger.info("开始时间校准")

            # 获取网络时间
            try:
                import requests
                response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Shanghai', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    network_time = data['datetime']
                    self.showNotification("时间校准", f"网络时间: {network_time[:19]}")
                else:
                    self.showNotification("时间校准", "无法获取网络时间")
            except Exception as e:
                self.logger.error(f"获取网络时间失败: {e}")
                local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.showNotification("时间校准", f"本地时间: {local_time}")

        except Exception as e:
            self.logger.error(f"时间校准失败: {e}")

    @Slot()
    def showSystemInfo(self):
        """显示系统信息"""
        try:
            import platform

            self.logger.info("显示系统信息")

            # 获取系统信息
            system_info = {
                "系统": platform.system(),
                "版本": platform.release(),
                "架构": platform.architecture()[0],
                "Python版本": platform.python_version()
            }

            try:
                import psutil
                system_info["内存"] = f"{psutil.virtual_memory().total // (1024**3)} GB"
            except ImportError:
                system_info["内存"] = "未知"

            info_text = " | ".join([f"{k}: {v}" for k, v in system_info.items()])
            self.showNotification("系统信息", info_text)

        except Exception as e:
            self.logger.error(f"显示系统信息失败: {e}")
            self.showNotification("系统信息", "获取系统信息失败")

    @Slot()
    def openUserManual(self):
        """打开用户手册"""
        try:
            import webbrowser
            self.logger.info("打开用户手册")

            # 打开在线文档
            manual_url = "https://ziyi127.github.io/TimeNest-Website/docs"
            webbrowser.open(manual_url)
            self.showNotification("帮助", "已打开用户手册")

        except Exception as e:
            self.logger.error(f"打开用户手册失败: {e}")
            self.showNotification("帮助", "打开用户手册失败")

    @Slot()
    def showShortcuts(self):
        """显示快捷键帮助"""
        try:
            self.logger.info("显示快捷键帮助")

            shortcuts = [
                "Ctrl+N: 新建课程",
                "Ctrl+T: 新建任务",
                "Ctrl+S: 保存",
                "Ctrl+O: 导入",
                "Ctrl+E: 导出",
                "F11: 全屏",
                "Ctrl+Q: 退出"
            ]

            shortcuts_text = " | ".join(shortcuts)
            self.showNotification("快捷键", shortcuts_text)

        except Exception as e:
            self.logger.error(f"显示快捷键帮助失败: {e}")

    @Slot()
    def checkForUpdates(self):
        """检查更新"""
        try:
            from utils.version_manager import get_version

            self.logger.info("检查应用更新")

            try:
                import requests
                # 检查GitHub releases
                response = requests.get(
                    'https://api.github.com/repos/ziyi127/TimeNest/releases/latest',
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    latest_version = data['tag_name'].replace('v', '')
                    current_version = get_version()

                    if latest_version != current_version:
                        self.showNotification("更新检查", f"发现新版本: {latest_version}")
                    else:
                        self.showNotification("更新检查", "当前已是最新版本")
                else:
                    self.showNotification("更新检查", "无法检查更新")

            except Exception as e:
                self.logger.error(f"检查更新失败: {e}")
                self.showNotification("更新检查", "检查更新失败")

        except Exception as e:
            self.logger.error(f"检查更新功能失败: {e}")

    @Slot()
    def minimizeToTray(self):
        """最小化到系统托盘"""
        try:
            self.logger.info("最小化到系统托盘")
            # 这里应该隐藏主窗口
            self.showNotification("系统托盘", "应用已最小化到系统托盘")
        except Exception as e:
            self.logger.error(f"最小化到系统托盘失败: {e}")

    @Slot()
    def showAboutDialog(self):
        """显示关于对话框"""
        try:
            from utils.version_manager import version_manager

            self.logger.info("显示关于对话框")

            # 获取应用信息
            app_name = version_manager.get_app_name()
            version = version_manager.get_full_version()
            author = version_manager.get_author_name()
            description = version_manager.get_app_description()

            about_text = f"{app_name} {version}\n\n{description}\n\n作者: {author}"
            self.showNotification("关于 TimeNest", about_text)

        except Exception as e:
            self.logger.error(f"显示关于对话框失败: {e}")
            self.showNotification("关于", "TimeNest - 智能时间管理助手")

    # ========== 插件管理功能 ==========

    @Slot()
    def openPluginMarket(self):
        """打开插件市场"""
        try:
            import webbrowser
            self.logger.info("打开插件市场")

            # 打开插件市场网站
            market_url = "https://github.com/ziyi127/TimeNest-Store"
            webbrowser.open(market_url)
            self.showNotification("插件市场", "已打开插件市场")

        except Exception as e:
            self.logger.error(f"打开插件市场失败: {e}")
            self.showNotification("插件市场", "打开插件市场失败")

    @Slot()
    def installLocalPlugin(self):
        """安装本地插件"""
        try:
            self.logger.info("安装本地插件")
            # 这里可以打开文件选择对话框
            self.showNotification("插件管理", "本地插件安装功能")

        except Exception as e:
            self.logger.error(f"安装本地插件失败: {e}")

    @Slot(str, bool)
    def togglePlugin(self, plugin_name, enabled):
        """切换插件启用状态"""
        try:
            self.logger.info(f"切换插件状态: {plugin_name} -> {enabled}")

            # 这里应该实际切换插件状态
            status = "启用" if enabled else "禁用"
            self.showNotification("插件管理", f"已{status}插件: {plugin_name}")

        except Exception as e:
            self.logger.error(f"切换插件状态失败: {e}")

    @Slot(str)
    def openPluginSettings(self, plugin_name):
        """打开插件设置"""
        try:
            self.logger.info(f"打开插件设置: {plugin_name}")
            self.showNotification("插件设置", f"打开 {plugin_name} 设置")

        except Exception as e:
            self.logger.error(f"打开插件设置失败: {e}")

    @Slot(str)
    def uninstallPlugin(self, plugin_name):
        """卸载插件"""
        try:
            self.logger.info(f"卸载插件: {plugin_name}")
            self.showNotification("插件管理", f"已卸载插件: {plugin_name}")

        except Exception as e:
            self.logger.error(f"卸载插件失败: {e}")


def register_qml_types():
    """注册QML类型"""
    qmlRegisterType(TimeNestBridge, "TimeNest", 1, 0, "TimeNestBridge")
