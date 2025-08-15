"""
插件配置模型类
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PluginConfig:
    """插件配置模型类"""
    id: str
    name: str
    version: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.config is None:
            self.config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfig':
        """从字典创建PluginConfig实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            enabled=data.get('enabled', True),
            config=data.get('config', {})
        )