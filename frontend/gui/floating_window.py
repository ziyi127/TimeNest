#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
悬浮窗组件
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

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
from PySide6.QtCore import QEvent, Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QFont, QCursor, QAction, QMouseEvent, QGuiApplication


# 悬浮窗类
class FloatingWindow(QWidget):
    def __init__(self, app: 'TimeNestFrontendApp'):
        super().__init__()
        self.app = app
        # 添加编辑模式标志
        self.edit_mode = False
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
        # 设置窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 设置触控穿透属性（在初始化完成后会在__init__中再次设置）
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # 窗口大小和位置 - 调整为屏幕中上部
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = 300
        window_height = 120
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3  # 屏幕中上部

        # 获取窗口位置设置，如果不存在则使用默认值
        window_position = self.app.settings.get("window_position", {"x": 100, "y": 100})
        
        # 如果是首次启动（使用默认设置），则设置为屏幕中上部
        if (window_position["x"] == 100 and 
            window_position["y"] == 100):
            self.setGeometry(x, y, window_width, window_height)
            # 更新设置
            self.app.settings["window_position"] = {
                "x": x,
                "y": y
            }
            self.app.save_data()
        else:
            # 否则使用用户之前保存的位置
            self.setGeometry(
                window_position["x"],
                window_position["y"],
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
        transparency = self.app.settings.get("floating_window", {}).get("transparency", 80)
        self.setWindowOpacity(transparency / 100.0)

        # 自动隐藏计时器
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)
        # 设置自动隐藏时间
        auto_hide_threshold = self.app.settings.get("floating_window", {}).get("auto_hide_threshold", 50)
        self.auto_hide_timeout = auto_hide_threshold * 100  # 转换为毫秒

        # 数据更新计时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        update_interval = self.app.settings.get("update_interval", 1000)
        self.update_timer.start(update_interval)

        # 更新时间和状态
        self.update_time()
        self.update_status()

        # 启动时间更新计时器
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

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
        schedule = self.app.get_today_schedule()
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
            temp_course_style = self.app.settings.get("floating_window", {}).get("temp_course_style", "临时调课标红边框")
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
        self.app.load_data()
        self.update_status()
        pass

    def start_fade_out(self):
        """开始淡出动画并隐藏窗口"""
        # 动态设置动画起始值为当前透明度
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()
        
    def show(self):
        """重写show方法，确保在显示时更新托盘菜单项文本"""
        super().show()
        # 更新托盘菜单项文本
        if hasattr(self.app, 'tray_icon') and hasattr(self.app.tray_icon, 'update_toggle_action_text'):
            self.app.tray_icon.update_toggle_action_text()
    
    def hide(self):
        """重写hide方法，确保在隐藏时更新托盘菜单项文本"""
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
            snap_to_edge = self.app.settings.get("floating_window", {}).get("snap_to_edge", False)
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
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.show()
        else:
            # 非编辑模式下，启用触控穿透
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            # 恢复原始窗口标志，添加Qt.Tool避免在任务栏显示图标
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.Tool)
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
            snap_priority = self.app.settings.get("floating_window", {}).get("snap_priority", "右侧 > 顶部 > 左侧")
            
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