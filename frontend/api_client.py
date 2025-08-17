#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
API客户端
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入配置
from config import FRONTEND_API_BASE_URL

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str = FRONTEND_API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 缓存机制
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=5)  # 5分钟缓存
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return datetime.now() - cached_time < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def _set_cache(self, cache_key: str, data: Any) -> None:
        """设置缓存数据"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _clear_cache(self) -> None:
        """清除所有缓存"""
        self.cache.clear()
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """获取所有课程"""
        cache_key = 'courses'
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            response = self.session.get(f"{self.base_url}/courses")
            response.raise_for_status()
            data = response.json()
            
            # 缓存数据
            self._set_cache(cache_key, data)
            return data
        except requests.RequestException as e:
            logger.error(f"获取课程失败: {e}")
            return []
    
    def save_courses(self, courses: List[Dict[str, Any]]) -> bool:
        """保存课程"""
        try:
            success = True
            for course in courses:
                # 发送单个课程对象
                response = self.session.post(f"{self.base_url}/courses", json=course)
                # 检查响应状态码，409表示数据已存在，这是预期的行为
                if response.status_code != 409:
                    response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"保存课程失败: {e}")
            return False
    
    def get_schedules(self) -> List[Dict[str, Any]]:
        """获取所有课表"""
        cache_key = 'schedules'
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            response = self.session.get(f"{self.base_url}/schedules")
            response.raise_for_status()
            data = response.json()
            
            # 缓存数据
            self._set_cache(cache_key, data)
            return data
        except requests.RequestException as e:
            logger.error(f"获取课表失败: {e}")
            return []
    
    def create_schedule(self, schedule: Dict[str, Any]) -> bool:
        """创建课表"""
        try:
            response = self.session.post(f"{self.base_url}/schedules", json=schedule)
            response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"创建课表失败: {e}")
            return False
    
    def update_schedule(self, schedule_id: str, schedule: Dict[str, Any]) -> bool:
        """更新课表"""
        try:
            response = self.session.put(f"{self.base_url}/schedules/{schedule_id}", json=schedule)
            response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"更新课表失败: {e}")
            return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """删除课表"""
        try:
            response = self.session.delete(f"{self.base_url}/schedules/{schedule_id}")
            response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"删除课表失败: {e}")
            return False
    
    def get_temp_changes(self) -> List[Dict[str, Any]]:
        """获取临时换课记录"""
        cache_key = 'temp_changes'
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            response = self.session.get(f"{self.base_url}/temp_changes")
            response.raise_for_status()
            data = response.json()
            
            # 缓存数据
            self._set_cache(cache_key, data)
            return data
        except requests.RequestException as e:
            logger.error(f"获取临时换课记录失败: {e}")
            return []
    
    def update_temp_change(self, temp_change_id: str, temp_change: Dict[str, Any]) -> bool:
        """更新临时换课记录"""
        try:
            response = self.session.put(f"{self.base_url}/temp_changes/{temp_change_id}", json=temp_change)
            response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"更新临时换课记录失败: {e}")
            return False
    
    def delete_temp_change(self, temp_change_id: str) -> bool:
        """删除临时换课记录"""
        try:
            response = self.session.delete(f"{self.base_url}/temp_changes/{temp_change_id}")
            response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"删除临时换课记录失败: {e}")
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """获取设置"""
        cache_key = 'settings'
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            response = self.session.get(f"{self.base_url}/settings")
            response.raise_for_status()
            data = response.json()
            
            # 缓存数据
            self._set_cache(cache_key, data)
            return data
        except requests.RequestException as e:
            logger.error(f"获取设置失败: {e}")
            return {}
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """保存设置"""
        try:
            response = self.session.put(f"{self.base_url}/settings", json=settings)
            response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"保存设置失败: {e}")
            return False
    
    def get_today_schedule(self) -> Dict[str, Any]:
        """获取今日课表"""
        cache_key = 'today_schedule'
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            response = self.session.get(f"{self.base_url}/today_schedule")
            response.raise_for_status()
            data = response.json()
            
            # 缓存数据
            self._set_cache(cache_key, data)
            return data
        except requests.RequestException as e:
            logger.error(f"获取今日课表失败: {e}")
            return {"type": "none"}
    
    def get_weather(self) -> Optional[Dict[str, Any]]:
        """获取天气数据"""
        cache_key = 'weather'
        
        # 检查缓存
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            response = self.session.get(f"{self.base_url}/weather")
            response.raise_for_status()
            data = response.json()
            
            # 缓存数据
            self._set_cache(cache_key, data)
            return data
        except requests.RequestException as e:
            logger.error(f"获取天气数据失败: {e}")
            return None
    
    def save_schedules(self, schedules: List[Dict[str, Any]]) -> bool:
        """保存课表"""
        try:
            success = True
            for schedule in schedules:
                # 发送单个课表对象
                response = self.session.post(f"{self.base_url}/schedules", json=schedule)
                # 检查响应状态码，409表示数据已存在，这是预期的行为
                if response.status_code != 409:
                    response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"保存课表失败: {e}")
            return False
    
    def save_temp_changes(self, temp_changes: List[Dict[str, Any]]) -> bool:
        """保存临时换课记录"""
        try:
            success = True
            for temp_change in temp_changes:
                # 发送单个临时换课记录对象
                response = self.session.post(f"{self.base_url}/temp_changes", json=temp_change)
                # 检查响应状态码，409表示数据已存在，这是预期的行为
                if response.status_code != 409:
                    response.raise_for_status()
            
            # 清除缓存
            self._clear_cache()
            return True
        except requests.RequestException as e:
            logger.error(f"保存临时换课记录失败: {e}")
            return False