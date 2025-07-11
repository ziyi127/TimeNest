#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 附加设置服务
基于 ClassIsland AttachedSettings 规范实现
"""

import logging
from typing import Dict, List, Optional, Any, Union, Type, TypeVar, Generic

T = TypeVar('T')
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QTextEdit, QPushButton, QGroupBox, QFormLayout
import uuid
import yaml

class SettingType(Enum):
    """设置类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    TEXT = "text"
    COLOR = "color"
    FILE = "file"
    DIRECTORY = "directory"


class SettingPriority(Enum):
    """设置优先级"""
    GLOBAL = 1      # 全局设置
    LAYOUT = 2      # 时间布局设置
    PLAN = 3        # 课程计划设置
    ITEM = 4        # 时间项设置
    SUBJECT = 5     # 科目设置


@dataclass
class SettingDefinition:
    """设置定义"""
    key: str
    name: str
    description: str = ""
    setting_type: SettingType = SettingType.STRING
    default_value: Any = None
    choices: Optional[List[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    required: bool = False
    category: str = "general"
    priority: SettingPriority = SettingPriority.GLOBAL
    validation_pattern: Optional[str] = None
    help_text: Optional[str] = None
    depends_on: Optional[str] = None  # 依赖的其他设置
    

@dataclass
class AttachedSetting:
    """附加设置"""
    definition: SettingDefinition
    value: Any
    source_object: Optional[Any] = None
    source_type: Optional[str] = None
    priority: SettingPriority = SettingPriority.GLOBAL
    

class IAttachedSettingsProvider(ABC):
    """附加设置提供者接口"""
    
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """提供者ID"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供者名称"""
        pass
    
    @property
    @abstractmethod
    def supported_types(self) -> List[str]:
        """支持的对象类型"""
        pass
    
    @abstractmethod
    def get_setting_definitions(self) -> List[SettingDefinition]:
        """获取设置定义"""
        pass
    
    @abstractmethod
    def get_settings_for_object(self, obj: Any) -> Dict[str, Any]:
        """获取对象的设置"""
        pass
    
    @abstractmethod
    def set_setting_for_object(self, obj: Any, key: str, value: Any) -> bool:
        """为对象设置值"""
        pass
    
    @abstractmethod
    def can_handle_object(self, obj: Any) -> bool:
        """检查是否可以处理指定对象"""
        pass


class SubjectSettingsProvider(IAttachedSettingsProvider):
    """科目设置提供者"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.SubjectSettingsProvider')
        self._definitions = [
            SettingDefinition(
                key="color",
                name="科目颜色",
                description="科目在界面中显示的颜色",
                setting_type=SettingType.COLOR,
                default_value="#3498db",
                category="appearance",
                priority=SettingPriority.SUBJECT
            ),
            SettingDefinition(
                key="icon",
                name="科目图标",
                description="科目的图标文件路径",
                setting_type=SettingType.FILE,
                default_value="",
                category="appearance",
                priority=SettingPriority.SUBJECT
            ),
            SettingDefinition(
                key="teacher",
                name="任课教师",
                description="科目的任课教师姓名",
                setting_type=SettingType.STRING,
                default_value="",
                category="info",
                priority=SettingPriority.SUBJECT
            ),
            SettingDefinition(
                key="classroom",
                name="教室",
                description="上课教室",
                setting_type=SettingType.STRING,
                default_value="",
                category="info",
                priority=SettingPriority.SUBJECT
            ),
            SettingDefinition(
                key="enable_reminder",
                name="启用提醒",
                description="是否为此科目启用课前提醒",
                setting_type=SettingType.BOOLEAN,
                default_value=True,
                category="notification",
                priority=SettingPriority.SUBJECT
            ),
            SettingDefinition(
                key="reminder_minutes",
                name="提醒时间",
                description="课前多少分钟提醒",
                setting_type=SettingType.INTEGER,
                default_value=5,
                min_value=1,
                max_value=60,
                category="notification",
                priority=SettingPriority.SUBJECT,
                depends_on="enable_reminder"
            )
        ]
    
    @property
    def provider_id(self) -> str:
        return "subject_settings"
    
    @property
    def provider_name(self) -> str:
        return "科目设置"
    
    @property
    def supported_types(self) -> List[str]:
        return ["Subject"]
    
    def get_setting_definitions(self) -> List[SettingDefinition]:
        return self._definitions.copy()
    
    def get_settings_for_object(self, obj: Any) -> Dict[str, Any]:
        """获取科目的设置"""
        try:
            if not self.can_handle_object(obj):
                return {}
            
            settings = {}
            for definition in self._definitions:
                value = getattr(obj, f'setting_{definition.key}', definition.default_value)
                settings[definition.key] = value
            
            return settings
            
        except Exception as e:
            self.logger.error(f"获取科目设置失败: {e}", exc_info=True)
            return {}
    
    def set_setting_for_object(self, obj: Any, key: str, value: Any) -> bool:
        """为科目设置值"""
        try:
            if not self.can_handle_object(obj):
                return False
            
            # 查找设置定义
            definition = next((d for d in self._definitions if d.key == key), None)
            if not definition:
                return False
            
            # 验证值
            if not self._validate_value(definition, value):
                return False
            
            # 设置值
            setattr(obj, f'setting_{key}', value)
            return True
            
        except Exception as e:
            self.logger.error(f"设置科目设置失败: {e}", exc_info=True)
            return False
    
    def can_handle_object(self, obj: Any) -> bool:
        """检查是否为科目对象"""
        return hasattr(obj, '__class__') and obj.__class__.__name__ == 'Subject'
    
    def _validate_value(self, definition: SettingDefinition, value: Any) -> bool:
        """验证设置值"""
        try:
            if definition.setting_type == SettingType.INTEGER:
                if not isinstance(value, int):
                    return False
                if definition.min_value is not None and value < definition.min_value:
                    return False
                if definition.max_value is not None and value > definition.max_value:
                    return False
            elif definition.setting_type == SettingType.FLOAT:
                if not isinstance(value, (int, float)):
                    return False
                if definition.min_value is not None and value < definition.min_value:
                    return False
                if definition.max_value is not None and value > definition.max_value:
                    return False
            elif definition.setting_type == SettingType.BOOLEAN:
                if not isinstance(value, bool):
                    return False
            elif definition.setting_type == SettingType.CHOICE:
                if definition.choices and value not in definition.choices:
                    return False
            
            return True
            
        except Exception:
            return False


class TimeLayoutItemSettingsProvider(IAttachedSettingsProvider):
    """时间布局项设置提供者"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.TimeLayoutItemSettingsProvider')
        self._definitions = [
            SettingDefinition(
                key="display_name",
                name="显示名称",
                description="在界面中显示的名称",
                setting_type=SettingType.STRING,
                default_value="",
                category="display",
                priority=SettingPriority.ITEM
            ),
            SettingDefinition(
                key="background_color",
                name="背景颜色",
                description="时间项的背景颜色",
                setting_type=SettingType.COLOR,
                default_value="#ffffff",
                category="appearance",
                priority=SettingPriority.ITEM
            ),
            SettingDefinition(
                key="text_color",
                name="文字颜色",
                description="时间项的文字颜色",
                setting_type=SettingType.COLOR,
                default_value="#000000",
                category="appearance",
                priority=SettingPriority.ITEM
            ),
            SettingDefinition(
                key="show_countdown",
                name="显示倒计时",
                description="是否显示倒计时",
                setting_type=SettingType.BOOLEAN,
                default_value=True,
                category="display",
                priority=SettingPriority.ITEM
            ),
            SettingDefinition(
                key="countdown_format",
                name="倒计时格式",
                description="倒计时的显示格式",
                setting_type=SettingType.CHOICE,
                choices=["HH:MM:SS", "MM:SS", "剩余X分钟", "剩余X秒"],
                default_value="MM:SS",
                category="display",
                priority=SettingPriority.ITEM,
                depends_on="show_countdown"
            )
        ]
    
    @property
    def provider_id(self) -> str:
        return "time_layout_item_settings"
    
    @property
    def provider_name(self) -> str:
        return "时间布局项设置"
    
    @property
    def supported_types(self) -> List[str]:
        return ["TimeLayoutItem"]
    
    def get_setting_definitions(self) -> List[SettingDefinition]:
        return self._definitions.copy()
    
    def get_settings_for_object(self, obj: Any) -> Dict[str, Any]:
        """获取时间布局项的设置"""
        try:
            if not self.can_handle_object(obj):
                return {}
            
            settings = {}
            for definition in self._definitions:
                value = getattr(obj, f'setting_{definition.key}', definition.default_value)
                settings[definition.key] = value
            
            return settings
            
        except Exception as e:
            self.logger.error(f"获取时间布局项设置失败: {e}", exc_info=True)
            return {}
    
    def set_setting_for_object(self, obj: Any, key: str, value: Any) -> bool:
        """为时间布局项设置值"""
        try:
            if not self.can_handle_object(obj):
                return False
            
            # 查找设置定义
            definition = next((d for d in self._definitions if d.key == key), None)
            if not definition:
                return False
            
            # 设置值
            setattr(obj, f'setting_{key}', value)
            return True
            
        except Exception as e:
            self.logger.error(f"设置时间布局项设置失败: {e}", exc_info=True)
            return False
    
    def can_handle_object(self, obj: Any) -> bool:
        """检查是否为时间布局项对象"""
        return hasattr(obj, '__class__') and obj.__class__.__name__ == 'TimeLayoutItem'


class AttachedSettingsControl(QWidget):
    """附加设置控件"""
    
    settings_changed = pyqtSignal(str, object)  # key, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.AttachedSettingsControl')
        self.current_object = None
        self.current_settings = {}
        self.setting_widgets = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        self.layout = QVBoxLayout(self)
        
        # 标题
        self.title_label = QLabel("附加设置")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        
        # 设置容器
        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.layout.addWidget(self.settings_container)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("重置")
        self.apply_button = QPushButton("应用")
        
        self.reset_button.clicked.connect(self.reset_settings)
        self.apply_button.clicked.connect(self.apply_settings)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.apply_button)
        self.layout.addLayout(button_layout)
        
        # 初始状态
        self.setEnabled(False)
    
    def set_object(self, obj: Any, settings: Dict[str, AttachedSetting]):
        """设置当前对象和设置"""
        try:
            self.current_object = obj
            self.current_settings = settings
            
            # 清除现有控件
            self.clear_settings_widgets()
            
            if not settings:
                self.setEnabled(False)
                return
            
            # 按类别分组
            categories = {}
            for key, setting in settings.items():
                category = setting.definition.category
                if category not in categories:
                    categories[category] = []
                categories[category].append((key, setting))
            
            # 创建设置控件
            for category, category_settings in categories.items():
                self.create_category_group(category, category_settings)
            
            self.setEnabled(True)
            
        except Exception as e:
            self.logger.error(f"设置对象失败: {e}", exc_info=True)
    
    def create_category_group(self, category: str, settings: List[tuple]):
        """创建类别分组"""
        try:
            group_box = QGroupBox(category.title())
            form_layout = QFormLayout(group_box)
            
            for key, setting in settings:
                widget = self.create_setting_widget(key, setting)
                if widget:
                    form_layout.addRow(setting.definition.name, widget)
                    self.setting_widgets[key] = widget
            
            self.settings_layout.addWidget(group_box)
            
        except Exception as e:
            self.logger.error(f"创建类别分组失败: {e}", exc_info=True)
    
    def create_setting_widget(self, key: str, setting: AttachedSetting) -> Optional[QWidget]:
        """创建设置控件"""
        try:
            definition = setting.definition
            value = setting.value
            
            if definition.setting_type == SettingType.STRING:
                widget = QLineEdit()
                widget.setText(str(value) if value is not None else "")
                widget.textChanged.connect(lambda text, k=key: self.on_setting_changed(k, text))
                return widget
                
            elif definition.setting_type == SettingType.INTEGER:
                widget = QSpinBox()
                if definition.min_value is not None:
                    widget.setMinimum(int(definition.min_value))
                if definition.max_value is not None:
                    widget.setMaximum(int(definition.max_value))
                widget.setValue(int(value) if value is not None else 0)
                widget.valueChanged.connect(lambda val, k=key: self.on_setting_changed(k, val))
                return widget
                
            elif definition.setting_type == SettingType.FLOAT:
                widget = QDoubleSpinBox()
                if definition.min_value is not None:
                    widget.setMinimum(float(definition.min_value))
                if definition.max_value is not None:
                    widget.setMaximum(float(definition.max_value))
                widget.setValue(float(value) if value is not None else 0.0)
                widget.valueChanged.connect(lambda val, k=key: self.on_setting_changed(k, val))
                return widget
                
            elif definition.setting_type == SettingType.BOOLEAN:
                widget = QCheckBox()
                widget.setChecked(bool(value) if value is not None else False)
                widget.toggled.connect(lambda checked, k=key: self.on_setting_changed(k, checked))
                return widget
                
            elif definition.setting_type == SettingType.CHOICE:
                widget = QComboBox()
                if definition.choices:
                    widget.addItems(definition.choices)
                    if value in definition.choices:
                        widget.setCurrentText(str(value))
                widget.currentTextChanged.connect(lambda text, k=key: self.on_setting_changed(k, text))
                return widget
                
            elif definition.setting_type == SettingType.TEXT:
                widget = QTextEdit()
                widget.setPlainText(str(value) if value is not None else "")
                widget.setMaximumHeight(100)
                widget.textChanged.connect(lambda k=key: self.on_setting_changed(k, widget.toPlainText()))
                return widget
            
            return None
            
        except Exception as e:
            self.logger.error(f"创建设置控件失败: {e}", exc_info=True)
            return None
    
    def on_setting_changed(self, key: str, value: Any):
        """设置值改变"""
        try:
            if key in self.current_settings:
                self.current_settings[key].value = value
                self.settings_changed.emit(key, value)
                
        except Exception as e:
            self.logger.error(f"处理设置改变失败: {e}", exc_info=True)
    
    def reset_settings(self):
        """重置设置"""
        try:
            for key, setting in self.current_settings.items():
                setting.value = setting.definition.default_value
                
                # 更新控件
                if key in self.setting_widgets:
                    widget = self.setting_widgets[key]
                    self.update_widget_value(widget, setting.definition, setting.value)
                    
        except Exception as e:
            self.logger.error(f"重置设置失败: {e}", exc_info=True)
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 这里可以添加应用设置的逻辑
            self.logger.info("设置已应用")
            
        except Exception as e:
            self.logger.error(f"应用设置失败: {e}", exc_info=True)
    
    def update_widget_value(self, widget: QWidget, definition: SettingDefinition, value: Any):
        """更新控件值"""
        try:
            if isinstance(widget, QLineEdit):
                widget.setText(str(value) if value is not None else "")
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value) if value is not None else 0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(value) if value is not None else 0.0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value) if value is not None else False)
            elif isinstance(widget, QComboBox):
                if value in definition.choices:
                    widget.setCurrentText(str(value))
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(value) if value is not None else "")
                
        except Exception as e:
            self.logger.error(f"更新控件值失败: {e}", exc_info=True)
    
    def clear_settings_widgets(self):
        """清除设置控件"""
        try:
            # 清除所有子控件
            while self.settings_layout.count():
                child = self.settings_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            self.setting_widgets.clear()
            
        except Exception as e:
            self.logger.error(f"清除设置控件失败: {e}", exc_info=True)


