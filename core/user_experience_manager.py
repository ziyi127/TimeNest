#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 用户体验管理器
负责用户界面优化、交互体验提升、可访问性支持

该模块提供了完整的用户体验管理功能，包括：
- 界面响应性优化
- 用户行为分析
- 可访问性支持
- 主题和布局管理
- 用户偏好设置
- 交互反馈优化
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, auto
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import QWidget, QApplication, QGraphicsOpacityEffect
from PyQt6.QtGui import QFont, QFontMetrics, QPalette, QColor


class InteractionType(Enum):
    """交互类型"""
    CLICK = auto()
    HOVER = auto()
    KEYBOARD = auto()
    SCROLL = auto()
    DRAG = auto()
    RESIZE = auto()


class AccessibilityLevel(Enum):
    """可访问性级别"""
    BASIC = auto()      # 基础支持
    ENHANCED = auto()   # 增强支持
    FULL = auto()       # 完全支持


@dataclass
class UserInteraction:
    """
    用户交互记录
    
    Attributes:
        timestamp: 交互时间
        type: 交互类型
        widget_name: 控件名称
        position: 交互位置
        duration: 交互持续时间
        success: 是否成功
        metadata: 额外元数据
    """
    timestamp: datetime
    type: InteractionType
    widget_name: str = ""
    position: Tuple[int, int] = (0, 0)
    duration: float = 0.0
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """
    性能指标
    
    Attributes:
        timestamp: 时间戳
        metric_name: 指标名称
        value: 指标值
        unit: 单位
        threshold: 阈值
        status: 状态（正常/警告/错误）
    """
    timestamp: datetime
    metric_name: str
    value: float
    unit: str = ""
    threshold: float = 0.0
    status: str = "normal"


class AnimationManager:
    """
    动画管理器
    
    管理界面动画效果，提供流畅的用户体验。
    """
    
    def __init__(self):
        """初始化动画管理器"""
        self.logger = logging.getLogger(f'{__name__}.AnimationManager')
        self.active_animations: Dict[str, QPropertyAnimation] = {}
        self.animation_enabled = True
        self.animation_duration = 300  # 默认动画时长（毫秒）
        
    def fade_in(self, widget: QWidget, duration: int = None, callback: Callable = None) -> str:
        """
        淡入动画
        
        Args:
            widget: 目标控件
            duration: 动画时长
            callback: 完成回调
            
        Returns:
            动画ID
        """
        if not self.animation_enabled:
            widget.setVisible(True)
            if callback:
                callback()
            return ""
        
        duration = duration or self.animation_duration
        animation_id = f"fade_in_{id(widget)}"
        
        # 创建透明度效果
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 设置回调
        if callback:
            animation.finished.connect(callback)
        
        # 清理动画
        animation.finished.connect(lambda: self._cleanup_animation(animation_id))
        
        # 开始动画
        widget.setVisible(True)
        animation.start()
        
        self.active_animations[animation_id] = animation
        return animation_id
    
    def fade_out(self, widget: QWidget, duration: int = None, callback: Callable = None) -> str:
        """
        淡出动画
        
        Args:
            widget: 目标控件
            duration: 动画时长
            callback: 完成回调
            
        Returns:
            动画ID
        """
        if not self.animation_enabled:
            widget.setVisible(False)
            if callback:
                callback()
            return ""
        
        duration = duration or self.animation_duration
        animation_id = f"fade_out_{id(widget)}"
        
        # 获取或创建透明度效果
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 设置回调
        def on_finished():
            widget.setVisible(False)
            if callback:
                callback()
        
        animation.finished.connect(on_finished)
        animation.finished.connect(lambda: self._cleanup_animation(animation_id))
        
        # 开始动画
        animation.start()
        
        self.active_animations[animation_id] = animation
        return animation_id
    
    def slide_in(self, widget: QWidget, direction: str = "left", duration: int = None, callback: Callable = None) -> str:
        """
        滑入动画
        
        Args:
            widget: 目标控件
            direction: 滑入方向 ("left", "right", "top", "bottom")
            duration: 动画时长
            callback: 完成回调
            
        Returns:
            动画ID
        """
        if not self.animation_enabled:
            widget.setVisible(True)
            if callback:
                callback()
            return ""
        
        duration = duration or self.animation_duration
        animation_id = f"slide_in_{id(widget)}_{direction}"
        
        # 获取目标位置
        target_rect = widget.geometry()
        
        # 计算起始位置
        start_rect = QRect(target_rect)
        if direction == "left":
            start_rect.moveLeft(-target_rect.width())
        elif direction == "right":
            start_rect.moveLeft(widget.parent().width())
        elif direction == "top":
            start_rect.moveTop(-target_rect.height())
        elif direction == "bottom":
            start_rect.moveTop(widget.parent().height())
        
        # 设置起始位置
        widget.setGeometry(start_rect)
        widget.setVisible(True)
        
        # 创建动画
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_rect)
        animation.setEndValue(target_rect)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 设置回调
        if callback:
            animation.finished.connect(callback)
        
        animation.finished.connect(lambda: self._cleanup_animation(animation_id))
        
        # 开始动画
        animation.start()
        
        self.active_animations[animation_id] = animation
        return animation_id
    
    def stop_animation(self, animation_id: str) -> bool:
        """
        停止动画
        
        Args:
            animation_id: 动画ID
            
        Returns:
            是否成功停止
        """
        if animation_id in self.active_animations:
            animation = self.active_animations[animation_id]
            animation.stop()
            self._cleanup_animation(animation_id)
            return True
        return False
    
    def stop_all_animations(self) -> None:
        """停止所有动画"""
        for animation_id in list(self.active_animations.keys()):
            self.stop_animation(animation_id)
    
    def set_animation_enabled(self, enabled: bool) -> None:
        """设置动画启用状态"""
        self.animation_enabled = enabled
        if not enabled:
            self.stop_all_animations()
    
    def set_animation_duration(self, duration: int) -> None:
        """设置默认动画时长"""
        self.animation_duration = max(0, duration)
    
    def _cleanup_animation(self, animation_id: str) -> None:
        """清理动画"""
        if animation_id in self.active_animations:
            del self.active_animations[animation_id]


