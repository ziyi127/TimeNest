"""
<<<<<<< HEAD
用户设置数据模型
定义用户个性化设置相关的核心数据结构
=======
用户设置模型类
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
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
    window_position: dict = None  # 窗口位置
    update_interval: int = 1000  # 更新间隔（毫秒）
    
    def __post_init__(self):
        if self.window_position is None:
            self.window_position = {"x": 100, "y": 100}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 创建字典副本并确保window_position字段正确序列化
        result = asdict(self)
        result['window_position'] = self.window_position.copy()
        result['update_interval'] = self.update_interval
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSettings':
        """从字典创建UserSettings实例"""
        return cls(
            theme=data.get('theme', 'light'),
            language=data.get('language', 'zh-CN'),
            auto_backup=data.get('auto_backup', True),
            backup_interval=data.get('backup_interval', 24),
            data_dir=data.get('data_dir', './data'),
            window_position=data.get('window_position', {"x": 100, "y": 100}),
            update_interval=data.get('update_interval', 1000)
        )
