#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
前端应用入口
"""

import sys
import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

# 导入GUI组件
from frontend.gui.floating_window import FloatingWindow
# 导入系统托盘图标
from frontend.system_tray_icon import FrontendSystemTrayIcon

# 设置中文字体支持
font = QFont()
font.setFamily("SimHei")


class TimeNestFrontendApp(QApplication):
    def __init__(self, args: list[str]):
        super().__init__(args)
        self.setApplicationName("TimeNest")
        self.setApplicationVersion("1.0.0")
        self.setStyle("Fusion")
        # Windows系统托盘图标支持
        self.setQuitOnLastWindowClosed(False)

        # 确保数据目录存在
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
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
        # 课程数据
        courses_file = os.path.join(self.data_dir, "courses.json")
        if os.path.exists(courses_file):
            with open(courses_file, 'r', encoding='utf-8') as f:
                self.courses = json.load(f)
        else:
            self.courses = []
        
        # 课程表数据
        schedules_file = os.path.join(self.data_dir, "schedules.json")
        if os.path.exists(schedules_file):
            with open(schedules_file, 'r', encoding='utf-8') as f:
                self.schedules = json.load(f)
        else:
            self.schedules = []
        
        # 临时换课数据
        temp_changes_file = os.path.join(self.data_dir, "temp_changes.json")
        if os.path.exists(temp_changes_file):
            with open(temp_changes_file, 'r', encoding='utf-8') as f:
                self.temp_changes = json.load(f)
        else:
            self.temp_changes = []
        
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
                "update_interval": 1000  # 1秒更新间隔
            }
    
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
        
        # 保存设置数据
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
        if today_weekday == 6:  # 如果是星期日
            today_weekday = 0
        else:
            today_weekday += 1  # 其他日期加1
        
        # 检查是否有临时换课
        today_str = today.strftime("%Y-%m-%d")
        for temp_change in self.temp_changes:
            if temp_change["date"] == today_str:
                course = self.get_course_by_id(temp_change["course_id"])
                if course:
                    return {
                        "type": "temp",
                        "course": course
                    }
        
        # 检查常规课程表
        for schedule in self.schedules:
            if schedule["day_of_week"] == today_weekday:
                course = self.get_course_by_id(schedule["course_id"])
                if course:
                    return {
                        "type": "regular",
                        "course": course
                    }
        
        # 没有课程
        return {
            "type": "none"
        }
    
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