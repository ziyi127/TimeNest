#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 浮窗管理器
负责浮窗的创建、销毁、状态管理和配置更新
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

from utils.common_imports import QObject, Signal

if TYPE_CHECKING:
    from core.app_manager import AppManager
    from core.config_manager import ConfigManager
    from core.theme_system import ThemeManager


class FloatingManager(QObject):
    """
    浮窗管理器，负责浮窗的生命周期和与系统其他部分的交互。

    Args:
        app_manager (AppManager): 主应用管理器实例。
    """
    visibility_changed = Signal(bool)

    def __init__(self, app_manager):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.FloatingManager')
        self.app_manager = app_manager
        self.config_manager = app_manager.config_manager
        self.theme_manager = app_manager.theme_manager

        self.floating_widget = None
        self._is_visible = False

        self._initialize_widget()

        try:
            self.config_manager.config_changed.connect(self.on_config_changed)
            self.theme_manager.theme_changed.connect(self.on_theme_changed)
        except Exception as e:
            self.logger.error(f"连接信号失败: {e}")

    def _initialize_widget(self):
        """初始化浮窗"""
        try:
            if self.config_manager.get_config('floating_widget.enabled', True):
                # self.floating_widget = FloatingWidget(self.app_manager)  # 已迁移到RinUI
                self.logger.info("浮窗组件已迁移到RinUI。")
                # if self.config_manager.get_config('floating_widget.show_on_startup', True):
                #     self.show_widget()
            else:
                self.logger.info("浮窗组件已禁用，未创建。")
        except Exception as e:
            self.logger.error(f"初始化浮窗失败: {e}", exc_info=True)

    def create_widget(self) -> bool:
        """创建浮窗组件"""
        try:
            # 避免重复创建
            if self.floating_widget is not None:
                return True

            self._initialize_widget()
            return self.floating_widget is not None
        except Exception as e:
            self.logger.error(f"创建浮窗失败: {e}")
            return False

    def show_widget(self):
        """显示浮窗"""
        try:
            if self.floating_widget and not self._is_visible:
                if hasattr(self.floating_widget, 'show_with_animation'):
                    self.floating_widget.show_with_animation()
                else:
                    self.floating_widget.show()
                self._is_visible = True
                self.visibility_changed.emit(True)
                self.logger.info("浮窗已显示。")
        except Exception as e:
            self.logger.error(f"显示浮窗失败: {e}")

    def hide_widget(self):
        """隐藏浮窗"""
        try:
            if self.floating_widget and self._is_visible:
                if hasattr(self.floating_widget, 'hide_with_animation'):
                    self.floating_widget.hide_with_animation()
                else:
                    self.floating_widget.hide()
                self._is_visible = False
                self.visibility_changed.emit(False)
                self.logger.info("浮窗已隐藏。")
        except Exception as e:
            self.logger.error(f"隐藏浮窗失败: {e}")

    def toggle_widget(self):
        """切换浮窗显示/隐藏状态"""
        if self._is_visible:
            self.hide_widget()
        else:
            self.show_widget()

    def on_config_changed(self, section: str, config: dict = None):
        """处理配置变更（优化版本）"""
        if section != 'floating_widget':
            return

        self.logger.debug("接收到浮窗配置变更，正在更新...")
        try:
            if self.floating_widget:
                enabled = self.config_manager.get_config('floating_widget.enabled', True)
                if not enabled:
                    self.cleanup()
                else:
                    if hasattr(self.floating_widget, 'update_from_config'):
                        self.floating_widget.update_from_config()
            else:
                self._initialize_widget()
        except Exception as e:
            self.logger.error(f"配置变更处理失败: {e}")

    def on_theme_changed(self, theme_id: str):
        """处理主题变更"""
        try:
            if self.floating_widget:
                self.logger.debug(f"接收到主题变更 '{theme_id}'，正在更新浮窗样式...")
                if hasattr(self.floating_widget, 'apply_theme'):
                    self.floating_widget.apply_theme()
        except Exception as e:
            self.logger.error(f"主题变更处理失败: {e}")

    def get_widget(self):
        """获取浮窗实例"""
        return self.floating_widget

    def is_visible(self) -> bool:
        """检查浮窗是否可见"""
        return self._is_visible

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        if not self.config_manager:
            return {}

        try:
            return self.config_manager.get_config('floating_widget', {})
        except (AttributeError, KeyError) as e:
            self.logger.error(f"获取当前配置失败: {e}", exc_info=True)
            return {}

    def apply_config(self, config: Dict[str, Any]):
        """应用配置"""
        try:
            if not config:
                return

            # 保存配置到配置管理器
            if self.config_manager:
                self.config_manager.set_config('floating_widget', config, save=True)

            # 立即应用到浮窗
            if self.floating_widget:
                self.floating_widget.update_from_config()
                self.logger.info("配置已应用到浮窗")

        except Exception as e:
            self.logger.error(f"应用配置失败: {e}")

    def show_settings_dialog(self):
        """显示浮窗设置对话框"""
        try:
            # 检查必要条件
            if not self.app_manager:
                self.logger.error("应用管理器未初始化，无法显示设置对话框")
                return

            # 延迟导入避免循环依赖 (已迁移到RinUI)
            # from ui.floating_widget.floating_settings import FloatingSettingsDialog

            # 检查是否已有对话框打开
            if (hasattr(self, '_settings_dialog') and
                self._settings_dialog and
                hasattr(self._settings_dialog, 'isVisible') and
                self._settings_dialog.isVisible()):
                self._settings_dialog.raise_()
                self._settings_dialog.activateWindow()
                return

            # 创建新对话框 (已迁移到RinUI)
            # self._settings_dialog = FloatingSettingsDialog(self.app_manager, self.floating_widget)
            self.logger.info("悬浮窗设置已迁移到RinUI界面")
            if self._settings_dialog:
                self._settings_dialog.show()
            else:
                self.logger.error("创建设置对话框失败")

        except ImportError as e:
            self.logger.error(f"导入设置对话框失败: {e}")
        except Exception as e:
            self.logger.error(f"显示设置对话框失败: {e}")

    def cleanup(self):
        """清理资源"""
        self.logger.info("正在清理浮窗管理器...")
        try:
            if self.floating_widget:
                if hasattr(self.floating_widget, 'close'):
                    self.floating_widget.close()
                self.floating_widget = None

            if hasattr(self.config_manager, 'config_changed'):
                self.config_manager.config_changed.disconnect(self.on_config_changed)
            if hasattr(self.theme_manager, 'theme_changed'):
                self.theme_manager.theme_changed.disconnect(self.on_theme_changed)
        except (TypeError, AttributeError) as e:
            self.logger.debug(f"清理信号连接时出错: {e}")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")

        self.logger.info("浮窗管理器清理完成。")