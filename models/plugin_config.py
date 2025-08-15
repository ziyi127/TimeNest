"""
插件配置数据模型
定义插件配置相关的核心数据结构
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path


@dataclass
class PluginConfig:
    """插件配置模型类"""
    id: str
    name: str
    version: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.config is None:
            self.config = {}
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}
    
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
            config=data.get('config', {}),
            dependencies=data.get('dependencies', []),
            metadata=data.get('metadata', {})
        )
    
    def save_to_file(self, filepath: str) -> bool:
        """
        保存配置到文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存插件配置失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: str) -> Optional['PluginConfig']:
        """
        从文件加载配置
        
        Args:
            filepath: 文件路径
            
        Returns:
            Optional[PluginConfig]: 插件配置实例或None
        """
        try:
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"加载插件配置失败: {e}")
            return None
