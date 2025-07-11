#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 插件系统
支持插件加载、管理、联动机制等功能
"""

import os
import sys
import json
import logging
import importlib
import importlib.util
import requests
import zipfile
import tempfile
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer


class PluginStatus(Enum):
    """插件状态"""
    UNKNOWN = "unknown"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class PluginType(Enum):
    """插件类型"""
    COMPONENT = "component"  # 组件插件
    NOTIFICATION = "notification"  # 通知插件
    THEME = "theme"  # 主题插件
    EXPORT = "export"  # 导出插件
    INTEGRATION = "integration"  # 集成插件
    UTILITY = "utility"  # 工具插件


@dataclass
class PluginMetadata:
    """插件元数据"""
    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    plugin_type: PluginType = PluginType.UTILITY
    dependencies: List[str] = field(default_factory=list)
    api_version: str = "1.0.0"
    min_app_version: str = "1.0.0"
    max_app_version: str = ""
    homepage: str = ""
    repository: str = ""
    license: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'plugin_type': self.plugin_type.value,
            'dependencies': self.dependencies,
            'api_version': self.api_version,
            'min_app_version': self.min_app_version,
            'max_app_version': self.max_app_version,
            'homepage': self.homepage,
            'repository': self.repository,
            'license': self.license,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """从字典创建"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            author=data.get('author', ''),
            plugin_type=PluginType(data.get('plugin_type', 'utility')),
            dependencies=data.get('dependencies', []),
            api_version=data.get('api_version', '1.0.0'),
            min_app_version=data.get('min_app_version', '1.0.0'),
            max_app_version=data.get('max_app_version', ''),
            homepage=data.get('homepage', ''),
            repository=data.get('repository', ''),
            license=data.get('license', ''),
            tags=data.get('tags', [])
        )


class IPlugin(ABC):
    """插件接口"""
    
    def __init__(self):
        self.metadata: Optional[PluginMetadata] = None
        self.status = PluginStatus.UNKNOWN
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
    
    @abstractmethod
    def initialize(self, plugin_manager: 'PluginManager') -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def activate(self) -> bool:
        """激活插件"""
        pass
    
    @abstractmethod
    def deactivate(self) -> bool:
        """停用插件"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理插件资源"""
        pass
    
    def get_metadata(self) -> Optional[PluginMetadata]:
        """获取插件元数据"""
        return self.metadata
    
    def get_status(self) -> PluginStatus:
        """获取插件状态"""
        return self.status


class PluginEvent:
    """插件事件"""
    
    def __init__(self, event_type: str, data: Any = None, source_plugin: str = None):
        self.event_type = event_type
        self.data = data
        self.source_plugin = source_plugin
        self.handled = False
    
    def mark_handled(self):
        """标记事件已处理"""
        self.handled = True


