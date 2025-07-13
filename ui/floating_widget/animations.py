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
TimeNest 浮窗动画系统
提供平滑的显示、隐藏和内容切换动画
"""

import logging
from typing import Optional, Callable
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


class FloatingAnimations(QObject):
    """
    浮窗动画管理器
    
    提供各种动画效果的统一管理
    """
    
    # 信号定义
    animation_finished = pyqtSignal(str)  # 动画完成信号
    
    def __init__(self, widget: QWidget):
        """
        初始化动画管理器
        
        Args:
            widget: 要应用动画的浮窗组件
        """
        super().__init__()
        
        self.widget = widget
        self.logger = logging.getLogger(f'{__name__}.FloatingAnimations')
        
        # 动画实例
        self.slide_animation: Optional[QPropertyAnimation] = None
        self.opacity_animation: Optional[QPropertyAnimation] = None
        self.size_animation: Optional[QPropertyAnimation] = None
        
        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect()
        self.widget.setGraphicsEffect(self.opacity_effect)
        
        # 动画配置
        self.animation_duration = 300  # 默认动画时长（毫秒）
        self.easing_curve = QEasingCurve.Type.OutCubic
        
        self.logger.debug("浮窗动画管理器初始化完成")
    
    def set_animation_duration(self, duration_ms: int) -> None:
        """
        设置动画时长
        
        Args:
            duration_ms: 动画时长（毫秒）
        """
        self.animation_duration = max(100, min(1000, duration_ms))
        self.logger.debug(f"动画时长设置为 {self.animation_duration}ms")
    
    def set_easing_curve(self, curve: QEasingCurve.Type) -> None:
        """
        设置缓动曲线
        
        Args:
            curve: 缓动曲线类型
        """
        self.easing_curve = curve
        self.logger.debug(f"缓动曲线设置为 {curve}")
    
    def slide_in_from_top(self, callback: Optional[Callable] = None) -> None:
        """
        从顶部滑入动画
        
        Args:
            callback: 动画完成后的回调函数
        """
        try:
            # 获取屏幕和窗口信息
            screen = self.widget.screen()
            if not screen:
                self.logger.warning("无法获取屏幕信息")
                return
            
            screen_geometry = screen.availableGeometry()
            widget_size = self.widget.size()
            
            # 计算目标位置（屏幕顶部居中）
            target_x = (screen_geometry.width() - widget_size.width()) // 2
            target_y = 10  # 距离顶部10px
            
            # 设置起始位置（屏幕顶部外）
            start_y = -widget_size.height()
            self.widget.move(target_x, start_y)
            self.widget.show()
            
            # 创建滑动动画
            self.slide_animation = QPropertyAnimation(self.widget, b"geometry")
            self.slide_animation.setDuration(self.animation_duration)
            self.slide_animation.setEasingCurve(self.easing_curve)
            
            start_rect = QRect(target_x, start_y, widget_size.width(), widget_size.height())
            end_rect = QRect(target_x, target_y, widget_size.width(), widget_size.height())
            
            self.slide_animation.setStartValue(start_rect)
            self.slide_animation.setEndValue(end_rect)
            
            # 连接完成信号
            if callback:
                self.slide_animation.finished.connect(callback)
            
            self.slide_animation.finished.connect(
                lambda: self.animation_finished.emit("slide_in")
            )
            
            # 开始动画
            self.slide_animation.start()
            self.logger.debug("开始从顶部滑入动画")
            
        except Exception as e:
            self.logger.error(f"滑入动画失败: {e}")
    
    def slide_out_to_top(self, callback: Optional[Callable] = None) -> None:
        """
        向顶部滑出动画
        
        Args:
            callback: 动画完成后的回调函数
        """
        try:
            current_geometry = self.widget.geometry()
            widget_size = self.widget.size()
            
            # 目标位置（屏幕顶部外）
            target_y = -widget_size.height()
            
            # 创建滑动动画
            self.slide_animation = QPropertyAnimation(self.widget, b"geometry")
            self.slide_animation.setDuration(self.animation_duration)
            self.slide_animation.setEasingCurve(self.easing_curve)
            
            start_rect = current_geometry
            end_rect = QRect(current_geometry.x(), target_y, 
                           widget_size.width(), widget_size.height())
            
            self.slide_animation.setStartValue(start_rect)
            self.slide_animation.setEndValue(end_rect)
            
            # 连接完成信号
            def on_finished():
                self.widget.hide()
                if callback:
                    callback()
                self.animation_finished.emit("slide_out")
            
            self.slide_animation.finished.connect(on_finished)
            
            # 开始动画
            self.slide_animation.start()
            self.logger.debug("开始向顶部滑出动画")
            
        except Exception as e:
            self.logger.error(f"滑出动画失败: {e}")
    
    def fade_in(self, callback: Optional[Callable] = None) -> None:
        """
        淡入动画
        
        Args:
            callback: 动画完成后的回调函数
        """
        try:
            self.widget.show()
            
            # 创建透明度动画
            self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.opacity_animation.setDuration(self.animation_duration)
            self.opacity_animation.setEasingCurve(self.easing_curve)
            
            self.opacity_animation.setStartValue(0.0)
            self.opacity_animation.setEndValue(1.0)
            
            # 连接完成信号
            if callback:
                self.opacity_animation.finished.connect(callback)
            
            self.opacity_animation.finished.connect(
                lambda: self.animation_finished.emit("fade_in")
            )
            
            # 开始动画
            self.opacity_animation.start()
            self.logger.debug("开始淡入动画")
            
        except Exception as e:
            self.logger.error(f"淡入动画失败: {e}")
    
    def fade_out(self, callback: Optional[Callable] = None) -> None:
        """
        淡出动画
        
        Args:
            callback: 动画完成后的回调函数
        """
        try:
            # 创建透明度动画
            self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.opacity_animation.setDuration(self.animation_duration)
            self.opacity_animation.setEasingCurve(self.easing_curve)
            
            self.opacity_animation.setStartValue(1.0)
            self.opacity_animation.setEndValue(0.0)
            
            # 连接完成信号
            def on_finished():
                self.widget.hide()
                if callback:
                    callback()
                self.animation_finished.emit("fade_out")
            
            self.opacity_animation.finished.connect(on_finished)
            
            # 开始动画
            self.opacity_animation.start()
            self.logger.debug("开始淡出动画")
            
        except Exception as e:
            self.logger.error(f"淡出动画失败: {e}")
    
    def smooth_resize(self, new_width: int, new_height: int, 
                     callback: Optional[Callable] = None) -> None:
        """
        平滑调整大小动画
        
        Args:
            new_width: 新宽度
            new_height: 新高度
            callback: 动画完成后的回调函数
        """
        try:
            current_geometry = self.widget.geometry()
            
            # 创建大小调整动画
            self.size_animation = QPropertyAnimation(self.widget, b"geometry")
            self.size_animation.setDuration(self.animation_duration)
            self.size_animation.setEasingCurve(self.easing_curve)
            
            # 保持位置居中
            new_x = current_geometry.x() + (current_geometry.width() - new_width) // 2
            new_y = current_geometry.y()
            
            start_rect = current_geometry
            end_rect = QRect(new_x, new_y, new_width, new_height)
            
            self.size_animation.setStartValue(start_rect)
            self.size_animation.setEndValue(end_rect)
            
            # 连接完成信号
            if callback:
                self.size_animation.finished.connect(callback)
            
            self.size_animation.finished.connect(
                lambda: self.animation_finished.emit("resize")
            )
            
            # 开始动画
            self.size_animation.start()
            self.logger.debug(f"开始调整大小动画: {new_width}x{new_height}")
            
        except Exception as e:
            self.logger.error(f"调整大小动画失败: {e}")
    
    def stop_all_animations(self) -> None:
        """停止所有动画"""
        try:
            if self.slide_animation and self.slide_animation.state() == QPropertyAnimation.State.Running:
                self.slide_animation.stop()
            
            if self.opacity_animation and self.opacity_animation.state() == QPropertyAnimation.State.Running:
                self.opacity_animation.stop()
            
            if self.size_animation and self.size_animation.state() == QPropertyAnimation.State.Running:
                self.size_animation.stop()
            
            self.logger.debug("所有动画已停止")
            
        except Exception as e:
            self.logger.error(f"停止动画失败: {e}")
    
    def cleanup(self) -> None:
        """清理动画资源"""
        try:
            self.stop_all_animations()
            
            # 清理动画对象
            if self.slide_animation:
                self.slide_animation.deleteLater()
                self.slide_animation = None
            
            if self.opacity_animation:
                self.opacity_animation.deleteLater()
                self.opacity_animation = None
            
            if self.size_animation:
                self.size_animation.deleteLater()
                self.size_animation = None
            
            self.logger.debug("动画资源清理完成")
            
        except Exception as e:
            self.logger.error(f"清理动画资源失败: {e}")
