"""
提醒服务
提供课程开始前提醒、作业提醒等自动提醒功能
"""

import datetime
import threading
import time
from typing import List, Dict, Optional, Callable
from models.class_item import ClassItem
from utils.logger import get_service_logger

# 初始化日志记录器
logger = get_service_logger("reminder_service")


class ReminderService:
    """提醒服务类"""
    
    def __init__(self):
        """初始化提醒服务"""
        self.is_running = False
        self.reminder_thread: Optional[threading.Thread] = None
        self.reminder_callbacks: List[Callable] = []
        logger.info("ReminderService initialized")
    
    def start_reminder_service(self):
        """
        启动提醒服务
        """
        if self.is_running:
            logger.warning("提醒服务已在运行中")
            return

        self.is_running = True
        self.reminder_thread = threading.Thread(target=self._reminder_worker, daemon=True)
        self.reminder_thread.start()
        logger.info("提醒服务已启动")

    def stop_reminder_service(self):
        """
        停止提醒服务
        """
        if not self.is_running:
            logger.warning("提醒服务未在运行中")
            return

        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=5.0)
        logger.info("提醒服务已停止")

    def add_reminder_callback(self, callback: Callable[[Dict[str, str]], None]):
        """
        添加提醒回调函数

        Args:
            callback: 回调函数，接收提醒信息作为参数
        """
        self.reminder_callbacks.append(callback)
        logger.debug("添加提醒回调函数，当前共有 %d 个回调函数", len(self.reminder_callbacks))
    
    def remove_reminder_callback(self, callback: Callable[[Dict[str, str]], None]):
        """
        移除提醒回调函数

        Args:
            callback: 要移除的回调函数
        """
        if callback in self.reminder_callbacks:
            self.reminder_callbacks.remove(callback)
            logger.debug("移除提醒回调函数，当前共有 %d 个回调函数", len(self.reminder_callbacks))

    def _reminder_worker(self):
        """
        提醒工作线程
        """
        logger.info("提醒工作线程已启动")

        while self.is_running:
            try:
                # 检查是否有即将到来的课程
                upcoming_courses = self._check_upcoming_courses()

                # 触发提醒
                for course_info in upcoming_courses:
                    self._trigger_reminder(course_info)

                # 每分钟检查一次
                time.sleep(60)

            except Exception as e:
                logger.error("提醒工作线程出现错误: %s", str(e))
                # 继续运行，避免线程崩溃
                time.sleep(60)

        logger.info("提醒工作线程已停止")

    def _check_upcoming_courses(self) -> List[Dict[str, str]]:
        """
        检查即将到来的课程

        Returns:
            即将到来的课程信息列表
        """
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory

            # 获取课程服务和课程表服务
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()

            # 获取今天和明天的日期
            today = datetime.date.today()
            tomorrow = today + datetime.timedelta(days=1)

            upcoming_courses = []

            # 检查今天的课程
            today_schedules = schedule_service.get_schedules_by_date(today.strftime("%Y-%m-%d"))
            for schedule in today_schedules:
                course = course_service.get_course_by_id(schedule.course_id)
                if course:
                    # 检查是否在接下来30分钟内开始
                    if self._is_course_starting_soon(course, today):
                        upcoming_courses.append({
                            "type": "course_start",
                            "course_name": course.name,
                            "teacher": course.teacher,
                            "location": course.location,
                            "start_time": course.duration.start_time,
                            "time_until_start": self._get_time_until_start(course, today)
                        })

            # 检查明天的课程
            tomorrow_schedules = schedule_service.get_schedules_by_date(tomorrow.strftime("%Y-%m-%d"))
            for schedule in tomorrow_schedules:
                course = course_service.get_course_by_id(schedule.course_id)
                if course:
                    # 检查是否在接下来24小时内开始
                    if self._is_course_starting_tomorrow(course, tomorrow):
                        upcoming_courses.append({
                            "type": "course_tomorrow",
                            "course_name": course.name,
                            "teacher": course.teacher,
                            "location": course.location,
                            "start_time": course.duration.start_time,
                            "date": tomorrow.strftime("%Y-%m-%d")
                        })

            return upcoming_courses

        except Exception as e:
            logger.error("检查即将到来的课程失败: %s", str(e))
            return []

    def _is_course_starting_soon(self, course: ClassItem, date: datetime.date) -> bool:
        """
        检查课程是否在接下来30分钟内开始

        Args:
            course: 课程对象
            date: 日期

        Returns:
            是否在接下来30分钟内开始
        """
        try:
            # 获取当前时间
            now = datetime.datetime.now()

            # 解析课程开始时间
            start_parts = course.duration.start_time.split(':')
            start_hour = int(start_parts[0])
            start_minute = int(start_parts[1])

            # 构造课程开始时间
            course_start = datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_hour,
                minute=start_minute
            )

            # 计算时间差
            time_diff = course_start - now

            # 检查是否在接下来30分钟内开始（且未开始）
            return datetime.timedelta(minutes=0) <= time_diff <= datetime.timedelta(minutes=30)

        except Exception as e:
            logger.warning("检查课程开始时间失败: %s", str(e))
            return False

    def _is_course_starting_tomorrow(self, course: ClassItem, date: datetime.date) -> bool:
        """
        检查课程是否在明天开始

        Args:
            course: 课程对象
            date: 日期

        Returns:
            是否在明天开始
        """
        try:
            # 获取当前时间
            now = datetime.datetime.now()

            # 解析课程开始时间
            start_parts = course.duration.start_time.split(':')
            start_hour = int(start_parts[0])
            start_minute = int(start_parts[1])

            # 构造课程开始时间
            course_start = datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_hour,
                minute=start_minute
            )

            # 计算时间差
            time_diff = course_start - now

            # 检查是否在接下来24小时内开始
            return datetime.timedelta(hours=0) <= time_diff <= datetime.timedelta(hours=24)

        except Exception as e:
            logger.warning("检查明天课程开始时间失败: %s", str(e))
            return False

    def _get_time_until_start(self, course: ClassItem, date: datetime.date) -> str:
        """
        获取距离课程开始的时间

        Args:
            course: 课程对象
            date: 日期

        Returns:
            距离开始的时间描述
        """
        try:
            # 获取当前时间
            now = datetime.datetime.now()

            # 解析课程开始时间
            start_parts = course.duration.start_time.split(':')
            start_hour = int(start_parts[0])
            start_minute = int(start_parts[1])

            # 构造课程开始时间
            course_start = datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_hour,
                minute=start_minute
            )

            # 计算时间差
            time_diff = course_start - now

            # 转换为分钟
            minutes_until_start = int(time_diff.total_seconds() / 60)

            if minutes_until_start < 60:
                return f"{minutes_until_start}分钟后"
            else:
                hours = minutes_until_start // 60
                minutes = minutes_until_start % 60
                if minutes == 0:
                    return f"{hours}小时后"
                else:
                    return f"{hours}小时{minutes}分钟后"

        except Exception as e:
            logger.warning("计算课程开始时间失败: %s", str(e))
            return "即将开始"

    def _trigger_reminder(self, reminder_info: Dict[str, str]):
        """
        触发提醒

        Args:
            reminder_info: 提醒信息
        """
        logger.info("触发提醒: %s", reminder_info)

        # 调用所有回调函数
        for callback in self.reminder_callbacks:
            try:
                callback(reminder_info)
            except Exception as e:
                logger.error("提醒回调函数执行失败: %s", str(e))

        # 记录提醒日志
        if reminder_info["type"] == "course_start":
            logger.info("课程即将开始提醒: %s %s开始", reminder_info["course_name"], reminder_info["time_until_start"])
        elif reminder_info["type"] == "course_tomorrow":
            logger.info("明日课程提醒: %s 明天%s开始", reminder_info["course_name"], reminder_info["start_time"])
