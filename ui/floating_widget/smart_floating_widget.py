#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 智能浮窗主组件
仿苹果灵动岛的动态信息显示功能
"""

import logging
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QMenu, QApplication
)
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QCursor, 
    QPaintEvent, QMouseEvent, QContextMenuEvent
)

from .floating_modules import (
    FloatingModule, TimeModule, ScheduleModule, 
    CountdownModule, WeatherModule, SystemStatusModule
)
from .animations import FloatingAnimations

if TYPE_CHECKING:
    from core.app_manager import AppManager


class SmartFloatingWidget(QWidget):
    """
    智能浮窗主组件
    
    仿苹果灵动岛设计的动态信息显示浮窗
    """
    
    # 信号定义
    settings_requested = pyqtSignal()  # 请求打开设置
    main_window_requested = pyqtSignal()  # 请求打开主窗口
    visibility_changed = pyqtSignal(bool)  # 可见性变化
    
    def __init__(self, app_manager: 'AppManager'):
        """
        初始化智能浮窗
        
        Args:
            app_manager: 应用管理器实例（依赖注入）
        """
        super().__init__()
        
        # 依赖注入
        self.app_manager = app_manager
        self.logger = logging.getLogger(f'{__name__}.SmartFloatingWidget')
        
        # 浮窗配置
        self.config = {}
        self.load_config()

        # 外观配置
        self.default_width = 400
        self.default_height = 60
        self.min_width = 300
        self.min_height = 50
        self.max_width = 600
        self.max_height = 80
        self.border_radius = 30
        self.opacity_value = 0.9

        # 交互配置
        self.mouse_transparent = True  # 默认启用鼠标穿透
        self.fixed_position = True     # 固定位置，不可拖拽
        self.auto_rotate_content = True  # 自动轮播内容
        
        # 模块管理
        self.modules: Dict[str, FloatingModule] = {}
        self.enabled_modules: List[str] = []
        self.module_order: List[str] = []
        
        # UI组件
        self.content_label: Optional[QLabel] = None
        self.layout: Optional[QHBoxLayout] = None
        
        # 动画管理器
        self.animations: Optional[FloatingAnimations] = None
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)

        # 内容轮播定时器
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_content)
        self.current_rotation_index = 0
        self.rotation_interval = 5000  # 5秒轮播间隔

        # 拖拽相关
        self.dragging = False
        self.drag_start_position = QPoint()
        
        # 初始化
        self.init_ui()
        self.init_modules()
        self.init_animations()
        self.apply_config()

        # 启动更新定时器并立即更新一次
        self.update_timer.start(1000)  # 每秒更新
        QTimer.singleShot(100, self.update_display)  # 100ms后首次更新

        # 启动置顶检查定时器
        self.top_check_timer = QTimer()
        self.top_check_timer.timeout.connect(self.ensure_always_on_top)
        self.top_check_timer.start(5000)  # 每5秒检查一次置顶状态

        # 初始化增强模块
        self.init_enhanced_modules()

        self.logger.info("智能浮窗初始化完成")
    
    def load_config(self) -> None:
        """加载浮窗配置"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.config = self.app_manager.config_manager.get_config('floating_widget', {}, 'component')
                
                # 加载基本配置
                self.default_width = self.config.get('width', 400)
                self.default_height = self.config.get('height', 60)
                self.opacity_value = self.config.get('opacity', 0.9)
                self.border_radius = self.config.get('border_radius', 30)

                # 加载交互配置
                self.mouse_transparent = self.config.get('mouse_transparent', True)
                self.fixed_position = self.config.get('fixed_position', True)
                self.auto_rotate_content = self.config.get('auto_rotate_content', True)
                self.rotation_interval = self.config.get('rotation_interval', 5000)
                
                # 加载模块配置
                modules_config = self.config.get('modules', {})
                self.enabled_modules = [
                    module_id for module_id, config in modules_config.items()
                    if config.get('enabled', True)
                ]

                # 如果没有启用的模块，使用默认模块
                if not self.enabled_modules:
                    self.enabled_modules = ['time', 'schedule']
                    # 保存默认模块配置
                    default_modules_config = {
                        'time': {'enabled': True, 'order': 0},
                        'schedule': {'enabled': True, 'order': 1}
                    }
                    self.config['modules'] = default_modules_config

                # 按顺序排序
                self.module_order = sorted(
                    self.enabled_modules,
                    key=lambda x: modules_config.get(x, {}).get('order', 0)
                )
                
        except Exception as e:
            self.logger.warning(f"加载配置失败: {e}")
            # 使用默认配置
            self.enabled_modules = ['time', 'schedule']
            self.module_order = ['time', 'schedule']
    
    def save_config(self) -> None:
        """保存浮窗配置"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'config_manager'):
                self.config.update({
                    'width': self.width(),
                    'height': self.height(),
                    'opacity': self.opacity_value,
                    'border_radius': self.border_radius,
                    'position': {'x': self.x(), 'y': self.y()},
                    'mouse_transparent': self.mouse_transparent,
                    'fixed_position': self.fixed_position,
                    'auto_rotate_content': self.auto_rotate_content,
                    'rotation_interval': self.rotation_interval
                })
                
                self.app_manager.config_manager.set_config('floating_widget', self.config, 'component')
                
        except Exception as e:
            self.logger.warning(f"保存配置失败: {e}")
    
    def init_ui(self) -> None:
        """初始化UI"""
        try:
            # 设置窗口属性 - 确保不在任务栏显示且始终置顶
            window_flags = (
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool |
                Qt.WindowType.WindowDoesNotAcceptFocus |
                Qt.WindowType.BypassWindowManagerHint
            )

            # 添加鼠标穿透标志
            if self.mouse_transparent:
                window_flags |= Qt.WindowType.WindowTransparentForInput

            self.setWindowFlags(window_flags)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            # 确保始终置顶
            self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            
            # 设置大小
            self.setFixedSize(self.default_width, self.default_height)
            
            # 创建布局
            self.layout = QHBoxLayout(self)
            self.layout.setContentsMargins(15, 10, 15, 10)
            self.layout.setSpacing(10)
            
            # 创建内容标签
            self.content_label = QLabel("TimeNest 智能浮窗")
            self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                }
            """)
            
            self.layout.addWidget(self.content_label)
            
            # 位置设置将在 apply_config() 中处理
            
        except Exception as e:
            self.logger.error(f"初始化UI失败: {e}")
    
    def init_modules(self) -> None:
        """初始化功能模块"""
        try:
            # 创建所有可用模块
            available_modules = {
                'time': TimeModule,
                'schedule': ScheduleModule,
                'countdown': CountdownModule,
                'weather': WeatherModule,
                'system': SystemStatusModule
            }
            
            # 实例化启用的模块
            for module_id in self.enabled_modules:
                if module_id in available_modules:
                    module_class = available_modules[module_id]
                    module = module_class(self.app_manager)
                    
                    # 连接信号
                    module.content_updated.connect(self.on_module_content_updated)
                    module.error_occurred.connect(self.on_module_error)
                    
                    self.modules[module_id] = module
                    self.logger.debug(f"模块 {module_id} 初始化完成")
            
            # 启动模块更新
            for module in self.modules.values():
                module.start_updates(1000)  # 每秒更新一次
                self.logger.debug(f"模块 {module.module_id} 已启动")
                
        except Exception as e:
            self.logger.error(f"初始化模块失败: {e}")
    
    def init_animations(self) -> None:
        """初始化动画管理器"""
        try:
            self.animations = FloatingAnimations(self)
            self.animations.animation_finished.connect(self.on_animation_finished)
            
            # 设置动画配置
            duration = self.config.get('animation_duration', 300)
            self.animations.set_animation_duration(duration)
            
        except Exception as e:
            self.logger.error(f"初始化动画失败: {e}")
    
    def apply_config(self) -> None:
        """应用配置"""
        try:
            # 应用透明度
            self.setWindowOpacity(self.opacity_value)
            
            # 强制设置到屏幕顶部居中（忽略配置中的位置）
            self.logger.info("强制设置浮窗到屏幕顶部居中")
            self.center_on_screen()
            
            # 应用主题
            self.apply_theme()
            
            # 启动更新定时器
            self.update_timer.start(1000)  # 每秒更新

            # 启动内容轮播（如果启用）
            if self.auto_rotate_content and len(self.enabled_modules) > 1:
                self.rotation_timer.start(self.rotation_interval)

        except Exception as e:
            self.logger.error(f"应用配置失败: {e}")

    def update_from_config(self) -> None:
        """从配置更新浮窗设置"""
        try:
            # 重新加载配置
            self.load_config()

            # 重新应用配置
            self.apply_config()

            self.logger.debug("浮窗配置已更新")

        except Exception as e:
            self.logger.error(f"从配置更新失败: {e}")

    def ensure_always_on_top(self) -> None:
        """确保浮窗始终置顶"""
        try:
            if self.isVisible():
                # 重新设置窗口标志以确保置顶
                current_flags = self.windowFlags()
                if not (current_flags & Qt.WindowType.WindowStaysOnTopHint):
                    self.setWindowFlags(current_flags | Qt.WindowType.WindowStaysOnTopHint)
                    self.show()

                # 强制提升窗口层级
                self.raise_()
                self.activateWindow()

        except Exception as e:
            self.logger.warning(f"确保置顶失败: {e}")

    def init_enhanced_modules(self) -> None:
        """初始化增强模块"""
        try:
            from ui.floating_widget.enhanced_modules import EnhancedFloatingModules

            self.enhanced_modules = EnhancedFloatingModules()

            # 创建增强组件
            self.scrolling_text = self.enhanced_modules.create_scrolling_text("欢迎使用 TimeNest 智能浮窗")
            self.weather_widget = self.enhanced_modules.create_weather_widget()
            self.notification_banner = self.enhanced_modules.create_notification_banner()

            self.logger.info("增强模块初始化完成")

        except Exception as e:
            self.logger.error(f"初始化增强模块失败: {e}")

    def show_reminder_message(self, message: str) -> None:
        """显示提醒消息"""
        try:
            if hasattr(self, 'notification_banner'):
                self.notification_banner.show_message(message, 5000)
            else:
                self.logger.warning("通知横幅未初始化")

        except Exception as e:
            self.logger.error(f"显示提醒消息失败: {e}")

    def update_scrolling_text(self, text: str) -> None:
        """更新滚动文本"""
        try:
            if hasattr(self, 'scrolling_text'):
                self.scrolling_text.set_text(text)
            else:
                self.logger.warning("滚动文本组件未初始化")

        except Exception as e:
            self.logger.error(f"更新滚动文本失败: {e}")

    def get_weather_data(self) -> Dict[str, Any]:
        """获取天气数据"""
        try:
            if hasattr(self, 'weather_widget'):
                return self.weather_widget.weather_data
            return {}

        except Exception as e:
            self.logger.error(f"获取天气数据失败: {e}")
            return {}
    
    def apply_theme(self) -> None:
        """应用主题样式"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'theme_manager'):
                theme = self.app_manager.theme_manager.get_current_theme()
                if theme:
                    # 根据主题调整样式
                    theme_type = getattr(theme, 'type', None)
                    if theme_type and hasattr(theme_type, 'value'):
                        theme_type_value = theme_type.value
                    else:
                        theme_type_value = getattr(theme, 'name', 'light')

                    if theme_type_value == 'dark':
                        self.content_label.setStyleSheet("""
                            QLabel {
                                color: white;
                                font-size: 12px;
                                font-weight: bold;
                                background: transparent;
                            }
                        """)
                    else:
                        self.content_label.setStyleSheet("""
                            QLabel {
                                color: #333333;
                                font-size: 12px;
                                font-weight: bold;
                                background: transparent;
                            }
                        """)
        except Exception as e:
            self.logger.warning(f"应用主题失败: {e}")
    
    def center_on_screen(self) -> None:
        """将浮窗居中到屏幕顶部"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                # 计算水平居中位置
                x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
                # 设置到屏幕顶部，留出一些边距
                y = screen_geometry.y() + 10  # 距离顶部10px

                self.move(x, y)
                self.logger.info(f"浮窗位置设置为: ({x}, {y})")

                # 保存位置到配置
                self.config['position'] = {'x': x, 'y': y}
                self.save_config()

        except Exception as e:
            self.logger.warning(f"设置浮窗位置失败: {e}")
    
    def update_display(self) -> None:
        """更新显示内容"""
        try:
            self.logger.debug(f"更新显示 - 模块数量: {len(self.modules)}, 启用模块: {self.enabled_modules}")

            if not self.modules:
                self.logger.warning("没有可用的模块")
                self.content_label.setText("TimeNest - 无模块")
                return

            if self.auto_rotate_content and len(self.enabled_modules) > 1:
                # 轮播模式：只显示当前轮播的模块
                self.display_rotated_content()
            else:
                # 正常模式：显示所有启用的模块
                self.display_all_content()

        except Exception as e:
            self.logger.error(f"更新显示失败: {e}")
            self.content_label.setText("TimeNest - 显示错误")

    def display_all_content(self) -> None:
        """显示所有模块内容"""
        try:
            # 收集所有模块的显示内容
            content_parts = []
            self.logger.debug(f"模块顺序: {self.module_order}")

            for module_id in self.module_order:
                if module_id in self.modules:
                    module = self.modules[module_id]
                    self.logger.debug(f"模块 {module_id}: enabled={module.enabled}, visible={module.visible}")

                    if module.enabled and module.visible:
                        text = module.get_display_text()
                        self.logger.debug(f"模块 {module_id} 文本: '{text}'")
                        if text:
                            content_parts.append(text)
                else:
                    self.logger.warning(f"模块 {module_id} 不在模块字典中")

            # 更新显示
            if content_parts:
                display_text = " | ".join(content_parts)
                self.logger.debug(f"最终显示文本: '{display_text}'")
                self.content_label.setText(display_text)
            else:
                self.logger.warning("没有内容可显示，使用默认文本")
                self.content_label.setText("TimeNest")

        except Exception as e:
            self.logger.error(f"显示所有内容失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def display_rotated_content(self) -> None:
        """显示轮播内容"""
        try:
            if not self.enabled_modules:
                self.content_label.setText("TimeNest")
                return

            # 获取当前轮播模块
            if self.current_rotation_index >= len(self.enabled_modules):
                self.current_rotation_index = 0

            current_module_id = self.enabled_modules[self.current_rotation_index]

            if current_module_id in self.modules:
                module = self.modules[current_module_id]
                if module.enabled:
                    text = module.get_display_text()
                    if text:
                        # 添加模块指示器
                        indicator = f"[{self.current_rotation_index + 1}/{len(self.enabled_modules)}]"
                        display_text = f"{text} {indicator}"
                        self.content_label.setText(display_text)
                    else:
                        self.content_label.setText("TimeNest")
                else:
                    self.content_label.setText("TimeNest")
            else:
                self.content_label.setText("TimeNest")

        except Exception as e:
            self.logger.error(f"显示轮播内容失败: {e}")

    def rotate_content(self) -> None:
        """轮播到下一个内容"""
        try:
            if len(self.enabled_modules) > 1:
                self.current_rotation_index = (self.current_rotation_index + 1) % len(self.enabled_modules)
                self.display_rotated_content()

        except Exception as e:
            self.logger.error(f"内容轮播失败: {e}")

    def set_auto_rotate(self, enabled: bool, interval_ms: int = 5000) -> None:
        """
        设置自动轮播

        Args:
            enabled: 是否启用轮播
            interval_ms: 轮播间隔（毫秒）
        """
        try:
            self.auto_rotate_content = enabled
            self.rotation_interval = interval_ms

            if enabled and len(self.enabled_modules) > 1:
                self.rotation_timer.start(self.rotation_interval)
            else:
                self.rotation_timer.stop()

            self.save_config()
            self.logger.debug(f"自动轮播设置: {enabled}, 间隔: {interval_ms}ms")

        except Exception as e:
            self.logger.error(f"设置自动轮播失败: {e}")
    
    def on_module_content_updated(self, content: str) -> None:
        """模块内容更新处理"""
        # 触发显示更新
        self.update_display()
    
    def on_module_error(self, error_message: str) -> None:
        """模块错误处理"""
        self.logger.warning(f"模块错误: {error_message}")
        
        # 可以选择显示错误通知
        if self.app_manager and hasattr(self.app_manager, 'notification_manager'):
            self.app_manager.notification_manager.send_notification(
                title="浮窗模块错误",
                message=error_message,
                channels=['tray']
            )
    
    def on_animation_finished(self, animation_type: str) -> None:
        """动画完成处理"""
        self.logger.debug(f"动画完成: {animation_type}")

        if animation_type in ['slide_out', 'fade_out']:
            self.visibility_changed.emit(False)
        elif animation_type in ['slide_in', 'fade_in']:
            self.visibility_changed.emit(True)

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制事件"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 获取主题颜色
            bg_color = self.get_background_color()
            border_color = self.get_border_color()

            # 绘制背景
            rect = self.rect()
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 1))
            painter.drawRoundedRect(rect, self.border_radius, self.border_radius)

        except Exception as e:
            self.logger.error(f"绘制失败: {e}")
        finally:
            painter.end()

    def get_background_color(self) -> QColor:
        """获取背景颜色"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'theme_manager'):
                theme = self.app_manager.theme_manager.get_current_theme()
                if theme:
                    theme_type = getattr(theme, 'type', None)
                    if theme_type and hasattr(theme_type, 'value'):
                        theme_type_value = theme_type.value
                    else:
                        theme_type_value = getattr(theme, 'name', 'light')

                    if theme_type_value == 'dark':
                        return QColor(30, 30, 30, int(255 * self.opacity_value))
                    else:
                        return QColor(240, 240, 240, int(255 * self.opacity_value))

            # 默认颜色
            return QColor(50, 50, 50, int(255 * self.opacity_value))

        except Exception as e:
            self.logger.warning(f"获取背景颜色失败: {e}")
            return QColor(50, 50, 50, int(255 * self.opacity_value))

    def get_border_color(self) -> QColor:
        """获取边框颜色"""
        try:
            if self.app_manager and hasattr(self.app_manager, 'theme_manager'):
                theme = self.app_manager.theme_manager.get_current_theme()
                if theme:
                    theme_type = getattr(theme, 'type', None)
                    if theme_type and hasattr(theme_type, 'value'):
                        theme_type_value = theme_type.value
                    else:
                        theme_type_value = getattr(theme, 'name', 'light')

                    if theme_type_value == 'dark':
                        return QColor(80, 80, 80, 150)
                    else:
                        return QColor(200, 200, 200, 150)

            # 默认颜色
            return QColor(100, 100, 100, 150)

        except Exception as e:
            self.logger.warning(f"获取边框颜色失败: {e}")
            return QColor(100, 100, 100, 150)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件"""
        try:
            # 在固定位置模式下禁用拖拽
            if not self.fixed_position and event.button() == Qt.MouseButton.LeftButton:
                self.dragging = True
                self.drag_start_position = event.globalPosition().toPoint() - self.pos()

        except Exception as e:
            self.logger.error(f"鼠标按下事件处理失败: {e}")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """鼠标移动事件"""
        try:
            # 在固定位置模式下禁用拖拽
            if (not self.fixed_position and
                self.dragging and
                event.buttons() == Qt.MouseButton.LeftButton):

                new_pos = event.globalPosition().toPoint() - self.drag_start_position

                # 限制在屏幕边界内
                screen = QApplication.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    new_pos.setX(max(0, min(new_pos.x(),
                                           screen_geometry.width() - self.width())))
                    new_pos.setY(max(0, min(new_pos.y(),
                                           screen_geometry.height() - self.height())))

                self.move(new_pos)

        except Exception as e:
            self.logger.error(f"鼠标移动事件处理失败: {e}")

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标释放事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.dragging = False
                # 在非固定模式下保存新位置
                if not self.fixed_position:
                    self.save_config()

        except Exception as e:
            self.logger.error(f"鼠标释放事件处理失败: {e}")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """鼠标双击事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.main_window_requested.emit()

        except Exception as e:
            self.logger.error(f"鼠标双击事件处理失败: {e}")

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """右键菜单事件"""
        try:
            menu = QMenu(self)

            # 显示/隐藏动作
            if self.isVisible():
                hide_action = menu.addAction("隐藏浮窗")
                hide_action.triggered.connect(self.hide_with_animation)
            else:
                show_action = menu.addAction("显示浮窗")
                show_action.triggered.connect(self.show_with_animation)

            menu.addSeparator()

            # 设置动作
            settings_action = menu.addAction("浮窗设置")
            settings_action.triggered.connect(self.settings_requested.emit)

            # 主窗口动作
            main_window_action = menu.addAction("打开主窗口")
            main_window_action.triggered.connect(self.main_window_requested.emit)

            menu.addSeparator()

            # 退出动作
            quit_action = menu.addAction("退出 TimeNest")
            quit_action.triggered.connect(QApplication.quit)

            # 显示菜单
            menu.exec(event.globalPos())

        except Exception as e:
            self.logger.error(f"右键菜单事件处理失败: {e}")

    def show_with_animation(self) -> None:
        """带动画显示浮窗"""
        try:
            if self.animations:
                self.animations.slide_in_from_top()
            else:
                self.show()
                self.visibility_changed.emit(True)

        except Exception as e:
            self.logger.error(f"显示动画失败: {e}")
            self.show()

    def hide_with_animation(self) -> None:
        """带动画隐藏浮窗"""
        try:
            if self.animations:
                self.animations.slide_out_to_top()
            else:
                self.hide()
                self.visibility_changed.emit(False)

        except Exception as e:
            self.logger.error(f"隐藏动画失败: {e}")
            self.hide()

    def set_opacity(self, opacity: float) -> None:
        """
        设置透明度

        Args:
            opacity: 透明度值 (0.0-1.0)
        """
        try:
            self.opacity_value = max(0.0, min(1.0, opacity))
            self.setWindowOpacity(self.opacity_value)
            self.update()  # 重绘背景
            self.save_config()

        except Exception as e:
            self.logger.error(f"设置透明度失败: {e}")

    def set_border_radius(self, radius: int) -> None:
        """
        设置圆角半径

        Args:
            radius: 圆角半径
        """
        try:
            self.border_radius = max(0, min(50, radius))
            self.update()  # 重绘
            self.save_config()

        except Exception as e:
            self.logger.error(f"设置圆角半径失败: {e}")

    def set_mouse_transparent(self, transparent: bool) -> None:
        """
        设置鼠标穿透状态

        Args:
            transparent: 是否启用鼠标穿透
        """
        try:
            self.mouse_transparent = transparent

            # 重新设置窗口标志
            window_flags = (
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )

            if self.mouse_transparent:
                window_flags |= Qt.WindowType.WindowTransparentForInput

            self.setWindowFlags(window_flags)
            self.show()  # 重新显示以应用新标志

            self.save_config()
            self.logger.debug(f"鼠标穿透设置为: {transparent}")

        except Exception as e:
            self.logger.error(f"设置鼠标穿透失败: {e}")

    def set_fixed_position(self, fixed: bool) -> None:
        """
        设置固定位置模式

        Args:
            fixed: 是否固定位置
        """
        try:
            self.fixed_position = fixed
            if fixed:
                # 固定到屏幕顶部中央
                self.center_on_screen()
            self.save_config()

        except Exception as e:
            self.logger.error(f"设置固定位置失败: {e}")

    def add_module(self, module_id: str, module: FloatingModule) -> None:
        """
        添加模块

        Args:
            module_id: 模块ID
            module: 模块实例
        """
        try:
            if module_id not in self.modules:
                # 连接信号
                module.content_updated.connect(self.on_module_content_updated)
                module.error_occurred.connect(self.on_module_error)

                self.modules[module_id] = module

                # 更新启用模块列表
                if module.enabled and module_id not in self.enabled_modules:
                    self.enabled_modules.append(module_id)
                    self.module_order.append(module_id)

                # 启动模块
                module.start_updates()

                self.logger.info(f"模块 {module_id} 添加成功")

        except Exception as e:
            self.logger.error(f"添加模块失败: {e}")

    def remove_module(self, module_id: str) -> None:
        """
        移除模块

        Args:
            module_id: 模块ID
        """
        try:
            if module_id in self.modules:
                module = self.modules[module_id]
                module.cleanup()
                del self.modules[module_id]

                # 更新列表
                if module_id in self.enabled_modules:
                    self.enabled_modules.remove(module_id)
                if module_id in self.module_order:
                    self.module_order.remove(module_id)

                self.logger.info(f"模块 {module_id} 移除成功")

        except Exception as e:
            self.logger.error(f"移除模块失败: {e}")

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            self.update_timer.stop()

            # 清理模块
            for module in self.modules.values():
                module.cleanup()
            self.modules.clear()

            # 清理动画
            if self.animations:
                self.animations.cleanup()

            # 保存配置
            self.save_config()

            self.logger.info("智能浮窗清理完成")

        except Exception as e:
            self.logger.error(f"清理失败: {e}")
