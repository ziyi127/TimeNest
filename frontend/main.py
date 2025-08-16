#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
前端应用入口
"""

import sys
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import QApplication

# 导入GUI组件
from frontend.gui.floating_window import FloatingWindow
# 导入系统托盘图标
from frontend.system_tray_icon import FrontendSystemTrayIcon
# 导入API客户端
from frontend.api_client import APIClient


class TimeNestFrontendApp(QApplication):
    def __init__(self, args: list[str]):
        super().__init__(args)
        self.setApplicationName("TimeNest")
        self.setApplicationVersion("1.0.0")
        self.setStyle("Fusion")
        # Windows系统托盘图标支持
        self.setQuitOnLastWindowClosed(False)

        # 初始化API客户端
        self.api_client = APIClient("http://localhost:5000")
        
        # 初始化数据
        self.load_data()
        
        # 初始化天气数据
        self.weather_data = None

        # 创建悬浮窗
        self.floating_window = FloatingWindow(self)
        self.floating_window.show()

        # 创建系统托盘图标
        self.tray_icon = FrontendSystemTrayIcon(self)
        self.tray_icon.show()
    
    def load_data(self):
        """加载数据"""
        # 从后端API获取数据
        self.courses = self.api_client.get_courses()
        self.schedules = self.api_client.get_schedules()
        self.temp_changes = self.api_client.get_temp_changes()
        self.settings = self.api_client.get_settings()
    
    def save_data(self):
        """保存所有数据到后端"""
        # 保存数据到后端API
        success_courses = self.api_client.save_courses(self.courses)
        success_schedules = self.api_client.save_schedules(self.schedules)
        success_temp_changes = self.api_client.save_temp_changes(self.temp_changes)
        success_settings = self.api_client.save_settings(self.settings)
        
        # 如果API保存失败，打印错误信息
        if not (success_courses and success_schedules and success_temp_changes and success_settings):
            print("警告：无法保存数据到后端")
    
    def get_course_by_id(self, course_id: str):
        """根据ID获取课程"""
        for course in self.courses:
            if course["id"] == course_id:
                return course
        return None
    
    def get_today_schedule(self):
        """获取今天的课程表"""
        # 从后端API获取今天的课程安排
        schedule = self.api_client.get_today_schedule()
        return schedule
    
    def get_weather_data(self):
        """获取天气数据"""
        try:
            # 从后端API获取天气数据
            response = requests.get("http://localhost:5000/api/weather/current", timeout=5)
            if response.status_code == 200:
                self.weather_data = response.json()
                return self.weather_data
            else:
                print(f"获取天气数据失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"获取天气数据时发生错误: {str(e)}")
            return None


def main():
    """前端应用程序主入口点"""
    app = TimeNestFrontendApp(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
