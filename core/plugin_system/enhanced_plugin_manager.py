#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Plugin Manager
Integrates all plugin system components for comprehensive plugin management
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from functools import lru_cache
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager
from core.plugin_base import IPlugin, PluginMetadata, PluginStatus
from .interface_registry import PluginInterfaceRegistry, IServiceProvider
from .dependency_validator import DependencyValidator, PluginDependency, ValidationResult
from .message_bus import PluginMessageBus
from .communication_bus import PluginCommunicationBus, EventType


class EnhancedPluginManager(BaseManager):
    """
    Enhanced Plugin Manager
    
    Integrates interface registry, dependency validation, message bus, and communication bus
    for comprehensive plugin management with inter-plugin communication capabilities.
    """
    
    # Signals
    plugin_loaded = pyqtSignal(str, str)  # plugin_id, plugin_name
    plugin_unloaded = pyqtSignal(str)     # plugin_id
    plugin_activated = pyqtSignal(str)    # plugin_id
    plugin_deactivated = pyqtSignal(str)  # plugin_id
    plugin_error = pyqtSignal(str, str)   # plugin_id, error_message
    dependency_validation_completed = pyqtSignal(str, bool)  # plugin_id, is_valid
    
    def __init__(self, config_manager=None, app_version: str = "1.0.0"):
        super().__init__(config_manager, "EnhancedPluginManager")
        
        self.app_version = app_version
        
        # Core components
        self.interface_registry = PluginInterfaceRegistry(config_manager)
        self.dependency_validator = DependencyValidator(config_manager)
        self.message_bus = PluginMessageBus(config_manager)
        self.communication_bus = PluginCommunicationBus(
            config_manager, self.message_bus, self.interface_registry
        )
        
        # Plugin storage
        self.plugins: Dict[str, IPlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_dependencies: Dict[str, List[PluginDependency]] = {}
        self.validation_results: Dict[str, ValidationResult] = {}
        
        # Plugin directories
        self.plugins_dir = Path.home() / '.timenest' / 'plugins'
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Load order tracking
        self._load_order: List[str] = []
        
        self.logger.info("Enhanced Plugin Manager initialized")
    
    def initialize(self) -> bool:
        """Initialize the enhanced plugin manager"""
        try:
            # Initialize core components
            if not self.interface_registry.initialize():
                self.logger.error("Failed to initialize interface registry")
                return False
            
            if not self.dependency_validator.initialize():
                self.logger.error("Failed to initialize dependency validator")
                return False
            
            if not self.message_bus.initialize():
                self.logger.error("Failed to initialize message bus")
                return False
            
            if not self.communication_bus.initialize():
                self.logger.error("Failed to initialize communication bus")
                return False
            
            # Connect signals
            self._connect_signals()
            
            self.logger.info("Enhanced Plugin Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Enhanced Plugin Manager: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup plugin manager resources"""
        try:
            # Unload all plugins
            self.unload_all_plugins()
            
            # Cleanup core components
            self.communication_bus.cleanup()
            self.message_bus.cleanup()
            self.dependency_validator.cleanup()
            self.interface_registry.cleanup()
            
            self.logger.info("Enhanced Plugin Manager cleaned up")
        except Exception as e:
            self.logger.error(f"Error during plugin manager cleanup: {e}")
    
    def load_plugins(self) -> bool:
        """Load all plugins from the plugins directory"""
        try:
            self.logger.info("Starting plugin loading process...")
            
            # Scan for plugins
            plugin_dirs = [d for d in self.plugins_dir.iterdir() if d.is_dir()]
            
            # First pass: Load metadata and validate dependencies
            plugin_load_plan = []
            
            for plugin_dir in plugin_dirs:
                try:
                    metadata = self._load_plugin_metadata(plugin_dir)
                    if metadata:
                        dependencies = self._extract_dependencies(metadata)
                        validation_result = self.dependency_validator.validate_dependencies(
                            metadata.id, dependencies
                        )
                        
                        self.plugin_metadata[metadata.id] = metadata
                        self.plugin_dependencies[metadata.id] = dependencies
                        self.validation_results[metadata.id] = validation_result
                        
                        if validation_result.is_valid:
                            plugin_load_plan.append((metadata.id, plugin_dir))
                        else:
                            self.logger.warning(
                                f"Plugin {metadata.id} failed validation: {validation_result.errors}"
                            )
                            
                except Exception as e:
                    self.logger.error(f"Error processing plugin directory {plugin_dir.name}: {e}")
            
            # Second pass: Load plugins in dependency order
            loaded_count = 0
            for plugin_id, plugin_dir in self._sort_by_dependencies(plugin_load_plan):
                if self._load_single_plugin(plugin_id, plugin_dir):
                    loaded_count += 1
            
            self.logger.info(f"Plugin loading completed. Loaded {loaded_count} plugins.")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading plugins: {e}")
            return False
    
    def load_plugin(self, plugin_path: Path) -> bool:
        """Load a single plugin"""
        try:
            metadata = self._load_plugin_metadata(plugin_path)
            if not metadata:
                return False
            
            # Validate dependencies
            dependencies = self._extract_dependencies(metadata)
            validation_result = self.dependency_validator.validate_dependencies(
                metadata.id, dependencies
            )
            
            if not validation_result.is_valid:
                self.logger.error(f"Plugin {metadata.id} failed validation: {validation_result.errors}")
                self.plugin_error.emit(metadata.id, "; ".join(validation_result.errors))
                return False
            
            return self._load_single_plugin(metadata.id, plugin_path)
            
        except Exception as e:
            self.logger.error(f"Error loading plugin from {plugin_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin"""
        try:
            if plugin_id not in self.plugins:
                self.logger.warning(f"Plugin not loaded: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            
            # Deactivate if active
            if plugin.get_status() == PluginStatus.ENABLED:
                self.deactivate_plugin(plugin_id)
            
            # Unregister services
            if isinstance(plugin, IServiceProvider):
                self.interface_registry.unregister_service(plugin_id)
            
            # Unsubscribe from events
            self.communication_bus.unsubscribe_plugin(plugin_id)
            
            # Cleanup plugin
            plugin.cleanup()
            
            # Remove from storage
            del self.plugins[plugin_id]
            if plugin_id in self._load_order:
                self._load_order.remove(plugin_id)
            
            # Publish unload event
            self.communication_bus.publish_system_event(
                EventType.PLUGIN_UNLOADED,
                {"plugin_id": plugin_id}
            )
            
            # Emit signal
            self.plugin_unloaded.emit(plugin_id)
            
            self.logger.info(f"Plugin unloaded: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def unload_all_plugins(self) -> None:
        """Unload all plugins"""
        # Unload in reverse order to respect dependencies
        for plugin_id in reversed(self._load_order.copy()):
            self.unload_plugin(plugin_id)
    
    def activate_plugin(self, plugin_id: str) -> bool:
        """Activate a plugin"""
        try:
            if plugin_id not in self.plugins:
                self.logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            
            if plugin.get_status() == PluginStatus.ENABLED:
                self.logger.warning(f"Plugin already active: {plugin_id}")
                return True
            
            # Activate plugin
            if plugin.activate():
                plugin.status = PluginStatus.ENABLED
                
                # Register services if applicable
                if isinstance(plugin, IServiceProvider):
                    self.interface_registry.register_service(plugin)
                
                # Emit signal
                self.plugin_activated.emit(plugin_id)
                
                self.logger.info(f"Plugin activated: {plugin_id}")
                return True
            else:
                self.logger.error(f"Failed to activate plugin: {plugin_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error activating plugin {plugin_id}: {e}")
            return False
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate a plugin"""
        try:
            if plugin_id not in self.plugins:
                self.logger.error(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            
            if plugin.get_status() != PluginStatus.ENABLED:
                self.logger.warning(f"Plugin not active: {plugin_id}")
                return True
            
            # Unregister services
            if isinstance(plugin, IServiceProvider):
                self.interface_registry.unregister_service(plugin_id)
            
            # Deactivate plugin
            if plugin.deactivate():
                plugin.status = PluginStatus.DISABLED
                
                # Emit signal
                self.plugin_deactivated.emit(plugin_id)
                
                self.logger.info(f"Plugin deactivated: {plugin_id}")
                return True
            else:
                self.logger.error(f"Failed to deactivate plugin: {plugin_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deactivating plugin {plugin_id}: {e}")
            return False
    
    def get_plugin(self, plugin_id: str) -> Optional[IPlugin]:
        """Get a plugin instance"""
        return self.plugins.get(plugin_id)
    
    def get_plugin_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata"""
        return self.plugin_metadata.get(plugin_id)
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin IDs"""
        return list(self.plugins.keys())
    
    def get_active_plugins(self) -> List[str]:
        """Get list of active plugin IDs"""
        return [
            plugin_id for plugin_id, plugin in self.plugins.items()
            if plugin.get_status() == PluginStatus.ENABLED
        ]
    
    def get_plugin_status(self, plugin_id: str) -> Optional[PluginStatus]:
        """Get plugin status"""
        plugin = self.plugins.get(plugin_id)
        return plugin.get_status() if plugin else None
    
    def get_validation_result(self, plugin_id: str) -> Optional[ValidationResult]:
        """Get plugin validation result"""
        return self.validation_results.get(plugin_id)
    
    def get_interface_registry(self) -> PluginInterfaceRegistry:
        """Get the interface registry"""
        return self.interface_registry
    
    def get_message_bus(self) -> PluginMessageBus:
        """Get the message bus"""
        return self.message_bus
    
    def get_communication_bus(self) -> PluginCommunicationBus:
        """Get the communication bus"""
        return self.communication_bus
    
    def get_dependency_validator(self) -> DependencyValidator:
        """Get the dependency validator"""
        return self.dependency_validator

    def _load_plugin_metadata(self, plugin_dir: Path) -> Optional[PluginMetadata]:
        """Load plugin metadata from directory"""
        try:
            manifest_file = plugin_dir / "plugin.json"
            if not manifest_file.exists():
                self.logger.warning(f"No plugin.json found in {plugin_dir}")
                return None

            # 检查文件大小
            if manifest_file.stat().st_size > 1024 * 100:  # 100KB限制
                self.logger.warning(f"Plugin manifest too large: {manifest_file}")
                return None

            import json
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)

            # Create metadata object
            metadata = PluginMetadata(
                id=manifest_data.get('id', ''),
                name=manifest_data.get('name', ''),
                version=manifest_data.get('version', '1.0.0'),
                description=manifest_data.get('description', ''),
                author=manifest_data.get('author', ''),
                dependencies=manifest_data.get('dependencies', []),
                api_version=manifest_data.get('api_version', '1.0.0'),
                min_app_version=manifest_data.get('min_app_version', '1.0.0'),
                max_app_version=manifest_data.get('max_app_version', ''),
                homepage=manifest_data.get('homepage', ''),
                repository=manifest_data.get('repository', ''),
                license=manifest_data.get('license', ''),
                tags=manifest_data.get('tags', [])
            )

            return metadata

        except Exception as e:
            self.logger.error(f"Error loading plugin metadata from {plugin_dir}: {e}")
            return None

    def _extract_dependencies(self, metadata: PluginMetadata) -> List[PluginDependency]:
        """Extract dependencies from metadata"""
        dependencies = []

        for dep_info in metadata.dependencies:
            if isinstance(dep_info, str):
                # Simple string dependency
                dependencies.append(PluginDependency(
                    name=dep_info,
                    dependency_type=DependencyType.PLUGIN
                ))
            elif isinstance(dep_info, dict):
                # Detailed dependency info
                from .dependency_validator import DependencyType
                dep_type_str = dep_info.get('type', 'plugin')
                dep_type = DependencyType(dep_type_str) if dep_type_str in [t.value for t in DependencyType] else DependencyType.PLUGIN

                dependencies.append(PluginDependency(
                    name=dep_info.get('name', ''),
                    dependency_type=dep_type,
                    version_constraint=dep_info.get('version', '*'),
                    optional=dep_info.get('optional', False),
                    description=dep_info.get('description', '')
                ))

        return dependencies

    def _sort_by_dependencies(self, plugin_load_plan: List[tuple]) -> List[tuple]:
        """Sort plugins by dependency order"""
        # Simple topological sort implementation
        # In a real implementation, you'd want a more robust algorithm

        # For now, just return the original order
        # TODO: Implement proper topological sorting
        return plugin_load_plan

    def _load_single_plugin(self, plugin_id: str, plugin_dir: Path) -> bool:
        """Load a single plugin from directory"""
        try:
            # Import plugin module
            import sys
            import importlib.util

            main_file = plugin_dir / "main.py"
            if not main_file.exists():
                self.logger.error(f"No main.py found in plugin {plugin_id}")
                return False

            # Load module
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_id}", main_file)
            if not spec or not spec.loader:
                self.logger.error(f"Failed to create module spec for plugin {plugin_id}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugin_{plugin_id}"] = module
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, IPlugin) and
                    attr != IPlugin):
                    plugin_class = attr
                    break

            if not plugin_class:
                self.logger.error(f"No plugin class found in {plugin_id}")
                return False

            # Create plugin instance
            plugin_instance = plugin_class()
            plugin_instance.metadata = self.plugin_metadata[plugin_id]
            plugin_instance.status = PluginStatus.LOADED

            # Initialize plugin
            if not plugin_instance.initialize(self):
                self.logger.error(f"Failed to initialize plugin {plugin_id}")
                return False

            # Store plugin
            self.plugins[plugin_id] = plugin_instance
            self._load_order.append(plugin_id)

            # Register with dependency validator
            self.dependency_validator.register_plugin(plugin_id, plugin_instance.metadata.version)

            # Publish load event
            self.communication_bus.publish_system_event(
                EventType.PLUGIN_LOADED,
                {"plugin_id": plugin_id, "plugin_name": plugin_instance.metadata.name}
            )

            # Emit signal
            self.plugin_loaded.emit(plugin_id, plugin_instance.metadata.name)

            self.logger.info(f"Plugin loaded successfully: {plugin_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_id}: {e}")
            return False

    def _connect_signals(self) -> None:
        """Connect internal signals"""
        try:
            # Connect dependency validator signals
            self.dependency_validator.validation_completed.connect(
                self.dependency_validation_completed
            )

            # Connect interface registry signals
            self.interface_registry.service_registered.connect(
                lambda name, provider: self.logger.debug(f"Service registered: {name} by {provider}")
            )

        except Exception as e:
            self.logger.error(f"Error connecting signals: {e}")
