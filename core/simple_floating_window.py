"""
简单悬浮窗实现 - 使用QWidget
"""

import logging
import time
from datetime import datetime
from typing import Optional
from PySide6.QtCore import QObject, Signal, QTimer, Qt, QPoint
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont


class SimpleFloatingWindow(QWidget):
    """简单悬浮窗"""
    
    # 信号定义
    visibility_changed = Signal(bool)
    position_changed = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.SimpleFloatingWindow')
        
        # 窗口属性 - 增强置顶效果
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint  # Linux下绕过窗口管理器
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # 显示时不激活
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)  # 始终显示工具提示
        
        # 窗口大小和位置
        self.setFixedSize(450, 70)
        self._position_window()
        
        # 拖拽相关
        self.dragging = False
        self.drag_position = QPoint()
        
        # 数据
        self.current_time = ""
        self.next_class = "暂无课程"
        self.weather_info = "25°C"

        # 设置属性
        self.settings = {
            'auto_hide': True,
            'always_on_top': True,
            'transparent': False,
            'show_time': True,
            'show_course': True,
            'show_weather': True,
            'show_tasks': False,
            'opacity': 0.9,
            'font_size': 12,
            'theme': 'auto'
        }

        # 初始化UI
        self._init_ui()
        
        # 定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_time)
        self.update_timer.start(1000)  # 每秒更新
        
        # 强制置顶定时器
        self.always_on_top_timer = QTimer()
        self.always_on_top_timer.timeout.connect(self._ensure_always_on_top)
        self.always_on_top_timer.start(5000)  # 每5秒检查一次置顶状态

        self.logger.info("简单悬浮窗初始化完成")
        
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(20)
        
        # 时间模块
        time_layout = QVBoxLayout()
        time_layout.setSpacing(2)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                background: transparent;
            }
        """)
        
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.date_label)
        
        # 课程模块
        course_layout = QVBoxLayout()
        course_layout.setSpacing(2)
        
        self.course_label = QLabel(self.next_class)
        self.course_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        self.course_desc_label = QLabel("下节课程")
        self.course_desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                background: transparent;
            }
        """)
        
        course_layout.addWidget(self.course_label)
        course_layout.addWidget(self.course_desc_label)
        
        # 天气模块
        weather_layout = QVBoxLayout()
        weather_layout.setSpacing(2)
        
        self.weather_label = QLabel(self.weather_info)
        self.weather_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        self.weather_desc_label = QLabel("天气")
        self.weather_desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
                background: transparent;
            }
        """)
        
        weather_layout.addWidget(self.weather_label)
        weather_layout.addWidget(self.weather_desc_label)
        
        # 添加到主布局
        main_layout.addLayout(time_layout)
        main_layout.addStretch()
        main_layout.addLayout(course_layout)
        main_layout.addStretch()
        main_layout.addLayout(weather_layout)
        
        self.setLayout(main_layout)
        
        # 更新时间
        self._update_time()
        
    def _position_window(self):
        """定位窗口到屏幕右上角"""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.width() - self.width() - 20
            y = 20
            self.move(x, y)
            
    def _update_time(self):
        """更新时间显示"""
        now = datetime.now()
        self.current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        
        self.time_label.setText(self.current_time)
        self.date_label.setText(current_date)
        
    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形背景
        rect = self.rect()
        painter.setBrush(QBrush(QColor(45, 45, 45, 230)))  # 半透明深色背景
        painter.setPen(QPen(QColor(64, 64, 64), 1))
        painter.drawRoundedRect(rect, 35, 35)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            self.position_changed.emit(new_pos.x(), new_pos.y())
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
            
    def mouseDoubleClickEvent(self, event):
        """双击事件 - 切换主题"""
        if event.button() == Qt.MouseButton.LeftButton:
            # TODO: 实现主题切换
            self.logger.info("双击切换主题")
            event.accept()
            
    def contextMenuEvent(self, event):
        """右键菜单事件"""
        # TODO: 实现右键菜单
        self.logger.info("显示右键菜单")
        event.accept()
        
    def show_with_animation(self):
        """显示动画"""
        self.show()
        self.force_to_top()  # 显示时立即强制置顶
        self.visibility_changed.emit(True)
        self.logger.info("悬浮窗已显示")
        
    def hide_with_animation(self):
        """隐藏动画"""
        self.hide()
        self.visibility_changed.emit(False)
        self.logger.info("悬浮窗已隐藏")
        
    def update_next_class(self, class_name: str):
        """更新下节课程"""
        self.next_class = class_name
        self.course_label.setText(class_name)
        
    def update_weather(self, weather: str):
        """更新天气信息"""
        self.weather_info = weather
        self.weather_label.setText(weather)

    def _ensure_always_on_top(self):
        """确保窗口始终置顶"""
        try:
            if self.isVisible():
                # 重新设置窗口标志以确保置顶
                current_flags = self.windowFlags()
                if not (current_flags & Qt.WindowType.WindowStaysOnTopHint):
                    self.setWindowFlags(
                        Qt.WindowType.WindowStaysOnTopHint |
                        Qt.WindowType.FramelessWindowHint |
                        Qt.WindowType.Tool |
                        Qt.WindowType.X11BypassWindowManagerHint
                    )
                    self.show()  # 重新显示以应用新标志

                # 强制提升窗口到最前面
                self.raise_()
                self.activateWindow()

                # 在Linux下额外的置顶处理
                import platform
                if platform.system() == "Linux":
                    try:
                        # 尝试使用X11方法强制置顶
                        import subprocess
                        window_id = str(int(self.winId()))
                        subprocess.run(['wmctrl', '-i', '-r', window_id, '-b', 'add,above'],
                                     capture_output=True, check=False)
                    except (ImportError, FileNotFoundError, subprocess.SubprocessError):
                        # wmctrl不可用时的备用方法
                        pass

        except Exception as e:
            self.logger.warning(f"强制置顶失败: {e}")

    def force_to_top(self):
        """立即强制置顶"""
        self._ensure_always_on_top()

    def is_on_top(self):
        """检测窗口是否在最顶层（优化版本，带缓存）"""
        try:
            if not self.window or not self.window.isVisible():
                return False

            # 使用缓存减少系统调用
            current_time = time.time()
            if (hasattr(self, '_top_status_cache') and
                hasattr(self, '_top_status_cache_time') and
                current_time - self._top_status_cache_time < 0.5):  # 500ms缓存
                return self._top_status_cache

            # 检查窗口标志是否包含AlwaysOnTop
            flags = self.window.flags()
            is_top = bool(flags & Qt.WindowType.WindowStaysOnTopHint)

            # 更新缓存
            self._top_status_cache = is_top
            self._top_status_cache_time = current_time

            return is_top
        except Exception as e:
            self.logger.warning(f"检测置顶状态失败: {e}")
            return False

    def cleanup(self):
        """清理资源"""
        if self.update_timer:
            self.update_timer.stop()
        if self.always_on_top_timer:
            self.always_on_top_timer.stop()
        self.logger.info("简单悬浮窗已清理")

    # 设置方法
    def set_auto_hide(self, auto_hide: bool):
        """设置自动隐藏"""
        self.settings['auto_hide'] = auto_hide
        self.logger.info(f"自动隐藏设置为: {auto_hide}")

    def set_always_on_top(self, always_on_top: bool):
        """设置始终置顶"""
        self.settings['always_on_top'] = always_on_top
        if always_on_top:
            self.force_to_top()
        self.logger.info(f"始终置顶设置为: {always_on_top}")

    def set_transparent(self, transparent: bool):
        """设置透明背景"""
        self.settings['transparent'] = transparent
        if transparent:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        else:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.update()
        self.logger.info(f"透明背景设置为: {transparent}")

    def set_position(self, x: int, y: int):
        """设置位置"""
        self.move(x, y)
        self.position_changed.emit(x, y)
        self.logger.info(f"位置设置为: ({x}, {y})")

    def set_position_preset(self, preset: str) -> bool:
        """设置预设位置"""
        try:
            screen = QApplication.primaryScreen().geometry()
            window_size = self.size()

            if preset == "topLeft":
                x, y = 50, 50
            elif preset == "topRight":
                x, y = screen.width() - window_size.width() - 50, 50
            elif preset == "bottomLeft":
                x, y = 50, screen.height() - window_size.height() - 100
            elif preset == "bottomRight":
                x, y = screen.width() - window_size.width() - 50, screen.height() - window_size.height() - 100
            elif preset == "center":
                x = (screen.width() - window_size.width()) // 2
                y = (screen.height() - window_size.height()) // 2
            else:
                return False

            self.set_position(x, y)
            return True
        except Exception as e:
            self.logger.error(f"设置预设位置失败: {e}")
            return False

    def reset_position(self) -> bool:
        """重置位置到默认"""
        try:
            self._position_window()
            return True
        except Exception as e:
            self.logger.error(f"重置位置失败: {e}")
            return False

    def get_position(self) -> tuple:
        """获取当前位置"""
        pos = self.pos()
        return (pos.x(), pos.y())

    def set_show_time(self, show_time: bool):
        """设置显示时间"""
        self.settings['show_time'] = show_time
        self._update_display()
        self.logger.info(f"显示时间设置为: {show_time}")

    def set_show_course(self, show_course: bool):
        """设置显示课程"""
        self.settings['show_course'] = show_course
        self._update_display()
        self.logger.info(f"显示课程设置为: {show_course}")

    def set_show_weather(self, show_weather: bool):
        """设置显示天气"""
        self.settings['show_weather'] = show_weather
        self._update_display()
        self.logger.info(f"显示天气设置为: {show_weather}")

    def set_show_tasks(self, show_tasks: bool):
        """设置显示任务"""
        self.settings['show_tasks'] = show_tasks
        self._update_display()
        self.logger.info(f"显示任务设置为: {show_tasks}")

    def set_opacity(self, opacity: float):
        """设置透明度"""
        self.settings['opacity'] = opacity
        self.setWindowOpacity(opacity)
        self.logger.info(f"透明度设置为: {opacity}")

    def set_font_size(self, font_size: int):
        """设置字体大小"""
        self.settings['font_size'] = font_size
        # 通过主题应用字体大小
        self._apply_theme()
        self.logger.info(f"字体大小设置为: {font_size}")

    def set_theme(self, theme: str):
        """设置主题"""
        self.settings['theme'] = theme
        self._update_display()
        self.logger.info(f"主题设置为: {theme}")

    def get_settings(self) -> dict:
        """获取当前设置"""
        return self.settings.copy()

    def _update_display(self):
        """更新显示内容"""
        try:
            # 根据设置更新显示内容
            if hasattr(self, 'time_label'):
                self.time_label.setVisible(self.settings['show_time'])
            if hasattr(self, 'course_label'):
                self.course_label.setVisible(self.settings['show_course'])
            if hasattr(self, 'weather_label'):
                self.weather_label.setVisible(self.settings['show_weather'])

            # 更新样式（主题已经包含字体设置）
            self._apply_theme()
            self.update()
        except Exception as e:
            self.logger.error(f"更新显示失败: {e}")

    def _apply_theme(self):
        """应用主题"""
        try:
            theme = self.settings['theme']
            if theme == 'dark':
                text_color = "#ffffff"
                desc_color = "#cccccc"
            elif theme == 'light':
                text_color = "#000000"
                desc_color = "#666666"
            else:  # auto
                # 根据系统主题自动选择
                text_color = "#ffffff"
                desc_color = "#cccccc"

            # 应用完整样式（包含字体大小和颜色）
            font_size = self.settings['font_size']

            if hasattr(self, 'time_label'):
                self.time_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: {font_size + 6}px;
                        font-weight: bold;
                        background: transparent;
                    }}
                """)

            if hasattr(self, 'course_label'):
                self.course_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: {font_size + 2}px;
                        font-weight: bold;
                        background: transparent;
                    }}
                """)

            if hasattr(self, 'weather_label'):
                self.weather_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: {font_size + 2}px;
                        font-weight: bold;
                        background: transparent;
                    }}
                """)

            # 更新描述标签
            if hasattr(self, 'date_label'):
                self.date_label.setStyleSheet(f"""
                    QLabel {{
                        color: {desc_color};
                        font-size: {font_size}px;
                        background: transparent;
                    }}
                """)

            if hasattr(self, 'course_desc_label'):
                self.course_desc_label.setStyleSheet(f"""
                    QLabel {{
                        color: {desc_color};
                        font-size: {font_size - 1}px;
                        background: transparent;
                    }}
                """)

            if hasattr(self, 'weather_desc_label'):
                self.weather_desc_label.setStyleSheet(f"""
                    QLabel {{
                        color: {desc_color};
                        font-size: {font_size - 1}px;
                        background: transparent;
                    }}
                """)

        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")


