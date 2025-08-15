"""
<<<<<<< HEAD
通知数据模型
定义系统通知相关的核心数据结构
=======
通知模型类
用于通知管理功能
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    """通知模型类"""
    id: str
    title: str
    content: str
    created_at: str  # 日期格式: YYYY-MM-DD HH:MM:SS
    is_read: bool = False
    priority: str = "normal"  # "low", "normal", "high"
    category: str = "general"  # 通知分类
    target_users: Optional[List[str]] = None  # 目标用户列表，空列表表示所有用户
    
    def __post_init__(self):
        """初始化后处理"""
        if self.target_users is None:
            self.target_users = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'is_read': self.is_read,
            'priority': self.priority,
            'category': self.category,
            'target_users': self.target_users
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """从字典创建Notification实例"""
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            created_at=data['created_at'],
            is_read=data.get('is_read', False),
            priority=data.get('priority', 'normal'),
            category=data.get('category', 'general'),
            target_users=data.get('target_users', [])
        )
