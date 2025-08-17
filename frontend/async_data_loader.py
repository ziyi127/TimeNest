#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
异步数据加载器
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import sys
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

# 导入PySide6模块
from PySide6.QtCore import QRunnable, QThreadPool, Signal, QObject, QThread

# 配置日志 - 减少日志输出以提高性能
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class DataLoadResult:
    """数据加载结果"""
    data_type: str
    data: Any
    success: bool
    error: Optional[str] = None


class DataLoadWorker(QRunnable):
    """数据加载工作线程"""
    
    def __init__(self, api_client, data_type: str, callback: Callable):
        super().__init__()
        self.api_client = api_client
        self.data_type = data_type
        self.callback = callback
        self.setAutoDelete(True)
    
    def run(self):
        """执行数据加载任务"""
        try:
            if self.data_type == "courses":
                data = self.api_client.get_courses()
                result = DataLoadResult(data_type=self.data_type, data=data, success=True)
            elif self.data_type == "schedules":
                data = self.api_client.get_schedules()
                result = DataLoadResult(data_type=self.data_type, data=data, success=True)
            elif self.data_type == "temp_changes":
                data = self.api_client.get_temp_changes()
                result = DataLoadResult(data_type=self.data_type, data=data, success=True)
            elif self.data_type == "settings":
                data = self.api_client.get_settings()
                result = DataLoadResult(data_type=self.data_type, data=data, success=True)
            elif self.data_type == "today_schedule":
                data = self.api_client.get_today_schedule()
                result = DataLoadResult(data_type=self.data_type, data=data, success=True)
            elif self.data_type == "weather":
                data = self.api_client.get_weather()
                result = DataLoadResult(data_type=self.data_type, data=data, success=True)
            else:
                result = DataLoadResult(data_type=self.data_type, data=None, success=False, 
                                     error=f"Unknown data type: {self.data_type}")
        except Exception as e:
            logger.error(f"加载{self.data_type}数据失败: {str(e)}")
            result = DataLoadResult(data_type=self.data_type, data=None, success=False, 
                                 error=str(e))
        
        # 调用回调函数
        self.callback(result)


class AsyncDataLoader(QObject):
    """异步数据加载器"""
    
    # 数据加载完成信号
    data_loaded = Signal(str, object, bool, str)  # data_type, data, success, error
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.thread_pool = QThreadPool()
        logger.debug(f"线程池最大线程数: {self.thread_pool.maxThreadCount()}")
    
    def load_data_async(self, data_type: str):
        """异步加载指定类型的数据"""
        worker = DataLoadWorker(self.api_client, data_type, self._on_data_loaded)
        self.thread_pool.start(worker)
    
    def load_incremental_data_async(self) -> Dict[str, Any]:
        """
        增量异步加载数据
        返回已缓存的数据，并在后台更新
        """
        # 先返回已有的数据
        result = {}
        
        # 检查缓存中的数据
        for data_type in ["courses", "schedules", "temp_changes", "settings"]:
            cached_data = self.api_client._get_from_cache(data_type)
            if cached_data is not None:
                result[data_type] = cached_data
        
        # 在后台异步加载所有数据
        for data_type in ["courses", "schedules", "temp_changes", "settings"]:
            self.load_data_async(data_type)
        
        return result
    
    def _on_data_loaded(self, result: DataLoadResult):
        """数据加载完成的回调函数"""
        # 更新API客户端的缓存
        if result.success and result.data is not None:
            self.api_client._set_cache(result.data_type, result.data)
        
        # 发出信号
        self.data_loaded.emit(result.data_type, result.data, result.success, result.error or "")