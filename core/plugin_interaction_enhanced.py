#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 插件交互机制增强
支持依赖管理、接口注册、事件总线
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal
import json
import importlib
import inspect


class PluginDependencyType(Enum):
    """插件依赖类型"""
    REQUIRED = "required"    # 必需依赖
    OPTIONAL = "optional"    # 可选依赖
    CONFLICT = "conflict"    # 冲突依赖


class PluginStatus(Enum):
    """插件状态"""
    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginDependency:
    """插件依赖"""
    name: str
    version: str = "*"
    type: PluginDependencyType = PluginDependencyType.REQUIRED
    description: str = ""


@dataclass
class PluginInterface:
    """插件接口"""
    name: str
    version: str
    methods: Dict[str, Callable] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    description: str = ""
    
    def add_method(self, name: str, method: Callable):
        """添加方法"""
        self.methods[name] = method
    
    def add_event(self, event_name: str):
        """添加事件"""
        if event_name not in self.events:
            self.events.append(event_name)


@dataclass
class PluginMetadata:
    """插件元数据"""
    id: str
    name: str
    version: str
    author: str
    description: str
    dependencies: List[PluginDependency] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    entry_point: str = ""
    config_schema: Dict[str, Any] = field(default_factory=dict)
    status: PluginStatus = PluginStatus.INACTIVE


class PluginEventBus(QObject):
    """插件事件总线"""
    
    # 通用事件信号
    event_triggered = pyqtSignal(str, dict)  # 事件名, 事件数据
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginEventBus')
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
    
    def subscribe(self, event_name: str, callback: Callable):
        """订阅事件"""
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        
        if callback not in self.subscribers[event_name]:
            self.subscribers[event_name].append(callback)
            self.logger.debug(f"订阅事件: {event_name}")
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """取消订阅事件"""
        if event_name in self.subscribers:
            if callback in self.subscribers[event_name]:
                self.subscribers[event_name].remove(callback)
                self.logger.debug(f"取消订阅事件: {event_name}")
    
    def publish(self, event_name: str, event_data: Dict[str, Any] = None):
        """发布事件"""
        if event_data is None:
            event_data = {}
        
        try:
            # 记录事件历史
            self.event_history.append({
                'event_name': event_name,
                'event_data': event_data,
                'timestamp': str(datetime.now())
            })
            
            # 限制历史记录数量
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-500:]
            
            # 通知订阅者
            if event_name in self.subscribers:
                for callback in self.subscribers[event_name]:
                    try:
                        callback(event_data)
                    except Exception as e:
                        self.logger.error(f"事件回调执行失败 {event_name}: {e}")
            
            # 发出Qt信号
            self.event_triggered.emit(event_name, event_data)
            
            self.logger.debug(f"发布事件: {event_name}")
            
        except Exception as e:
            self.logger.error(f"发布事件失败 {event_name}: {e}")
    
    def get_event_history(self, event_name: str = None) -> List[Dict[str, Any]]:
        """获取事件历史"""
        if event_name is None:
            return self.event_history.copy()
        
        return [event for event in self.event_history if event['event_name'] == event_name]


