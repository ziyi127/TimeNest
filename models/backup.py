"""
备份模型类
用于数据备份和恢复功能
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class BackupInfo:
    """备份信息模型"""
    id: str                           # 备份ID
    name: str                         # 备份名称
    created_at: str                   # 创建时间，日期格式: YYYY-MM-DD HH:MM:SS
    file_path: str                    # 备份文件路径
    file_size: int = 0                # 文件大小（字节）
    description: str = ""             # 备份描述
    version: str = "1.0"              # 备份版本
    include_courses: bool = True      # 是否包含课程数据
    include_schedules: bool = True    # 是否包含课程表数据
    include_temp_changes: bool = True # 是否包含临时换课数据
    include_cycle_schedules: bool = True # 是否包含循环课程表数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'description': self.description,
            'version': self.version,
            'include_courses': self.include_courses,
            'include_schedules': self.include_schedules,
            'include_temp_changes': self.include_temp_changes,
            'include_cycle_schedules': self.include_cycle_schedules
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """从字典创建BackupInfo实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            created_at=data['created_at'],
            file_path=data['file_path'],
            file_size=data.get('file_size', 0),
            description=data.get('description', ''),
            version=data.get('version', '1.0'),
            include_courses=data.get('include_courses', True),
            include_schedules=data.get('include_schedules', True),
            include_temp_changes=data.get('include_temp_changes', True),
            include_cycle_schedules=data.get('include_cycle_schedules', True)
        )


@dataclass
class BackupConfig:
    """备份配置模型"""
    auto_backup_enabled: bool = False        # 是否启用自动备份
    auto_backup_interval: int = 24           # 自动备份间隔（小时）
    max_backup_count: int = 10               # 最大备份数量
    backup_location: str = "./data/backups"  # 备份存储位置
    compress_backup: bool = True             # 是否压缩备份文件
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'auto_backup_enabled': self.auto_backup_enabled,
            'auto_backup_interval': self.auto_backup_interval,
            'max_backup_count': self.max_backup_count,
            'backup_location': self.backup_location,
            'compress_backup': self.compress_backup
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupConfig':
        """从字典创建BackupConfig实例"""
        return cls(
            auto_backup_enabled=data.get('auto_backup_enabled', False),
            auto_backup_interval=data.get('auto_backup_interval', 24),
            max_backup_count=data.get('max_backup_count', 10),
            backup_location=data.get('backup_location', './data/backups'),
            compress_backup=data.get('compress_backup', True)
        )