class PluginEventBus(QObject):
    """插件事件总线"""
    
    # 信号定义
    event_published = pyqtSignal(str, object)  # 事件类型, 事件对象
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginEventBus')
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        try:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            
            if callback not in self.subscribers[event_type]:
                self.subscribers[event_type].append(callback)
                self.logger.debug(f"订阅事件: {event_type}")
                
        except Exception as e:
            self.logger.error(f"订阅事件失败: {e}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅事件"""
        try:
            if event_type in self.subscribers:
                if callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
                    self.logger.debug(f"取消订阅事件: {event_type}")
                    
        except Exception as e:
            self.logger.error(f"取消订阅事件失败: {e}")
    
    def publish(self, event: PluginEvent):
        """发布事件"""
        try:
            if event.event_type in self.subscribers:
                for callback in self.subscribers[event.event_type]:
                    try:
                        callback(event)
                        if event.handled:
                            break
                    except Exception as e:
                        self.logger.error(f"事件处理失败: {e}")
            
            self.event_published.emit(event.event_type, event)
            self.logger.debug(f"发布事件: {event.event_type}")
            
        except Exception as e:
            self.logger.error(f"发布事件失败: {e}")


class PluginManager(QObject):
    """插件管理器"""
    
    # 信号定义
    plugin_loaded = pyqtSignal(str)  # 插件ID
    plugin_activated = pyqtSignal(str)  # 插件ID
    plugin_deactivated = pyqtSignal(str)  # 插件ID
    plugin_error = pyqtSignal(str, str)  # 插件ID, 错误信息
    
    def __init__(self, app_version: str = "1.0.0", config_manager=None):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PluginManager')
        self.app_version = app_version
        self.config_manager = config_manager

        # 插件存储
        self.plugins: Dict[str, IPlugin] = {}
        self.plugin_modules: Dict[str, Any] = {}

        # 插件目录
        self.plugins_dir = Path.home() / '.timenest' / 'plugins'
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # 事件总线
        self.event_bus = PluginEventBus()

        # 插件依赖图
        self.dependency_graph: Dict[str, List[str]] = {}

        # 插件配置
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

        # 插件商城（延迟初始化）
        self.marketplace = None
    
    def load_plugins(self) -> bool:
        """加载所有插件"""
        try:
            self.logger.info("开始加载插件...")
            
            # 扫描插件目录
            plugin_dirs = [d for d in self.plugins_dir.iterdir() if d.is_dir()]
            
            for plugin_dir in plugin_dirs:
                try:
                    self._load_plugin_from_directory(plugin_dir)
                except Exception as e:
                    self.logger.error(f"加载插件失败 {plugin_dir.name}: {e}")
            
            # 解析依赖关系
            self._resolve_dependencies()
            
            self.logger.info(f"插件加载完成，共加载 {len(self.plugins)} 个插件")
            return True
            
        except Exception as e:
            self.logger.error(f"加载插件失败: {e}")
            return False
    
    def _load_plugin_from_directory(self, plugin_dir: Path):
        """从目录加载插件"""
        try:
            # 查找插件清单文件
            manifest_file = plugin_dir / 'plugin.json'
            if not manifest_file.exists():
                self.logger.warning(f"插件清单文件不存在: {manifest_file}")
                return
            
            # 读取插件元数据
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            metadata = PluginMetadata.from_dict(manifest_data)
            
            # 检查版本兼容性
            if not self._check_version_compatibility(metadata):
                self.logger.warning(f"插件版本不兼容: {metadata.name}")
                return
            
            # 查找插件主模块
            main_module = manifest_data.get('main_module', 'main.py')
            module_file = plugin_dir / main_module
            
            if not module_file.exists():
                self.logger.error(f"插件主模块不存在: {module_file}")
                return
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(
                f"plugin_{metadata.id}", 
                module_file
            )
            module = importlib.util.module_from_spec(spec)
            
            # 添加插件目录到sys.path
            if str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            try:
                spec.loader.exec_module(module)
            finally:
                # 移除插件目录
                if str(plugin_dir) in sys.path:
                    sys.path.remove(str(plugin_dir))
            
            # 查找插件类
            plugin_class = getattr(module, manifest_data.get('plugin_class', 'Plugin'), None)
            if not plugin_class:
                self.logger.error(f"插件类不存在: {manifest_data.get('plugin_class', 'Plugin')}")
                return
            
            # 创建插件实例
            plugin_instance = plugin_class()
            plugin_instance.metadata = metadata
            plugin_instance.status = PluginStatus.LOADED
            
            # 初始化插件
            if plugin_instance.initialize(self):
                self.plugins[metadata.id] = plugin_instance
                self.plugin_modules[metadata.id] = module
                self.plugin_loaded.emit(metadata.id)
                
                self.logger.info(f"插件加载成功: {metadata.name}")
            else:
                self.logger.error(f"插件初始化失败: {metadata.name}")
                
        except Exception as e:
            self.logger.error(f"从目录加载插件失败: {e}")
    
    def _check_version_compatibility(self, metadata: PluginMetadata) -> bool:
        """检查版本兼容性"""
        try:
            # 这里应该实现版本比较逻辑
            # 简化实现，假设都兼容
            return True
            
        except Exception as e:
            self.logger.error(f"检查版本兼容性失败: {e}")
            return False

    def _resolve_dependencies(self):
        """解析插件依赖关系并处理循环依赖"""
        try:
            # 构建依赖图
            self.dependency_graph = {}
            for plugin_id, plugin in self.plugins.items():
                metadata = plugin.get_metadata()
                if metadata and metadata.dependencies:
                    # 确保所有依赖都是已知的插件
                    valid_deps = [dep for dep in metadata.dependencies if dep in self.plugins]
                    if len(valid_deps) != len(metadata.dependencies):
                        missing_deps = set(metadata.dependencies) - set(valid_deps)
                        self.logger.warning(f"插件 '{plugin_id}' 缺少依赖: {', '.join(missing_deps)}. 这些依赖将被忽略。")
                    self.dependency_graph[plugin_id] = valid_deps
                else:
                    self.dependency_graph[plugin_id] = []

            # 查找并处理循环依赖
            cycles = self._find_circular_dependencies()
            if cycles:
                self.logger.error("检测到插件间的循环依赖！将禁用相关插件。")
                all_cyclic_plugins = set()
                for i, cycle in enumerate(cycles):
                    cycle_str = " -> ".join(cycle) + f" -> {cycle[0]}"
                    self.logger.error(f"  循环 {i+1}: {cycle_str}")
                    all_cyclic_plugins.update(cycle)

                for plugin_id in all_cyclic_plugins:
                    if plugin_id in self.plugins:
                        plugin = self.plugins[plugin_id]
                        plugin.status = PluginStatus.ERROR
                        error_msg = "存在循环依赖"
                        self.plugin_error.emit(plugin_id, error_msg)
                        self.logger.warning(f"因循环依赖，插件 '{plugin_id}' 已被禁用。")
            
            return not bool(cycles)

        except Exception as e:
            self.logger.error(f"解析依赖关系失败: {e}", exc_info=True)
            return False

    def _find_circular_dependencies(self) -> List[List[str]]:
        """查找所有循环依赖."""
        cycles = []
        path = []
        visiting = set()
        visited = set()

        def dfs(plugin_id: str):
            path.append(plugin_id)
            visiting.add(plugin_id)
            visited.add(plugin_id)

            for dep in self.dependency_graph.get(plugin_id, []):
                if dep in visiting:
                    try:
                        cycle_start_index = path.index(dep)
                        cycle = path[cycle_start_index:]
                        sorted_cycle = tuple(sorted(cycle))
                        if sorted_cycle not in [tuple(sorted(c)) for c in cycles]:
                            cycles.append(cycle)
                    except ValueError:
                        pass
                elif dep not in visited:
                    dfs(dep)

            visiting.remove(plugin_id)
            path.pop()

        for plugin_id in list(self.dependency_graph.keys()):
            if plugin_id not in visited:
                dfs(plugin_id)
        
        return cycles

    def activate_plugin(self, plugin_id: str) -> bool:
        """激活插件"""
        try:
            if plugin_id not in self.plugins:
                self.logger.error(f"插件不存在: {plugin_id}")
                return False

            plugin = self.plugins[plugin_id]

            # 检查状态
            if plugin.status == PluginStatus.ENABLED:
                self.logger.warning(f"插件已激活: {plugin_id}")
                return True

            # 激活依赖插件
            metadata = plugin.get_metadata()
            if metadata and metadata.dependencies:
                for dep_id in metadata.dependencies:
                    if not self.activate_plugin(dep_id):
                        self.logger.error(f"激活依赖插件失败: {dep_id}")
                        return False

            # 激活插件
            if plugin.activate():
                plugin.status = PluginStatus.ENABLED
                self.plugin_activated.emit(plugin_id)
                self.logger.info(f"插件激活成功: {plugin_id}")

                # 发布插件激活事件
                event = PluginEvent("plugin_activated", {"plugin_id": plugin_id}, plugin_id)
                self.event_bus.publish(event)

                return True
            else:
                plugin.status = PluginStatus.ERROR
                self.plugin_error.emit(plugin_id, "激活失败")
                return False

        except Exception as e:
            error_msg = f"激活插件失败: {e}"
            self.logger.error(error_msg)
            self.plugin_error.emit(plugin_id, error_msg)
            return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """停用插件"""
        try:
            if plugin_id not in self.plugins:
                self.logger.error(f"插件不存在: {plugin_id}")
                return False

            plugin = self.plugins[plugin_id]

            # 检查状态
            if plugin.status != PluginStatus.ENABLED:
                self.logger.warning(f"插件未激活: {plugin_id}")
                return True

            # 检查是否有其他插件依赖此插件
            dependent_plugins = self._get_dependent_plugins(plugin_id)
            if dependent_plugins:
                self.logger.error(f"有其他插件依赖此插件: {dependent_plugins}")
                return False

            # 停用插件
            if plugin.deactivate():
                plugin.status = PluginStatus.DISABLED
                self.plugin_deactivated.emit(plugin_id)
                self.logger.info(f"插件停用成功: {plugin_id}")

                # 发布插件停用事件
                event = PluginEvent("plugin_deactivated", {"plugin_id": plugin_id}, plugin_id)
                self.event_bus.publish(event)

                return True
            else:
                plugin.status = PluginStatus.ERROR
                self.plugin_error.emit(plugin_id, "停用失败")
                return False

        except Exception as e:
            error_msg = f"停用插件失败: {e}"
            self.logger.error(error_msg)
            self.plugin_error.emit(plugin_id, error_msg)
            return False

    def _get_dependent_plugins(self, plugin_id: str) -> List[str]:
        """获取依赖指定插件的插件列表"""
        dependent = []
        for pid, deps in self.dependency_graph.items():
            if plugin_id in deps and self.plugins[pid].status == PluginStatus.ENABLED:
                dependent.append(pid)
        return dependent

    def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        try:
            if plugin_id not in self.plugins:
                self.logger.error(f"插件不存在: {plugin_id}")
                return False

            plugin = self.plugins[plugin_id]

            # 先停用插件
            if plugin.status == PluginStatus.ENABLED:
                if not self.deactivate_plugin(plugin_id):
                    return False

            # 清理插件资源
            plugin.cleanup()

            # 从管理器中移除
            del self.plugins[plugin_id]
            if plugin_id in self.plugin_modules:
                del self.plugin_modules[plugin_id]
            if plugin_id in self.dependency_graph:
                del self.dependency_graph[plugin_id]

            self.logger.info(f"插件卸载成功: {plugin_id}")
            return True

        except Exception as e:
            self.logger.error(f"卸载插件失败: {e}")
            return False

    def get_plugin(self, plugin_id: str) -> Optional[IPlugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_id)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[IPlugin]:
        """按类型获取插件"""
        result = []
        for plugin in self.plugins.values():
            metadata = plugin.get_metadata()
            if metadata and metadata.plugin_type == plugin_type:
                result.append(plugin)
        return result

    def get_enabled_plugins(self) -> List[IPlugin]:
        """获取已激活的插件"""
        return [plugin for plugin in self.plugins.values()
                if plugin.status == PluginStatus.ENABLED]

    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """获取插件配置"""
        return self.plugin_configs.get(plugin_id, {})

    def set_plugin_config(self, plugin_id: str, config: Dict[str, Any]):
        """设置插件配置"""
        self.plugin_configs[plugin_id] = config

    def get_event_bus(self) -> PluginEventBus:
        """获取事件总线"""
        return self.event_bus

    def get_statistics(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        try:
            total_plugins = len(self.plugins)
            enabled_plugins = len([p for p in self.plugins.values()
                                 if p.status == PluginStatus.ENABLED])
            disabled_plugins = len([p for p in self.plugins.values()
                                  if p.status == PluginStatus.DISABLED])
            error_plugins = len([p for p in self.plugins.values()
                               if p.status == PluginStatus.ERROR])

            return {
                'total': total_plugins,
                'enabled': enabled_plugins,
                'disabled': disabled_plugins,
                'error': error_plugins,
                'types': self._get_plugin_types_stats()
            }

        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}

    def _get_plugin_types_stats(self) -> Dict[str, int]:
        """获取插件类型统计"""
        type_stats = {}
        for plugin in self.plugins.values():
            metadata = plugin.get_metadata()
            if metadata:
                plugin_type = metadata.plugin_type.value
                type_stats[plugin_type] = type_stats.get(plugin_type, 0) + 1
        return type_stats

    def get_marketplace(self):
        """获取插件商城实例"""
        if self.marketplace is None:
            from .plugin_marketplace import PluginMarketplace
            self.marketplace = PluginMarketplace(self, self.config_manager)
        return self.marketplace

    def install_plugin_from_marketplace(self, plugin_id: str) -> bool:
        """从商城安装插件"""
        try:
            marketplace = self.get_marketplace()
            return marketplace.download_plugin(plugin_id)

        except Exception as e:
            self.logger.error(f"从商城安装插件失败: {e}")
            return False

    def check_plugin_updates(self) -> List[str]:
        """检查插件更新"""
        try:
            marketplace = self.get_marketplace()
            updates = []

            for plugin_id in self.plugins.keys():
                if marketplace.has_update(plugin_id):
                    updates.append(plugin_id)

            return updates

        except Exception as e:
            self.logger.error(f"检查插件更新失败: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        status_count = {}
        type_count = {}

        for plugin in self.plugins.values():
            # 统计状态
            status = plugin.status.value
            status_count[status] = status_count.get(status, 0) + 1

            # 统计类型
            metadata = plugin.get_metadata()
            if metadata:
                plugin_type = metadata.plugin_type.value
                type_count[plugin_type] = type_count.get(plugin_type, 0) + 1

        return {
            'total_plugins': len(self.plugins),
            'enabled_plugins': len(self.get_enabled_plugins()),
            'status_distribution': status_count,
            'type_distribution': type_count
        }
