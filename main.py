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

class TimeNestBackendService:
    def __init__(self):
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