class SimpleFloatingWindowManager(QObject):
    """简单悬浮窗管理器"""
    
    # 信号定义
    visibility_changed = Signal(bool)
    position_changed = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.SimpleFloatingWindowManager')
        
        # 悬浮窗实例
        self.floating_window: Optional[SimpleFloatingWindow] = None
        self.is_visible = False
        
    def create_floating_window(self) -> bool:
        """创建悬浮窗"""
        try:
            if self.floating_window is not None:
                return True
                
            self.floating_window = SimpleFloatingWindow()
            
            # 连接信号
            self.floating_window.visibility_changed.connect(self._on_visibility_changed)
            self.floating_window.position_changed.connect(self._on_position_changed)
            
            self.logger.info("简单悬浮窗创建成功")
            return True
            
        except Exception as e:
            self.logger.error(f"创建简单悬浮窗失败: {e}")
            return False
            
    def show_floating_window(self):
        """显示悬浮窗"""
        if not self.floating_window:
            if not self.create_floating_window():
                return
                
        self.floating_window.show_with_animation()
        self.is_visible = True
        
    def hide_floating_window(self):
        """隐藏悬浮窗"""
        if self.floating_window and self.is_visible:
            self.floating_window.hide_with_animation()
            self.is_visible = False
            
    def toggle_floating_window(self):
        """切换悬浮窗显示状态"""
        if self.is_visible:
            self.hide_floating_window()
        else:
            self.show_floating_window()
            
    def is_window_visible(self) -> bool:
        """检查悬浮窗是否可见"""
        return self.is_visible
        
    def _on_visibility_changed(self, visible: bool):
        """悬浮窗可见性变化"""
        self.is_visible = visible
        self.visibility_changed.emit(visible)
        
    def _on_position_changed(self, x: int, y: int):
        """悬浮窗位置变化"""
        self.position_changed.emit(x, y)
        
    def cleanup(self):
        """清理资源"""
        if self.floating_window:
            self.floating_window.cleanup()
            self.floating_window.deleteLater()
            self.floating_window = None
            
        self.is_visible = False
        self.logger.info("简单悬浮窗管理器已清理")

    # 设置方法代理
    def set_auto_hide(self, auto_hide: bool):
        """设置自动隐藏"""
        if self.floating_window:
            self.floating_window.set_auto_hide(auto_hide)

    def set_always_on_top(self, always_on_top: bool):
        """设置始终置顶"""
        if self.floating_window:
            self.floating_window.set_always_on_top(always_on_top)

    def set_transparent(self, transparent: bool):
        """设置透明背景"""
        if self.floating_window:
            self.floating_window.set_transparent(transparent)

    def set_position(self, x: int, y: int):
        """设置位置"""
        if self.floating_window:
            self.floating_window.set_position(x, y)

    def set_position_preset(self, preset: str) -> bool:
        """设置预设位置"""
        if self.floating_window:
            return self.floating_window.set_position_preset(preset)
        return False

    def reset_position(self) -> bool:
        """重置位置"""
        if self.floating_window:
            return self.floating_window.reset_position()
        return False

    def get_position(self) -> tuple:
        """获取位置"""
        if self.floating_window:
            return self.floating_window.get_position()
        return (0, 0)

    def set_show_time(self, show_time: bool):
        """设置显示时间"""
        if self.floating_window:
            self.floating_window.set_show_time(show_time)

    def set_show_course(self, show_course: bool):
        """设置显示课程"""
        if self.floating_window:
            self.floating_window.set_show_course(show_course)

    def set_show_weather(self, show_weather: bool):
        """设置显示天气"""
        if self.floating_window:
            self.floating_window.set_show_weather(show_weather)

    def set_show_tasks(self, show_tasks: bool):
        """设置显示任务"""
        if self.floating_window:
            self.floating_window.set_show_tasks(show_tasks)

    def set_opacity(self, opacity: float):
        """设置透明度"""
        if self.floating_window:
            self.floating_window.set_opacity(opacity)

    def set_font_size(self, font_size: int):
        """设置字体大小"""
        if self.floating_window:
            self.floating_window.set_font_size(font_size)

    def set_theme(self, theme: str):
        """设置主题"""
        if self.floating_window:
            self.floating_window.set_theme(theme)

    def get_settings(self) -> dict:
        """获取设置"""
        if self.floating_window:
            return self.floating_window.get_settings()
        return {}