class AccessibilityManager:
    """
    可访问性管理器
    
    提供可访问性支持，包括键盘导航、屏幕阅读器支持等。
    """
    
    def __init__(self):
        """初始化可访问性管理器"""
        self.logger = logging.getLogger(f'{__name__}.AccessibilityManager')
        self.accessibility_level = AccessibilityLevel.BASIC
        self.high_contrast_mode = False
        self.large_font_mode = False
        self.keyboard_navigation_enabled = True
        
    def enable_high_contrast(self, widget: QWidget) -> None:
        """
        启用高对比度模式
        
        Args:
            widget: 目标控件
        """
        try:
            if self.high_contrast_mode:
                palette = widget.palette()
                
                # 设置高对比度颜色
                palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
                palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
                palette.setColor(QPalette.ColorRole.Button, QColor(64, 64, 64))
                palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
                
                widget.setPalette(palette)
                
        except Exception as e:
            self.logger.error(f"启用高对比度模式失败: {e}")
    
    def enable_large_font(self, widget: QWidget, scale_factor: float = 1.2) -> None:
        """
        启用大字体模式
        
        Args:
            widget: 目标控件
            scale_factor: 缩放因子
        """
        try:
            if self.large_font_mode:
                font = widget.font()
                original_size = font.pointSize()
                new_size = int(original_size * scale_factor)
                font.setPointSize(new_size)
                widget.setFont(font)
                
        except Exception as e:
            self.logger.error(f"启用大字体模式失败: {e}")
    
    def setup_keyboard_navigation(self, widget: QWidget) -> None:
        """
        设置键盘导航
        
        Args:
            widget: 目标控件
        """
        try:
            if self.keyboard_navigation_enabled:
                widget.setFocusPolicy(widget.focusPolicy() | widget.focusPolicy().TabFocus)
                
        except Exception as e:
            self.logger.error(f"设置键盘导航失败: {e}")
    
    def set_accessibility_level(self, level: AccessibilityLevel) -> None:
        """设置可访问性级别"""
        self.accessibility_level = level
        self.logger.info(f"可访问性级别设置为: {level.name}")
    
    def set_high_contrast_mode(self, enabled: bool) -> None:
        """设置高对比度模式"""
        self.high_contrast_mode = enabled
        self.logger.info(f"高对比度模式: {'启用' if enabled else '禁用'}")
    
    def set_large_font_mode(self, enabled: bool) -> None:
        """设置大字体模式"""
        self.large_font_mode = enabled
        self.logger.info(f"大字体模式: {'启用' if enabled else '禁用'}")


