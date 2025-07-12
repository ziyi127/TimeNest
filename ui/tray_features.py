#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 托盘程序功能模块
实现托盘程序的各种功能
"""

import logging
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon

from ui.notification_window import NotificationWindow


class TrayFeatureManager(QObject):
    """托盘功能管理器"""
    
    # 信号定义
    feature_activated = pyqtSignal(str)  # 功能激活
    notification_sent = pyqtSignal(str, str)  # 通知发送
    
    def __init__(self, app_manager=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.TrayFeatureManager')
        self.app_manager = app_manager
        
        # 功能状态
        self.features_enabled = {
            'schedule_reminder': True,
            'time_calibration': True,
            'quick_notes': True,
            'system_monitor': True
        }
        
        # 定时器
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self._check_schedule_reminders)
        self.reminder_timer.start(60000)  # 每分钟检查一次
        
        # 通知窗口池
        self.notification_windows = []
        
        # 快速操作缓存
        self.quick_actions_cache = {}
        self.last_cache_update = None

        self.logger.info("托盘功能管理器初始化完成")
    
    def show_schedule_management(self):
        """显示课程表管理"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("课程表管理", "应用管理器不可用")
                return

            from ui.modules.schedule_management_dialog import ScheduleManagementDialog
            dialog = ScheduleManagementDialog(self.app_manager)
            dialog.exec()
            self.feature_activated.emit("schedule_management")
        except ImportError:
            self._show_feature_unavailable("课程表管理")
        except Exception as e:
            self.logger.error(f"显示课程表管理失败: {e}")
            self._show_error("课程表管理", str(e))
    
    def show_app_settings(self):
        """显示应用设置"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("应用设置", "应用管理器不可用")
                return

            from ui.modules.app_settings_dialog import AppSettingsDialog
            dialog = AppSettingsDialog(self.app_manager)
            dialog.exec()
            self.feature_activated.emit("app_settings")
        except ImportError:
            self._show_feature_unavailable("应用设置")
        except Exception as e:
            self.logger.error(f"显示应用设置失败: {e}")
            self._show_error("应用设置", str(e))
    
    def show_plugin_marketplace(self):
        """显示插件市场"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("插件市场", "应用管理器不可用")
                return

            from ui.modules.plugin_marketplace_dialog import PluginMarketplaceDialog
            dialog = PluginMarketplaceDialog(self.app_manager)
            dialog.exec()
            self.feature_activated.emit("plugin_marketplace")
        except ImportError:
            self._show_feature_unavailable("插件市场")
        except Exception as e:
            self.logger.error(f"显示插件市场失败: {e}")
            self._show_error("插件市场", str(e))
    
    def show_time_calibration(self):
        """显示时间校准"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("时间校准", "应用管理器不可用")
                return

            from ui.modules.time_calibration_dialog import TimeCalibrationDialog
            dialog = TimeCalibrationDialog(self.app_manager)
            dialog.exec()
            self.feature_activated.emit("time_calibration")
        except ImportError:
            self._show_feature_unavailable("时间校准")
        except Exception as e:
            self.logger.error(f"显示时间校准失败: {e}")
            self._show_error("时间校准", str(e))
    
    def show_floating_settings(self):
        """显示浮窗设置"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("浮窗设置", "应用管理器不可用")
                return

            from ui.floating_settings_tab import FloatingSettingsTab
            dialog = QDialog()
            dialog.setWindowTitle("浮窗设置")
            dialog.setFixedSize(500, 400)

            layout = QVBoxLayout(dialog)
            settings_widget = FloatingSettingsTab(self.app_manager.config_manager, self.app_manager.theme_manager)
            layout.addWidget(settings_widget)

            dialog.exec()
            self.feature_activated.emit("floating_settings")
        except ImportError:
            self._show_feature_unavailable("浮窗设置")
        except Exception as e:
            self.logger.error(f"显示浮窗设置失败: {e}")
            self._show_error("浮窗设置", str(e))
    
    def send_notification(self, title: str, message: str, duration: int = 5000):
        """发送通知"""
        try:
            notification = NotificationWindow(title, message, duration)
            notification.show_with_animation("top-right")
            
            # 管理通知窗口
            self.notification_windows.append(notification)
            notification.closed.connect(lambda: self._remove_notification(notification))
            
            # 限制同时显示的通知数量
            if len(self.notification_windows) > 3:
                oldest = self.notification_windows.pop(0)
                oldest.hide_with_animation()
            
            self.notification_sent.emit(title, message)
            self.logger.debug(f"发送通知: {title} - {message}")
            
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
    
    def _remove_notification(self, notification):
        """移除通知窗口"""
        if notification in self.notification_windows:
            self.notification_windows.remove(notification)
    
    def _check_schedule_reminders(self):
        """检查课程提醒"""
        if not self.features_enabled.get('schedule_reminder', False):
            return
        
        try:
            # 这里应该检查课程表并发送提醒
            # 暂时使用模拟数据
            current_time = datetime.now()
            
            # 模拟课程提醒逻辑
            if current_time.minute == 0:  # 整点提醒
                self.send_notification(
                    "课程提醒",
                    f"当前时间: {current_time.strftime('%H:%M')}\n请注意即将开始的课程",
                    3000
                )
                
        except Exception as e:
            self.logger.error(f"检查课程提醒失败: {e}")
    
    def _show_feature_unavailable(self, feature_name: str, reason: str = None):
        """显示功能不可用消息"""
        if reason:
            message = f"{feature_name}功能暂不可用：{reason}"
        else:
            message = f"{feature_name}功能正在开发中，敬请期待！"

        QMessageBox.information(
            None,
            "功能暂不可用",
            message
        )
    
    def _show_error(self, feature_name: str, error_msg: str):
        """显示错误消息"""
        QMessageBox.critical(
            None,
            f"{feature_name}错误",
            f"启动{feature_name}时发生错误：\n{error_msg}"
        )
    
    def enable_feature(self, feature_name: str, enabled: bool = True):
        """启用/禁用功能"""
        if feature_name in self.features_enabled:
            self.features_enabled[feature_name] = enabled
            self.logger.info(f"功能 {feature_name} {'启用' if enabled else '禁用'}")
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """检查功能是否启用"""
        return self.features_enabled.get(feature_name, False)
    
    def get_feature_status(self) -> Dict[str, bool]:
        """获取所有功能状态"""
        return self.features_enabled.copy()
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止定时器
            if self.reminder_timer:
                self.reminder_timer.stop()
            
            # 关闭所有通知窗口
            for notification in self.notification_windows:
                notification.close()
            self.notification_windows.clear()
            
            self.logger.info("托盘功能管理器已清理")

        except Exception as e:
            self.logger.error(f"托盘功能管理器清理失败: {e}")

    def start_quick_study_session(self, subject: str = "通用"):
        """快速开始学习会话"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("快速学习", "应用管理器不可用")
                return

            # 检查是否有学习助手
            if hasattr(self.app_manager, 'study_assistant'):
                # 创建快速任务
                task_id = self.app_manager.study_assistant.schedule_enhancement.add_study_task(
                    title=f"快速学习 - {subject}",
                    subject=subject,
                    due_date=datetime.now() + timedelta(hours=2),
                    estimated_duration=25
                )

                if task_id:
                    # 开始学习会话
                    session_id = self.app_manager.study_assistant.schedule_enhancement.start_study_session(task_id)
                    if session_id:
                        self.send_notification("学习会话开始", f"已开始 {subject} 学习会话")
                        self.feature_activated.emit("quick_study_session")
                    else:
                        self._show_error("快速学习", "无法开始学习会话")
                else:
                    self._show_error("快速学习", "无法创建学习任务")
            else:
                self._show_feature_unavailable("快速学习", "学习助手功能未启用")

        except Exception as e:
            self.logger.error(f"快速开始学习会话失败: {e}")
            self._show_error("快速学习", str(e))

    def start_focus_mode(self, duration: int = 25):
        """启动专注模式"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("专注模式", "应用管理器不可用")
                return

            # 检查是否有通知增强功能
            if hasattr(self.app_manager, 'notification_enhancement'):
                success = self.app_manager.notification_enhancement.start_focus_mode(duration)
                if success:
                    self.send_notification("专注模式", f"专注模式已启动，持续 {duration} 分钟")
                    self.feature_activated.emit("focus_mode")
                else:
                    self._show_error("专注模式", "无法启动专注模式")
            else:
                self._show_feature_unavailable("专注模式", "通知增强功能未启用")

        except Exception as e:
            self.logger.error(f"启动专注模式失败: {e}")
            self._show_error("专注模式", str(e))

    def show_study_statistics(self):
        """显示学习统计"""
        try:
            if not self.app_manager:
                self._show_feature_unavailable("学习统计", "应用管理器不可用")
                return

            # 检查是否有学习助手
            if hasattr(self.app_manager, 'study_assistant'):
                analytics = self.app_manager.study_assistant.get_learning_analytics()
                if analytics:
                    # 创建简单的统计显示对话框
                    from PyQt6.QtWidgets import QMessageBox

                    stats_text = f"""学习统计信息:

总学习时间: {analytics.total_study_time} 分钟
平均会话长度: {analytics.average_session_length:.1f} 分钟
任务完成率: {analytics.completion_rate:.1%}
连续学习天数: {analytics.streak_days} 天

最高效时间段: {', '.join(f'{h}:00' for h in analytics.most_productive_hours[:3])}
"""

                    QMessageBox.information(None, "学习统计", stats_text)
                    self.feature_activated.emit("study_statistics")
                else:
                    self._show_feature_unavailable("学习统计", "暂无足够的学习数据")
            else:
                self._show_feature_unavailable("学习统计", "学习助手功能未启用")

        except Exception as e:
            self.logger.error(f"显示学习统计失败: {e}")
            self._show_error("学习统计", str(e))

    def get_quick_actions(self) -> List[Dict[str, Any]]:
        """获取快速操作列表"""
        try:
            # 检查缓存
            if (self.last_cache_update and
                datetime.now() - self.last_cache_update < timedelta(minutes=5)):
                return self.quick_actions_cache.get('actions', [])

            actions = [
                {
                    'name': '快速学习',
                    'description': '开始25分钟学习会话',
                    'icon': '📚',
                    'action': 'start_quick_study',
                    'shortcut': 'Ctrl+Q'
                },
                {
                    'name': '专注模式',
                    'description': '启动专注模式',
                    'icon': '🎯',
                    'action': 'start_focus_mode',
                    'shortcut': 'Ctrl+F'
                },
                {
                    'name': '学习统计',
                    'description': '查看学习数据',
                    'icon': '📊',
                    'action': 'show_statistics',
                    'shortcut': 'Ctrl+S'
                },
                {
                    'name': '今日总结',
                    'description': '查看今日学习总结',
                    'icon': '📋',
                    'action': 'daily_summary',
                    'shortcut': 'Ctrl+D'
                }
            ]

            # 更新缓存
            self.quick_actions_cache['actions'] = actions
            self.last_cache_update = datetime.now()

            return actions

        except Exception as e:
            self.logger.error(f"获取快速操作失败: {e}")
            return []


class QuickActionDialog(QDialog):
    """快速操作对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快速操作")
        self.setFixedSize(300, 200)
        self.setWindowIcon(QIcon())
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("选择要执行的操作：")
        layout.addWidget(title_label)
        
        # 按钮区域
        button_layout = QVBoxLayout()
        
        # 快速按钮
        buttons = [
            ("📅 打开课程表", self._open_schedule),
            ("⏰ 时间校准", self._open_time_calibration),
            ("🔧 应用设置", self._open_settings),
            ("🔌 插件市场", self._open_plugins)
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
    
    def _open_schedule(self):
        """打开课程表"""
        self.close()
        # 这里应该发送信号或调用相应功能
    
    def _open_time_calibration(self):
        """打开时间校准"""
        self.close()
        # 这里应该发送信号或调用相应功能
    
    def _open_settings(self):
        """打开设置"""
        self.close()
        # 这里应该发送信号或调用相应功能
    
    def _open_plugins(self):
        """打开插件市场"""
        self.close()
        # 这里应该发送信号或调用相应功能
