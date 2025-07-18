#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest 应用管理器
负责协调和管理应用的各个核心组件
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

from utils.common_imports import QObject, Signal, QTimer
from utils.shared_utilities import cleanup_timers, retry_operation
from utils.config_constants import ERROR_MESSAGES, SUCCESS_MESSAGES

try:
    from PySide6.QtWidgets import QApplication
    QT_WIDGETS_AVAILABLE = True
except ImportError:
    logging.error("PySide6 widgets not available")
    QT_WIDGETS_AVAILABLE = False

    class QApplication:
        @staticmethod
        def instance():
            return None

# 本地模块
from core.component_system import ComponentManager as ComponentSystemManager
from core.config_manager import ConfigManager
from core.floating_manager import FloatingManager
from core.notification_manager import NotificationManager
from core.plugin_base import PluginManager
from core.schedule_manager import ScheduleManager
from core.theme_system import ThemeManager, ThemeMarketManager
from core.time_manager import TimeManager
from core.weather_service import WeatherService

class AppManager(QObject):
    """
    应用管理器
    
    负责初始化、协调和管理应用的所有核心组件，包括：
    - 配置管理
    - 课程表管理
    - 通知管理
    - 时间管理
    - 组件管理
    """
    
    # 信号定义
    app_initialized = Signal()  # 应用初始化完成
    app_closing = Signal()      # 应用即将关闭
    error_occurred = Signal(str)  # 发生错误

    def __init__(self):
        """初始化应用管理器"""
        super().__init__()
        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.AppManager')

        # 初始化状态
        self._initialized = False
        self._closing = False

        # 核心管理器实例
        self.config_manager: ConfigManager
        self.time_manager: TimeManager
        self.theme_manager: ThemeManager
        self.notification_manager: 'NotificationManager'
        self.plugin_manager: PluginManager
        self.schedule_manager: ScheduleManager
        self.floating_manager: FloatingManager
        self.component_manager: ComponentSystemManager
        self.weather_service: WeatherService

        # 新增功能管理器
        self.theme_marketplace = None
        self.time_calibration_service = None
        self.plugin_interaction_manager = None

        # 增强功能组件
        self.schedule_enhancement = None
        self.notification_enhancement = None
        self.study_assistant = None

        # 新增细分功能组件
        self.environment_optimizer = None
        self.study_planner = None
        self.resource_manager = None

        # 定时器用于定期更新
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._periodic_update)

        self.logger.info("应用管理器已创建")

    def initialize(self) -> bool:
        """
        初始化应用管理器和所有核心组件

        Returns:
            bool: 初始化是否成功
        """
        if self._initialized:
            self.logger.warning("应用管理器已经初始化")
            return True

        try:
            self.logger.info("开始初始化应用管理器...")

            # 1. 初始化配置管理器
            self.logger.info("初始化配置管理器...")
            self.config_manager = ConfigManager()

            # 2. 初始化时间管理器
            self.logger.info("初始化时间管理器...")
            self.time_manager = TimeManager(self.config_manager)

            # 2.5. 初始化字体管理器
            self.logger.info("初始化字体管理器...")
            from core.font_manager import FontManager
            self.font_manager = FontManager(self.config_manager)

            # 3. 初始化主题管理器
            self.logger.info("初始化主题管理器...")
            self.theme_manager = ThemeManager(self.config_manager)

            # 4. 初始化通知管理器 (v2)
            self.logger.info("初始化通知管理器...")
            self.notification_manager = NotificationManager(self.config_manager)

            # 5. 初始化插件管理器
            self.logger.info("初始化插件管理器...")
            self.plugin_manager = PluginManager(config_manager=self.config_manager)
            self.plugin_manager.load_plugins()

            # 6. 初始化浮窗管理器
            self.logger.info("初始化浮窗管理器...")
            self.floating_manager = FloatingManager(self)

            # 7. 初始化新增功能
            self._initialize_enhanced_features()

            # 8. 加载和应用保存的配置
            self.logger.info("加载和应用保存的配置...")
            self._load_and_apply_configs()

            # 9. 连接信号
            self._connect_signals()

            # 10. 启动定期更新
            self._start_periodic_update()

            self._initialized = True
            self.logger.info("应用管理器初始化完成")

            # 发送初始化完成信号
            self.app_initialized.emit()

            return True

        except Exception as e:
            self.logger.error(f"应用管理器初始化失败: {e}", exc_info=True)
            self.error_occurred.emit(f"初始化失败: {str(e)}")
            return False

    def _initialize_feature(self, feature_name: str, module_path: str, class_name: str, 
                          init_args: tuple = (), fallback_module: str = None, 
                          attr_name: str = None) -> bool:
        """
        通用功能初始化方法
        
        Args:
            feature_name: 功能名称(用于日志)
            module_path: 模块路径
            class_name: 类名
            init_args: 初始化参数元组
            fallback_module: 备选模块路径(可选)
            attr_name: 属性名称(可选，默认为小写feature_name)
            
        Returns:
            bool: 是否初始化成功
        """
        attr_name = attr_name or feature_name.lower().replace(' ', '_')
        try:
            # 参数验证
            if not module_path or not class_name:
                raise ValueError(f"模块路径或类名为空: {module_path}, {class_name}")

            module = __import__(module_path, fromlist=[class_name])
            if not hasattr(module, class_name):
                raise AttributeError(f"模块 {module_path} 中未找到类 {class_name}")

            cls = getattr(module, class_name)
            if not callable(cls):
                raise TypeError(f"类 {class_name} 不可调用")

            # 安全实例化
            instance = cls(*init_args) if init_args else cls()
            setattr(self, attr_name, instance)
            self.logger.info(f"{feature_name}初始化完成")
            return True
        except Exception as e:
            if fallback_module:
                # 删除多余的try语句，因为外层已经有try-except结构
                try:
                    if not fallback_module:
                        raise ValueError("备选模块路径为空")

                    module = __import__(fallback_module, fromlist=[class_name])
                    if not hasattr(module, class_name):
                        raise AttributeError(f"备选模块 {fallback_module} 中未找到类 {class_name}")

                    cls = getattr(module, class_name)
                    instance = cls(*init_args) if init_args else cls()
                    setattr(self, attr_name, instance)
                    self.logger.info(f"{feature_name}(备选)初始化完成")
                    return True
                except Exception as fallback_e:
                    self.logger.warning(f"{feature_name}初始化失败 (主模块: {e}, 备选模块: {fallback_e})")
                    setattr(self, attr_name, None)
                    return False
            else:
                self.logger.warning(f"{feature_name}初始化失败: {e}")
                setattr(self, attr_name, None)
                return False

    def _initialize_enhanced_features(self):
        """初始化增强功能（延迟加载优化）"""
        try:
            self.logger.info("准备增强功能（延迟加载）...")

            # 标记增强功能未初始化，将在需要时加载
            self._enhanced_features_loaded = False
            self._feature_loading_cache = {}

            # 初始化新增的增强功能
            self._initialize_new_enhancements()

        except Exception as e:
            self.logger.error(f"准备增强功能失败: {e}")

    def _initialize_new_enhancements(self):
        """初始化新增的增强功能"""
        try:
            self.logger.info("初始化增强功能组件...")

            # 1. 初始化课程表增强功能
            try:
                from core.schedule_enhancements import ScheduleEnhancementManager
                self.schedule_enhancement = ScheduleEnhancementManager(self.config_manager)
                self.logger.info("课程表增强功能初始化成功")
            except ImportError:
                self.logger.warning("课程表增强功能模块不可用")
            except Exception as e:
                self.logger.error(f"课程表增强功能初始化失败: {e}")

            # 2. 初始化通知增强功能
            try:
                from core.notification_enhancements import NotificationEnhancementManager
                self.notification_enhancement = NotificationEnhancementManager(
                    self.config_manager,
                    self.notification_manager
                )
                self.logger.info("通知增强功能初始化成功")
            except ImportError:
                self.logger.warning("通知增强功能模块不可用")
            except Exception as e:
                self.logger.error(f"通知增强功能初始化失败: {e}")

            # 3. 初始化智能学习助手
            try:
                from core.study_assistant import StudyAssistantManager
                self.study_assistant = StudyAssistantManager(
                    self.config_manager,
                    self.schedule_enhancement
                )
                self.logger.info("智能学习助手初始化成功")
            except ImportError:
                self.logger.warning("智能学习助手模块不可用")
            except Exception as e:
                self.logger.error(f"智能学习助手初始化失败: {e}")

            # 4. 初始化学习环境优化器
            try:
                from core.environment_optimizer import EnvironmentOptimizer
                self.environment_optimizer = EnvironmentOptimizer(self.config_manager)
                self.logger.info("学习环境优化器初始化成功")
            except ImportError:
                self.logger.warning("学习环境优化器模块不可用")
            except Exception as e:
                self.logger.error(f"学习环境优化器初始化失败: {e}")

            # 5. 初始化学习计划生成器
            try:
                from core.study_planner import StudyPlannerManager
                self.study_planner = StudyPlannerManager(
                    self.config_manager,
                    self.schedule_enhancement,
                    self.study_assistant
                )
                self.logger.info("学习计划生成器初始化成功")
            except ImportError:
                self.logger.warning("学习计划生成器模块不可用")
            except Exception as e:
                self.logger.error(f"学习计划生成器初始化失败: {e}")

            # 6. 初始化学习资源管理器
            try:
                from core.resource_manager import ResourceManager
                self.resource_manager = ResourceManager(self.config_manager)
                self.logger.info("学习资源管理器初始化成功")
            except ImportError:
                self.logger.warning("学习资源管理器模块不可用")
            except Exception as e:
                self.logger.error(f"学习资源管理器初始化失败: {e}")

            self.logger.info("所有增强功能组件初始化完成")

        except Exception as e:
            self.logger.error(f"初始化增强功能组件失败: {e}")

    def _load_enhanced_feature(self, feature_name: str):
        """按需加载增强功能"""
        if feature_name in self._feature_loading_cache:
            return self._feature_loading_cache[feature_name]

        try:
            features = [
                ("模块管理器", "core.module_manager", "ModuleManager", (self,)),
                ("主题市场", "core.theme_marketplace", "ThemeMarketplace",
                 (self.config_manager, self.theme_manager)),
                ("时间校准服务", "core.time_calibration_service", "TimeCalibrationService",
                 (self.config_manager,)),
                ("插件开发工具", "core.plugin_development_tools", "PluginDevelopmentTools",
                 (self.config_manager,)),
                ("插件交互管理器", "core.plugin_interaction_enhanced", "PluginInteractionManager", ()),
                ("Remind API v2", "core.remind_api_v2", "RemindAPIv2", (self,))
            ]

            for name, module, class_name, args in features:
                if name == "插件交互管理器":
                    self._initialize_feature(name, module, class_name,
                                           fallback_module="core.plugin_interaction")
                else:
                    self._initialize_feature(name, module, class_name, args)
            
            self._initialize_feature(
                "Excel导出增强",
                "core.excel_export_enhanced",
                "ExcelExportEnhanced"
            )

            self._initialize_feature(
                "性能管理器",
                "core.performance_manager",
                "PerformanceManager",
                (self.config_manager,)
            )

        except Exception as e:
            self.logger.error(f"初始化增强功能失败: {e}")

    def _connect_signals(self):
        """
        连接各组件之间的信号
        """
        try:
            # 配置变化信号 - 实现即时生效
            self.config_manager.config_changed.connect(self._on_config_changed)

            # 性能警告信号
            if hasattr(self, 'performance_manager') and self.performance_manager:
                self.performance_manager.performance_warning.connect(self._on_performance_warning)

            self.logger.info("信号连接完成")

        except Exception as e:
            self.logger.error(f"信号连接失败: {e}", exc_info=True)

    def _load_and_apply_configs(self):
        """加载和应用保存的配置"""
        try:
            # 应用浮窗配置
            self._apply_floating_widget_config()

            # 应用通知配置
            self._apply_notification_config()

            # 应用主题配置
            self._apply_theme_config()

            # 应用时间配置
            self._apply_time_config()

            self.logger.info("所有保存的配置已加载并应用")

        except Exception as e:
            self.logger.error(f"加载和应用配置失败: {e}")

    def _apply_floating_widget_config(self):
        """应用浮窗配置"""
        try:
            if self.floating_manager and self.config_manager:
                floating_config = self.config_manager.get_config('floating_widget', {})
                if floating_config:
                    self.floating_manager.apply_config(floating_config)
                    self.logger.debug("浮窗配置已应用")
        except Exception as e:
            self.logger.error(f"应用浮窗配置失败: {e}")

    def _apply_notification_config(self):
        """应用通知配置"""
        try:
            if self.notification_manager and self.config_manager:
                notification_config = self.config_manager.get_config('notification', {})
                if notification_config:
                    self.notification_manager.apply_config(notification_config)
                    self.logger.debug("通知配置已应用")
        except Exception as e:
            self.logger.error(f"应用通知配置失败: {e}")

    def _apply_theme_config(self):
        """应用主题配置"""
        try:
            if self.theme_manager and self.config_manager:
                theme_config = self.config_manager.get_config('theme', {})
                theme_name = theme_config.get('current', 'builtin_light')
                if theme_name != 'builtin_light':
                    self.theme_manager.apply_theme(theme_name)
                    self.logger.debug(f"主题配置已应用: {theme_name}")
        except Exception as e:
            self.logger.error(f"应用主题配置失败: {e}")

    def _apply_time_config(self):
        """应用时间配置"""
        try:
            if self.time_manager and self.config_manager:
                time_config = self.config_manager.get_config('time', {})
                if time_config and hasattr(self.time_manager, 'apply_config'):
                    self.time_manager.apply_config(time_config)
                    self.logger.debug("时间配置已应用")
        except Exception as e:
            self.logger.error(f"应用时间配置失败: {e}")

    def _start_periodic_update(self):
        """
        启动定期更新
        """
        try:
            # 获取更新间隔（默认1秒）
            update_interval = self.config_manager.get_config('app.update_interval', 1000)

            self.update_timer.start(update_interval)
            self.logger.info(f"定期更新已启动，间隔: {update_interval}ms")

        except Exception as e:
            self.logger.error(f"启动定期更新失败: {e}", exc_info=True)

    def _periodic_update(self):
        """
        定期更新处理
        """
        try:
            # 更新时间相关服务
            if hasattr(self, 'time_calibration_service') and self.time_calibration_service:
                self.time_calibration_service.check_time_sync()
                
            # 更新天气服务
            if hasattr(self, 'weather_service') and self.weather_service:
                self.weather_service.update_weather()
                
            # 更新通知服务
            if hasattr(self, 'notification_manager') and self.notification_manager:
                self.notification_manager.check_pending_notifications()
                
            # 更新插件状态
            if hasattr(self, 'plugin_manager') and self.plugin_manager:
                self.plugin_manager.update_plugins_status()

                # 检查插件更新
                marketplace = self.plugin_manager.get_marketplace()
                if marketplace and marketplace.get_status().value == 'online':
                    updates = self.plugin_manager.check_plugin_updates()
                    if updates:
                        self.logger.info(f"发现 {len(updates)} 个插件更新")

        except Exception as e:
            self.logger.error(f"定期更新失败: {e}", exc_info=True)

    def _on_config_changed(self, key: str, old_value: Any, new_value: Any):
        """
        配置变化处理 - 实现即时生效

        Args:
            key: 配置键
            old_value: 旧值
            new_value: 新值
        """
        try:
            self.logger.debug(f"配置变化: {key} = {new_value}")

            # 根据配置键进行相应处理，实现即时生效
            if key.startswith('floating_widget.'):
                self._handle_floating_widget_config_change(key, new_value)
            elif key.startswith('notification.'):
                self._handle_notification_config_change(key, new_value)
            elif key.startswith('theme.'):
                self._handle_theme_config_change(key, new_value)
            elif key.startswith('time.'):
                self._handle_time_config_change(key, new_value)
            elif key.startswith('system.'):
                self._handle_system_config_change(key, new_value)

        except Exception as e:
            self.logger.error(f"处理配置变化失败: {e}", exc_info=True)

    def _handle_floating_widget_config_change(self, key: str, value: Any):
        """处理浮窗配置变化"""
        try:
            if self.floating_manager:
                # 获取完整的浮窗配置
                floating_config = self.config_manager.get_config('floating_widget', {})
                # 立即应用到浮窗
                self.floating_manager.apply_config(floating_config)
                self.logger.debug(f"浮窗配置已即时应用: {key}")
        except Exception as e:
            self.logger.error(f"处理浮窗配置变化失败: {e}")

    def _handle_notification_config_change(self, key: str, value: Any):
        """处理通知配置变化"""
        try:
            if self.notification_manager:
                # 获取完整的通知配置
                notification_config = self.config_manager.get_config('notification', {})
                # 立即应用到通知管理器
                self.notification_manager.apply_config(notification_config)
                self.logger.debug(f"通知配置已即时应用: {key}")
        except Exception as e:
            self.logger.error(f"处理通知配置变化失败: {e}")

    def _handle_theme_config_change(self, key: str, value: Any):
        """处理主题配置变化"""
        try:
            if self.theme_manager and key == 'theme.name':
                # 立即切换主题
                self.theme_manager.apply_theme(value)
                self.logger.debug(f"主题已即时切换: {value}")
        except Exception as e:
            self.logger.error(f"处理主题配置变化失败: {e}")

    def _handle_time_config_change(self, key: str, value: Any):
        """处理时间配置变化"""
        try:
            if self.time_manager and hasattr(self.time_manager, 'apply_config'):
                # 获取完整的时间配置
                time_config = self.config_manager.get_config('time', {})
                # 立即应用到时间管理器
                self.time_manager.apply_config(time_config)
                self.logger.debug(f"时间配置已即时应用: {key}")
        except Exception as e:
            self.logger.error(f"处理时间配置变化失败: {e}")

    def _handle_system_config_change(self, key: str, value: Any):
        """处理系统配置变化"""
        try:
            if key == 'system.auto_start':
                # 处理开机自启动设置
                self._handle_auto_start_setting(value)
            elif key == 'system.minimize_to_tray':
                # 处理最小化到托盘设置
                self._handle_minimize_to_tray_setting(value)
            self.logger.debug(f"系统配置已即时应用: {key}")
        except Exception as e:
            self.logger.error(f"处理系统配置变化失败: {e}")

    def _handle_auto_start_setting(self, enabled: bool):
        """处理开机自启动设置"""
        try:
            # 这里可以添加设置开机自启动的逻辑
            # 例如在Windows上创建/删除注册表项
            self.logger.info(f"开机自启动设置: {enabled}")
        except Exception as e:
            self.logger.error(f"设置开机自启动失败: {e}")

    def _handle_minimize_to_tray_setting(self, enabled: bool):
        """处理最小化到托盘设置"""
        try:
            # 这里可以添加处理最小化到托盘的逻辑
            self.logger.info(f"最小化到托盘设置: {enabled}")
        except Exception as e:
            self.logger.error(f"设置最小化到托盘失败: {e}")

    def _on_performance_warning(self, warning_type: str, value: float) -> None:
        """
        处理性能警告（静默处理，不显示用户通知）

        Args:
            warning_type: 警告类型 ('high_cpu', 'high_memory', 'slow_response')
            value: 警告数值
        """
        try:
            # 只记录调试日志，不显示警告
            self.logger.debug(f"性能指标: {warning_type} = {value}")

            # 静默优化，不通知用户
            if warning_type == "high_memory" and value > 95:  # 提高阈值到95%
                # 内存使用率极高时，静默优化
                if hasattr(self, 'performance_manager') and self.performance_manager:
                    self.performance_manager.optimize_memory()

            # 不再显示任何用户通知或警告弹窗

        except Exception as e:
            self.logger.debug(f"性能优化处理: {e}")  # 降级为debug日志

    def get_manager(self, manager_type: str) -> Optional[QObject]:
        """
        获取指定类型的管理器

        Args:
            manager_type: 管理器类型 ('config', 'schedule', 'notification', 'time', 'component', 'theme', 'plugin')

        Returns:
            对应的管理器实例，如果不存在则返回None
        """
        managers = {
            'config': self.config_manager,
            'notification': self.notification_manager,
            'time': self.time_manager,
            'theme': self.theme_manager,
            'plugin': self.plugin_manager,
            'floating': self.floating_manager,
            'plugin_marketplace': getattr(self.plugin_manager, 'marketplace', None),
            # 'schedule': self.schedule_manager,
            # 'component': self.component_manager,
            # 'weather': self.weather_service,
        }

        return managers.get(manager_type)

    def is_initialized(self) -> bool:
        """
        检查是否已初始化

        Returns:
            是否已初始化
        """
        return self._initialized

    def is_closing(self) -> bool:
        """
        检查是否正在关闭

        Returns:
            是否正在关闭
        """
        return self._closing

    def save_state(self):
        """
        保存应用状态
        """
        try:
            self.logger.info("保存应用状态...")

            # 保存配置
            self.config_manager.save_all_configs()

            self.logger.info("应用状态保存完成")

        except Exception as e:
            self.logger.error(f"保存应用状态失败: {e}", exc_info=True)

    def cleanup(self):
        """
        清理资源
        """
        if self._closing:
            return

        self._closing = True
        self.logger.info("开始清理应用资源...")

        try:
            # 发送关闭信号
            self.app_closing.emit()

            # 停止定期更新
            if self.update_timer.isActive():
                self.update_timer.stop()

            # 保存状态
            self.save_state()

            managers = [
                self.notification_manager, self.time_manager, self.config_manager,
                self.plugin_manager, self.theme_manager, self.floating_manager,
                getattr(self, 'plugin_interaction_manager', None),
                getattr(self, 'remind_api_v2', None)
            ]

            for manager in managers:
                if manager and hasattr(manager, 'cleanup'):
                    try:
                        manager.cleanup()
                    except Exception as e:
                        self.logger.error(f"清理管理器失败: {e}")

            cleanup_timers(
                getattr(self, 'startup_timer', None),
                getattr(self, 'health_check_timer', None)
            )

            self.logger.info("应用资源清理完成")

        except Exception as e:
            self.logger.error(f"清理资源失败: {e}", exc_info=True)

        finally:
            self._initialized = False