class UserExperienceManager(QObject):
    """
    TimeNest 用户体验管理器
    
    提供完整的用户体验管理功能，包括动画、可访问性、性能监控等。
    
    Attributes:
        animation_manager: 动画管理器
        accessibility_manager: 可访问性管理器
        interaction_history: 用户交互历史
        performance_metrics: 性能指标
        
    Signals:
        interaction_recorded: 交互记录信号 (interaction: UserInteraction)
        performance_warning: 性能警告信号 (metric: PerformanceMetric)
        accessibility_changed: 可访问性设置变更信号 (setting: str, value: Any)
    """
    
    # 信号定义
    interaction_recorded = pyqtSignal(object)  # UserInteraction
    performance_warning = pyqtSignal(object)  # PerformanceMetric
    accessibility_changed = pyqtSignal(str, object)  # setting, value
    
    def __init__(self, config_manager=None):
        """
        初始化用户体验管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        super().__init__()
        
        self.logger = logging.getLogger(f'{__name__}.UserExperienceManager')
        self.config_manager = config_manager
        
        # 子管理器
        self.animation_manager = AnimationManager()
        self.accessibility_manager = AccessibilityManager()
        
        # 用户交互记录
        self.interaction_history: List[UserInteraction] = []
        self.max_history_size = 1000
        
        # 性能指标
        self.performance_metrics: List[PerformanceMetric] = []
        self.max_metrics_size = 500
        
        # 性能监控定时器
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._collect_performance_metrics)
        self.performance_timer.start(5000)  # 5秒间隔
        
        # 加载配置
        self._load_configuration()
        
        self.logger.info("用户体验管理器初始化完成")
    
    def record_interaction(self, interaction_type: InteractionType, widget_name: str = "", 
                          position: Tuple[int, int] = (0, 0), duration: float = 0.0, 
                          success: bool = True, metadata: Dict[str, Any] = None) -> None:
        """
        记录用户交互
        
        Args:
            interaction_type: 交互类型
            widget_name: 控件名称
            position: 交互位置
            duration: 交互持续时间
            success: 是否成功
            metadata: 额外元数据
        """
        try:
            interaction = UserInteraction(
                timestamp=datetime.now(),
                type=interaction_type,
                widget_name=widget_name,
                position=position,
                duration=duration,
                success=success,
                metadata=metadata or {}
            )
            
            # 添加到历史记录
            self.interaction_history.append(interaction)
            
            # 限制历史记录大小
            if len(self.interaction_history) > self.max_history_size:
                self.interaction_history = self.interaction_history[-self.max_history_size//2:]
            
            # 发出信号
            self.interaction_recorded.emit(interaction)
            
            self.logger.debug(f"记录用户交互: {interaction_type.name} - {widget_name}")
            
        except Exception as e:
            self.logger.error(f"记录用户交互失败: {e}")
    
    def get_interaction_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取交互统计信息
        
        Args:
            hours: 统计时间范围（小时）
            
        Returns:
            统计信息字典
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_interactions = [i for i in self.interaction_history if i.timestamp >= cutoff_time]
            
            if not recent_interactions:
                return {}
            
            # 统计各种交互类型
            type_counts = {}
            success_count = 0
            total_duration = 0.0
            
            for interaction in recent_interactions:
                type_name = interaction.type.name
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
                
                if interaction.success:
                    success_count += 1
                
                total_duration += interaction.duration
            
            # 计算统计信息
            total_interactions = len(recent_interactions)
            success_rate = success_count / total_interactions if total_interactions > 0 else 0
            avg_duration = total_duration / total_interactions if total_interactions > 0 else 0
            
            return {
                'total_interactions': total_interactions,
                'success_rate': success_rate,
                'average_duration': avg_duration,
                'interaction_types': type_counts,
                'time_range_hours': hours
            }
            
        except Exception as e:
            self.logger.error(f"获取交互统计失败: {e}")
            return {}
    
    def optimize_for_user_behavior(self) -> None:
        """根据用户行为优化界面"""
        try:
            stats = self.get_interaction_statistics()
            
            if not stats:
                return
            
            # 根据成功率调整界面
            if stats.get('success_rate', 1.0) < 0.8:
                self.logger.info("检测到用户操作成功率较低，建议优化界面")
                # 可以在这里添加具体的优化逻辑
            
            # 根据交互类型调整
            interaction_types = stats.get('interaction_types', {})
            if interaction_types.get('KEYBOARD', 0) > interaction_types.get('CLICK', 0):
                # 用户更偏好键盘操作
                self.accessibility_manager.keyboard_navigation_enabled = True
                self.logger.info("检测到用户偏好键盘操作，启用键盘导航优化")
            
        except Exception as e:
            self.logger.error(f"用户行为优化失败: {e}")
    
    def _collect_performance_metrics(self) -> None:
        """收集性能指标"""
        try:
            # 收集应用响应时间
            app = QApplication.instance()
            if app:
                # 这里可以添加具体的性能指标收集逻辑
                pass
            
        except Exception as e:
            self.logger.error(f"收集性能指标失败: {e}")
    
    def _load_configuration(self) -> None:
        """加载配置"""
        try:
            if not self.config_manager:
                return
            
            # 加载动画设置
            animation_config = self.config_manager.get('animation', {})
            self.animation_manager.set_animation_enabled(animation_config.get('enabled', True))
            self.animation_manager.set_animation_duration(animation_config.get('duration', 300))
            
            # 加载可访问性设置
            accessibility_config = self.config_manager.get('accessibility', {})
            self.accessibility_manager.set_high_contrast_mode(accessibility_config.get('high_contrast', False))
            self.accessibility_manager.set_large_font_mode(accessibility_config.get('large_font', False))
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            self.performance_timer.stop()
            
            # 停止所有动画
            self.animation_manager.stop_all_animations()
            
            # 清空历史记录
            self.interaction_history.clear()
            self.performance_metrics.clear()
            
            self.logger.info("用户体验管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"用户体验管理器清理失败: {e}")
