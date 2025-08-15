"""
用户界面相关插件接口
<<<<<<< HEAD
定义用户界面相关插件的标准接口
=======
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from plugins.plugin_interface import PluginInterface


class UIPluginInterface(PluginInterface, ABC):
    """用户界面相关插件接口"""
    
    @abstractmethod
    def render_widget(self, widget_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        渲染UI组件
        
        Args:
            widget_id: 组件ID
            params: 组件参数
            
        Returns:
            str: 渲染后的HTML或组件代码
        """
        pass
    
    @abstractmethod
    def handle_ui_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        处理UI事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            
        Returns:
            bool: 是否处理成功
        """
        pass
    
    @abstractmethod
    def get_ui_config(self) -> Dict[str, Any]:
        """
        获取UI配置
        
        Returns:
            Dict[str, Any]: UI配置信息
        """
        pass