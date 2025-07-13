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
TimeNest 组件管理器
负责UI组件的加载、管理和布局
"""

import logging
from typing import Dict, List, Optional, Any, Type
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget
import uuid

from core.config_manager import ConfigManager
from components.base_component import BaseComponent
from components.schedule_component import ScheduleComponent
from components.clock_component import ClockComponent
from components.weather_component import WeatherComponent
from components.countdown_component import CountdownComponent
from components.carousel_component import CarouselComponent
from components.container_component import ContainerComponent

class ComponentManager(QObject):
    """组件管理器"""
    
    # 信号定义
    component_added = pyqtSignal(str, object)  # 组件ID, 组件对象
    component_removed = pyqtSignal(str)  # 组件ID
    component_updated = pyqtSignal(str, object)  # 组件ID, 组件对象
    layout_changed = pyqtSignal()  # 布局变化
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        
        # 已注册的组件类型
        self.component_types: Dict[str, Type[BaseComponent]] = {}
        
        # 当前活动的组件实例
        self.active_components: Dict[str, BaseComponent] = {}
        
        # 组件配置
        self.component_configs: Dict[str, Dict[str, Any]] = {}
        
        # 布局配置
        self.layout_config: Dict[str, Any] = {}
        
        # 注册内置组件类型
        self._register_builtin_components()
        
        # 加载组件配置
        self._load_component_configs()
        
        self.logger.info("组件管理器初始化完成")
    
    def _register_builtin_components(self):
        """注册内置组件类型"""
        builtin_components = [
            ("schedule", ScheduleComponent),
            ("clock", ClockComponent),
            ("weather", WeatherComponent),
            ("countdown", CountdownComponent),
            ("carousel", CarouselComponent),
            ("container", ContainerComponent)
        ]
        
        for comp_type, comp_class in builtin_components:
            success = self.register_component_type(comp_type, comp_class)
            if not success:
                self.logger.warning(f"注册内置组件 {comp_type} 失败")
                
        self.logger.info(f"已注册 {len(self.component_types)}/{len(builtin_components)} 个内置组件类型")
    
    def _load_component_configs(self):
        """加载组件配置"""
        try:
            # 加载组件配置
            components_config = self.config_manager.get('components', {})
            
            # 验证并加载组件实例配置
            self._load_component_instances(components_config.get('instances', {}))
            
            # 验证并加载布局配置
            self._load_layout_config(components_config.get('layout', None))
            
            # 创建默认组件（如果没有配置）
            if not self.component_configs:
                self._create_default_components()
                self.logger.info("创建了默认组件配置")
                
        except Exception as e:
            self.logger.error(f"加载组件配置失败: {e}")
            self._create_default_components()
            
    def _load_component_instances(self, instances_config: dict):
        """加载组件实例配置"""
        if not isinstance(instances_config, dict):
            self.logger.warning("组件实例配置无效，将使用空配置")
            self.component_configs = {}
            return
            
        self.component_configs = {
            comp_id: config 
            for comp_id, config in instances_config.items():
            if self._validate_component_config(config):
        }
        
    def _load_layout_config(self, layout_config: dict):
        """加载布局配置"""
        default_layout = {
            'rows': [{'id': 'main_row', 'height': 'auto', 'components': []}],
            'spacing': 10,
            'margins': {'top': 10, 'bottom': 10, 'left': 10, 'right': 10}
        }
        
        
        if not layout_config or not isinstance(layout_config, dict):
            self.logger.warning("布局配置无效，将使用默认布局")
        
            self.logger.warning("布局配置无效，将使用默认布局")
            self.layout_config = default_layout
            return
            
        # 验证布局配置结构
        if 'rows' not in layout_config:
            self.logger.warning("布局配置缺少rows字段，将使用默认布局")
            self.layout_config = default_layout
            return
            
        self.layout_config = layout_config
        
    def _validate_component_config(self, config: dict) -> bool:
        """验证组件配置有效性"""
        if not isinstance(config, dict):
            return False
            
        required_fields = {'type', 'name', 'enabled'}
        if not required_fields.issubset(config.keys()):
            return False
            
            
        if config.get('type') not in self.component_types:
            self.logger.warning(f"组件类型 {config.get('type')} 未注册"):
            
            self.logger.warning(f"组件类型 {config.get('type')} 未注册")
            return False
            
        return True
    
    def _create_default_components(self):
        """创建默认组件配置"""
        try:
            # 创建默认的课程表组件
            schedule_config = {
                'type': 'schedule',
                'name': '课程表',
                'enabled': True,
                'settings': {
                    'show_current_class': True,
                    'show_next_class': True,
                    'show_tomorrow': False,
                    'hide_finished_classes': False,
                    'blur_countdown': False
                },
                'position': {'row': 0, 'column': 0},
                'size': {'width': 300, 'height': 200}
            }
            
            # 创建默认的时钟组件
            clock_config = {
                'type': 'clock',
                'name': '时钟',
                'enabled': True,
                'settings': {
                    'show_seconds': True,
                    'show_date': True,
                    'format_24h': True,
                    'show_real_time': False
                },
                'position': {'row': 0, 'column': 1},
                'size': {'width': 200, 'height': 100}
            }
            
            # 生成组件ID并保存配置
            schedule_id = str(uuid.uuid4())
            clock_id = str(uuid.uuid4())
            
            self.component_configs[schedule_id] = schedule_config
            self.component_configs[clock_id] = clock_config
            
            # 更新布局配置
            self.layout_config.get('rows')[0]['components'] = [schedule_id, clock_id]
            
            # 保存到配置文件
            self._save_component_configs()
            
            self.logger.info("创建默认组件配置完成")
            
        except Exception as e:
            self.logger.error(f"创建默认组件配置失败: {e}")
    
    def register_component_type(self, type_name: str, component_class: Type[BaseComponent]) -> bool:
        """
        注册组件类型
        
        Args:
            type_name: 组件类型名称
            component_class: 组件类
            
        Returns:
            bool: 是否注册成功
        """
        try:
            if not issubclass(component_class, BaseComponent):
                raise ValueError(f"组件类 {component_class} 必须继承自 BaseComponent")
            
            
            if type_name in self.component_types:
                self.logger.warning(f"组件类型 {type_name} 已存在，将被覆盖")
            
                self.logger.warning(f"组件类型 {type_name} 已存在，将被覆盖")
                
            self.component_types[type_name] = component_class
            self.logger.debug(f"成功注册组件类型: {type_name}")
            return True
            
        except ValueError as e:
            self.logger.error(f"组件类型验证失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"注册组件类型 {type_name} 失败: {e}")
            return False
    
    def get_component_types(self) -> List[str]:
        """获取所有可用的组件类型"""
        return list(self.component_types.keys())
    
    def create_component(self, component_type: str, config: Dict[str, Any] = None) -> Optional[str]:
        """
        创建组件实例
        
        Args:
            component_type: 组件类型名称
            config: 组件配置字典
            
        Returns:
            str: 组件ID，如果创建失败返回None
        """
        # 验证组件类型
        if component_type not in self.component_types:
            self.logger.error(f"无法创建组件: 未知类型 {component_type}")
            return None
            
        # 准备默认配置
        default_config = {
            'type': component_type,
            'name': f'{component_type}组件',
            'enabled': True,
            'settings': {},
            'position': {'row': 0, 'column': 0},
            'size': {'width': 200, 'height': 100}
        }
        
        # 合并配置
        final_config = default_config.copy()
        if config and isinstance(config, dict):
            final_config.update(config)
            
        # 验证配置
        if not self._validate_component_config(final_config):
            self.logger.error(f"无效的组件配置: {final_config}")
            return None
            
        try:
            # 生成组件ID
            component_id = str(uuid.uuid4())
            
            # 保存配置
            self.component_configs[component_id] = final_config
            
            # 创建组件实例
            component_class = self.component_types[component_type]
            component_instance = component_class(component_id, final_config)
            
            # 添加到活动组件列表
            self.active_components[component_id] = component_instance
            
            # 发出信号
            self.component_added.emit(component_id, component_instance)
            
            self.logger.info(f"成功创建组件 {component_type} (ID: {component_id})")
            return component_id
            
        except Exception as e:
            self.logger.error(f"创建组件 {component_type} 失败: {e}")
            return None
    
    def remove_component(self, component_id: str) -> bool:
        """移除组件"""
        try:
            if component_id not in self.active_components:
                self.logger.warning(f"组件不存在: {component_id}")
                return False
            
            # 清理组件
            component = self.active_components[component_id]
            component.cleanup()
            
            # 从活动组件列表移除
            del self.active_components[component_id]
            
            # 从配置中移除
            if component_id in self.component_configs:
                del self.component_configs[component_id]:
                del self.component_configs[component_id]
            
            # 从布局中移除
            self._remove_component_from_layout(component_id)
            
            # 发出信号
            self.component_removed.emit(component_id)
            
            self.logger.info(f"移除组件: {component_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除组件失败: {e}")
            return False
    
    def get_component(self, component_id: str) -> Optional[BaseComponent]:
        """获取组件实例"""
        return self.active_components.get(component_id)
    
    def get_component_config(self, component_id: str) -> Optional[Dict[str, Any]]:
        """获取组件配置"""
        return self.component_configs.get(component_id)
    
    def update_component_config(self, component_id: str, config: Dict[str, Any]) -> bool:
        """更新组件配置"""
        try:
            if component_id not in self.component_configs:
                self.logger.error(f"组件配置不存在: {component_id}")
                return False
            
            # 更新配置
            self.component_configs[component_id].update(config)
            
            # 如果组件实例存在，更新组件
            if component_id in self.active_components:
                component = self.active_components[component_id]
                component.update_config(self.component_configs[component_id])
                
                # 发出信号
                self.component_updated.emit(component_id, component)
            
            self.logger.info(f"更新组件配置: {component_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新组件配置失败: {e}")
            return False
    
    def get_component_list(self) -> List[Dict[str, Any]]:
        """获取组件列表"""
        component_list = []
        
        for component_id, config in self.component_configs.items():
            component_info = {
                'id': component_id,
                'type': config.get('type', 'unknown'),
                'name': config.get('name', '未命名组件'),
                'enabled': config.get('enabled', True),
                'active': component_id in self.active_components
            }
            component_list.append(component_info)
        
        return component_list
    
    def enable_component(self, component_id: str, enabled: bool = True) -> bool
        """启用/禁用组件"""
        try:
            if component_id not in self.component_configs:
                return False
            
            self.component_configs[component_id]['enabled'] = enabled
            
            
            if enabled and component_id not in self.active_components:
                # 创建组件实例:
            
                # 创建组件实例
                config = self.component_configs[component_id]
                component_type = config.get('type')
                if component_type in self.component_types:
                    component_class = self.component_types[component_type]
                    component_instance = component_class(component_id, config)
                    self.active_components[component_id] = component_instance
                    self.component_added.emit(component_id, component_instance)
            
            elif not enabled and component_id in self.active_components:
                # 移除组件实例
                component = self.active_components[component_id]
                component.cleanup()
                del self.active_components[component_id]
                self.component_removed.emit(component_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"启用/禁用组件失败: {e}")
            return False
    
    def get_layout_config(self) -> Dict[str, Any]:
        """获取布局配置"""
        return self.layout_config.copy()
    
    def update_layout_config(self, layout_config: Dict[str, Any]):
        """更新布局配置"""
        try:
            self.layout_config = layout_config
            self.layout_changed.emit()
            self._save_component_configs()
            self.logger.info("布局配置已更新")
            
        except Exception as e:
            self.logger.error(f"更新布局配置失败: {e}")
    
    def _remove_component_from_layout(self, component_id: str):
        """从布局中移除组件"""
        try:
            for row in self.layout_config.get('rows', []):
                if component_id in row.get('components', []):
                    row.get('components').remove(component_id)
            
        except Exception as e:
            self.logger.error(f"从布局中移除组件失败: {e}")
    
    def add_component(self, component_type: str, config: Dict[str, Any] = None) -> Optional[str]:
        """添加组件（创建并添加到布局）"""
        try:
            # 创建组件
            component_id = self.create_component(component_type, config)
            if not component_id:
                return None
            
            # 添加到布局（添加到第一行）
            if self.layout_config.get('rows'):
                first_row = self.layout_config.get('rows')[0]
                if component_id not in first_row.get('components', []):
                    first_row.setdefault('components', []).append(component_id)
            
            # 保存配置
            self._save_component_configs()
            
            return component_id
            
        except Exception as e:
            self.logger.error(f"添加组件失败: {e}")
            return None
    
    def duplicate_component(self, component_id: str) -> Optional[str]:
        """复制组件"""
        try:
            if component_id not in self.component_configs:
                return None
            
            # 复制配置
            original_config = self.component_configs[component_id].copy()
            original_config['name'] = original_config.get('name', 0) + ' (副本)'
            
            # 创建新组件
            return self.create_component(original_config.get('type'), original_config)
            
        except Exception as e:
            self.logger.error(f"复制组件失败: {e}")
            return None
    
    def _save_component_configs(self):
        """保存组件配置"""
        try:
            components_config = {
                'instances': self.component_configs,
                'layout': self.layout_config
            }
            self.config_manager.set('components', components_config)
            
        except Exception as e:
            self.logger.error(f"保存组件配置失败: {e}")
    
    def load_all_components(self):
        """加载所有启用的组件"""
        try:
            for component_id, config in self.component_configs.items():
                if config.get('enabled', True) and component_id not in self.active_components:
                    component_type = config.get('type')
                    if component_type in self.component_types:
                        component_class = self.component_types[component_type]
                        component_instance = component_class(component_id, config)
                        self.active_components[component_id] = component_instance
                        self.component_added.emit(component_id, component_instance)
            
            self.logger.info(f"加载了 {len(self.active_components)} 个组件")
            
        except Exception as e:
            self.logger.error(f"加载组件失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 清理所有组件
            for component in self.active_components.values():
                component.cleanup()
            
            self.active_components.clear()
            
            # 保存配置
            self._save_component_configs()
            
            self.logger.info("组件管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理组件管理器失败: {e}")