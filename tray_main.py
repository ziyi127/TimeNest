#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 托盘程序主入口
提供完整的托盘功能，包括浮窗、通知、状态监控等
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon

# 导入核心组件
from core.config_manager import ConfigManager
from core.floating_manager import FloatingManager
from core.notification_manager import NotificationManager
from core.time_manager import TimeManager
from core.theme_system import ThemeSystem

# 导入UI组件
from ui.system_tray import SystemTrayManager
from ui.tray_features import TrayFeatureManager
from ui.tray_status_monitor import TrayStatusManager


class TimeNestTrayApp(QObject):
    """TimeNest 托盘应用主类"""
    
    # 应用信号
    app_ready = pyqtSignal()
    app_closing = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.TimeNestTrayApp')
        
        # 应用状态
        self.initialized = False
        self.qt_app = None
        
        # 核心管理器
        self.config_manager = None
        self.theme_system = None
        self.time_manager = None
        self.notification_manager = None
        self.floating_manager = None
        
        # 托盘组件
        self.tray_manager = None
        self.feature_manager = None
        self.status_monitor = None
        
        # 初始化应用
        self._init_application()
    
    def _init_application(self):
        """初始化应用"""
        try:
            self.logger.info("初始化 TimeNest 托盘应用...")
            
            # 检查系统托盘支持
            if not self._check_system_tray_support():
                return False
            
            # 初始化核心组件
            if not self._init_core_managers():
                return False
            
            # 初始化托盘组件
            if not self._init_tray_components():
                return False
            
            # 设置信号连接
            self._setup_connections()
            
            self.initialized = True
            self.logger.info("TimeNest 托盘应用初始化完成")
            self.app_ready.emit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"应用初始化失败: {e}")
            return False
    
    def _check_system_tray_support(self) -> bool:
        """检查系统托盘支持"""
        from PyQt6.QtWidgets import QSystemTrayIcon
        
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                None,
                "系统托盘不可用",
                "系统托盘功能不可用，无法启动托盘程序。"
            )
            return False
        return True
    
    def _init_core_managers(self) -> bool:
        """初始化核心管理器"""
        try:
            # 配置管理器
            self.config_manager = ConfigManager()
            if not self.config_manager.initialize():
                self.logger.error("配置管理器初始化失败")
                return False
            
            # 主题系统
            self.theme_system = ThemeSystem(self.config_manager)
            if not self.theme_system.initialize():
                self.logger.error("主题系统初始化失败")
                return False
            
            # 时间管理器
            self.time_manager = TimeManager(self.config_manager)
            if not self.time_manager.initialize():
                self.logger.error("时间管理器初始化失败")
                return False
            
            # 通知管理器
            self.notification_manager = NotificationManager(
                config_manager=self.config_manager,
                theme_manager=self.theme_system
            )
            if not self.notification_manager.initialize():
                self.logger.error("通知管理器初始化失败")
                return False
            
            # 浮窗管理器
            self.floating_manager = FloatingManager(
                config_manager=self.config_manager,
                theme_manager=self.theme_system
            )
            if not self.floating_manager.initialize():
                self.logger.error("浮窗管理器初始化失败")
                return False
            
            self.logger.info("核心管理器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"核心管理器初始化失败: {e}")
            return False
    
    def _init_tray_components(self) -> bool:
        """初始化托盘组件"""
        try:
            # 系统托盘管理器
            self.tray_manager = SystemTrayManager(
                floating_manager=self.floating_manager
            )
            
            # 功能管理器
            self.feature_manager = TrayFeatureManager()
            
            # 状态监控器
            self.status_monitor = TrayStatusManager()
            self.status_monitor.start_monitoring()
            
            self.logger.info("托盘组件初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"托盘组件初始化失败: {e}")
            return False
    
    def _setup_connections(self):
        """设置信号连接"""
        try:
            # 托盘管理器信号
            if self.tray_manager:
                self.tray_manager.floating_toggled.connect(self._on_floating_toggled)
                self.tray_manager.floating_settings_requested.connect(self.feature_manager.show_floating_settings)
                self.tray_manager.schedule_module_requested.connect(self.feature_manager.show_schedule_management)
                self.tray_manager.settings_module_requested.connect(self.feature_manager.show_app_settings)
                self.tray_manager.plugins_module_requested.connect(self.feature_manager.show_plugin_marketplace)
                self.tray_manager.time_calibration_requested.connect(self.feature_manager.show_time_calibration)
                self.tray_manager.quit_requested.connect(self.quit_application)
            
            # 状态监控器信号
            if self.status_monitor:
                self.status_monitor.alert_triggered.connect(self._on_system_alert)
                self.status_monitor.status_changed.connect(self._on_status_changed)
            
            # 功能管理器信号
            if self.feature_manager:
                self.feature_manager.notification_sent.connect(self._on_notification_request)
            
            self.logger.info("信号连接设置完成")
            
        except Exception as e:
            self.logger.error(f"设置信号连接失败: {e}")
    
    def _on_floating_toggled(self, visible: bool):
        """处理浮窗切换"""
        try:
            if self.floating_manager:
                if visible:
                    self.floating_manager.show_widget()
                else:
                    self.floating_manager.hide_widget()
                    
                self.logger.debug(f"浮窗状态切换: {visible}")
                
        except Exception as e:
            self.logger.error(f"浮窗切换失败: {e}")
    
    def _on_system_alert(self, alert_type: str, message: str):
        """处理系统警告"""
        try:
            if self.notification_manager:
                self.notification_manager.send_notification(
                    title="系统警告",
                    message=message,
                    notification_type="warning",
                    duration=5000
                )
                
            if self.tray_manager:
                self.tray_manager.show_message(
                    "系统警告",
                    message,
                    timeout=5000
                )
                
        except Exception as e:
            self.logger.error(f"处理系统警告失败: {e}")
    
    def _on_status_changed(self, status_type: str, status_data: dict):
        """处理状态变化"""
        try:
            if status_type == 'system' and self.tray_manager:
                # 更新托盘提示文本
                summary = self.status_monitor.get_status_summary()
                self.tray_manager.set_tooltip(f"TimeNest - {summary}")
                
        except Exception as e:
            self.logger.error(f"处理状态变化失败: {e}")
    
    def _on_notification_request(self, title: str, message: str):
        """处理通知请求"""
        try:
            if self.notification_manager:
                self.notification_manager.send_notification(
                    title=title,
                    message=message,
                    notification_type="info"
                )
                
        except Exception as e:
            self.logger.error(f"处理通知请求失败: {e}")
    
    def show_main_window(self):
        """显示主窗口（如果存在）"""
        try:
            # 这里可以启动完整的主应用
            self.logger.info("请求显示主窗口")
            
            # 发送通知
            if self.notification_manager:
                self.notification_manager.send_notification(
                    title="TimeNest",
                    message="主窗口功能正在开发中...",
                    notification_type="info"
                )
                
        except Exception as e:
            self.logger.error(f"显示主窗口失败: {e}")
    
    def quit_application(self):
        """退出应用"""
        try:
            self.logger.info("正在退出 TimeNest 托盘应用...")
            self.app_closing.emit()
            
            # 清理组件
            self._cleanup_components()
            
            # 退出Qt应用
            if self.qt_app:
                self.qt_app.quit()
                
        except Exception as e:
            self.logger.error(f"退出应用失败: {e}")
    
    def _cleanup_components(self):
        """清理组件"""
        try:
            # 清理托盘组件
            if self.status_monitor:
                self.status_monitor.cleanup()
            
            if self.feature_manager:
                self.feature_manager.cleanup()
            
            if self.tray_manager:
                self.tray_manager.cleanup()
            
            # 清理核心组件
            if self.floating_manager:
                self.floating_manager.cleanup()
            
            if self.notification_manager:
                self.notification_manager.cleanup()
            
            self.logger.info("组件清理完成")
            
        except Exception as e:
            self.logger.error(f"组件清理失败: {e}")
    
    def run(self):
        """运行应用"""
        if not self.initialized:
            self.logger.error("应用未正确初始化")
            return 1
        
        try:
            self.logger.info("TimeNest 托盘程序开始运行")
            return self.qt_app.exec()
            
        except Exception as e:
            self.logger.error(f"应用运行失败: {e}")
            return 1


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('timenest_tray.log', encoding='utf-8')
        ]
    )


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 创建Qt应用
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出应用
        
        # 设置应用信息
        app.setApplicationName("TimeNest Tray")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TimeNest")
        
        # 创建托盘应用
        tray_app = TimeNestTrayApp()
        tray_app.qt_app = app
        
        if not tray_app.initialized:
            logger.error("托盘应用初始化失败")
            return 1
        
        # 运行应用
        return tray_app.run()
        
    except Exception as e:
        logger.error(f"主函数执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
