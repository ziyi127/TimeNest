#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
前端主应用
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from frontend.api_client import APIClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# 导入其他模块
from frontend.api_client import APIClient
from frontend.gui.floating_window import FloatingWindow
from frontend.gui.system_tray import FrontendSystemTrayIcon


# 前端主应用类
class TimeNestFrontendApp(QApplication):
    def __init__(self, args=None):
        if args is None:
            args = []
        super().__init__(args)
        self.setApplicationName("TimeNest")
        self.setApplicationVersion("1.0")
        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei";
                font-size: 12px;
            }
        """)
        
        # 初始化API客户端
        self.api_client = APIClient()
        
        # 初始化数据
        self.courses: List[Dict] = []
        self.schedules: List[Dict] = []
        self.temp_changes: List[Dict] = []
        self.settings: Dict = {}
        
        # 初始化UI
        self.initUI()
        
        # 使用QTimer.singleShot将数据加载推迟到事件循环开始后执行
        QTimer.singleShot(0, self.load_data)
    
    def initUI(self):
        """初始化UI"""
        # 创建悬浮窗
        self.floating_window = FloatingWindow(self)
        
        # 创建系统托盘图标
        self.tray_icon = FrontendSystemTrayIcon(self)
        self.tray_icon.show()
    
    def load_data(self):
        """加载数据"""
        # 从API获取数据
        self.courses = self.api_client.get_courses()
        self.schedules = self.api_client.get_schedules()
        self.temp_changes = self.api_client.get_temp_changes()
        self.settings = self.api_client.get_settings()
        
        # 更新UI
        self.floating_window.update_data()
    
    def save_data(self):
        """保存数据"""
        # 保存数据到API
        self.api_client.save_courses(self.courses)
        self.api_client.save_schedules(self.schedules)
        self.api_client.save_temp_changes(self.temp_changes)
        self.api_client.save_settings(self.settings)
    
    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """根据ID获取课程"""
        for course in self.courses:
            if course["id"] == course_id:
                return course
        return None
    
    def get_today_schedule(self) -> Dict:
        """获取今日课表"""
        return self.api_client.get_today_schedule()


# 主函数
def main():
    # 创建前端应用实例
    app = TimeNestFrontendApp()
    
    # 设置窗口位置和大小
    window_position = app.settings.get("window_position", {"x": 100, "y": 100})
    app.floating_window.move(window_position["x"], window_position["y"])
    
    # 启动定时器
    # 每分钟检查一次是否需要更新数据
    timer = QTimer()
    timer.timeout.connect(app.load_data)
    timer.start(60000)  # 60秒
    
    # 显示系统托盘图标
    app.tray_icon.show()
    
    # 连接激活信号
    app.tray_icon.activated.connect(app.floating_window.show)
    
    # 启动应用事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()