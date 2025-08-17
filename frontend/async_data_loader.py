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

# 配置日志
logging.basicConfig(level=logging.INFO)
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
    
    # 定义信号
    data_loaded = Signal(str, object, bool, str)  # data_type, data, success, error
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.thread_pool = QThreadPool.globalInstance()
        
        # 本地数据存储路径
        self.local_data_dir = Path(project_root) / "local_data"
        self.local_data_dir.mkdir(exist_ok=True)
    
    def load_data_async(self, data_type: str):
        """异步加载数据"""
        def callback(result: DataLoadResult):
            # 发送信号
            self.data_loaded.emit(result.data_type, result.data, result.success, result.error or "")
            
            # 保存到本地存储
            if result.success:
                self._save_to_local_storage(result.data_type, result.data)
        
        # 创建工作线程
        worker = DataLoadWorker(self.api_client, data_type, callback)
        
        # 启动线程
        self.thread_pool.start(worker)
    
    def load_all_data_async(self, data_types: List[str] = None):
        """异步加载所有数据"""
        if data_types is None:
            data_types = ["courses", "schedules", "temp_changes", "settings", "today_schedule", "weather"]
        
        for data_type in data_types:
            self.load_data_async(data_type)
    
    def load_incremental_data_async(self, data_types: List[str] = None):
        """增量异步加载数据，只加载发生变化的数据类型"""
        if data_types is None:
            data_types = ["courses", "schedules", "temp_changes", "settings", "today_schedule", "weather"]
        
        # TODO: 实现增量加载逻辑，检查数据是否发生变化
        # 这里可以添加检查数据变化的逻辑，例如通过ETag或Last-Modified头
        # 暂时先调用普通异步加载
        for data_type in data_types:
            self.load_data_async(data_type)
    
    def load_data_with_local_fallback(self, data_type: str):
        """加载数据，优先从本地存储加载，然后在后台更新"""
        # 首先从本地存储加载
        local_data = self._load_from_local_storage(data_type)
        if local_data is not None:
            # 发送本地数据
            self.data_loaded.emit(data_type, local_data, True, "")
        
        # 然后在后台更新数据
        self.load_data_async(data_type)
    
    def load_all_data_with_local_fallback(self, data_types: List[str] = None):
        """加载所有数据，优先从本地存储加载，然后在后台更新"""
        if data_types is None:
            data_types = ["courses", "schedules", "temp_changes", "settings", "today_schedule", "weather"]
        
        for data_type in data_types:
            self.load_data_with_local_fallback(data_type)
    
    def load_incremental_data_with_local_fallback(self, data_types: List[str] = None):
        """增量加载数据，优先从本地存储加载，然后在后台更新"""
        if data_types is None:
            data_types = ["courses", "schedules", "temp_changes", "settings", "today_schedule", "weather"]
        
        # TODO: 实现增量加载逻辑，检查数据是否发生变化
        # 这里可以添加检查数据变化的逻辑，例如通过ETag或Last-Modified头
        # 暂时先调用普通异步加载
        for data_type in data_types:
            self.load_data_with_local_fallback(data_type)
    
    def _save_to_local_storage(self, data_type: str, data: Any):
        """保存数据到本地存储"""
        try:
            file_path = self.local_data_dir / f"{data_type}.json"
            # 对于较大的数据，使用更紧凑的JSON格式
            if isinstance(data, (list, dict)) and len(str(data)) > 1000:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存{data_type}数据到本地存储失败: {str(e)}")
    
    def _load_from_local_storage(self, data_type: str) -> Optional[Any]:
        """从本地存储加载数据"""
        try:
            file_path = self.local_data_dir / f"{data_type}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"从本地存储加载{data_type}数据失败: {str(e)}")
            return None
    
    def _save_compressed_to_local_storage(self, data_type: str, data: Any):
        """保存压缩数据到本地存储"""
        try:
            import gzip
            file_path = self.local_data_dir / f"{data_type}.json.gz"
            with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        except Exception as e:
            logger.error(f"保存压缩{data_type}数据到本地存储失败: {str(e)}")
    
    def _load_compressed_from_local_storage(self, data_type: str) -> Optional[Any]:
        """从本地存储加载压缩数据"""
        try:
            import gzip
            file_path = self.local_data_dir / f"{data_type}.json.gz"
            if file_path.exists():
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"从本地存储加载压缩{data_type}数据失败: {str(e)}")
            return None