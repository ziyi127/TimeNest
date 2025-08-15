"""
课程简称数据模型
定义课程简称相关的核心数据结构
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class CourseAlias:
    """课程简称模型类"""
    course_id: str
    alias: str
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CourseAlias':
        """从字典创建CourseAlias实例"""
        return cls(
            course_id=data['course_id'],
            alias=data['alias'],
            description=data.get('description', '')
        )


@dataclass
class CourseAliasSettings:
    """课程简称设置模型类"""
    enabled: bool = True
    auto_generate: bool = True
    max_alias_length: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CourseAliasSettings':
        """从字典创建CourseAliasSettings实例"""
        return cls(
            enabled=data.get('enabled', True),
            auto_generate=data.get('auto_generate', True),
            max_alias_length=data.get('max_alias_length', 10)
        )