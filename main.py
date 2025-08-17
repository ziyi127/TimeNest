#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
主应用程序入口
"""

import sys
from pathlib import Path
from typing import Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import QSystemTrayIcon, QStyle
from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication, QIcon

# 导入GUI组件
from frontend.gui.floating_window import FloatingWindow
# 导入系统托盘图标
from frontend.system_tray_icon import FrontendSystemTrayIcon
# 导入API客户端
from frontend.api_client import APIClient
# 导入前端应用类
from frontend.main import TimeNestFrontendApp


class TimeNestApp(TimeNestFrontendApp):
    def __init__(self, args: list[str]):
        super().__init__(args)
        self.setApplicationName("TimeNest")
        self.setApplicationVersion("1.0.0")
        self.setStyle("Fusion")
        # Windows系统托盘图标支持
        self.setQuitOnLastWindowClosed(False)

        # 初始化API客户端
        self.api_client = APIClient()
        
        # 初始化数据
        self.load_data()
        
        # 初始化天气数据
        self.weather_data = None

        # 创建悬浮窗
        self.floating_window = FloatingWindow(self)
        self.floating_window.show()

        # 注意：托盘图标已经在父类TimeNestFrontendApp中创建，无需重复创建
    
    def load_data(self) -> None:
        """加载数据"""
        # 从后端API获取数据
        self.courses = self.api_client.get_courses()
        self.schedules = self.api_client.get_schedules()
        self.temp_changes = self.api_client.get_temp_changes()
        self.settings = self.api_client.get_settings()
    
    def save_data(self) -> None:
        """保存所有数据到后端"""
        # 保存数据到后端API
        success_courses = self.api_client.save_courses(self.courses)
        success_schedules = self.api_client.save_schedules(self.schedules)
        success_temp_changes = self.api_client.save_temp_changes(self.temp_changes)
        success_settings = self.api_client.save_settings(self.settings)
        
        # 如果API保存失败，打印错误信息
        if not (success_courses and success_schedules and success_temp_changes and success_settings):
            print("警告：无法保存数据到后端")
    
    def get_course_by_id(self, course_id: str) -> dict[str, str] | None:
        """根据ID获取课程"""
        for course in self.courses:
            if course["id"] == course_id:
                return course
        return None
    
    def get_today_schedule(self) -> dict[str, str]:
        """获取今天的课程表"""
        # 从后端API获取今天的课程安排
        schedule = self.api_client.get_today_schedule()
        return schedule
    
    def get_weather_data(self) -> dict[str, Any] | None:
        """获取天气数据"""
        try:
            # 从后端API获取天气数据
            weather_data = self.api_client.get_weather_data()
            if weather_data:
                self.weather_data = weather_data
                return self.weather_data
            else:
                print("获取天气数据失败")
                return None
        except Exception as e:
            print(f"获取天气数据时发生错误: {str(e)}")
            return None


def main() -> None:
    """应用程序主入口点"""
    # 创建应用程序实例
    app = TimeNestApp(sys.argv)
    
    # 设置窗口位置和大小
    screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()
    window_width = 300
    window_height = 150
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 3
    
    # 如果是首次启动（使用默认设置），则设置为屏幕中上部
    if (app.settings["window_position"]["x"] == 100 and 
        app.settings["window_position"]["y"] == 100):
        app.floating_window.setGeometry(x, y, window_width, window_height)
        # 更新设置
        app.settings["window_position"] = {
            "x": x,
            "y": y
        }
        app.save_data()
    else:
        # 否则使用用户之前保存的位置
        app.floating_window.setGeometry(
            app.settings["window_position"]["x"],
            app.settings["window_position"]["y"],
            window_width,
            window_height
        )
    
    # 启动定时器
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # 不显示Timer tick
    timer.start(app.settings.get("update_interval", 1000))
    
    # 显示系统托盘图标
    app.tray_icon.show()
    
    # 连接系统托盘激活信号
    app.tray_icon.activated.connect(on_activated)
    
    # 显示悬浮窗
    app.floating_window.show()
    
    sys.exit(app.exec())

def on_activated(reason: int) -> None:
    """系统托盘激活回调函数"""
    print(f"Tray icon activated with reason: {reason}")

if __name__ == "__main__":
    main()