class AttachedSettingsBase:
    """附加设置基类"""
    is_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_enabled": self.is_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttachedSettingsBase':
        """从字典创建实例"""
        return cls(
            is_enabled=data.get("is_enabled", True)
        )

class AttachedSettingsHelper:
    """附加设置帮助器"""
    
    def __init__(self, settings_id: str, default_settings: T):
        self.settings_id = settings_id
        self.default_settings = default_settings
        self._settings: Optional[T] = None
    
    @property
    def attached_settings(self) -> T:
        """获取附加设置"""
        return self._settings or self.default_settings
    
    @attached_settings.setter
    def attached_settings(self, value: T):
        """设置附加设置"""
        self._settings = value

class AttachedSettingsManager:
    """附加设置管理器"""
    
    def __init__(self):
        self._settings: Dict[str, Dict[str, AttachedSettingsBase]] = {}
    
    def get_settings(
        self,
        settings_id: str,
        subject: Optional[str] = None,
        time_layout_item: Optional[str] = None,
        class_plan: Optional[str] = None,
        time_layout: Optional[str] = None
    ) -> Optional[AttachedSettingsBase]:
        """按优先级获取附加设置"""
        # 按优先级检查
        for context in [subject, time_layout_item, class_plan, time_layout]:
            if not context:
                continue
            if settings_id in self._settings and context in self._settings[settings_id]:
                settings = self._settings[settings_id][context]
                if settings.is_enabled:
                    return settings
        return None
    
    def set_settings(
        self,
        settings_id: str,
        context: str,
        settings: AttachedSettingsBase
    ) -> None:
        """设置附加设置"""
        if settings_id not in self._settings:
            self._settings[settings_id] = {}
        self._settings[settings_id][context] = settings
    
    def save_to_file(self, filepath: str) -> None:
        """保存设置到文件"""
        data = {
            settings_id: {
                context: settings.to_dict()
                for context, settings in context_settings.items()
            }
            for settings_id, context_settings in self._settings.items()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)
    
    def load_from_file(self, filepath: str) -> None:
        """从文件加载设置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if not data:
                return
                
            for settings_id, context_settings in data.items():
                if settings_id not in self._settings:
                    self._settings[settings_id] = {}
                for context, settings_data in context_settings.items():
                    self._settings[settings_id][context] = \
                        AttachedSettingsBase.from_dict(settings_data)
        except FileNotFoundError:
            pass


class AttachedSettingsHostService(QObject):
    """附加设置主机服务"""
    
    settings_changed = pyqtSignal(object, str, object)  # obj, key, value
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.AttachedSettingsHostService')
        self.providers: Dict[str, IAttachedSettingsProvider] = {}
        
        # 注册默认提供者
        self.register_provider(SubjectSettingsProvider())
        self.register_provider(TimeLayoutItemSettingsProvider())
    
    def register_provider(self, provider: IAttachedSettingsProvider):
        """注册设置提供者"""
        try:
            self.providers[provider.provider_id] = provider
            self.logger.info(f"附加设置提供者已注册: {provider.provider_name}")
        except Exception as e:
            self.logger.error(f"注册附加设置提供者失败: {e}", exc_info=True)
    
    def unregister_provider(self, provider_id: str):
        """注销设置提供者"""
        try:
            if provider_id in self.providers:
                provider = self.providers.pop(provider_id)
                self.logger.info(f"附加设置提供者已注销: {provider.provider_name}")
        except Exception as e:
            self.logger.error(f"注销附加设置提供者失败: {e}", exc_info=True)
    
    def get_attached_settings_by_priority(self, settings_id: str, subject=None, time_layout_item=None, class_plan=None, time_layout=None) -> Optional[Any]:
        """
        按优先级链路获取附加设置（严格遵循 doc/AttachedSettings.md）
        优先级: Subject → TimeLayoutItem → ClassPlan → TimeLayout → null

        Args:
            settings_id: 设置ID (对应文档中的Guid id参数)
            subject: Subject对象 (可选)
            time_layout_item: TimeLayoutItem对象 (可选)
            class_plan: ClassPlan对象 (可选)
            time_layout: TimeLayout对象 (可选)

        Returns:
            第一个找到的启用设置对象，如果没有找到则返回None
        """
        try:
            # 按照文档规定的优先级顺序检查
            objects = [subject, time_layout_item, class_plan, time_layout]

            for obj in objects:
                if obj is None:
                    continue

                # 检查对象是否有对应的附加设置
                if hasattr(obj, 'attached_settings') and obj.attached_settings:
                    settings = obj.attached_settings.get(settings_id)
                    if settings and hasattr(settings, 'is_attach_settings_enabled'):
                        # 检查IsAttachSettingsEnabled是否为True
                        if settings.is_attach_settings_enabled:
                            self.logger.debug(f"找到启用的附加设置: {settings_id} 在 {obj.__class__.__name__}")
                            return settings

            # 如果什么也没有找到，返回None
            self.logger.debug(f"未找到启用的附加设置: {settings_id}")
            return None

        except Exception as e:
            self.logger.error(f"按优先级获取附加设置失败: {e}", exc_info=True)
            return None
    
    def get_settings_for_object(self, obj: Any) -> Dict[str, AttachedSetting]:
        """获取对象的设置"""
        try:
            settings = {}
            
            for provider in self.providers.values():
                if provider.can_handle_object(obj):
                    provider_settings = provider.get_settings_for_object(obj)
                    definitions = provider.get_setting_definitions()
                    
                    for definition in definitions:
                        key = definition.key
                        value = provider_settings.get(key, definition.default_value)
                        
                        settings[key] = AttachedSetting(
                            definition=definition,
                            value=value,
                            source_object=obj,
                            source_type=obj.__class__.__name__,
                            priority=definition.priority
                        )
            
            return settings
            
        except Exception as e:
            self.logger.error(f"获取对象设置失败: {e}", exc_info=True)
            return {}
    
    def set_setting_for_object(self, obj: Any, key: str, value: Any) -> bool:
        """为对象设置值"""
        try:
            for provider in self.providers.values():
                if provider.can_handle_object(obj):
                    if provider.set_setting_for_object(obj, key, value):
                        self.settings_changed.emit(obj, key, value)
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"设置对象设置失败: {e}", exc_info=True)
            return False
    
    def _get_object_priority(self, obj: Any) -> int:
        """获取对象优先级"""
        try:
            class_name = obj.__class__.__name__
            
            priority_map = {
                'Subject': SettingPriority.SUBJECT.value,
                'TimeLayoutItem': SettingPriority.ITEM.value,
                'ClassPlan': SettingPriority.PLAN.value,
                'TimeLayout': SettingPriority.LAYOUT.value
            }
            
            return priority_map.get(class_name, SettingPriority.GLOBAL.value)
            
        except Exception:
            return SettingPriority.GLOBAL.value
    
    def get_all_setting_definitions(self) -> List[SettingDefinition]:
        """获取所有设置定义"""
        try:
            all_definitions = []
            
            for provider in self.providers.values():
                definitions = provider.get_setting_definitions()
                all_definitions.extend(definitions)
            
            return all_definitions
            
        except Exception as e:
            self.logger.error(f"获取所有设置定义失败: {e}", exc_info=True)
            return []
    
    def get_providers(self) -> List[IAttachedSettingsProvider]:
        """获取所有提供者"""
        return list(self.providers.values())


# AttachedSettingsControl 相关类（对应文档规范）

class IAttachedSettingsHelper(ABC):
    """附加设置助手接口"""

    @property
    @abstractmethod
    def attached_settings(self) -> Optional[Any]:
        """获取附加设置对象"""
        pass


class AttachedSettingsControlHelper(IAttachedSettingsHelper):
    """
    附加设置控件助手（对应文档中的AttachedSettingsControlHelper<T>）
    """

    def __init__(self, settings_id: str, default_settings: T):
        """
        初始化附加设置控件助手

        Args:
            settings_id: 设置ID（对应文档中的Guid）
            default_settings: 默认设置对象
        """
        self.settings_id = settings_id
        self.default_settings = default_settings
        self._attached_settings: Optional[T] = None

    @property
    def attached_settings(self) -> Optional[T]:
        """获取附加设置对象"""
        return self._attached_settings or self.default_settings

    @attached_settings.setter
    def attached_settings(self, value: T):
        """设置附加设置对象"""
        self._attached_settings = value


class IAttachedSettingsControlBase(ABC):
    """附加设置控件基接口"""

    @property
    @abstractmethod
    def attached_settings_control_helper(self) -> IAttachedSettingsHelper:
        """获取附加设置控件助手"""
        pass


class AttachedSettingsControlBase(QWidget):
    """
    附加设置控件基类（对应文档中的AttachedSettingsControl）
    仅继承 QWidget，泛型和接口功能通过组合实现，避免 metaclass 冲突。
    """
    def __init__(self, settings_id: str, default_settings, parent=None):
        super().__init__(parent)
        self._attached_settings_control_helper = AttachedSettingsControlHelper(
            settings_id, default_settings
        )
        self.setup_ui()

    @property
    def attached_settings_control_helper(self):
        return self._attached_settings_control_helper

    @property
    def settings(self):
        return self.attached_settings_control_helper.attached_settings

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("附加设置控件"))
        self.setLayout(layout)

    def load_settings(self, settings):
        self.attached_settings_control_helper.attached_settings = settings
        self.update_ui_from_settings()

    def save_settings(self):
        """从UI保存设置"""
        self.update_settings_from_ui()
        return self.settings

    def update_ui_from_settings(self):
        """从设置更新UI（子类需要重写）"""
        pass

    def update_settings_from_ui(self):
        """从UI更新设置（子类需要重写）"""
        pass


# 示例：课后通知附加设置控件
@dataclass
class AfterSchoolNotificationAttachedSettings:
    """课后通知附加设置"""
    is_attach_settings_enabled: bool = True
    enable_notification: bool = True
    notification_message: str = "放学了！"
    delay_minutes: int = 0


class AfterSchoolNotificationAttachedSettingsControl(AttachedSettingsControlBase):
    """
    课后通知附加设置控件（对应文档示例）
    """

    def __init__(self, parent=None):
        # 使用文档中的GUID示例
        settings_id = "8FBC3A26-6D20-44DD-B895-B9411E3DDC51"
        default_settings = AfterSchoolNotificationAttachedSettings()
        super().__init__(settings_id, default_settings, parent)

    def setup_ui(self):
        """设置UI界面"""
        layout = QFormLayout(self)

        # 启用设置
        self.enable_checkbox = QCheckBox("启用课后通知")
        layout.addRow("启用:", self.enable_checkbox)

        # 通知消息
        self.message_edit = QLineEdit()
        layout.addRow("通知消息:", self.message_edit)

        # 延迟时间
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(0, 60)
        self.delay_spinbox.setSuffix(" 分钟")
        layout.addRow("延迟时间:", self.delay_spinbox)

        self.setLayout(layout)

    def update_ui_from_settings(self):
        """从设置更新UI"""
        settings = self.settings
        self.enable_checkbox.setChecked(settings.enable_notification)
        self.message_edit.setText(settings.notification_message)
        self.delay_spinbox.setValue(settings.delay_minutes)

    def update_settings_from_ui(self):
        """从UI更新设置"""
        settings = self.settings
        settings.enable_notification = self.enable_checkbox.isChecked()
        settings.notification_message = self.message_edit.text()
        settings.delay_minutes = self.delay_spinbox.value()