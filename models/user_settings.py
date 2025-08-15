"""
用户设置数据模型
定义用户个性化设置相关的核心数据结构
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class UserSettings:
    """用户设置模型类"""
    theme: str = "light"  # 主题设置: light, dark
    language: str = "zh-CN"  # 语言设置
    auto_backup: bool = True  # 是否自动备份
    backup_interval: int = 24  # 自动备份间隔（小时）
    data_dir: str = "./data"  # 数据存储目录
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """从字典创建UserSettings实例"""
        return cls(
            theme=data.get('theme', 'light'),
            language=data.get('language', 'zh-CN'),
            auto_backup=data.get('auto_backup', True),
            backup_interval=data.get('backup_interval', 24),
            data_dir=data.get('data_dir', './data')
        )
