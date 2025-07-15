#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtCore import QObject
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 预览管理器
提供实时预览功能，支持主题、通知和插件状态的预览
"""

import logging
from typing import Dict, Any, Optional, Callable
from PySide6.QtCore import QObject, QTimer, Signal

from core.theme_manager import ThemeManager
from core.notification_system_v2 import NotificationSystemV2
from core.plugin_system import PluginManager


class PreviewManager(QObject):
    """
    预览管理器
    
    提供实时预览功能，支持主题、通知和插件状态的预览
    """
    
    # 信号定义
    preview_applied = Signal(str, dict)  # 预览已应用（类型，数据）
    preview_canceled = Signal(str)       # 预览已取消（类型）
    
    def __init__(self, theme_manager: Optional[ThemeManager] = None,
                 notification_system: Optional[NotificationSystemV2] = None,
                 plugin_manager: Optional[PluginManager] = None):
        """
        初始化预览管理器
        
        Args:
            theme_manager: 主题管理器
            notification_system: 通知系统
            plugin_manager: 插件管理器
        """
        super().__init__()
        
        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.PreviewManager')
        
        # 核心管理器
        self.theme_manager = theme_manager
        self.notification_system = notification_system
        self.plugin_manager = plugin_manager
        
        # 预览状态
        self.active_previews: Dict[str, Dict[str, Any]] = {}
        
        # 预览延迟定时器
        self.preview_timers: Dict[str, QTimer] = {}
        
        # 原始状态备份
        self.original_states: Dict[str, Any] = {}
        
        self.logger.info("预览管理器初始化完成")
    
    def preview_theme(self, theme_id: str, delay_ms: int = 500):
        """
        预览主题
        
        Args:
            theme_id: 主题ID
            delay_ms: 延迟应用时间（毫秒）
        """
        if not self.theme_manager:
            self.logger.warning("主题管理器未初始化，无法预览主题")
            return
        
        # 取消之前的主题预览定时器
        if 'theme' in self.preview_timers:
            self.preview_timers.get('theme').stop()
        
        # 备份原始主题（如果尚未备份）
        if 'theme' not in self.original_states:
            self.original_states['theme'] = self.theme_manager.get_current_theme_id()
        
        # 创建预览数据
        preview_data = {
            'theme_id': theme_id
        }
        self.active_previews['theme'] = preview_data
        
        # 创建延迟定时器
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._apply_theme_preview(theme_id))
        timer.start(delay_ms)
        
        self.preview_timers['theme'] = timer
        
        self.logger.debug(f"已安排主题预览: {theme_id}，延迟 {delay_ms}ms")
    
    def _apply_theme_preview(self, theme_id: str):
        """
        应用主题预览
        
        Args:
            theme_id: 主题ID
        """
        try:
            if self.theme_manager:
                self.theme_manager.preview_theme(theme_id)
                self.logger.info(f"已应用主题预览: {theme_id}")
                self.preview_applied.emit('theme', {'theme_id': theme_id})
        except Exception as e:
            self.logger.error(f"应用主题预览失败: {e}", exc_info=True)
    
    def cancel_theme_preview(self):
        """
        取消主题预览
        """
        if 'theme' not in self.original_states:
            return
        
        try:
            if self.theme_manager:
                original_theme_id = self.original_states.get('theme')
                self.theme_manager.apply_theme(original_theme_id)
                self.logger.info(f"已取消主题预览，恢复为: {original_theme_id}")
                
                # 清理状态
                if 'theme' in self.preview_timers:
                    self.preview_timers['theme'].stop()
                    del self.preview_timers['theme']

                if 'theme' in self.active_previews:
                    del self.active_previews['theme']

                del self.original_states['theme']
                
                self.preview_canceled.emit('theme')
        except Exception as e:
            self.logger.error(f"取消主题预览失败: {e}", exc_info=True)
    
    def test_notification(self, channels: list, template_data: Dict[str, Any] = None):
        """
        测试通知
        
        Args:
            channels: 通知渠道列表
            template_data: 模板数据
        """
        if not self.notification_system:
            self.logger.warning("通知系统未初始化，无法测试通知")
            return
        
        try:
            # 准备测试数据
            title = "测试通知"
            message = "这是一条测试通知，用于验证通知系统是否正常工作。"
            
            # 如果提供了模板数据，则使用模板
            if template_data:
                title = "测试通知: {subject}"
                message = "这是一条关于{subject}的测试通知，将在{classroom}进行。"
            
            # 发送测试通知
            self.notification_system.send_notification(
                title=title,
                message=message,
                channels=channels,
                template_data=template_data,
                notification_type="test"
            )
            
            self.logger.info(f"已发送测试通知，渠道: {channels}")
            self.preview_applied.emit('notification', {
                'channels': channels,
                'template_data': template_data
            })
        except Exception as e:
            self.logger.error(f"发送测试通知失败: {e}", exc_info=True)
    
    def preview_plugin_status(self, plugin_id: str, enabled: bool):
        """
        预览插件状态
        
        Args:
            plugin_id: 插件ID
            enabled: 是否启用
        """
        if not self.plugin_manager:
            self.logger.warning("插件管理器未初始化，无法预览插件状态")
            return
        
        try:
            # 备份原始状态（如果尚未备份）
            if 'plugin' not in self.original_states:
                self.original_states['plugin'] = {}
            
            
            if plugin_id not in self.original_states.get('plugin'):
                plugin = self.plugin_manager.get_plugin(plugin_id)
            
                plugin = self.plugin_manager.get_plugin(plugin_id)
                if plugin and hasattr(self, "original_states"):
                    self.original_states['plugin'][plugin_id] = plugin.is_enabled()
            
            # 应用预览状态
            if enabled and hasattr(self, "plugin_manager"):
                self.plugin_manager.activate_plugin(plugin_id, temporary=True)
            else:
                self.plugin_manager.deactivate_plugin(plugin_id, temporary=True)
            
            # 记录活动预览
            if 'plugin' not in self.active_previews:
                self.active_previews['plugin'] = {}
            
            self.active_previews.get('plugin')[plugin_id] = enabled
            
            self.logger.info(f"已预览插件状态: {plugin_id} -> {'启用' if enabled else '禁用'}")
            self.preview_applied.emit('plugin', {
                'plugin_id': plugin_id,
                'enabled': enabled
            })
        except Exception as e:
            self.logger.error(f"预览插件状态失败: {e}", exc_info=True)
    
    def cancel_plugin_preview(self, plugin_id: str = None):
        """
        取消插件预览
        
        Args:
            plugin_id: 插件ID，如果为None则取消所有插件预览
        """
        if 'plugin' not in self.original_states:
            return
        
        try:
            if plugin_id:
                # 取消单个插件预览:
                # 取消单个插件预览
                if plugin_id in self.original_states.get('plugin'):
                    original_state = self.original_states.get('plugin')[plugin_id]
                    if original_state and hasattr(self, "plugin_manager"):
                        self.plugin_manager.activate_plugin(plugin_id)
                    else:
                        self.plugin_manager.deactivate_plugin(plugin_id)
                    
                    del self.original_states['plugin'][plugin_id]

                    if 'plugin' in self.active_previews and plugin_id in self.active_previews['plugin']:
                        del self.active_previews['plugin'][plugin_id]
                    
                    self.logger.info(f"已取消插件预览: {plugin_id}")
                    self.preview_canceled.emit(f'plugin:{plugin_id}')
            else:
                # 取消所有插件预览
                for pid, original_state in self.original_states.get('plugin').items():
                    if original_state and hasattr(self, "plugin_manager"):
                        self.plugin_manager.activate_plugin(pid)
                    else:
                        self.plugin_manager.deactivate_plugin(pid)
                
                self.original_states['plugin'] = {}
                
                
                if 'plugin' in self.active_previews:
                    self.active_previews['plugin'] = {}
                
                self.logger.info("已取消所有插件预览")
                self.preview_canceled.emit('plugin:all')
        except Exception as e:
            self.logger.error(f"取消插件预览失败: {e}", exc_info=True)
    
    def apply_all_previews(self):
        """
        应用所有预览为永久设置
        """
        try:
            # 应用主题预览
            if 'theme' in self.active_previews:
                theme_id = self.active_previews.get('theme')['theme_id']
                if self.theme_manager:
                    self.theme_manager.apply_theme(theme_id, save=True)
                    self.logger.info(f"已永久应用主题: {theme_id}")
            
            # 应用插件状态预览
            if 'plugin' in self.active_previews:
                for plugin_id, enabled in self.active_previews.get('plugin').items():
                    if enabled and hasattr(self, "plugin_manager"):
                        self.plugin_manager.activate_plugin(plugin_id, temporary=False)
                    else:
                        self.plugin_manager.deactivate_plugin(plugin_id, temporary=False)
                    self.logger.info(f"已永久应用插件状态: {plugin_id} -> {'启用' if enabled else '禁用'}")
            
            # 清理所有预览状态
            self.active_previews = {}
            self.original_states = {}
            
            # 停止所有定时器
            for timer in self.preview_timers.values():
                timer.stop()
            self.preview_timers = {}
            
            self.logger.info("已应用所有预览为永久设置")
        except Exception as e:
            self.logger.error(f"应用所有预览失败: {e}", exc_info=True)
    
    def cancel_all_previews(self):
        """
        取消所有预览
        """
        try:
            # 取消主题预览
            if 'theme' in self.original_states:
                self.cancel_theme_preview()
            
            # 取消插件预览
            if 'plugin' in self.original_states:
                self.cancel_plugin_preview()
            
            # 停止所有定时器
            for timer in self.preview_timers.values():
                timer.stop()
            self.preview_timers = {}
            
            self.logger.info("已取消所有预览")
        except Exception as e:
            self.logger.error(f"取消所有预览失败: {e}", exc_info=True)
    
    def has_active_previews(self) -> bool:
        """
        检查是否有活动的预览
        
        Returns:
            是否有活动的预览
        """
        return len(self.active_previews) > 0