#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest Enhanced Plugin System
Enhanced plugin system with inter-plugin communication, dependency validation, and service discovery
"""

from .interface_registry import PluginInterfaceRegistry, ServiceInterface
from .dependency_validator import DependencyValidator, PluginDependency
from .message_bus import PluginMessageBus, Message, MessageType
from .communication_bus import PluginCommunicationBus
from .enhanced_plugin_manager import EnhancedPluginManager

__all__ = [
    'PluginInterfaceRegistry',
    'ServiceInterface', 
    'DependencyValidator',
    'PluginDependency',
    'PluginMessageBus',
    'Message',
    'MessageType',
    'PluginCommunicationBus',
    'EnhancedPluginManager'
]
