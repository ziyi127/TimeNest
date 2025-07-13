#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 插件模板
这是一个基础的插件模板，您可以基于此模板开发自己的插件
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

# TimeNest 插件系统导入
from core.plugin_base import IPlugin, PluginMetadata, PluginType, PluginStatus


class MyPlugin(IPlugin):
    """
    我的插件类
    
    这是一个示例插件，展示了插件的基本结构和功能。
    您可以根据需要修改和扩展这个类。
    """
    
    def __init__(self):
        """初始化插件"""
        super().__init__()
        
        # 设置插件元数据
        self.metadata = PluginMetadata(
            id="my_plugin_template",
            name="插件模板",
            version="1.0.0",
            description="TimeNest 插件开发模板",
            author="Your Name",
            plugin_type=PluginType.UTILITY
        )
        
        # 插件配置
        self.config: Dict[str, Any] = {}
        
        # 插件状态
        self.is_running = False
        
        # 数据目录
        self.data_dir = Path.home() / '.timenest' / 'plugins' / self.metadata.id
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize(self, plugin_manager) -> bool:
        """
        初始化插件
        
        这个方法在插件加载时被调用，用于设置插件的基本配置和资源。
        
        Args:
            plugin_manager: 插件管理器实例
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 保存插件管理器引用
            self.plugin_manager = plugin_manager
            
            # 加载插件配置
            self._load_config()
            
            # 订阅系统事件
            self._subscribe_events()
            
            # 初始化插件资源
            self._initialize_resources()
            
            self.logger.info(f"插件 {self.metadata.name} 初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def activate(self) -> bool:
        """
        激活插件
        
        这个方法在插件被启用时调用，用于启动插件的主要功能。
        
        Returns:
            bool: 激活是否成功
        """
        try:
            # 检查插件是否已经激活
            if self.is_running:
                self.logger.warning("插件已经在运行中")
                return True
            
            # 启动插件功能
            self._start_plugin_functionality()
            
            # 注册 UI 组件（如果有）
            self._register_ui_components()
            
            # 启动后台任务（如果有）
            self._start_background_tasks()
            
            # 标记插件为运行状态
            self.is_running = True
            
            # 发布插件激活事件
            self._publish_event('plugin_activated', {'plugin_id': self.metadata.id})
            
            self.logger.info(f"插件 {self.metadata.name} 已激活")
            return True
            
        except Exception as e:
            self.logger.error(f"插件激活失败: {e}")
            return False
    
    def deactivate(self) -> bool:
        """
        停用插件
        
        这个方法在插件被禁用时调用，用于停止插件的功能。
        
        Returns:
            bool: 停用是否成功
        """
        try:
            # 检查插件是否在运行
            if not self.is_running:
                self.logger.warning("插件未在运行中")
                return True
            
            # 停止后台任务
            self._stop_background_tasks()
            
            # 注销 UI 组件
            self._unregister_ui_components()
            
            # 停止插件功能
            self._stop_plugin_functionality()
            
            # 保存插件状态
            self._save_config()
            
            # 标记插件为停止状态
            self.is_running = False
            
            # 发布插件停用事件
            self._publish_event('plugin_deactivated', {'plugin_id': self.metadata.id})
            
            self.logger.info(f"插件 {self.metadata.name} 已停用")
            return True
            
        except Exception as e:
            self.logger.error(f"插件停用失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """
        清理插件资源
        
        这个方法在插件被卸载时调用，用于清理所有资源。
        
        Returns:
            bool: 清理是否成功
        """
        try:
            # 确保插件已停用
            if self.is_running:
                self.deactivate()
            
            # 取消事件订阅
            self._unsubscribe_events()
            
            # 清理插件资源
            self._cleanup_resources()
            
            # 保存最终配置
            self._save_config()
            
            self.logger.info(f"插件 {self.metadata.name} 资源已清理")
            return True
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
            return False
    
    # ==  ==  ==  ==  ==  ==  ==  ==  ==  == 私有方法 ==  ==  ==  ==  ==  ==  ==  ==  ==  ==
    def _load_config(self):
        """加载插件配置"""
        try:
            # 从插件管理器获取配置
            self.config = self.plugin_manager.get_plugin_config(self.metadata.id)
            
            # 设置默认配置
            default_config = {
                'enabled': True,
                'example_setting': '默认值'
            }
            
            # 合并默认配置
            for key, value in default_config.items():
                if key not in self.config:
                    self.config[key] = value
            
            self.logger.debug("插件配置加载完成")
            
        except Exception as e:
            self.logger.error(f"加载插件配置失败: {e}")
            self.config = {}
    
    def _save_config(self):
        """保存插件配置"""
        try:
            self.plugin_manager.set_plugin_config(self.metadata.id, self.config)
            self.logger.debug("插件配置保存完成")
            
        except Exception as e:
            self.logger.error(f"保存插件配置失败: {e}")
    
    def _subscribe_events(self):
        """订阅系统事件"""
        try:
            event_bus = self.plugin_manager.get_event_bus()
            
            # 订阅感兴趣的事件
            event_bus.subscribe('app_started', self._on_app_started)
            event_bus.subscribe('app_closing', self._on_app_closing)
            event_bus.subscribe('schedule_changed', self._on_schedule_changed)
            
            self.logger.debug("事件订阅完成")
            
        except Exception as e:
            self.logger.error(f"订阅事件失败: {e}")
    
    def _unsubscribe_events(self):
        """取消事件订阅"""
        try:
            event_bus = self.plugin_manager.get_event_bus()
            
            # 取消事件订阅
            event_bus.unsubscribe('app_started', self._on_app_started)
            event_bus.unsubscribe('app_closing', self._on_app_closing)
            event_bus.unsubscribe('schedule_changed', self._on_schedule_changed)
            
            self.logger.debug("事件订阅已取消")
            
        except Exception as e:
            self.logger.error(f"取消事件订阅失败: {e}")
    
    def _initialize_resources(self):
        """初始化插件资源"""
        try:
            # 在这里初始化插件需要的资源
            # 例如：数据库连接、文件句柄、网络连接等
            
            self.logger.debug("插件资源初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化插件资源失败: {e}")
            raise
    
    def _cleanup_resources(self):
        """清理插件资源"""
        try:
            # 在这里清理插件使用的资源
            # 例如：关闭数据库连接、释放文件句柄、断开网络连接等
            
            self.logger.debug("插件资源清理完成")
            
        except Exception as e:
            self.logger.error(f"清理插件资源失败: {e}")
    
    def _start_plugin_functionality(self):
        """启动插件功能"""
        try:
            # 在这里启动插件的主要功能
            # 例如：启动定时器、开始监听事件、初始化 UI 等
            
            self.logger.debug("插件功能已启动")
            
        except Exception as e:
            self.logger.error(f"启动插件功能失败: {e}")
            raise
    
    def _stop_plugin_functionality(self):
        """停止插件功能"""
        try:
            # 在这里停止插件的主要功能
            # 例如：停止定时器、停止监听事件、隐藏 UI 等
            
            self.logger.debug("插件功能已停止")
            
        except Exception as e:
            self.logger.error(f"停止插件功能失败: {e}")
    
    def _register_ui_components(self):
        """注册 UI 组件"""
        try:
            # 在这里注册插件的 UI 组件
            # 例如：添加菜单项、注册浮窗组件、添加工具栏按钮等
            
            self.logger.debug("UI 组件注册完成")
            
        except Exception as e:
            self.logger.error(f"注册 UI 组件失败: {e}")
    
    def _unregister_ui_components(self):
        """注销 UI 组件"""
        try:
            # 在这里注销插件的 UI 组件
            # 例如：移除菜单项、注销浮窗组件、移除工具栏按钮等
            
            self.logger.debug("UI 组件注销完成")
            
        except Exception as e:
            self.logger.error(f"注销 UI 组件失败: {e}")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        try:
            # 在这里启动插件的后台任务
            # 例如：启动工作线程、开始定期任务等
            
            self.logger.debug("后台任务已启动")
            
        except Exception as e:
            self.logger.error(f"启动后台任务失败: {e}")
    
    def _stop_background_tasks(self):
        """停止后台任务"""
        try:
            # 在这里停止插件的后台任务
            # 例如：停止工作线程、取消定期任务等
            
            self.logger.debug("后台任务已停止")
            
        except Exception as e:
            self.logger.error(f"停止后台任务失败: {e}")
    
    def _publish_event(self, event_type: str, data: Dict[str, Any]):
        """发布事件"""
        try:
            from core.plugin_system import PluginEvent
            
            event_bus = self.plugin_manager.get_event_bus()
            event = PluginEvent(event_type, data, self.metadata.id)
            event_bus.publish(event)
            
        except Exception as e:
            self.logger.error(f"发布事件失败: {e}")
    
    # ==  ==  ==  ==  ==  ==  ==  ==  ==  == 事件处理方法 ==  ==  ==  ==  ==  ==  ==  ==  ==  ==
    def _on_app_started(self, event):
        """处理应用启动事件"""
        self.logger.info("应用已启动")
        # 在这里处理应用启动后需要执行的操作
    
    def _on_app_closing(self, event):
        """处理应用关闭事件"""
        self.logger.info("应用即将关闭")
        # 在这里处理应用关闭前需要执行的操作
    
    def _on_schedule_changed(self, event):
        """处理课程表变更事件"""
        self.logger.info("课程表已变更")
        # 在这里处理课程表变更后需要执行的操作
    
    # ==  ==  ==  ==  ==  ==  ==  ==  ==  == 公共方法 ==  ==  ==  ==  ==  ==  ==  ==  ==  ==
    def get_setting(self, key: str, default=None):
        """
        获取插件设置
        
        Args:
            key: 设置键名
            default: 默认值
            
        Returns:
            设置值
        """
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value):
        """
        设置插件配置
        
        Args:
            key: 设置键名
            value: 设置值
        """
        self.config[key] = value
        self._save_config()
    
    def get_data_file_path(self, filename: str) -> Path:
        """
        获取数据文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.data_dir / filename


# ==  ==  ==  ==  ==  ==  ==  ==  ==  == 插件入口点 ==  ==  ==  ==  ==  ==  ==  ==  ==  ==
def create_plugin():
    """
    创建插件实例
    
    这是插件的入口点，插件管理器会调用这个函数来创建插件实例。
    
    Returns:
        IPlugin: 插件实例
    """
    return MyPlugin()


# ==  ==  ==  ==  ==  ==  ==  ==  ==  == 插件信息 ==  ==  ==  ==  ==  ==  ==  ==  ==  ==
def get_plugin_info():
    """
    获取插件信息
    
    Returns:
        dict: 插件信息字典
    """
    return {
        'id': 'my_plugin_template',
        'name': '插件模板',
        'version': '1.0.0',
        'description': 'TimeNest 插件开发模板',
        'author': 'Your Name'
    }




if __name__ == '__main__':
    # 用于测试插件的代码:


    # 用于测试插件的代码
    print("这是一个 TimeNest 插件模板")
    print("插件信息:", get_plugin_info())
