"""
用户设置模型类
"""

from typing import Dict, Any, Set
from dataclasses import dataclass, asdict, field


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
    
    # 跟踪变更的字段
    _changed_fields: Set[str] = field(default_factory=set, init=False, repr=False)
    
    def __post_init__(self):
        if self.window_position is None:
            self.window_position = {"x": 100, "y": 100}
    
    def __setattr__(self, name, value):
        """重写__setattr__方法以跟踪变更的字段"""
        # 如果是_dataclass_fields__中的字段，则添加到变更字段集合中
        if hasattr(self, '_changed_fields') and name in self.__dataclass_fields__:
            super().__setattr__(name, value)
            self._changed_fields.add(name)
        else:
            super().__setattr__(name, value)
    
    def get_changed_fields(self) -> Dict[str, Any]:
        """获取变更的字段及其值"""
        return {field: getattr(self, field) for field in self._changed_fields}
    
    def clear_changed_fields(self):
        """清空变更字段记录"""
        self._changed_fields.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 创建字典副本并确保window_position字段正确序列化
        result = asdict(self)
        result['window_position'] = self.window_position.copy()
        result['update_interval'] = self.update_interval
        # 移除内部字段
        result.pop('_changed_fields', None)
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
