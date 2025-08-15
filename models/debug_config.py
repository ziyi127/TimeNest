"""
调试配置数据模型
定义调试配置相关的核心数据结构
"""

from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class DebugSettings:
    """调试设置模型类"""
    enabled: bool = False
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "./logs/debug.log"
    max_log_file_size: int = 10  # MB
    enable_performance_monitoring: bool = False
    enable_detailed_logging: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebugSettings':
        """从字典创建DebugSettings实例"""
        return cls(
            enabled=data.get('enabled', False),
            log_level=data.get('log_level', 'INFO'),
            log_to_file=data.get('log_to_file', True),
            log_file_path=data.get('log_file_path', './logs/debug.log'),
            max_log_file_size=data.get('max_log_file_size', 10),
            enable_performance_monitoring=data.get('enable_performance_monitoring', False),
            enable_detailed_logging=data.get('enable_detailed_logging', False)
        )