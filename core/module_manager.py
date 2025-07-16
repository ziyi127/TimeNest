#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
except ImportError:
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 核心模块管理器
管理三大核心功能模块：课程表管理、应用设置、插件市场
"""

import logging
from typing import Dict, Optional, Any, TYPE_CHECKING
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QMessageBox


if TYPE_CHECKING:
    from core.app_manager import AppManager


class ModuleManager(QObject):
    """核心模块管理器"""
    
    # 信号定义
    module_opened = Signal(str)  # 模块已打开
    module_closed = Signal(str)  # 模块已关闭
    module_error = Signal(str, str)  # 模块错误
    
    def __init__(self, app_manager: 'AppManager'):
        super().__init__()
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.ModuleManager')
        
        # 模块对话框实例
        self.active_dialogs: Dict[str, QDialog] = {}
        
        # 模块状态
        self.module_states: Dict[str, Dict[str, Any]] = {
            'schedule': {'enabled': True, 'last_opened': None},
            'settings': {'enabled': True, 'last_opened': None},
            'plugins': {'enabled': True, 'last_opened': None}
        }
        
        self.logger.info("模块管理器初始化完成")
    
    def open_schedule_module(self) -> bool:
        """打开课程表管理模块"""
        try:
            module_id = 'schedule'
            
            # 检查是否已经打开
            if module_id in self.active_dialogs and self.active_dialogs[module_id].isVisible():
                self.active_dialogs[module_id].raise_()
                self.active_dialogs[module_id].activateWindow()
                return True
            
            # 延迟导入避免循环依赖
            # from ui.modules.schedule_management_dialog import ScheduleManagementDialog  # 已迁移到RinUI
            
            dialog = ScheduleManagementDialog(self.app_manager)
            dialog.finished.connect(lambda: self._on_module_closed(module_id))
            
            self.active_dialogs[module_id] = dialog
            dialog.show()
            
            self.module_opened.emit(module_id)
            self.logger.info("课程表管理模块已打开")
            return True
            
        except Exception as e:
            self.logger.error(f"打开课程表管理模块失败: {e}")
            self.module_error.emit('schedule', str(e))
            QMessageBox.critical(None, "错误", f"打开课程表管理失败: {e}")
            return False
    
    def open_settings_module(self) -> bool:
        """打开应用设置模块"""
        try:
            module_id = 'settings'
            
            # 检查是否已经打开
            if module_id in self.active_dialogs and self.active_dialogs[module_id].isVisible():
                self.active_dialogs[module_id].raise_()
                self.active_dialogs[module_id].activateWindow()
                return True
            
            # 延迟导入避免循环依赖
            # from ui.modules.app_settings_dialog import AppSettingsDialog  # 已迁移到RinUI
            
            dialog = AppSettingsDialog(self.app_manager)
            dialog.finished.connect(lambda: self._on_module_closed(module_id))
            
            self.active_dialogs[module_id] = dialog
            dialog.show()
            
            self.module_opened.emit(module_id)
            self.logger.info("应用设置模块已打开")
            return True
            
        except Exception as e:
            self.logger.error(f"打开应用设置模块失败: {e}")
            self.module_error.emit('settings', str(e))
            QMessageBox.critical(None, "错误", f"打开应用设置失败: {e}")
            return False
    
    def open_plugins_module(self) -> bool:
        """打开插件市场模块"""
        try:
            module_id = 'plugins'
            
            # 检查是否已经打开
            if module_id in self.active_dialogs and self.active_dialogs[module_id].isVisible():
                self.active_dialogs[module_id].raise_()
                self.active_dialogs[module_id].activateWindow()
                return True
            
            # 延迟导入避免循环依赖
            # from ui.modules.plugin_marketplace_dialog import PluginMarketplaceDialog  # 已迁移到RinUI
            
            dialog = PluginMarketplaceDialog(self.app_manager)
            dialog.finished.connect(lambda: self._on_module_closed(module_id))
            
            self.active_dialogs[module_id] = dialog
            dialog.show()
            
            self.module_opened.emit(module_id)
            self.logger.info("插件市场模块已打开")
            return True
            
        except Exception as e:
            self.logger.error(f"打开插件市场模块失败: {e}")
            self.module_error.emit('plugins', str(e))
            QMessageBox.critical(None, "错误", f"打开插件市场失败: {e}")
            return False
    
    def open_floating_settings(self) -> bool:
        """打开浮窗设置（快捷入口）"""
        try:
            if self.app_manager and self.app_manager.floating_manager:
                self.app_manager.floating_manager.show_settings_dialog()
                return True
            else:
                QMessageBox.warning(None, "警告", "浮窗管理器不可用")
                return False
                
        except Exception as e:
            self.logger.error(f"打开浮窗设置失败: {e}")
            QMessageBox.critical(None, "错误", f"打开浮窗设置失败: {e}")
            return False
    
    def open_time_calibration(self) -> bool:
        """打开时间校准（快捷入口）"""
        try:
            if not self.app_manager or not self.app_manager.time_calibration_service:
                QMessageBox.warning(None, "警告", "时间校准服务不可用")
                return False
            
            # 简单的时间校准对话框
            reply = QMessageBox.question(
                None, "时间校准", "是否开始自动时间校准？\n这将从多个时间服务器同步时间。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            
            if reply == QMessageBox.StandardButton.Yes:
                # 显示进度对话框:
            
                # 显示进度对话框
                from PySide6.QtWidgets import QProgressDialog
                from PySide6.QtCore import Qt
                
                progress = QProgressDialog("正在校准时间...", "取消", 0, 100)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()
                
                # 连接校准服务信号
                calibration_service = self.app_manager.time_calibration_service
                
                def on_progress(value, status):
                    progress.setValue(value)
                    progress.setLabelText(status)
                
                def on_completed(success, offset, message):
                    progress.close()
                    if success and hasattr(QMessageBox, "information"):
                        QMessageBox.information(None, "校准完成", message)
                    else:
                        QMessageBox.warning(None, "校准失败", message)
                
                calibration_service.calibration_progress.connect(on_progress)
                calibration_service.calibration_completed.connect(on_completed)
                
                # 开始校准
                calibration_service.start_calibration()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"时间校准失败: {e}")
            QMessageBox.critical(None, "错误", f"时间校准失败: {e}")
            return False
    
    def _on_module_closed(self, module_id: str):
        """模块关闭处理"""
        try:
            if module_id in self.active_dialogs:
                del self.active_dialogs[module_id]
            
            self.module_closed.emit(module_id)
            self.logger.debug(f"模块 {module_id} 已关闭")
            
        except Exception as e:
            self.logger.error(f"处理模块关闭失败: {e}")
    
    def close_all_modules(self):
        """关闭所有模块"""
        try:
            for module_id, dialog in list(self.active_dialogs.items()):
                if dialog and dialog.isVisible():
                    dialog.close()
            
            self.active_dialogs.clear()
            self.logger.info("所有模块已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭所有模块失败: {e}")
    
    def get_module_status(self, module_id: str) -> Dict[str, Any]:
        """获取模块状态"""
        return self.module_states.get(module_id, {})
    
    def is_module_open(self, module_id: str) -> bool:
        """检查模块是否打开"""
        return (module_id in self.active_dialogs and 
                self.active_dialogs[module_id].isVisible())
    
    def cleanup(self):
        """清理资源"""
        try:
            self.close_all_modules()
            self.logger.info("模块管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理模块管理器失败: {e}")
