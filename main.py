#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表后端服务
"""

import sys
import os
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# 移除不存在的导入
from utils.enhanced_exception_handler import global_exception_handler

def setup_logging():
    """配置应用程序日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('TimeNest.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def get_app_data_path():
    """获取应用数据目录，按平台规范设置"""
    if sys.platform == "win32":
        # Windows: %APPDATA%\TimeNest\
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            return Path(appdata) / 'TimeNest'
        else:
            # 如果APPDATA环境变量不存在，使用用户目录下的.config
            return Path.home() / '.config' / 'TimeNest'
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/TimeNest/
        return Path.home() / 'Library' / 'Application Support' / 'TimeNest'
    else:
        # Linux和其他类Unix系统: ~/.config/TimeNest/
        config_home = os.environ.get('XDG_CONFIG_HOME', '')
        if config_home:
            return Path(config_home) / 'TimeNest'
        else:
            return Path.home() / '.config' / 'TimeNest'

import json
from datetime import datetime, timedelta
import random
import uuid

# 导入PySide6模块
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                            QHBoxLayout, QPushButton, QMenu,
                            QSystemTrayIcon, QMessageBox, QDialog, QFormLayout,
                            QLineEdit, QComboBox, QDateEdit, QTimeEdit,
                            QListWidget, QListWidgetItem, QTabWidget,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QFrame, QCheckBox)
from PySide6.QtCore import QDate, QEvent, Qt, QTimer, QPropertyAnimation, QGuiApplication
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QAction, QMouseEvent

# 设置中文字体支持
font = QFont()
font.setFamily("SimHei")

# 悬浮窗类
class FloatingWindow(QWidget):
    def __init__(self, app: 'TimeNestApp'):
        super().__init__()
        self.app = app
        self.initUI()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """鼠标双击事件，显示管理窗口"""
        self.app.tray_icon.show_management_window()
        event.accept()

    def initUI(self):
        # 设置窗口样式
        self.setWindowFlags(Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 窗口大小和位置 - 调整为屏幕中上部
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = 300
        window_height = 120
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3  # 屏幕中上部

        # 如果是首次启动（使用默认设置），则设置为屏幕中上部
        if (self.app.settings["window_position"]["x"] == 100 and 
            self.app.settings["window_position"]["y"] == 100):
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
                self.app.settings["window_position"]["x"],
                self.app.settings["window_position"]["y"],
                window_width,
                window_height
            )

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # 创建背景框架
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # 创建背景框架
        self.background_frame = QFrame(self)
        self.background_frame.setStyleSheet("QFrame {background-color: rgba(255, 255, 255, 0.8); border-radius: 10px;}")
        self.background_frame.setMinimumSize(280, 100)
        background_layout = QVBoxLayout(self.background_frame)
        background_layout.setContentsMargins(15, 15, 15, 15)
        background_layout.setSpacing(5)

        # 时间标签
        self.time_label = QLabel("", self)
        self.time_label.setFont(QFont("SimHei", 16, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        background_layout.addWidget(self.time_label)

        # 课程状态标签
        # 先创建标签对象
        self.status_label = QLabel("今日无课程", self)
        self.status_label.setFont(QFont("SimHei", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        background_layout.addWidget(self.status_label)

        # 天气标签
        self.weather_label = QLabel("小雨 25℃", self)
        self.weather_label.setFont(QFont("SimHei", 12))
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        background_layout.addWidget(self.weather_label)

        main_layout.addWidget(self.background_frame)

        # 设置透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(1000)
        self.opacity_animation.setStartValue(0.8)
        self.opacity_animation.setEndValue(0.0)

        # 自动隐藏计时器 - 增加时间到10秒，避免误操作
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)
        # 延长自动隐藏时间到10秒
        self.auto_hide_timeout = 10000  # 10秒

        # 数据更新计时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(self.app.settings["update_interval"])

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
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
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
            self.status_label.setStyleSheet("color: #FF5722;")

    def update_data(self):
        """更新数据"""
        self.app.load_data()
        self.update_status()
        # 随机更新天气（实际应用中应从API获取）
        weathers = ["晴", "多云", "小雨", "大雨", "雷暴"]
        temp = random.randint(20, 35)
        self.weather_label.setText(f"{random.choice(weathers)} {temp}℃")

    def start_fade_out(self):
        """开始淡出动画并隐藏窗口"""
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()

    def stop_fade_out(self):
        """停止淡出动画并恢复透明度"""
        self.opacity_animation.stop()
        self.setWindowOpacity(0.8)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件，开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.stop_fade_out()
            # 用户交互后，重置自动隐藏计时器
            self.hide_timer.stop()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_menu()
            # 用户交互后，重置自动隐藏计时器
            self.hide_timer.stop()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件，处理拖动"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件，结束拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            # 保存窗口位置
            self.app.settings["window_position"] = {
                "x": self.x(),
                "y": self.y()
            }
            self.app.save_data()
            event.accept()

    def enterEvent(self, event: QEvent):
        """鼠标进入事件，停止自动隐藏"""
        self.stop_fade_out()
        self.hide_timer.stop()
        event.accept()

    def leaveEvent(self, event: QEvent):
        """鼠标离开事件，启动自动隐藏计时器"""
        self.hide_timer.start(self.auto_hide_timeout)
        event.accept()

    def show_menu(self):
        """显示右键菜单"""
        menu = QMenu(self)
        manage_action = QAction("课表管理", self)
        manage_action.triggered.connect(self.app.tray_icon.show_management_window)
        temp_change_action = QAction("临时调课", self)
        temp_change_action.triggered.connect(self.app.tray_icon.show_temp_change_window)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.app.quit)
        menu.addAction(manage_action)
        menu.addAction(temp_change_action)
        menu.addAction(exit_action)
        menu.exec_(QCursor.pos())

# 系统托盘图标类


class SystemTrayIcon(QSystemTrayIcon):
    # 重写show方法以更新菜单文本
    def show(self):
        super().show()
        self.update_show_action_text()
    def __init__(self, app: 'TimeNestApp'):
        super().__init__(app)
        self.app = app

        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "logo.ico")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # 使用默认图标
            self.setIcon(self.style().standardIcon(QApplication.style().SP_ComputerIcon))

        # 设置提示文本
        self.setToolTip("TimeNest 课表软件")

        # 创建右键菜单
        self.create_menu()

        # 连接信号
        self.activated.connect(self.on_activated)

    def create_menu(self):
        """创建右键菜单"""
        menu = QMenu()

        # 显示/隐藏悬浮窗动作
        self.show_action = QAction("显示悬浮窗", self)
        self.show_action.triggered.connect(self.toggle_floating_window)
        # 更新动作文本
        self.update_show_action_text()

        # 课表管理动作
        manage_action = QAction("课表管理", self)
        manage_action.triggered.connect(self.show_management_window)

        # 临时调课动作
        temp_change_action = QAction("临时调课", self)
        temp_change_action.triggered.connect(self.show_temp_change_window)

        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.app.quit)

        # 添加动作到菜单
        menu.addAction(self.show_action)
        menu.addAction(manage_action)
        menu.addAction(temp_change_action)
        menu.addSeparator()
        menu.addAction(exit_action)

        self.setContextMenu(menu)

    def on_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.Trigger:
            # 左键点击，显示/隐藏悬浮窗
            self.toggle_floating_window()

    def toggle_floating_window(self):
        """切换悬浮窗显示/隐藏状态"""
        if self.app.floating_window.isVisible():
            self.app.floating_window.hide()
        else:
            self.app.floating_window.show()
            self.app.floating_window.raise_()
        # 更新动作文本
        self.update_show_action_text()

    def update_show_action_text(self):
        """根据悬浮窗状态更新动作文本"""
        if self.app.floating_window.isVisible():
            self.show_action.setText("关闭悬浮窗")
        else:
            self.show_action.setText("显示悬浮窗")

    def show_management_window(self):
        """显示课表管理窗口"""
        if not hasattr(self, 'management_window') or self.management_window.isHidden():
            self.management_window = ManagementWindow(self.app)
            self.management_window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
            self.management_window.setParent(None)
        self.management_window.show()
        self.management_window.raise_()

    def show_temp_change_window(self):
        """显示临时调课窗口"""
        if not hasattr(self, 'temp_change_window') or self.temp_change_window.isHidden():
            self.temp_change_window = TempChangeWindow(self.app)
            self.temp_change_window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
            self.temp_change_window.setParent(None)
        self.temp_change_window.show()
        self.temp_change_window.raise_()

# 应用程序主类
class TimeNestApp(QApplication):
    def __init__(self, args: list[str]):
        super().__init__(args)
        self.setApplicationName("TimeNest")
        self.setApplicationVersion("1.0.0")
        self.setStyle("Fusion")

        # 确保数据目录存在
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化数据
        self.load_data()
        
    def load_data(self):
        """加载课程、课程表和临时换课数据"""
        # 课程数据
        courses_file = os.path.join(self.data_dir, "courses.json")
        if os.path.exists(courses_file):
            with open(courses_file, 'r', encoding='utf-8') as f:
                self.courses = json.load(f)
        else:
            # 示例数据
            self.courses = [
                {
                    "id": "course1",
                    "name": "高等数学",
                    "teacher": "张教授",
                    "location": "教学楼A101",
                    "duration": {
                        "start_time": "08:00",
                        "end_time": "09:40"
                    }
                },
                {
                    "id": "course2",
                    "name": "大学物理",
                    "teacher": "李教授",
                    "location": "实验楼B202",
                    "duration": {
                        "start_time": "10:00",
                        "end_time": "11:40"
                    }
                },
                {
                    "id": "course3",
                    "name": "程序设计",
                    "teacher": "王老师",
                    "location": "计算机房C303",
                    "duration": {
                        "start_time": "14:00",
                        "end_time": "15:40"
                    }
                }
            ]
            # 保存示例数据
            with open(courses_file, 'w', encoding='utf-8') as f:
                json.dump(self.courses, f, ensure_ascii=False, indent=2)
        
        # 课程表数据
        schedules_file = os.path.join(self.data_dir, "schedules.json")
        if os.path.exists(schedules_file):
            with open(schedules_file, 'r', encoding='utf-8') as f:
                self.schedules = json.load(f)
        else:
            # 示例数据
            today = datetime.now().strftime("%Y-%m-%d")
            next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            self.schedules = [
                {
                    "id": "schedule1",
                    "day_of_week": 0,  # 0表示星期日
                    "week_parity": "both",
                    "course_id": "course1",
                    "valid_from": today,
                    "valid_to": next_week
                },
                {
                    "id": "schedule2",
                    "day_of_week": 2,  # 星期二
                    "week_parity": "both",
                    "course_id": "course2",
                    "valid_from": today,
                    "valid_to": next_week
                },
                {
                    "id": "schedule3",
                    "day_of_week": 4,  # 星期四
                    "week_parity": "both",
                    "course_id": "course3",
                    "valid_from": today,
                    "valid_to": next_week
                }
            ]
            # 保存示例数据
            with open(schedules_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, ensure_ascii=False, indent=2)
        
        # 临时换课数据
        temp_changes_file = os.path.join(self.data_dir, "temp_changes.json")
        if os.path.exists(temp_changes_file):
            with open(temp_changes_file, 'r', encoding='utf-8') as f:
                self.temp_changes = json.load(f)
        else:
            self.temp_changes = []
            with open(temp_changes_file, 'w', encoding='utf-8') as f:
                json.dump(self.temp_changes, f, ensure_ascii=False, indent=2)
        
        # 设置数据
        settings_file = os.path.join(self.data_dir, "settings.json")
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "window_position": {
                    "x": 100,
                    "y": 100
                },
                "auto_hide_timeout": 5000,
                "update_interval": 60000
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def save_data(self):
        """保存所有数据"""
        # 保存课程数据
        courses_file = os.path.join(self.data_dir, "courses.json")
        with open(courses_file, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)
        
        # 保存课程表数据
        schedules_file = os.path.join(self.data_dir, "schedules.json")
        with open(schedules_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=2)
        
        # 保存临时换课数据
        temp_changes_file = os.path.join(self.data_dir, "temp_changes.json")
        with open(temp_changes_file, 'w', encoding='utf-8') as f:
            json.dump(self.temp_changes, f, ensure_ascii=False, indent=2)
        
        # 保存设置
        settings_file = os.path.join(self.data_dir, "settings.json")
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def get_course_by_id(self, course_id: str):
        """根据ID获取课程"""
        for course in self.courses:
            if course["id"] == course_id:
                return course
        return None
    
    def get_today_schedule(self):
        """获取今天的课程表"""
        today = datetime.now()
        today_weekday = today.weekday()  # 0-6, 0表示星期一
        # 调整为0表示星期日
        today_weekday = (today_weekday + 1) % 7
        today_date = today.strftime("%Y-%m-%d")
        
        # 检查临时换课
        for temp_change in self.temp_changes:
            if temp_change["change_date"] == today_date and not temp_change["used"]:
                course = self.get_course_by_id(temp_change["new_course_id"])
                if course:
                    return {
                        "type": "temp",
                        "course": course,
                        "original_schedule_id": temp_change["original_schedule_id"]
                    }
        
        # 检查常规课程表
        for schedule in self.schedules:
            if (
                schedule["day_of_week"] == today_weekday and
                schedule["valid_from"] <= today_date <= schedule["valid_to"]
            ):
                # 检查周奇偶性
                week_number = today.isocalendar()[1]
                if (
                    schedule["week_parity"] == "both" or
                    (schedule["week_parity"] == "odd" and week_number % 2 == 1) or
                    (schedule["week_parity"] == "even" and week_number % 2 == 0)
                ):
                    course = self.get_course_by_id(schedule["course_id"])
                    if course:
                        return {
                            "type": "regular",
                            "course": course,
                            "schedule_id": schedule["id"]
                        }
        
        # 今天没有课程
        return {
            "type": "none"
        }

def main():
    """后端服务主入口点"""
    logger = setup_logging()
    
    try:
        # 创建应用数据目录
        app_data_path = get_app_data_path()
        app_data_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"应用数据目录: {app_data_path}")
        
        # 创建并运行后端服务
        logger.info("启动TimeNest后端服务")
        backend_service = TimeNestBackendService()
        
        # 这里可以添加后端服务的逻辑，例如启动HTTP服务器等
        # 为了简化，我们只是初始化数据并保存
        
        # 保存数据
        backend_service.save_data()
        
        logger.info("TimeNest后端服务初始化完成")
        return 0
        
    except KeyboardInterrupt:
        logger.info("用户中断应用程序")
        return 0
    except Exception as e:
        logger.error(f"启动TimeNest时发生错误: {e}", exc_info=True)
        return 1
    

if __name__ == "__main__":
    # 设置全局异常处理器
    sys.excepthook = global_exception_handler
    sys.exit(main())
