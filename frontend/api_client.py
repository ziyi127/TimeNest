#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面前端应用
API客户端，用于与后端服务通信
"""

import sys
import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化API客户端
        
        Args:
            base_url: 后端服务的基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        
    def get_courses(self) -> List[Dict[str, Any]]:
        """
        获取所有课程
        
        Returns:
            课程列表
        """
        try:
            response = self.session.get(f"{self.base_url}/api/courses")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取课程失败: {e}")
            return []
            
    def get_schedules(self) -> List[Dict[str, Any]]:
        """
        获取所有课程表项
        
        Returns:
            课程表项列表
        """
        try:
            response = self.session.get(f"{self.base_url}/api/schedules")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取课程表项失败: {e}")
            return []
            
    def get_temp_changes(self) -> List[Dict[str, Any]]:
        """
        获取所有临时换课记录
        
        Returns:
            临时换课记录列表
        """
        try:
            response = self.session.get(f"{self.base_url}/api/temp_changes")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取临时换课记录失败: {e}")
            return []
            
    def get_settings(self) -> Dict[str, Any]:
        """
        获取应用设置
        
        Returns:
            应用设置字典
        """
        try:
            response = self.session.get(f"{self.base_url}/api/settings")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取设置失败: {e}")
            return {}
            
    def save_courses(self, courses: List[Dict[str, Any]]) -> bool:
        """
        保存课程数据
        
        Args:
            courses: 课程列表
            
        Returns:
            保存是否成功
        """
        try:
            response = self.session.post(f"{self.base_url}/api/courses", json=courses)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"保存课程失败: {e}")
            return False
            
    def save_schedules(self, schedules: List[Dict[str, Any]]) -> bool:
        """
        保存课程表项数据
        
        Args:
            schedules: 课程表项列表
            
        Returns:
            保存是否成功
        """
        try:
            response = self.session.post(f"{self.base_url}/api/schedules", json=schedules)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"保存课程表项失败: {e}")
            return False
            
    def save_temp_changes(self, temp_changes: List[Dict[str, Any]]) -> bool:
        """
        保存临时换课记录数据
        
        Args:
            temp_changes: 临时换课记录列表
            
        Returns:
            保存是否成功
        """
        try:
            response = self.session.post(f"{self.base_url}/api/temp_changes", json=temp_changes)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"保存临时换课记录失败: {e}")
            return False
            
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        保存应用设置数据
        
        Args:
            settings: 应用设置字典
            
        Returns:
            保存是否成功
        """
        try:
            response = self.session.post(f"{self.base_url}/api/settings", json=settings)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"保存设置失败: {e}")
            return False
            
    def get_today_schedule(self) -> Dict[str, Any]:
        """
        获取今天的课程安排
        
        Returns:
            今天的课程安排信息
        """
        try:
            response = self.session.get(f"{self.base_url}/api/today_schedule")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取今日课程安排失败: {e}")
            return {"type": "none"}