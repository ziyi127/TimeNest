#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
完整重构自ClassIsland的C#实现
"""

import sys
import os
import logging
from pathlib import Path

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
from PySide6.QtCore import QDate, QEvent, Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QIcon, QFont, QColor, QCursor, QAction, QMouseEvent, QGuiApplication

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

        # 创建悬浮窗
        self.floating_window = FloatingWindow(self)
        self.floating_window.show()

        # 创建系统托盘图标
        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.show()

    def load_data(self):
        """加载课程、课程表和临时换课数据"""
        # 课程数据
        courses_file = os.path.join(self.data_dir, "courses.json")
        if os.path.exists(courses_file):
            with open(courses_file, 'r', encoding='utf-8') as f:
                self.courses = json.load(f)
        else:
            # 示例数据
            self.courses: list[dict[str, any]] = [
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
            self.schedules: list[dict[str, any]] = [
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

    def get_course_by_id(self, course_id: str) -> dict[str, any] | None:
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
    """应用程序主入口点"""
    logger = setup_logging()

    try:
        # 创建应用数据目录
        app_data_path = get_app_data_path()
        app_data_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"应用数据目录: {app_data_path}")

        # 创建并运行应用程序
        logger.info("启动TimeNest应用程序")
        app = TimeNestApp(sys.argv)
        exit_code = app.exec_()

        logger.info("TimeNest应用程序已退出")
        return exit_code

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

# 移除重复的管理窗口类定义

    def add_course(self):
        """添加课程"""
        dialog = CourseEditDialog(self.app, None)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_course_list()

    def edit_course(self):
        """编辑课程"""
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要编辑的课程")
            return

        course_id = current_item.data(Qt.UserRole)
        course = self.app.get_course_by_id(course_id)
        if not course:
            QMessageBox.warning(self, "警告", "找不到选中的课程")
            return

        dialog = CourseEditDialog(self.app, course)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_course_list()

    def delete_course(self):
        """删除课程"""
        current_item = self.course_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的课程")
            return

        course_id = current_item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "确认", "确定要删除选中的课程吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除课程
            self.app.courses = [c for c in self.app.courses if c['id'] != course_id]
            # 删除相关的课程表项
            self.app.schedules = [s for s in self.app.schedules if s['course_id'] != course_id]
            # 删除相关的临时换课
            self.app.temp_changes = [t for t in self.app.temp_changes if t['new_course_id'] != course_id]
            self.app.save_data()
            self.update_course_list()
            self.update_schedule_table()
            self.update_temp_change_table()

    def init_schedule_tab(self):
        """初始化课程表管理标签页"""
        layout = QVBoxLayout(self.schedule_tab)

        # 创建课程表表格
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(["ID", "星期", "周次", "课程", "有效期从", "有效期至"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.schedule_table)

        # 添加按钮
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加课程表项")
        add_button.clicked.connect(self.add_schedule)
        edit_button = QPushButton("编辑课程表项")
        edit_button.clicked.connect(self.edit_schedule)
        delete_button = QPushButton("删除课程表项")
        delete_button.clicked.connect(self.delete_schedule)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        # 更新表格数据
        self.update_schedule_table()

    def update_schedule_table(self):
        """更新课程表表格"""
        self.schedule_table.setRowCount(0)
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        week_parity_map = {
            "both": "每周",
            "odd": "奇数周",
            "even": "偶数周"
        }

        for schedule in self.app.schedules:
            row = self.schedule_table.rowCount()
            self.schedule_table.insertRow(row)

            # ID
            self.schedule_table.setItem(row, 0, QTableWidgetItem(schedule['id']))

            # 星期
            weekday = weekdays[schedule['day_of_week']]
            self.schedule_table.setItem(row, 1, QTableWidgetItem(weekday))

            # 周次
            week_parity = week_parity_map.get(schedule['week_parity'], schedule['week_parity'])
            self.schedule_table.setItem(row, 2, QTableWidgetItem(week_parity))

            # 课程
            course = self.app.get_course_by_id(schedule['course_id'])
            course_name = course['name'] if course else "未知课程"
            self.schedule_table.setItem(row, 3, QTableWidgetItem(course_name))

            # 有效期从
            self.schedule_table.setItem(row, 4, QTableWidgetItem(schedule['valid_from']))

            # 有效期至
            self.schedule_table.setItem(row, 5, QTableWidgetItem(schedule['valid_to']))

    def add_schedule(self):
        """添加课程表项"""
        dialog = ScheduleEditDialog(self.app, None)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_schedule_table()

    def edit_schedule(self):
        """编辑课程表项"""
        current_row = self.schedule_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要编辑的课程表项")
            return

        schedule_id = self.schedule_table.item(current_row, 0).text()
        # 查找课程表项
        schedule = None
        for s in self.app.schedules:
            if s['id'] == schedule_id:
                schedule = s
                break

        if not schedule:
            QMessageBox.warning(self, "警告", "找不到选中的课程表项")
            return

        dialog = ScheduleEditDialog(self.app, schedule)
        if dialog.exec_() == QDialog.Accepted:
            self.app.load_data()
            self.update_schedule_table()

    def delete_schedule(self):
        """删除课程表项"""
        current_row = self.schedule_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要删除的课程表项")
            return

        schedule_id = self.schedule_table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "确认", "确定要删除选中的课程表项吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除课程表项
            self.app.schedules = [s for s in self.app.schedules if s['id'] != schedule_id]
            # 删除相关的临时换课
            self.app.temp_changes = [t for t in self.app.temp_changes if t['original_schedule_id'] != schedule_id]
            self.app.save_data()
            self.update_schedule_table()
            self.update_temp_change_table()

    def init_temp_change_tab(self):
        """初始化临时换课记录标签页"""
        layout = QVBoxLayout(self.temp_change_tab)

        # 创建临时换课表格
        self.temp_change_table = QTableWidget()
        self.temp_change_table.setColumnCount(5)
        self.temp_change_table.setHorizontalHeaderLabels(["ID", "日期", "原课程", "新课程", "状态"])
        self.temp_change_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.temp_change_table)

        # 添加按钮
        button_layout = QHBoxLayout()
        delete_button = QPushButton("删除记录")
        delete_button.clicked.connect(self.delete_temp_change)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        # 更新表格数据
        self.update_temp_change_table()

    def update_temp_change_table(self):
        """更新临时换课表格"""
        self.temp_change_table.setRowCount(0)

        for temp_change in self.app.temp_changes:
            row = self.temp_change_table.rowCount()
            self.temp_change_table.insertRow(row)

            # ID
            self.temp_change_table.setItem(row, 0, QTableWidgetItem(temp_change['id']))

            # 日期
            self.temp_change_table.setItem(row, 1, QTableWidgetItem(temp_change['change_date']))

            # 原课程（通过original_schedule_id查找）
            original_schedule = None
            for s in self.app.schedules:
                if s['id'] == temp_change['original_schedule_id']:
                    original_schedule = s
                    break

            original_course_name = "未知课程"
            if original_schedule:
                original_course = self.app.get_course_by_id(original_schedule['course_id'])
                if original_course:
                    original_course_name = original_course['name']

            self.temp_change_table.setItem(row, 2, QTableWidgetItem(original_course_name))

            # 新课程
            new_course = self.app.get_course_by_id(temp_change['new_course_id'])
            new_course_name = new_course['name'] if new_course else "未知课程"
            self.temp_change_table.setItem(row, 3, QTableWidgetItem(new_course_name))

            # 状态
            status = "已使用" if temp_change['used'] else "未使用"
            status_item = QTableWidgetItem(status)
            if temp_change['used']:
                status_item.setForeground(QColor(128, 128, 128))
            else:
                status_item.setForeground(QColor(255, 99, 71))  # 红色
            self.temp_change_table.setItem(row, 4, status_item)

    def delete_temp_change(self):
        """删除临时换课记录"""
        current_row = self.temp_change_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "请选择要删除的临时换课记录")
            return

        temp_change_id = self.temp_change_table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "确认", "确定要删除选中的临时换课记录吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 删除临时换课记录
            self.app.temp_changes = [t for t in self.app.temp_changes if t['id'] != temp_change_id]
            self.app.save_data()
            self.update_temp_change_table()

    def save_data(self):
        """保存数据"""
        self.app.save_data()
        QMessageBox.information(self, "成功", "数据保存成功")

# 课程编辑对话框
class CourseEditDialog(QDialog):
    def __init__(self, app, course=None):
        super().__init__()
        self.app = app
        self.course = course
        self.setWindowTitle("编辑课程" if course else "添加课程")
        self.initUI()

    def initUI(self):
        # 创建表单布局
        layout = QFormLayout(self)

        # 课程ID
        self.id_edit = QLineEdit()
        if self.course:
            self.id_edit.setText(self.course['id'])
            self.id_edit.setEnabled(False)  # 编辑时ID不可修改
        else:
            # 自动生成ID
            self.id_edit.setText(f"course{len(self.app.courses) + 1}")
        layout.addRow("课程ID:", self.id_edit)

        # 课程名称
        self.name_edit = QLineEdit()
        if self.course:
            self.name_edit.setText(self.course['name'])
        layout.addRow("课程名称:", self.name_edit)

        # 教师
        self.teacher_edit = QLineEdit()
        if self.course:
            self.teacher_edit.setText(self.course['teacher'])
        layout.addRow("教师:", self.teacher_edit)

        # 教室
        self.location_edit = QLineEdit()
        if self.course:
            self.location_edit.setText(self.course['location'])
        layout.addRow("教室:", self.location_edit)

        # 开始时间
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        if self.course:
            start_time = datetime.strptime(self.course['duration']['start_time'], "%H:%M").time()
            self.start_time_edit.setTime(start_time)
        layout.addRow("开始时间:", self.start_time_edit)

        # 结束时间
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        if self.course:
            end_time = datetime.strptime(self.course['duration']['end_time'], "%H:%M").time()
            self.end_time_edit.setTime(end_time)
        layout.addRow("结束时间:", self.end_time_edit)

        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def accept(self):
        """确认按钮事件"""
        # 验证输入
        id = self.id_edit.text().strip()
        name = self.name_edit.text().strip()
        teacher = self.teacher_edit.text().strip()
        location = self.location_edit.text().strip()
        start_time = self.start_time_edit.time().toString("HH:mm")
        end_time = self.end_time_edit.time().toString("HH:mm")

        if not id or not name or not teacher or not location:
            QMessageBox.warning(self, "警告", "所有字段都不能为空")
            return

        # 检查时间顺序
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        if start >= end:
            QMessageBox.warning(self, "警告", "开始时间必须早于结束时间")
            return

        # 检查ID是否已存在（添加时）
        if not self.course:
            for course in self.app.courses:
                if course['id'] == id:
                    QMessageBox.warning(self, "警告", f"课程ID '{id}' 已存在")
                    return

        # 创建或更新课程
        course_data = {
            "id": id,
            "name": name,
            "teacher": teacher,
            "location": location,
            "duration": {
                "start_time": start_time,
                "end_time": end_time
            }
        }

        if self.course:
            # 更新课程
            index = -1
            for i, c in enumerate(self.app.courses):
                if c['id'] == id:
                    index = i
                    break
            if index != -1:
                self.app.courses[index] = course_data
        else:
            # 添加新课程
            self.app.courses.append(course_data)

        # 保存数据
        self.app.save_data()
        super().accept()

# 课程表编辑对话框
class ScheduleEditDialog(QDialog):
    def __init__(self, app, schedule=None):
        super().__init__()
        self.app = app
        self.schedule = schedule
        self.setWindowTitle("编辑课程表项" if schedule else "添加课程表项")
        self.initUI()

    def initUI(self):
        # 创建表单布局
        layout = QFormLayout(self)

        # 课程表项ID
        self.id_edit = QLineEdit()
        if self.schedule:
            self.id_edit.setText(self.schedule['id'])
            self.id_edit.setEnabled(False)  # 编辑时ID不可修改
        else:
            # 自动生成ID
            self.id_edit.setText(f"schedule{len(self.app.schedules) + 1}")
        layout.addRow("课程表项ID:", self.id_edit)

        # 星期
        self.weekday_combo = QComboBox()
        weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
        self.weekday_combo.addItems(weekdays)
        if self.schedule:
            self.weekday_combo.setCurrentIndex(self.schedule['day_of_week'])
        layout.addRow("星期:", self.weekday_combo)

        # 周次
        self.week_parity_combo = QComboBox()
        self.week_parity_combo.addItems(["每周", "奇数周", "偶数周"])
        if self.schedule:
            week_parity_map = {
                "both": 0,
                "odd": 1,
                "even": 2
            }
            self.week_parity_combo.setCurrentIndex(week_parity_map.get(self.schedule['week_parity'], 0))
        layout.addRow("周次:", self.week_parity_combo)

        # 课程
        self.course_combo = QComboBox()
        self.course_ids = []
        for course in self.app.courses:
            self.course_combo.addItem(f"{course['name']} - {course['teacher']}")
            self.course_ids.append(course['id'])
        if self.schedule and self.schedule['course_id'] in self.course_ids:
            self.course_combo.setCurrentIndex(self.course_ids.index(self.schedule['course_id']))
        layout.addRow("课程:", self.course_combo)

        # 有效期从
        self.valid_from_edit = QDateEdit()
        self.valid_from_edit.setDisplayFormat("yyyy-MM-dd")
        if self.schedule:
            valid_from = datetime.strptime(self.schedule['valid_from'], "%Y-%m-%d").date()
            self.valid_from_edit.setDate(valid_from)
        else:
            self.valid_from_edit.setDate(datetime.now().date())
        layout.addRow("有效期从:", self.valid_from_edit)

        # 有效期至
        self.valid_to_edit = QDateEdit()
        self.valid_to_edit.setDisplayFormat("yyyy-MM-dd")
        if self.schedule:
            valid_to = datetime.strptime(self.schedule['valid_to'], "%Y-%m-%d").date()
            self.valid_to_edit.setDate(valid_to)
        else:
            next_month = datetime.now().date().replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            self.valid_to_edit.setDate(next_month)
        layout.addRow("有效期至:", self.valid_to_edit)

        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)

    def accept(self):
        """确认按钮事件"""
        # 获取输入
        id = self.id_edit.text().strip()
        day_of_week = self.weekday_combo.currentIndex()
        week_parity_index = self.week_parity_combo.currentIndex()
        week_parity_map = ["both", "odd", "even"]
        week_parity = week_parity_map[week_parity_index]
        course_index = self.course_combo.currentIndex()
        course_id = self.course_ids[course_index]
        valid_from = self.valid_from_edit.date().toString("yyyy-MM-dd")
        valid_to = self.valid_to_edit.date().toString("yyyy-MM-dd")

        # 验证日期
        from_date = datetime.strptime(valid_from, "%Y-%m-%d").date()
        to_date = datetime.strptime(valid_to, "%Y-%m-%d").date()
        if from_date > to_date:
            QMessageBox.warning(self, "警告", "有效期从必须早于有效期至")
            return

        # 检查ID是否已存在（添加时）
        if not self.schedule:
            for schedule in self.app.schedules:
                if schedule['id'] == id:
                    QMessageBox.warning(self, "警告", f"课程表项ID '{id}' 已存在")
                    return

        # 创建或更新课程表项
        schedule_data = {
            "id": id,
            "day_of_week": day_of_week,
            "week_parity": week_parity,
            "course_id": course_id,
            "valid_from": valid_from,
            "valid_to": valid_to
        }

        if self.schedule:
            # 更新课程表项
            index = -1
            for i, s in enumerate(self.app.schedules):
                if s['id'] == id:
                    index = i
                    break
            if index != -1:
                self.app.schedules[index] = schedule_data
        else:
            # 添加新课程表项
            self.app.schedules.append(schedule_data)

        # 保存数据
        self.app.save_data()
        super().accept()

# 主函数
if __name__ == "__main__":
    app = TimeNestApp(sys.argv)
    sys.exit(app.exec())

