"""
密码配置数据模型
定义密码安全配置相关的核心数据结构
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class PasswordConfig:
    """密码配置模型类"""
    is_enabled: bool = False  # 是否启用密码保护
    password_hash: str = ""   # 密码哈希值
    salt: str = ""           # 盐值
    created_at: str = ""     # 配置创建时间，日期格式: YYYY-MM-DD HH:MM:SS
    updated_at: str = ""     # 配置更新时间，日期格式: YYYY-MM-DD HH:MM:SS
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PasswordConfig':
        """从字典创建PasswordConfig实例"""
        return cls(
            is_enabled=data.get('is_enabled', False),
            password_hash=data.get('password_hash', ''),
            salt=data.get('salt', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )