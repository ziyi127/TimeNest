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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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
        
        # 创建带重试策略的会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,  # 总重试次数
            backoff_factor=1,  # 重试间隔
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认超时时间
        self.timeout = 10
        
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
            response = self.session.get(f"{self.base_url}/courses", timeout=self.timeout)
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
                response = self.session.post(f"{self.base_url}/courses", json=course_data, timeout=self.timeout)
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

    def update_course(self, course_id: str, course_data: Dict[str, Any]) -> bool:
        """更新课程"""
        try:
            # 检查课程数据是否已经包含duration字段
            if "duration" in course_data:
                # 如果已经包含duration字段，则直接使用
                data = course_data
            else:
                # 否则，转换课程数据格式以匹配后端API期望的结构
                data = {
                    "id": course_data["id"],
                    "name": course_data["name"],
                    "teacher": course_data["teacher"],
                    "location": course_data["location"],
                    "duration": {
                        "start_time": course_data["start_time"],
                        "end_time": course_data["end_time"]
                    }
                }
            
            response = self.session.put(f"{self.base_url}/courses/{course_id}", json=data, timeout=self.timeout)
            if response.status_code == 200:
                # 清除课程缓存
                if "courses" in self._cache:
                    del self._cache["courses"]
                if "courses" in self._cache_timestamps:
                    del self._cache_timestamps["courses"]
                return True
            else:
                print(f"更新课程失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"更新课程时发生错误: {e}")
            return False

    def delete_course(self, course_id: str) -> bool:
        """删除课程"""
        try:
            response = self.session.delete(f"{self.base_url}/courses/{course_id}", timeout=self.timeout)
            if response.status_code == 200:
                # 清除课程缓存
                if "courses" in self._cache:
                    del self._cache["courses"]
                if "courses" in self._cache_timestamps:
                    del self._cache_timestamps["courses"]
                return True
            else:
                print(f"删除课程失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"删除课程时发生错误: {e}")
            return False

    def get_schedules(self) -> List[Dict[str, Any]]:
        """获取所有课程表"""
        cache_key = "schedules"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = self.session.get(f"{self.base_url}/schedules", timeout=self.timeout)
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
                response = self.session.post(f"{self.base_url}/schedules", json=schedule, timeout=self.timeout)
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

    def update_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> bool:
        """更新课程表"""
        try:
            response = self.session.put(f"{self.base_url}/schedules/{schedule_id}", json=schedule_data, timeout=self.timeout)
            if response.status_code == 200:
                # 清除课程表缓存
                if "schedules" in self._cache:
                    del self._cache["schedules"]
                if "schedules" in self._cache_timestamps:
                    del self._cache_timestamps["schedules"]
                return True
            else:
                print(f"更新课程表失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"更新课程表时发生错误: {e}")
            return False

    def delete_schedule(self, schedule_id: str) -> bool:
        """删除课程表"""
        try:
            response = self.session.delete(f"{self.base_url}/schedules/{schedule_id}", timeout=self.timeout)
            if response.status_code == 200:
                # 清除课程表缓存
                if "schedules" in self._cache:
                    del self._cache["schedules"]
                if "schedules" in self._cache_timestamps:
                    del self._cache_timestamps["schedules"]
                return True
            else:
                print(f"删除课程表失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"删除课程表时发生错误: {e}")
            return False

    def get_temp_changes(self) -> List[Dict[str, Any]]:
        """获取所有临时换课记录"""
        cache_key = "temp_changes"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = self.session.get(f"{self.base_url}/temp_changes", timeout=self.timeout)
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
                response = self.session.post(f"{self.base_url}/temp_changes", json=temp_change, timeout=self.timeout)
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

    def update_temp_change(self, temp_change_id: str, temp_change_data: Dict[str, Any]) -> bool:
        """更新临时换课记录"""
        try:
            response = self.session.put(f"{self.base_url}/temp_changes/{temp_change_id}", json=temp_change_data, timeout=self.timeout)
            if response.status_code == 200:
                # 清除临时换课记录缓存
                if "temp_changes" in self._cache:
                    del self._cache["temp_changes"]
                if "temp_changes" in self._cache_timestamps:
                    del self._cache_timestamps["temp_changes"]
                return True
            else:
                print(f"更新临时换课记录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"更新临时换课记录时发生错误: {e}")
            return False

    def delete_temp_change(self, temp_change_id: str) -> bool:
        """删除临时换课记录"""
        try:
            response = self.session.delete(f"{self.base_url}/temp_changes/{temp_change_id}", timeout=self.timeout)
            if response.status_code == 200:
                # 清除临时换课记录缓存
                if "temp_changes" in self._cache:
                    del self._cache["temp_changes"]
                if "temp_changes" in self._cache_timestamps:
                    del self._cache_timestamps["temp_changes"]
                return True
            else:
                print(f"删除临时换课记录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"删除临时换课记录时发生错误: {e}")
            return False

    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        cache_key = "settings"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        try:
            response = self.session.get(f"{self.base_url}/settings", timeout=self.timeout)
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
            response = self.session.put(f"{self.base_url}/settings", json=settings, timeout=self.timeout)
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
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取今日课程表失败: {response.status_code}")
                return {"type": "none"}
        except Exception as e:
            print(f"获取今日课程表时发生错误: {e}")
            return {"type": "none"}

    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """获取天气数据"""
        # 天气数据不缓存，因为可能需要实时更新
        try:
            response = self.session.get(f"{self.base_url}/weather?location={location}", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"获取天气数据失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"获取天气数据时发生错误: {e}")
            return {}

    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()
        self._cache_timestamps.clear()