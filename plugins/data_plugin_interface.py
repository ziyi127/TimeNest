"""
数据处理相关插件接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from plugins.plugin_interface import PluginInterface


class DataPluginInterface(PluginInterface, ABC):
    """数据处理相关插件接口"""
    
    @abstractmethod
    def process_data(self, data: Any, processor_config: Optional[Dict[str, Any]] = None) -> Any:
        """
        处理数据
        
        Args:
            data: 待处理的数据
            processor_config: 处理器配置
            
        Returns:
            Any: 处理后的数据
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Any, validation_rules: Optional[Dict[str, Any]] = None) -> bool:
        """
        验证数据
        
        Args:
            data: 待验证的数据
            validation_rules: 验证规则
            
        Returns:
            bool: 数据是否有效
        """
        pass
    
    @abstractmethod
    def transform_data(self, data: Any, transformation_rules: Dict[str, Any]) -> Any:
        """
        转换数据
        
        Args:
            data: 待转换的数据
            transformation_rules: 转换规则
            
        Returns:
            Any: 转换后的数据
        """
        pass
    
    @abstractmethod
    def export_data(self, data: Any, export_format: str, export_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        导出数据
        
        Args:
            data: 待导出的数据
            export_format: 导出格式
            export_config: 导出配置
            
        Returns:
            bool: 是否导出成功
        """
        pass
    
    @abstractmethod
    def import_data(self, source: str, import_config: Optional[Dict[str, Any]] = None) -> Any:
        """
        导入数据
        
        Args:
            source: 数据源
            import_config: 导入配置
            
        Returns:
            Any: 导入的数据
        """
        pass