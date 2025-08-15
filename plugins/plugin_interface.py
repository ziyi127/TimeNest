"""
插件接口定义模块
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class PluginInterface(ABC):
    """插件接口定义类"""
    
    def __init__(self, plugin_id: str, name: str, version: str):
        """
        初始化插件接口
        
        Args:
            plugin_id: 插件唯一标识符
            name: 插件名称
            version: 插件版本
        """
        self.plugin_id = plugin_id
        self.name = name
        self.version = version
        self.enabled = False
    
    @abstractmethod
    def initialize(self, app_context: Any) -> bool:
        """
        初始化插件
        
        Args:
            app_context: 应用上下文
            
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        执行插件功能
        
        Args:
            params: 执行参数
            
        Returns:
            Any: 执行结果
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        清理插件资源
        
        Returns:
            bool: 清理是否成功
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取插件元数据
        
        Returns:
            Dict[str, Any]: 插件元数据
        """
        return {
            "id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled
        }