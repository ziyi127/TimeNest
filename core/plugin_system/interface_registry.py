#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
Plugin Interface Registry for Service Discovery
Manages plugin service interfaces and enables service discovery between plugins
"""

import logging
import threading
import inspect
from typing import Dict, List, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class ServiceType(Enum):
    """Service types for categorization"""
    NOTIFICATION = "notification"
    THEME = "theme"
    EXPORT = "export"
    INTEGRATION = "integration"
    UTILITY = "utility"
    COMPONENT = "component"
    DATA_PROVIDER = "data_provider"
    UI_EXTENSION = "ui_extension"


@dataclass
class ServiceMethod:
    """Service method definition"""
    name: str
    callable: Callable
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    return_type: Optional[Type] = None
    is_async: bool = False
    
    def __post_init__(self):
        """Extract method signature information"""
        if self.callable:
            sig = inspect.signature(self.callable)
            self.parameters = {
                name: {
                    'type': param.annotation if param.annotation != inspect.Parameter.empty else Any,
                    'default': param.default if param.default != inspect.Parameter.empty else None,
                    'required': param.default == inspect.Parameter.empty
                }
                for name, param in sig.parameters.items():
                if name != 'self':
            }
            
            if sig.return_annotation != inspect.Signature.empty:
                self.return_type = sig.return_annotation
            
            self.is_async = inspect.iscoroutinefunction(self.callable)


@dataclass
class ServiceInterface:
    """Plugin service interface definition"""
    name: str
    version: str
    provider_id: str
    service_type: ServiceType
    description: str = ""
    methods: Dict[str, ServiceMethod] = field(default_factory=dict)
    events: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_method(self, method: ServiceMethod) -> None:
        """Add a method to the service interface"""
        self.methods[method.name] = method
    
    def remove_method(self, method_name: str) -> bool:
        """Remove a method from the service interface"""
        if method_name in self.methods:
            del self.methods[method_name]
            return True
        return False
    
    def has_method(self, method_name: str) -> bool:
        """Check if service has a specific method"""
        return method_name in self.methods
    
    def get_method(self, method_name: str) -> Optional[ServiceMethod]:
        """Get a specific method"""
        return self.methods.get(method_name)
    
    def add_event(self, event_name: str) -> None:
        """Add an event to the service interface"""
        if event_name not in self.events:
            self.events.append(event_name)
    
    def supports_event(self, event_name: str) -> bool:
        """Check if service supports a specific event"""
        return event_name in self.events


class IServiceProvider(ABC):
    """Interface for service providers"""
    
    @abstractmethod
    def get_service_interface(self) -> ServiceInterface:
        """Get the service interface provided by this plugin"""
        pass
    
    @abstractmethod
    def initialize_service(self, registry: 'PluginInterfaceRegistry') -> bool:
        """Initialize the service with the registry"""
        pass
    
    @abstractmethod
    def cleanup_service(self) -> None:
        """Cleanup service resources"""
        pass


class PluginInterfaceRegistry(BaseManager):
    """
    Plugin Interface Registry for Service Discovery
    
    Manages plugin service interfaces and enables service discovery between plugins.
    Provides type-safe method calls and event handling.
    """
    
    # Signals
    service_registered = pyqtSignal(str, str)  # service_name, provider_id
    service_unregistered = pyqtSignal(str, str)  # service_name, provider_id
    service_called = pyqtSignal(str, str, str)  # service_name, method_name, provider_id
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "PluginInterfaceRegistry")
        
        # Service storage
        self._services: Dict[str, ServiceInterface] = {}
        self._service_providers: Dict[str, IServiceProvider] = {}
        
        # Service discovery cache
        self._service_cache: Dict[str, List[str]] = {}
        self._method_cache: Dict[str, Dict[str, ServiceMethod]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Call statistics
        self._call_stats: Dict[str, Dict[str, int]] = {}
        
        self.logger.info("Plugin Interface Registry initialized")
    
    def initialize(self) -> bool:
        """Initialize the registry"""
        try:
            self._clear_caches()
            self.logger.info("Plugin Interface Registry initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Plugin Interface Registry: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup registry resources"""
        try:
            with self._lock:
                # Cleanup all service providers
                for provider in self._service_providers.values():
                    try:
                        provider.cleanup_service()
                    except Exception as e:
                        self.logger.error(f"Error cleaning up service provider: {e}")
                
                self._services.clear()
                self._service_providers.clear()
                self._clear_caches()
            
            self.logger.info("Plugin Interface Registry cleaned up")
        except Exception as e:
            self.logger.error(f"Error during registry cleanup: {e}")
    
    def register_service(self, provider: IServiceProvider) -> bool:
        """
        Register a service provider
        
        Args:
            provider: Service provider instance
            
        Returns:
            bool: True if registration successful
        """
        try:
            with self._lock:
                service_interface = provider.get_service_interface()
                
                # Validate service interface
                if not self._validate_service_interface(service_interface):
                    self.logger.error(f"Invalid service interface: {service_interface.name}")
                    return False
                
                # Check for conflicts
                if service_interface.name in self._services:
                    existing = self._services[service_interface.name]
                    self.logger.warning(
                        f"Service {service_interface.name} already registered by {existing.provider_id}"
                    )
                    return False
                
                # Initialize service
                if not provider.initialize_service(self):
                    self.logger.error(f"Failed to initialize service: {service_interface.name}")
                    return False
                
                # Register service
                self._services[service_interface.name] = service_interface
                self._service_providers[service_interface.name] = provider
                
                # Update caches
                self._update_service_cache(service_interface)
                
                # Emit signal
                self.service_registered.emit(service_interface.name, service_interface.provider_id)
                
                self.logger.info(
                    f"Service registered: {service_interface.name} by {service_interface.provider_id}"
                )
                return True
                
        except Exception as e:
            self.logger.error(f"Error registering service: {e}")
            return False
    
    def unregister_service(self, service_name: str) -> bool:
        """
        Unregister a service
        
        Args:
            service_name: Name of the service to unregister
            
        Returns:
            bool: True if unregistration successful
        """
        try:
            with self._lock:
                if service_name not in self._services:
                    self.logger.warning(f"Service not found: {service_name}")
                    return False
                
                service_interface = self._services[service_name]
                provider = self._service_providers.get(service_name)
                
                # Cleanup provider
                if provider:
                    try:
                        provider.cleanup_service()
                    except Exception as e:
                        self.logger.error(f"Error cleaning up service provider: {e}")
                
                # Remove from registry
                del self._services[service_name]
                if service_name in self._service_providers:
                    del self._service_providers[service_name]
                
                # Update caches
                self._remove_from_cache(service_name)
                
                # Emit signal
                self.service_unregistered.emit(service_name, service_interface.provider_id)
                
                self.logger.info(f"Service unregistered: {service_name}")
                return True

        except Exception as e:
            self.logger.error(f"Error unregistering service: {e}")
            return False

    def discover_services(self, service_type: Optional[ServiceType] = None) -> List[ServiceInterface]:
        """
        Discover available services

        Args:
            service_type: Optional service type filter

        Returns:
            List of available service interfaces
        """
        try:
            with self._lock:
                services = list(self._services.values())


                if service_type:
                    services = [s for s in services if s.service_type == service_type]

                return services

        except Exception as e:
            self.logger.error(f"Error discovering services: {e}")
            return []

    def get_service(self, service_name: str) -> Optional[ServiceInterface]:
        """Get a specific service interface"""
        return self._services.get(service_name)

    def has_service(self, service_name: str) -> bool:
        """Check if a service is available"""
        return service_name in self._services

    def call_service_method(self, service_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        Call a service method with type safety

        Args:
            service_name: Name of the service
            method_name: Name of the method
            *args: Method arguments
            **kwargs: Method keyword arguments

        Returns:
            Method result

        Raises:
            ValueError: If service or method not found
            TypeError: If arguments don't match method signature
        """
        try:
            with self._lock:
                # Get service
                service = self._services.get(service_name)
                if not service:
                    raise ValueError(f"Service not found: {service_name}")

                # Get method
                method = service.get_method(method_name)
                if not method:
                    raise ValueError(f"Method not found: {method_name} in service {service_name}")

                # Validate arguments (basic validation)
                self._validate_method_call(method, args, kwargs)

                # Update statistics
                self._update_call_stats(service_name, method_name)

                # Call method
                result = method.callable(*args, **kwargs)

                # Emit signal
                self.service_called.emit(service_name, method_name, service.provider_id)

                return result

        except Exception as e:
            self.logger.error(f"Error calling service method: {e}")
            raise

    def get_service_methods(self, service_name: str) -> Dict[str, ServiceMethod]:
        """Get all methods for a service"""
        service = self._services.get(service_name)
        return service.methods if service else {}

    def get_call_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get method call statistics"""
        return self._call_stats.copy()

    def _validate_service_interface(self, interface: ServiceInterface) -> bool:
        """Validate service interface"""
        if not interface.name or not interface.version or not interface.provider_id:
            return False

        # Validate methods
        for method in interface.methods.values():
            if not method.name or not method.callable:
                return False

        return True

    def _validate_method_call(self, method: ServiceMethod, args: tuple, kwargs: dict) -> None:
        """Validate method call arguments"""
        # Basic validation - can be enhanced with more sophisticated type checking
        try:
            # Check if callable is valid
            if not callable(method.callable):
                raise TypeError(f"Method {method.name} is not callable")

            # Additional validation can be added here

        except Exception as e:
            raise TypeError(f"Invalid method call: {e}")

    def _update_service_cache(self, interface: ServiceInterface) -> None:
        """Update service discovery cache"""
        service_type_key = interface.service_type.value
        if service_type_key not in self._service_cache:
            self._service_cache[service_type_key] = []


        if interface.name not in self._service_cache[service_type_key]:
            self._service_cache[service_type_key].append(interface.name)

        # Update method cache
        self._method_cache[interface.name] = interface.methods

    def _remove_from_cache(self, service_name: str) -> None:
        """Remove service from cache"""
        # Remove from service cache
        for service_list in self._service_cache.values():
            if service_name in service_list:
                service_list.remove(service_name)

        # Remove from method cache
        if service_name in self._method_cache:
            del self._method_cache[service_name]

    def _clear_caches(self) -> None:
        """Clear all caches"""
        self._service_cache.clear()
        self._method_cache.clear()

    def _update_call_stats(self, service_name: str, method_name: str) -> None:
        """Update call statistics"""
        if service_name not in self._call_stats:
            self._call_stats[service_name] = {}


        if method_name not in self._call_stats[service_name]:
            self._call_stats[service_name][method_name] = 0

        self._call_stats[service_name][method_name] += 1
