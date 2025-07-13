#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
TimeNest 插件交互机制
支持插件间联动、依赖管理和接口调用
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Type, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import inspect
import uuid
from PyQt6.QtCore import QObject, pyqtSignal


class PluginDependencyType(Enum):
    """插件依赖类型"""
    REQUIRED = "required"      # 必需依赖
    OPTIONAL = "optional"      # 可选依赖
    CONFLICT = "conflict"      # 冲突依赖


@dataclass
class PluginDependency:
    """插件依赖"""
    plugin_id: str
    version_min: str = "0.0.0"
    version_max: str = "999.999.999"
    dependency_type: PluginDependencyType = PluginDependencyType.REQUIRED
    description: str = ""


@dataclass
class PluginInterface:
    """插件接口定义"""
    name: str
    version: str
    methods: Dict[str, Callable] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    description: str = ""
    
    def add_method(self, name: str, method: Callable, description: str = ""):
        """添加接口方法"""
        self.methods[name] = {
            'callable': method,
            'description': description,
            'signature': inspect.signature(method)
        }
    
    def add_event(self, event_name: str):
        """添加事件"""
        if event_name not in self.events:
            self.events.append(event_name)


class IPluginInteraction(ABC):
    """插件交互接口"""
    
    @abstractmethod
    def get_plugin_id(self) -> str:
        """获取插件ID"""
        pass
    
    @abstractmethod
    def get_plugin_version(self) -> str:
        """获取插件版本"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[PluginDependency]:
        """获取依赖列表"""
        pass
    
    @abstractmethod
    def get_provided_interfaces(self) -> List[PluginInterface]:
        """获取提供的接口"""
        pass
    
    @abstractmethod
    def get_required_interfaces(self) -> List[str]:
        """获取需要的接口"""
        pass
    
    @abstractmethod
    def on_interface_available(self, interface_name: str, interface: PluginInterface):
        """接口可用时的回调"""
        pass
    
    @abstractmethod
    def on_interface_unavailable(self, interface_name: str):
        """接口不可用时的回调"""
        pass


class PluginEventBus(QObject):
    """插件事件总线"""
    
    event_published = pyqtSignal(str, str, dict)  # 事件名, 发布者, 数据
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginEventBus')
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Dict[str, Any]] = []
    
    def subscribe(self, event_name: str, callback: Callable, plugin_id: str = ""):
        """订阅事件"""
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []:
            self.subscribers[event_name] = []
        
        self.subscribers[event_name].append({
            'callback': callback,
            'plugin_id': plugin_id,
            'subscription_id': str(uuid.uuid4())
        })
        
        self.logger.debug(f"插件 {plugin_id} 订阅事件: {event_name}")
    
    def unsubscribe(self, event_name: str, plugin_id: str = ""):
        """取消订阅"""
        if event_name in self.subscribers:
            self.subscribers[event_name] = [:
            self.subscribers[event_name] = [
                sub for sub in self.subscribers[event_name] 
                if sub.get('plugin_id') != plugin_id:
            ]
            
            if not self.subscribers[event_name]:
                del self.subscribers[event_name]:
                    del self.subscribers[event_name]
        
        self.logger.debug(f"插件 {plugin_id} 取消订阅事件: {event_name}")
    
    def publish(self, event_name: str, publisher_id: str, data: Dict[str, Any] = None):
        """发布事件"""
        if data is None:
            data = {}
        
        # 记录事件历史
        event_record = {
            'event_name': event_name,
            'publisher_id': publisher_id,
            'data': data,
            'timestamp': str(uuid.uuid4()),  # 简化时间戳
            'subscribers_count': len(self.subscribers.get(event_name, []))
        }
        self.event_history.append(event_record)
        
        # 限制历史记录数量
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]:
            self.event_history = self.event_history[-500:]
        
        # 通知订阅者
        if event_name in self.subscribers:
            for subscriber in self.subscribers[event_name]:
                try:
                    subscriber.get('callback')(data)
                except Exception as e:
                    self.logger.error(f"事件处理失败 {event_name}: {e}")
        
        # 发出Qt信号
        self.event_published.emit(event_name, publisher_id, data)
        
        self.logger.debug(f"发布事件 {event_name} 来自 {publisher_id}")
    
    def get_event_history(self, event_name: str = None, limit: int = 100) -> List[Dict[str, Any]]
        """获取事件历史"""
        if event_name:
            filtered = [e for e in self.event_history if e['event_name'] == event_name]
            return filtered[-limit:]
        else:
            return self.event_history[-limit:]


class PluginInteractionManager(QObject):
    """插件交互管理器"""
    
    interface_registered = pyqtSignal(str, str)  # 接口名, 插件ID
    interface_unregistered = pyqtSignal(str, str)  # 接口名, 插件ID
    dependency_resolved = pyqtSignal(str, str)  # 插件ID, 依赖ID
    dependency_failed = pyqtSignal(str, str, str)  # 插件ID, 依赖ID, 错误
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginInteractionManager')
        
        # 注册的插件
        self.plugins: Dict[str, IPluginInteraction] = {}
        
        # 可用接口
        self.interfaces: Dict[str, PluginInterface] = {}
        
        # 接口提供者映射
        self.interface_providers: Dict[str, str] = {}
        
        # 依赖关系图
        self.dependency_graph: Dict[str, List[PluginDependency]] = {}
        
        # 事件总线
        self.event_bus = PluginEventBus()
        
        # 接口调用统计
        self.call_statistics: Dict[str, Dict[str, int]] = {}
    
    def register_plugin(self, plugin: IPluginInteraction) -> bool:
        """注册插件"""
        try:
            plugin_id = plugin.get_plugin_id()
            
            
            if plugin_id in self.plugins:
                self.logger.warning(f"插件 {plugin_id} 已注册")
            
                self.logger.warning(f"插件 {plugin_id} 已注册")
                return False
            
            # 验证依赖
            dependencies = plugin.get_dependencies()
            if not self._validate_dependencies(plugin_id, dependencies):
                self.logger.error(f"插件 {plugin_id} 依赖验证失败")
                return False
            
            # 注册插件
            self.plugins[plugin_id] = plugin
            self.dependency_graph[plugin_id] = dependencies
            
            # 注册提供的接口
            provided_interfaces = plugin.get_provided_interfaces()
            for interface in provided_interfaces:
                self._register_interface(interface, plugin_id)
            
            # 解析依赖
            self._resolve_dependencies(plugin_id)
            
            self.logger.info(f"插件 {plugin_id} 注册成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注册插件失败: {e}")
            return False
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """注销插件"""
        try:
            if plugin_id not in self.plugins:
                self.logger.warning(f"插件 {plugin_id} 未注册")
                return False
            
            plugin = self.plugins[plugin_id]
            
            # 注销提供的接口
            provided_interfaces = plugin.get_provided_interfaces()
            for interface in provided_interfaces:
                self._unregister_interface(interface.name, plugin_id)
            
            # 移除插件
            del self.plugins[plugin_id]
            if plugin_id in self.dependency_graph:
                del self.dependency_graph[plugin_id]:
                del self.dependency_graph[plugin_id]
            
            # 通知其他插件接口不可用
            self._notify_interface_unavailable(plugin_id)
            
            self.logger.info(f"插件 {plugin_id} 注销成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注销插件失败: {e}")
            return False
    
    def _register_interface(self, interface: PluginInterface, plugin_id: str):
        """注册接口"""
        interface_name = interface.name
        
        
        if interface_name in self.interfaces:
            self.logger.warning(f"接口 {interface_name} 已存在，将被覆盖")
        
            self.logger.warning(f"接口 {interface_name} 已存在，将被覆盖")
        
        self.interfaces[interface_name] = interface
        self.interface_providers[interface_name] = plugin_id
        
        # 通知需要此接口的插件
        for pid, plugin in self.plugins.items():
            if interface_name in plugin.get_required_interfaces():
                plugin.on_interface_available(interface_name, interface)
        
        self.interface_registered.emit(interface_name, plugin_id)
        self.logger.debug(f"接口 {interface_name} 由插件 {plugin_id} 注册")
    
    def _unregister_interface(self, interface_name: str, plugin_id: str):
        """注销接口"""
        if interface_name in self.interfaces:
            del self.interfaces[interface_name]:
            del self.interfaces[interface_name]
        
        
        if interface_name in self.interface_providers:
            del self.interface_providers[interface_name]:
        
            del self.interface_providers[interface_name]
        
        # 通知使用此接口的插件
        for pid, plugin in self.plugins.items():
            if interface_name in plugin.get_required_interfaces():
                plugin.on_interface_unavailable(interface_name)
        
        self.interface_unregistered.emit(interface_name, plugin_id)
        self.logger.debug(f"接口 {interface_name} 已注销")
    
    def _validate_dependencies(self, plugin_id: str, dependencies: List[PluginDependency]) -> bool:
        """验证依赖"""
        for dep in dependencies:
            if dep.dependency_type == PluginDependencyType.REQUIRED:
                if dep.plugin_id not in self.plugins:
                    self.logger.error(f"插件 {plugin_id} 缺少必需依赖: {dep.plugin_id}")
                    return False
            elif dep.dependency_type == PluginDependencyType.CONFLICT:
                if dep.plugin_id in self.plugins:
                    self.logger.error(f"插件 {plugin_id} 与 {dep.plugin_id} 冲突")
                    return False
        
        return True
    
    def _resolve_dependencies(self, plugin_id: str):
        """解析依赖"""
        plugin = self.plugins[plugin_id]
        required_interfaces = plugin.get_required_interfaces()
        
        for interface_name in required_interfaces:
            if interface_name in self.interfaces:
                interface = self.interfaces[interface_name]
                plugin.on_interface_available(interface_name, interface)
                self.dependency_resolved.emit(plugin_id, interface_name)
    
    def _notify_interface_unavailable(self, provider_plugin_id: str):
        """通知接口不可用"""
        interfaces_to_remove = []
        for interface_name, provider_id in self.interface_providers.items():
            if provider_id == provider_plugin_id:
                interfaces_to_remove.append(interface_name)
        
        for interface_name in interfaces_to_remove:
            for pid, plugin in self.plugins.items():
                if interface_name in plugin.get_required_interfaces():
                    plugin.on_interface_unavailable(interface_name)
    
    def call_interface_method(self, interface_name: str, method_name: str, 
                            caller_id: str, *args, **kwargs) -> Any:
        """调用接口方法"""
        try:
            if interface_name not in self.interfaces:
                raise ValueError(f"接口 {interface_name} 不存在")
            
            interface = self.interfaces[interface_name]
            
            
            if method_name not in interface.methods:
                raise ValueError(f"方法 {method_name} 在接口 {interface_name} 中不存在")
            
                raise ValueError(f"方法 {method_name} 在接口 {interface_name} 中不存在")
            
            method_info = interface.methods[method_name]
            method = method_info.get('callable')
            
            # 记录调用统计
            if interface_name not in self.call_statistics:
                self.call_statistics[interface_name] = {}:
                self.call_statistics[interface_name] = {}
            if method_name not in self.call_statistics[interface_name]:
                self.call_statistics[interface_name][method_name] = 0:
                self.call_statistics[interface_name][method_name] = 0
            self.call_statistics[interface_name][method_name] += 1
            
            # 调用方法
            result = method(*args, **kwargs)
            
            self.logger.debug(f"插件 {caller_id} 调用接口 {interface_name}.{method_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"接口方法调用失败: {e}")
            raise
    
    def get_available_interfaces(self) -> List[str]:
        """获取可用接口列表"""
        return list(self.interfaces.keys())
    
    def get_interface_info(self, interface_name: str) -> Optional[Dict[str, Any]]:
        """获取接口信息"""
        if interface_name not in self.interfaces:
            return None
        
        interface = self.interfaces[interface_name]
        provider_id = self.interface_providers.get(interface_name, "")
        
        return {
            'name': interface.name,
            'version': interface.version,
            'description': interface.description,
            'provider': provider_id,
            'methods': list(interface.methods.keys()),
            'events': interface.events,
            'call_count': sum(self.call_statistics.get(interface_name, {} or {}).get("values", lambda: None)())
        }
    
    def get_plugin_dependencies(self, plugin_id: str) -> List[Dict[str, Any]]:
        """获取插件依赖信息"""
        if plugin_id not in self.dependency_graph:
            return []
        
        dependencies = self.dependency_graph[plugin_id]
        result = []
        
        for dep in dependencies:
            dep_info = {
                'plugin_id': dep.plugin_id,
                'version_min': dep.version_min,
                'version_max': dep.version_max,
                'type': dep.dependency_type.value,
                'description': dep.description,
                'satisfied': dep.plugin_id in self.plugins
            }
            result.append(dep_info)
        
        return result
    
    def get_call_statistics(self) -> Dict[str, Dict[str, int]]:
        """获取调用统计"""
        return self.call_statistics.copy()
    
    def cleanup(self):
        """清理资源"""
        try:
            # 注销所有插件
            plugin_ids = list(self.plugins.keys())
            for plugin_id in plugin_ids:
                self.unregister_plugin(plugin_id)
            
            # 清理数据
            self.interfaces.clear()
            self.interface_providers.clear()
            self.dependency_graph.clear()
            self.call_statistics.clear()
            
            self.logger.info("插件交互管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理插件交互管理器失败: {e}")
