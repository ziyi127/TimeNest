#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
API客户端
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入requests库
import requests


# API客户端类
class APIClient:
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        # 添加缓存字典
        self._cache: Dict[str, Any] = {}
        # 缓存过期时间（秒）
        self._cache_ttl = 300  # 5分钟
        # 上次缓存更新时间
        self._cache_timestamps: Dict[str, float] = {}
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        import time
        if cache_key not in self._cache_timestamps:
            return False
        return time.time() - self._cache_timestamps[cache_key] < self._cache_ttl

    def get_courses(self) -> List[Dict[str, Any]]:
        """获取所有课程"""
        cache_key = "courses"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = requests.get(f"{self.base_url}/courses")
            if response.status_code == 200:
                data = response.json()
                # 更新缓存
                self._cache[cache_key] = data
                import time
                self._cache_timestamps[cache_key] = time.time()
                return data
            else:
                print(f"获取课程失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取课程时发生错误: {e}")
            return []

    def save_courses(self, courses: List[Dict[str, Any]]) -> bool:
        """保存课程（创建新课程）"""
        success = True
        for course in courses:
            # 检查课程数据是否已经包含duration字段
            if "duration" in course:
                # 如果已经包含duration字段，则直接使用
                course_data = course
            else:
                # 否则，转换课程数据格式以匹配后端API期望的结构
                course_data = {
                    "id": course["id"],
                    "name": course["name"],
                    "teacher": course["teacher"],
                    "location": course["location"],
                    "duration": {
                        "start_time": course["start_time"],
                        "end_time": course["end_time"]
                    }
                }
            
            try:
                response = requests.post(f"{self.base_url}/courses", json=course_data)
                # 接受201（创建成功）和409（冲突，已存在）状态码
                if response.status_code not in [201, 409]:
                    print(f"创建课程失败: {response.status_code} - {response.text}")
                    success = False
            except Exception as e:
                print(f"创建课程时发生错误: {e}")
                success = False
        # 清除课程缓存
        if "courses" in self._cache:
            del self._cache["courses"]
        if "courses" in self._cache_timestamps:
            del self._cache_timestamps["courses"]
        return success

    def get_schedules(self) -> List[Dict[str, Any]]:
        """获取所有课程表"""
        cache_key = "schedules"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = requests.get(f"{self.base_url}/schedules")
            if response.status_code == 200:
                data = response.json()
                # 更新缓存
                self._cache[cache_key] = data
                import time
                self._cache_timestamps[cache_key] = time.time()
                return data
            else:
                print(f"获取课程表失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取课程表时发生错误: {e}")
            return []

    def save_schedules(self, schedules: List[Dict[str, Any]]) -> bool:
        """保存课程表（创建新课程表）"""
        success = True
        for schedule in schedules:
            try:
                response = requests.post(f"{self.base_url}/schedules", json=schedule)
                # 接受201（创建成功）和409（冲突，已存在）状态码
                if response.status_code not in [201, 409]:
                    print(f"创建课程表失败: {response.status_code} - {response.text}")
                    success = False
            except Exception as e:
                print(f"创建课程表时发生错误: {e}")
                success = False
        # 清除课程表缓存
        if "schedules" in self._cache:
            del self._cache["schedules"]
        if "schedules" in self._cache_timestamps:
            del self._cache_timestamps["schedules"]
        return success

    def get_temp_changes(self) -> List[Dict[str, Any]]:
        """获取所有临时换课记录"""
        cache_key = "temp_changes"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = requests.get(f"{self.base_url}/temp_changes")
            if response.status_code == 200:
                data = response.json()
                # 更新缓存
                self._cache[cache_key] = data
                import time
                self._cache_timestamps[cache_key] = time.time()
                return data
            else:
                print(f"获取临时换课记录失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"获取临时换课记录时发生错误: {e}")
            return []

    def save_temp_changes(self, temp_changes: List[Dict[str, Any]]) -> bool:
        """保存临时换课记录（创建新记录）"""
        success = True
        for temp_change in temp_changes:
            try:
                response = requests.post(f"{self.base_url}/temp_changes", json=temp_change)
                # 接受201（创建成功）和409（冲突，已存在）状态码
                if response.status_code not in [201, 409]:
                    print(f"创建临时换课记录失败: {response.status_code} - {response.text}")
                    success = False
            except Exception as e:
                print(f"创建临时换课记录时发生错误: {e}")
                success = False
        # 清除临时换课记录缓存
        if "temp_changes" in self._cache:
            del self._cache["temp_changes"]
        if "temp_changes" in self._cache_timestamps:
            del self._cache_timestamps["temp_changes"]
        return success

    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        cache_key = "settings"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = requests.get(f"{self.base_url}/settings")
            if response.status_code == 200:
                data = response.json()
                # 更新缓存
                self._cache[cache_key] = data
                import time
                self._cache_timestamps[cache_key] = time.time()
                return data
            else:
                print(f"获取设置失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"获取设置时发生错误: {e}")
            return {}

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """保存设置"""
        try:
            response = requests.put(f"{self.base_url}/settings", json=settings)
            if response.status_code == 200:
                # 清除设置缓存
                if "settings" in self._cache:
                    del self._cache["settings"]
                if "settings" in self._cache_timestamps:
                    del self._cache_timestamps["settings"]
                return True
            else:
                print(f"保存设置失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"保存设置时发生错误: {e}")
            return False

    def get_today_schedule(self, date: Optional[str] = None) -> Dict[str, Any]:
        """获取今日课程表"""
        # 今日课程表不缓存，因为可能依赖实时时间
        try:
            url = f"{self.base_url}/today_schedule"
            if date:
                url += f"?date={date}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取今日课程表失败: {response.status_code}")
                return {"type": "none"}
        except Exception as e:
            print(f"获取今日课程表时发生错误: {e}")
            return {"type": "none"}

    def get_weather_data(self) -> Dict[str, Any]:
        """获取天气数据"""
        # 天气数据通过ServiceFactory获取，不通过HTTP请求
        from backend.services import ServiceFactory
        weather_service = ServiceFactory.get_weather_service()
        return weather_service.get_weather_data()

    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()
        self._cache_timestamps.clear()