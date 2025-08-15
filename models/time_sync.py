"""
时间同步数据模型
定义时间同步相关的核心数据结构
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class TimeSyncSettings:
    """时间同步设置模型类"""
    enabled: bool = True
    sync_interval: int = 60  # 分钟
    ntp_server: str = "pool.ntp.org"
    enable_auto_sync: bool = True
    sync_on_startup: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSyncSettings':
        """从字典创建TimeSyncSettings实例"""
        return cls(
            enabled=data.get('enabled', True),
            sync_interval=data.get('sync_interval', 60),
            ntp_server=data.get('ntp_server', 'pool.ntp.org'),
            enable_auto_sync=data.get('enable_auto_sync', True),
            sync_on_startup=data.get('sync_on_startup', True)
        )