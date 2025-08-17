#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
前端主应用
"""

import sys
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Any

if TYPE_CHECKING:
    from frontend.api_client import APIClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 在sudo环境下修复X11显示权限问题
# 检查是否在sudo环境下运行且是Linux平台
if os.geteuid() == 0 and sys.platform.startswith('linux'):
    # 获取原始用户的DISPLAY环境变量
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        # 尝试从用户环境获取DISPLAY
        user_display = os.environ.get('DISPLAY', ':0')
        os.environ['DISPLAY'] = user_display
        
        # 尝试解决X11权限问题
        try:
            import subprocess
            # 添加xhost权限
            subprocess.run(['xhost', f'+SI:localuser:{sudo_user}'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"警告: 无法添加X11权限: {e}")

# 导入PySide6模块
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Signal

# 导入其他模块
from frontend.api_client import APIClient
from frontend.gui.floating_window import FloatingWindow
from frontend.gui.system_tray import FrontendSystemTrayIcon
from frontend.async_data_loader import AsyncDataLoader

# 配置日志 - 减少日志输出以提高性能
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

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
        
        # 初始化异步数据加载器
        self.async_data_loader = AsyncDataLoader(self.api_client)
        self.async_data_loader.data_loaded.connect(self.on_data_loaded)
        
        # 初始化数据
        self.courses: List[Dict] = []
        self.schedules: List[Dict] = []
        self.temp_changes: List[Dict] = []
        self.settings: Dict = {}
        
        # 初始化UI
        self.initUI()
        
        # 使用QTimer.singleShot将数据加载推迟到事件循环开始后执行
        QTimer.singleShot(100, self.load_data)  # 增加延迟以确保UI先初始化完成
    
    def initUI(self):
        """初始化UI"""
        # 创建悬浮窗
        self.floating_window = FloatingWindow(self)
        
        # 创建系统托盘图标
        self.tray_icon = FrontendSystemTrayIcon(self)
        self.tray_icon.show()
    
    def load_data(self):
        """加载数据"""
        try:
            logger.info("开始加载数据")
            
            # 使用增量加载并回退到本地存储
            data = self.async_data_loader.load_incremental_data_async()
            
            # 更新应用数据
            if 'courses' in data:
                self.courses = data['courses']
            if 'schedules' in data:
                self.schedules = data['schedules']
            if 'settings' in data:
                self.settings = data['settings']
            if 'temp_changes' in data:
                self.temp_changes = data['temp_changes']
            
            logger.info("数据加载完成")
            
            # 发出数据加载完成信号
            # self.data_loaded.emit()  # 这个信号在当前类中未定义，暂时注释掉
        except Exception as e:
            logger.error(f"加载数据时出错: {e}")
            # 显示错误消息
            # self.show_message("错误", f"加载数据时出错: {str(e)}", QMessageBox.Critical)  # 暂时注释掉
    
    def on_data_loaded(self, data_type: str, data: Any, success: bool, error: str):
        """处理数据加载完成事件"""
        if success:
            if data_type == "courses":
                self.courses = data
            elif data_type == "schedules":
                self.schedules = data
            elif data_type == "temp_changes":
                self.temp_changes = data
            elif data_type == "settings":
                self.settings = data
                # 设置窗口位置和大小
                window_position = self.settings.get("window_position", {"x": 100, "y": 100})
                self.floating_window.move(window_position["x"], window_position["y"])
            
            # 更新UI
            self.floating_window.update_data()
        else:
            print(f"加载{data_type}数据失败: {error}")
    
    def save_data(self):
        """保存数据"""
        logger.debug("开始保存数据")
        try:
            # 保存数据到API
            self.api_client.save_courses(self.courses)
            self.api_client.save_schedules(self.schedules)
            self.api_client.save_temp_changes(self.temp_changes)
            self.api_client.save_settings(self.settings)
            logger.debug("数据保存完成")
        except Exception as e:
            logger.error(f"保存数据时出错: {e}")
    
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

# 应用启动后设置窗口位置和大小
def set_window_position(app: TimeNestFrontendApp):
    """设置窗口位置和大小"""
    window_position = app.settings.get("window_position", {"x": 100, "y": 100})
    app.floating_window.move(window_position["x"], window_position["y"])


if __name__ == "__main__":
    main()