class PluginInterfaceRegistry:
    """插件接口注册表"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.PluginInterfaceRegistry')
        self.interfaces: Dict[str, PluginInterface] = {}
        self.providers: Dict[str, str] = {}  # 接口名 -> 提供者插件ID
        self.consumers: Dict[str, Set[str]] = {}  # 接口名 -> 消费者插件ID集合
    
    def register_interface(self, plugin_id: str, interface: PluginInterface) -> bool:
        """注册接口"""
        try:
            if interface.name in self.interfaces:
                self.logger.warning(f"接口已存在: {interface.name}")
                return False
            
            self.interfaces[interface.name] = interface
            self.providers[interface.name] = plugin_id
            self.consumers[interface.name] = set()
            
            self.logger.info(f"注册接口: {interface.name} (提供者: {plugin_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"注册接口失败: {e}")
            return False
    
    def unregister_interface(self, interface_name: str) -> bool:
        """注销接口"""
        try:
            if interface_name in self.interfaces:
                del self.interfaces[interface_name]
                del self.providers[interface_name]
                del self.consumers[interface_name]
                
                self.logger.info(f"注销接口: {interface_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"注销接口失败: {e}")
            return False
    
    def get_interface(self, interface_name: str) -> Optional[PluginInterface]:
        """获取接口"""
        return self.interfaces.get(interface_name)
    
    def subscribe_interface(self, plugin_id: str, interface_name: str) -> bool:
        """订阅接口"""
        try:
            if interface_name in self.consumers:
                self.consumers[interface_name].add(plugin_id)
                self.logger.debug(f"订阅接口: {interface_name} (消费者: {plugin_id})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"订阅接口失败: {e}")
            return False
    
    def unsubscribe_interface(self, plugin_id: str, interface_name: str) -> bool:
        """取消订阅接口"""
        try:
            if interface_name in self.consumers:
                self.consumers[interface_name].discard(plugin_id)
                self.logger.debug(f"取消订阅接口: {interface_name} (消费者: {plugin_id})")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"取消订阅接口失败: {e}")
            return False
    
    def call_interface_method(self, interface_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用接口方法"""
        try:
            interface = self.get_interface(interface_name)
            if not interface:
                raise ValueError(f"接口不存在: {interface_name}")
            
            if method_name not in interface.methods:
                raise ValueError(f"方法不存在: {method_name}")
            
            method = interface.methods[method_name]
            return method(*args, **kwargs)
            
        except Exception as e:
            self.logger.error(f"调用接口方法失败 {interface_name}.{method_name}: {e}")
            raise
    
    def get_interface_list(self) -> List[str]:
        """获取接口列表"""
        return list(self.interfaces.keys())
    
    def get_interface_info(self, interface_name: str) -> Dict[str, Any]:
        """获取接口信息"""
        if interface_name not in self.interfaces:
            return {}
        
        interface = self.interfaces[interface_name]
        return {
            'name': interface.name,
            'version': interface.version,
            'description': interface.description,
            'methods': list(interface.methods.keys()),
            'events': interface.events,
            'provider': self.providers.get(interface_name),
            'consumers': list(self.consumers.get(interface_name, set()))
        }


