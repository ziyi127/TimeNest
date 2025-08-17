#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
悬浮窗组件
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
import platform

if TYPE_CHECKING:
    from frontend.main import TimeNestFrontendApp

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QMenu, QFrame
)
from PySide6.QtCore import QEvent, Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QCursor, QAction, QMouseEvent, QGuiApplication


# Windows平台特定导入 - 延迟导入以提高启动速度
WINDOWS_API_AVAILABLE = False
if platform.system() == "Windows":
    try:
        import ctypes
        
        # Windows API常量
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        LWA_ALPHA = 0x2
        
        # Windows API函数
        try:
            GetWindowLong = ctypes.windll.user32.GetWindowLongPtrW  # type: ignore
            SetWindowLong = ctypes.windll.user32.SetWindowLongPtrW  # type: ignore
        except AttributeError:
            GetWindowLong = ctypes.windll.user32.GetWindowLongW  # type: ignore
            SetWindowLong = ctypes.windll.user32.SetWindowLongW  # type: ignore
        
        SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes  # type: ignore
        SetWindowPos = ctypes.windll.user32.SetWindowPos  # type: ignore
        
        # Windows常量
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        
        WINDOWS_API_AVAILABLE = True
    except Exception as e:
        print(f"Windows API导入失败: {e}")


# 悬浮窗类
class FloatingWindow(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        # 添加编辑模式标志
        self.edit_mode = False
        # 缓存今日课程表数据
        self.cached_schedule = None  # type: ignore
        # 上次更新时间
        self.last_update_time = None
        # 动态更新频率（秒）
        self.update_frequency = 60
        # 定时器确保窗口始终保持在最前面
        self.topmost_timer = QTimer(self)
        self.topmost_timer.timeout.connect(self.ensure_topmost)
        self.topmost_timer.start(1000)  # 每秒检查一次
        self.initUI()
        # 确保非编辑模式下启用触控穿透
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """鼠标双击事件，显示管理窗口"""
        # 只在编辑模式下响应双击事件
        if self.edit_mode:
            self.app.tray_icon.show_management_window()
        event.accept()

    def initUI(self):
        # 根据不同平台设置窗口样式
        if platform.system() == "Windows":
            # Windows平台使用增强的窗口标志
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.WindowTransparentForInput |
                Qt.Tool |
                Qt.WindowDoesNotAcceptFocus |
                Qt.NoDropShadowWindowHint
            )  # type: ignore
        elif platform.system() == "Darwin":  # macOS
            # macOS平台使用特定的窗口标志
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.WindowTransparentForInput |
                Qt.Tool |
                Qt.WindowDoesNotAcceptFocus |
                Qt.X11BypassWindowManagerHint  # 绕过窗口管理器以获得更高权限
            )  # type: ignore
        else:  # Linux和其他平台
            # Linux平台使用特定的窗口标志
            window_flags = (
                Qt.FramelessWindowHint | 
                Qt.WindowStaysOnTopHint | 
                Qt.WindowTransparentForInput | 
                Qt.Tool | 
                Qt.WindowDoesNotAcceptFocus
            )
            
            # 在sudo环境下添加特殊处理
            if os.geteuid() == 0 and sys.platform.startswith('linux'):
                # 在sudo环境下，可能需要特殊的窗口管理器绕过设置
                try:
                    # 尝试添加X11绕过标志
                    window_flags |= Qt.X11BypassWindowManagerHint
                except:
                    # 如果不支持该标志，则忽略
                    pass
            else:
                # 非sudo环境下正常添加绕过标志
                window_flags |= Qt.X11BypassWindowManagerHint
                
            self.setWindowFlags(window_flags)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 设置触控穿透属性（在初始化完成后会在__init__中再次设置）
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # 窗口大小和位置 - 调整为屏幕中上部
        window_width = 300
        window_height = 120
        
        # 获取窗口位置设置，如果不存在则使用默认值
        window_position: dict[str, int] = self.app.settings.get("window_position", {"x": 100, "y": 100})  # type: ignore
        
        # 设置窗口位置和大小
        self.setGeometry(
            window_position["x"],  # type: ignore
            window_position["y"],  # type: ignore
            window_width,
            window_height
        )

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # 创建背景框架
        self.background_frame = QFrame(self)
        self.background_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 1px solid rgba(200, 200, 200, 0.5);
            }
        """)
        self.background_frame.setMinimumSize(280, 100)
        background_layout = QVBoxLayout(self.background_frame)
        background_layout.setContentsMargins(15, 15, 15, 15)
        background_layout.setSpacing(8)

        # 时间标签
        self.time_label = QLabel("", self)
        self.time_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("QLabel { color: #333333; }")
        background_layout.addWidget(self.time_label)

        # 课程状态标签
        # 先创建标签对象
        self.status_label = QLabel("今日无课程", self)
        self.status_label.setFont(QFont("Microsoft YaHei", 13))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("QLabel { color: #666666; }")
        background_layout.addWidget(self.status_label)



        main_layout.addWidget(self.background_frame)

        # 设置透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(1000)
        # 动画起始值将在启动时动态设置
        self.opacity_animation.setEndValue(0.0)
        
        # 设置初始透明度
        transparency: int = self.app.settings.get("floating_window", {}).get("transparency", 80)  # type: ignore
        self.setWindowOpacity(transparency / 100.0)

        # 自动隐藏计时器
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)
        # 设置自动隐藏时间
        auto_hide_threshold: int = self.app.settings.get("floating_window", {}).get("auto_hide_threshold", 50)  # type: ignore
        self.auto_hide_timeout = auto_hide_threshold * 100  # 转换为毫秒

        # 数据更新计时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        # 设置初始更新频率
        self.update_timer.start(self.update_frequency * 1000)

        # 更新时间和状态
        self.update_time()
        # 不再在初始化时调用update_status，而是使用缓存的默认值
        # self.update_status()

        # 启动时间更新计时器
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # 使用QTimer.singleShot将首次数据更新推迟到事件循环开始后执行
        QTimer.singleShot(100, self.update_data)

    def update_time(self):
        """更新时间显示"""
        now = datetime.now()
        time_str = now.strftime("%H:%M %a %d/%m/%y")
        # 替换星期为中文
        # weekday()返回0-6代表周一到周日，需要调整索引
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday_zh = weekdays[now.weekday()]
        time_str = time_str.replace(now.strftime("%a"), weekday_zh)
        self.time_label.setText(time_str)

    def update_status(self):
        """更新课程状态显示"""
        # 使用缓存的数据更新界面，避免频繁API调用
        schedule: dict = self.cached_schedule if self.cached_schedule is not None else self.app.get_today_schedule()  # type: ignore
        
        if schedule["type"] == "none":
            self.status_label.setText("今日无课程")
            self.status_label.setStyleSheet("color: #666666;")
        elif schedule["type"] == "regular":
            course = schedule["course"]
            self.status_label.setText(f"{course['name']} ({course['teacher']}) {course['location']}")
            self.status_label.setStyleSheet("color: #000000;")
        elif schedule["type"] == "temp":
            course = schedule["course"]
            self.status_label.setText(f"【临时】{course['name']} ({course['teacher']}) {course['location']}")
            
            # 根据设置决定临时课程样式
            temp_course_style: str = self.app.settings.get("floating_window", {}).get("temp_course_style", "临时调课标红边框")  # type: ignore
            if temp_course_style == "临时调课标红边框":
                self.status_label.setStyleSheet("color: #FF5722;")
            elif temp_course_style == "临时调课闪烁提醒":
                # TODO: 实现闪烁提醒效果
                self.status_label.setStyleSheet("color: #FF5722;")
            elif temp_course_style == "临时调课标红边框+闪烁提醒":
                # TODO: 实现闪烁提醒效果
                self.status_label.setStyleSheet("color: #FF5722;")

    def update_data(self):
        """更新数据"""
        # 根据动态频率更新数据
        from datetime import datetime, timedelta
        
        # 检查是否需要更新数据
        should_update = (
            self.last_update_time is None or 
            datetime.now() - self.last_update_time > timedelta(seconds=self.update_frequency)
        )
        
        if should_update:
            self.app.load_data()
            self.last_update_time = datetime.now()
        
        # 更新缓存的今日课程表数据
        self.cached_schedule: dict = self.app.get_today_schedule()  # type: ignore
        self.update_status()
        
        # 调整更新频率
        self.adjust_update_frequency()
    
    def adjust_update_frequency(self):
        """根据系统负载和数据变化情况动态调整更新频率"""
        # TODO: 实现动态调整更新频率的逻辑
        # 这里可以根据系统负载、数据变化频率等因素来调整更新频率
        # 暂时保持固定频率
        pass
    
    def partial_update(self, data_type: str):
        """局部更新特定类型的数据"""
        try:
            if data_type == "status":
                self.update_status()
            elif data_type == "time":
                self.update_time()
        except Exception as e:
            print(f"局部更新{data_type}时出错: {e}")

    def ensure_topmost(self):
        """确保窗口始终保持在最前面"""
        if self.isVisible() and not self.edit_mode:
            # 在不同平台上使用不同的方法确保窗口置顶
            if platform.system() == "Windows" and WINDOWS_API_AVAILABLE:
                self.ensure_topmost_windows()
            else:
                # 对于其他平台，使用Qt原生方法
                self.raise_()
                self.show()
                # 确保窗口标志正确
                current_flags = self.windowFlags()
                if not (current_flags & Qt.WindowStaysOnTopHint):
                    self.setWindowFlags(current_flags | Qt.WindowStaysOnTopHint)  # type: ignore
                    self.show()

    def ensure_topmost_windows(self):
        """Windows平台下确保窗口置顶的特殊处理"""
        if platform.system() != "Windows" or not WINDOWS_API_AVAILABLE:
            return
            
        try:
            # 使用Windows API确保窗口置顶
            hwnd = self.winId()
            SetWindowPos(
                int(hwnd),
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except Exception:
            # 如果Windows API调用失败，回退到Qt原生方法
            self.raise_()
            self.show()

    def start_fade_out(self):
        """开始淡出动画并隐藏窗口"""
        # 只在非编辑模式下执行淡出动画
        if not self.edit_mode:
            # 动态设置动画起始值为当前透明度
            self.opacity_animation.setStartValue(self.windowOpacity())
            self.opacity_animation.setDuration(300)  # 缩短动画时间
            self.opacity_animation.setEasingCurve(QEasingCurve.Type.Linear)  # 使用线性动画曲线
            self.opacity_animation.finished.connect(self.hide)
            self.opacity_animation.start()
        
    def show(self):
        """show方法，确保在显示时更新托盘菜单项文本"""
        # 在sudo环境下尝试修复显示问题
        if os.geteuid() == 0 and sys.platform.startswith('linux'):
            try:
                # 确保有正确的显示环境
                current_flags = self.windowFlags()
                self.setWindowFlags(current_flags)
            except:
                pass
        
        super().show()
        # 确保显示时窗口在最前面
        self.raise_()
        # 更新托盘菜单项文本
        if hasattr(self.app, 'tray_icon') and hasattr(self.app.tray_icon, 'update_toggle_action_text'):
            self.app.tray_icon.update_toggle_action_text()
    
    def hide(self):
        """hide方法，确保在隐藏时更新托盘菜单项文本"""
        super().hide()
        # 更新托盘菜单项文本
        if hasattr(self.app, 'tray_icon') and hasattr(self.app.tray_icon, 'update_toggle_action_text'):
            self.app.tray_icon.update_toggle_action_text()

    def fade_to_transparent(self):
        """淡出到透明但不隐藏"""
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.setEndValue(0.0)
        # 断开可能的隐藏连接
        try:
            self.opacity_animation.finished.disconnect(self.hide)
        except TypeError:
            pass  # 如果没有连接则忽略
        self.opacity_animation.start()

    def stop_fade_out(self):
        """停止淡出动画并恢复透明度"""
        self.opacity_animation.stop()
        self.setWindowOpacity(0.8)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件，开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton and self.edit_mode:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.stop_fade_out()
            # 用户交互后，重置自动隐藏计时器
            self.hide_timer.stop()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton and self.edit_mode:
            self.show_menu()
            # 用户交互后，重置自动隐藏计时器
            self.hide_timer.stop()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件，处理拖动"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.edit_mode:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件，结束拖动"""
        if event.button() == Qt.MouseButton.LeftButton and self.edit_mode:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
            # 根据设置决定是否吸附到边缘
            snap_to_edge: bool = self.app.settings.get("floating_window", {}).get("snap_to_edge", False)  # type: ignore
            if snap_to_edge:
                self.snap_to_edge()
            
            # 保存窗口位置
            self.app.settings["window_position"] = {
                "x": self.x(),
                "y": self.y()
            }
            self.app.save_data()
            event.accept()

    def enterEvent(self, event: QEvent):
        """鼠标进入事件"""
        if not self.edit_mode:
            # 在非编辑模式下，降低透明度但不消失
            self.setWindowOpacity(0.4)
        else:
            # 在编辑模式下，重置透明度并停止淡出动画
            self.stop_fade_out()
        event.accept()

    def leaveEvent(self, event: QEvent):
        """鼠标离开事件"""
        if not self.edit_mode:
            # 在非编辑模式下，恢复透明度
            self.setWindowOpacity(0.8)
        else:
            # 在编辑模式下，不启动自动隐藏计时器，保持窗口显示
            pass
        event.accept()

    def show_menu(self):
        """显示右键菜单"""
        menu = QMenu(self)
        manage_action = QAction("课表管理", self)
        manage_action.triggered.connect(self.app.tray_icon.show_management_window)
        temp_change_action = QAction("临时调课", self)
        temp_change_action.triggered.connect(self.app.tray_icon.show_temp_change_window)
        edit_mode_action = QAction("编辑模式", self)
        edit_mode_action.setCheckable(True)
        edit_mode_action.setChecked(self.app.tray_icon.edit_mode)
        edit_mode_action.triggered.connect(self.app.tray_icon.toggle_edit_mode)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.app.quit)
        menu.addAction(manage_action)
        menu.addAction(temp_change_action)
        menu.addAction(edit_mode_action)
        menu.addAction(exit_action)
        menu.exec(QCursor.pos())

    def set_edit_mode(self, enabled: bool):
        """设置编辑模式"""
        self.edit_mode = enabled
        if enabled:
            # 编辑模式下，禁用触控穿透，恢复透明度
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.setWindowOpacity(0.8)
            # 确保窗口标志正确设置以支持拖动，添加Qt.Tool避免在任务栏显示图标
            if platform.system() == "Windows":
                self.setWindowFlags(
                    Qt.FramelessWindowHint |
                    Qt.WindowStaysOnTopHint |
                    Qt.Tool
                )  # type: ignore
            elif platform.system() == "Darwin":  # macOS
                self.setWindowFlags(
                    Qt.FramelessWindowHint |
                    Qt.WindowStaysOnTopHint |
                    Qt.Tool
                )  # type: ignore
            else:  # Linux和其他平台
                window_flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
                # 在sudo环境下添加特殊处理
                if os.geteuid() == 0 and sys.platform.startswith('linux'):
                    try:
                        # 尝试添加X11绕过标志
                        window_flags |= Qt.X11BypassWindowManagerHint
                    except:
                        # 如果不支持该标志，则忽略
                        pass
                else:
                    window_flags |= Qt.X11BypassWindowManagerHint
                    
                self.setWindowFlags(window_flags)  # type: ignore
            self.show()
        else:
            # 非编辑模式下，启用触控穿透
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            # 恢复原始窗口标志，添加Qt.Tool避免在任务栏显示图标
            if platform.system() == "Windows":
                self.setWindowFlags(
                    Qt.FramelessWindowHint |
                    Qt.WindowStaysOnTopHint |
                    Qt.WindowTransparentForInput |
                    Qt.Tool |
                    Qt.WindowDoesNotAcceptFocus |
                    Qt.NoDropShadowWindowHint
                )  # type: ignore
            elif platform.system() == "Darwin":  # macOS
                self.setWindowFlags(
                    Qt.FramelessWindowHint |
                    Qt.WindowStaysOnTopHint |
                    Qt.WindowTransparentForInput |
                    Qt.Tool |
                    Qt.WindowDoesNotAcceptFocus |
                    Qt.X11BypassWindowManagerHint
                )  # type: ignore
            else:  # Linux和其他平台
                window_flags = (
                    Qt.FramelessWindowHint |
                    Qt.WindowStaysOnTopHint |
                    Qt.WindowTransparentForInput |
                    Qt.Tool |
                    Qt.WindowDoesNotAcceptFocus
                )
                
                # 在sudo环境下添加特殊处理
                if os.geteuid() == 0 and sys.platform.startswith('linux'):
                    try:
                        # 尝试添加X11绕过标志
                        window_flags |= Qt.X11BypassWindowManagerHint
                    except:
                        # 如果不支持该标志，则忽略
                        pass
                else:
                    window_flags |= Qt.X11BypassWindowManagerHint
                    
                self.setWindowFlags(window_flags)  # type: ignore
            self.show()
    
    def snap_to_edge(self):
        """吸附到屏幕边缘"""
        # 获取屏幕尺寸
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            
            # 获取窗口当前位置
            x = self.x()
            y = self.y()
            window_width = self.width()
            
            # 计算到各边缘的距离
            distance_to_left = x
            distance_to_right = screen_width - (x + window_width)
            distance_to_top = y
            
            # 根据设置的优先级决定吸附到哪条边
            snap_priority: str = self.app.settings.get("floating_window", {}).get("snap_priority", "右侧 > 顶部 > 左侧")  # type: ignore
            
            if snap_priority == "右侧 > 顶部 > 左侧":
                if distance_to_right <= min(distance_to_top, distance_to_left):
                    self.move(screen_width - window_width, y)
                elif distance_to_top <= distance_to_left:
                    self.move(x, 0)
                else:
                    self.move(0, y)
            elif snap_priority == "顶部 > 右侧 > 左侧":
                if distance_to_top <= min(distance_to_right, distance_to_left):
                    self.move(x, 0)
                elif distance_to_right <= distance_to_left:
                    self.move(screen_width - window_width, y)
                else:
                    self.move(0, y)
            elif snap_priority == "左侧 > 顶部 > 右侧":
                if distance_to_left <= min(distance_to_top, distance_to_right):
                    self.move(0, y)
                elif distance_to_top <= distance_to_right:
                    self.move(x, 0)
                else:
                    self.move(screen_width - window_width, y)