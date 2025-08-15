"""
插件管理器模块
"""

import os
import importlib.util
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from plugins.plugin_interface import PluginInterface
from models.plugin_config import PluginConfig
from utils.logger import setup_logger


class PluginManager:
    """插件管理器类"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        初始化插件管理器
        
        Args:
            plugins_dir: 插件目录路径
        """
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, PluginConfig] = {}
        self.logger = setup_logger("PluginManager")
        self.app_context: Any = None
        
        # 确保插件目录存在
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建插件目录: {self.plugins_dir}")
            
        # 创建插件配置目录
        configs_dir = self.plugins_dir / "configs"
        if not configs_dir.exists():
            configs_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建插件配置目录: {configs_dir}")
    
    def set_app_context(self, app_context: Any) -> None:
        """
        设置应用上下文
        
        Args:
            app_context: 应用上下文
        """
        self.app_context = app_context
    
    def _check_dependencies(self, plugin: PluginInterface) -> bool:
        """
        检查插件依赖
        
        Args:
            plugin: 插件实例
            
        Returns:
            bool: 依赖是否满足
        """
        # 获取插件配置
        plugin_config = self.plugin_configs.get(plugin.plugin_id)
        if not plugin_config or not plugin_config.dependencies:
            return True
        
        # 检查每个依赖是否已加载
        for dep_id in plugin_config.dependencies:
            if dep_id not in self.plugins:
                self.logger.error(f"插件 {plugin.name} 依赖的插件未加载: {dep_id}")
                return False
        
        return True
    
    def _get_or_create_plugin_config(self, plugin: PluginInterface) -> PluginConfig:
        """
        获取或创建插件配置
        
        Args:
            plugin: 插件实例
            
        Returns:
            PluginConfig: 插件配置
        """
        # 检查是否已存在配置
        if plugin.plugin_id in self.plugin_configs:
            return self.plugin_configs[plugin.plugin_id]
        
        # 创建新的插件配置
        config = PluginConfig(
            id=plugin.plugin_id,
            name=plugin.name,
            version=plugin.version,
            enabled=True
        )
        
        # 保存配置到文件
        config_file = self.plugins_dir / "configs" / f"{plugin.plugin_id}.json"
        config.save_to_file(str(config_file))
        
        return config
    
    def load_plugin_configs(self) -> None:
        """加载所有插件配置"""
        configs_dir = self.plugins_dir / "configs"
        if not configs_dir.exists():
            configs_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建插件配置目录: {configs_dir}")
            return
        
        for config_file in configs_dir.glob("*.json"):
            try:
                # 从文件加载插件配置
                plugin_config = PluginConfig.load_from_file(str(config_file))
                if plugin_config:
                    self.plugin_configs[plugin_config.id] = plugin_config
                    self.logger.info(f"加载插件配置: {plugin_config.name} ({plugin_config.id})")
            except Exception as e:
                self.logger.error(f"加载插件配置失败 {config_file}: {e}")
    
    def discover_plugins(self) -> List[str]:
        """
        发现所有可用的插件
        
        Returns:
            List[str]: 插件模块路径列表
        """
        plugin_modules: List[str] = []
        
        # 遍历插件目录查找插件
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                # 检查是否存在插件主文件
                plugin_main = item / f"{item.name}.py"
                if plugin_main.exists():
                    plugin_modules.append(str(plugin_main))
        
        return plugin_modules
    
    def load_plugin(self, plugin_path: str) -> Optional[PluginInterface]:
        """
        加载指定插件
        
        Args:
            plugin_path: 插件路径
            
        Returns:
            Optional[PluginInterface]: 插件实例或None
        """
        try:
            # 从路径获取插件名称
            plugin_name = Path(plugin_path).stem
            module_name = f"plugins.{plugin_name}.{plugin_name}"
            
            # 加载插件模块
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"无法加载插件模块规范: {plugin_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取插件类（假设类名与模块名相同）
            plugin_class = getattr(module, plugin_name.capitalize(), None)
            if plugin_class is None:
                self.logger.error(f"插件模块中未找到插件类: {plugin_name}")
                return None
            
            # 创建插件实例
            plugin_instance = plugin_class()
            
            # 检查是否实现了PluginInterface
            if not isinstance(plugin_instance, PluginInterface):
                self.logger.error(f"插件 {plugin_name} 未正确实现PluginInterface")
                return None
            
            # 检查插件依赖
            if not self._check_dependencies(plugin_instance):
                self.logger.error(f"插件依赖检查失败: {plugin_instance.name} ({plugin_instance.plugin_id})")
                return None
            
            # 初始化插件
            if plugin_instance.initialize(self.app_context):
                plugin_instance.enabled = True
                self.plugins[plugin_instance.plugin_id] = plugin_instance
                
                # 加载或创建插件配置
                config = self._get_or_create_plugin_config(plugin_instance)
                if config:
                    self.plugin_configs[plugin_instance.plugin_id] = config
                
                self.logger.info(f"成功加载插件: {plugin_instance.name} ({plugin_instance.plugin_id})")
                return plugin_instance
            else:
                self.logger.error(f"插件初始化失败: {plugin_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"加载插件失败 {plugin_path}: {e}")
            return None
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        卸载指定插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            bool: 卸载是否成功
        """
        if plugin_id not in self.plugins:
            self.logger.warning(f"插件未加载: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        try:
            # 清理插件资源
            if plugin.cleanup():
                del self.plugins[plugin_id]
                plugin.enabled = False
                self.logger.info(f"成功卸载插件: {plugin.name} ({plugin_id})")
                return True
            else:
                self.logger.error(f"插件清理失败: {plugin.name} ({plugin_id})")
                return False
        except Exception as e:
            self.logger.error(f"卸载插件时发生错误 {plugin.name} ({plugin_id}): {e}")
            return False
    
    def reload_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """
        重新加载指定插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            Optional[PluginInterface]: 重新加载的插件实例或None
        """
        if plugin_id not in self.plugins:
            self.logger.warning(f"插件未加载: {plugin_id}")
            return None
        
        # 先卸载插件
        if not self.unload_plugin(plugin_id):
            return None
        
        # 重新发现并加载插件
        plugin_modules = self.discover_plugins()
        for module_path in plugin_modules:
            # 这里需要更精确地匹配插件
            # 暂时简化实现
            try:
                plugin = self.load_plugin(module_path)
                if plugin and plugin.plugin_id == plugin_id:
                    return plugin
            except Exception as e:
                self.logger.error(f"重新加载插件失败 {module_path}: {e}")
        
        return None
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """
        获取指定插件实例
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            Optional[PluginInterface]: 插件实例或None
        """
        return self.plugins.get(plugin_id)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        列出所有已加载的插件
        
        Returns:
            List[Dict[str, Any]]: 插件信息列表
        """
        plugin_list: List[Dict[str, Any]] = []
        for plugin in self.plugins.values():
            plugin_list.append(plugin.get_metadata())
        return plugin_list
    
    def execute_plugin(self, plugin_id: str, params: Dict[str, Any]) -> Any:
        """
        执行指定插件
        
        Args:
            plugin_id: 插件ID
            params: 执行参数
            
        Returns:
            Any: 执行结果
        """
        plugin = self.get_plugin(plugin_id)
        if plugin is None:
            self.logger.error(f"插件未找到或未加载: {plugin_id}")
            return None
        
        if not plugin.enabled:
            self.logger.warning(f"插件未启用: {plugin.name} ({plugin_id})")
            return None
        
        try:
            return plugin.execute(params)
        except Exception as e:
            self.logger.error(f"执行插件时发生错误 {plugin.name} ({plugin_id}): {e}")
            return None
    
    def load_all_plugins(self) -> None:
        """加载所有可用插件"""
        self.logger.info("开始加载所有插件")
        
        # 发现插件
        plugin_modules = self.discover_plugins()
        self.logger.info(f"发现 {len(plugin_modules)} 个插件")
        
        # 加载每个插件
        for module_path in plugin_modules:
            try:
                self.load_plugin(module_path)
            except Exception as e:
                self.logger.error(f"加载插件失败 {module_path}: {e}")
        
        self.logger.info(f"插件加载完成，成功加载 {len(self.plugins)} 个插件")
    
    def unload_all_plugins(self) -> None:
        """卸载所有插件"""
        self.logger.info("开始卸载所有插件")
        
        # 创建插件ID列表的副本，因为在迭代时不能修改字典
        plugin_ids = list(self.plugins.keys())
        
        # 卸载每个插件
        for plugin_id in plugin_ids:
            self.unload_plugin(plugin_id)
        
        self.logger.info("所有插件卸载完成")