class PluginDependencyManager:
    """插件依赖管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.PluginDependencyManager')
        self.plugins: Dict[str, PluginMetadata] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    def add_plugin(self, metadata: PluginMetadata):
        """添加插件"""
        self.plugins[metadata.id] = metadata
        self.dependency_graph[metadata.id] = set()
        
        # 构建依赖图
        for dep in metadata.dependencies:
            if dep.type != PluginDependencyType.CONFLICT:
                self.dependency_graph[metadata.id].add(dep.name)
    
    def remove_plugin(self, plugin_id: str):
        """移除插件"""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            del self.dependency_graph[plugin_id]
    
    def check_dependencies(self, plugin_id: str) -> Dict[str, Any]:
        """检查插件依赖"""
        if plugin_id not in self.plugins:
            return {'valid': False, 'errors': ['插件不存在']}
        
        plugin = self.plugins[plugin_id]
        errors = []
        warnings = []
        
        for dep in plugin.dependencies:
            if dep.type == PluginDependencyType.REQUIRED:
                if dep.name not in self.plugins:
                    errors.append(f"缺少必需依赖: {dep.name}")
                elif self.plugins[dep.name].status != PluginStatus.ACTIVE:
                    errors.append(f"依赖插件未激活: {dep.name}")
            
            elif dep.type == PluginDependencyType.OPTIONAL:
                if dep.name not in self.plugins:
                    warnings.append(f"缺少可选依赖: {dep.name}")
            
            elif dep.type == PluginDependencyType.CONFLICT:
                if dep.name in self.plugins and self.plugins[dep.name].status == PluginStatus.ACTIVE:
                    errors.append(f"存在冲突插件: {dep.name}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_load_order(self) -> List[str]:
        """获取插件加载顺序"""
        try:
            # 使用拓扑排序确定加载顺序
            visited = set()
            temp_visited = set()
            result = []
            
            def dfs(plugin_id: str):
                if plugin_id in temp_visited:
                    raise ValueError(f"检测到循环依赖: {plugin_id}")
                
                if plugin_id in visited:
                    return
                
                temp_visited.add(plugin_id)
                
                # 先访问依赖
                for dep_id in self.dependency_graph.get(plugin_id, set()):
                    if dep_id in self.plugins:
                        dfs(dep_id)
                
                temp_visited.remove(plugin_id)
                visited.add(plugin_id)
                result.append(plugin_id)
            
            for plugin_id in self.plugins:
                if plugin_id not in visited:
                    dfs(plugin_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"计算加载顺序失败: {e}")
            return list(self.plugins.keys())


class PluginInteractionManager(QObject):
    """插件交互管理器"""
    
    plugin_loaded = pyqtSignal(str)      # 插件ID
    plugin_unloaded = pyqtSignal(str)    # 插件ID
    interface_registered = pyqtSignal(str, str)  # 插件ID, 接口名
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginInteractionManager')
        
        # 核心组件
        self.event_bus = PluginEventBus()
        self.interface_registry = PluginInterfaceRegistry()
        self.dependency_manager = PluginDependencyManager()
        
        # 统计信息
        self.call_statistics: Dict[str, int] = {}
        
        self.logger.info("插件交互管理器初始化完成")
    
    def register_plugin_interface(self, plugin_id: str, interface: PluginInterface) -> bool:
        """注册插件接口"""
        try:
            success = self.interface_registry.register_interface(plugin_id, interface)
            if success:
                self.interface_registered.emit(plugin_id, interface.name)
                self.event_bus.publish('interface_registered', {
                    'plugin_id': plugin_id,
                    'interface_name': interface.name
                })
            return success
            
        except Exception as e:
            self.logger.error(f"注册插件接口失败: {e}")
            return False
    
    def call_plugin_method(self, interface_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用插件方法"""
        try:
            # 记录调用统计
            call_key = f"{interface_name}.{method_name}"
            self.call_statistics[call_key] = self.call_statistics.get(call_key, 0) + 1
            
            # 发布调用事件
            self.event_bus.publish('method_called', {
                'interface_name': interface_name,
                'method_name': method_name,
                'args': args,
                'kwargs': kwargs
            })
            
            # 执行调用
            result = self.interface_registry.call_interface_method(
                interface_name, method_name, *args, **kwargs
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"调用插件方法失败: {e}")
            raise
    
    def subscribe_event(self, event_name: str, callback: Callable):
        """订阅事件"""
        self.event_bus.subscribe(event_name, callback)
    
    def publish_event(self, event_name: str, event_data: Dict[str, Any] = None):
        """发布事件"""
        self.event_bus.publish(event_name, event_data)
    
    def get_available_interfaces(self) -> List[str]:
        """获取可用接口列表"""
        return self.interface_registry.get_interface_list()
    
    def get_interface_info(self, interface_name: str) -> Dict[str, Any]:
        """获取接口信息"""
        return self.interface_registry.get_interface_info(interface_name)
    
    def get_call_statistics(self) -> Dict[str, int]:
        """获取调用统计"""
        return self.call_statistics.copy()
    
    def get_event_history(self, event_name: str = None) -> List[Dict[str, Any]]:
        """获取事件历史"""
        return self.event_bus.get_event_history(event_name)
    
    def cleanup(self):
        """清理资源"""
        try:
            self.event_bus.subscribers.clear()
            self.interface_registry.interfaces.clear()
            self.dependency_manager.plugins.clear()
            self.call_statistics.clear()
            
            self.logger.info("插件交互管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
