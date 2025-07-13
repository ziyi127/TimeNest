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
Plugin Communication Bus
Event-driven communication system for loose coupling between plugins
"""

import logging
import threading
import asyncio
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager
from .message_bus import PluginMessageBus, Message, MessageType, MessagePriority
from .interface_registry import PluginInterfaceRegistry


class EventType(Enum):
    """Event types for the communication bus"""
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_UNLOADED = "plugin_unloaded"
    SERVICE_REGISTERED = "service_registered"
    SERVICE_UNREGISTERED = "service_unregistered"
    CONFIGURATION_CHANGED = "configuration_changed"
    SCHEDULE_UPDATED = "schedule_updated"
    NOTIFICATION_SENT = "notification_sent"
    THEME_CHANGED = "theme_changed"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    CUSTOM = "custom"


@dataclass
class CommunicationEvent:
    """Communication event data structure"""
    event_type: EventType
    source_plugin: str
    data: Any = None
    target_plugins: Optional[List[str]] = None  # None for broadcast
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the event"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)


class EventSubscription:
    """Event subscription information"""
    
    def __init__(self, plugin_id: str, event_type: EventType, callback: Callable[[CommunicationEvent], None],
                 filter_func: Optional[Callable[[CommunicationEvent], bool]] = None):
        self.plugin_id = plugin_id
        self.event_type = event_type
        self.callback = callback
        self.filter_func = filter_func
        self.subscription_id = f"{plugin_id}_{event_type.value}_{id(callback)}"
    
    def should_handle(self, event: CommunicationEvent) -> bool:
        """Check if this subscription should handle the event"""
        if event.event_type != self.event_type and self.event_type != EventType.CUSTOM:
            return False
        
        
        if self.filter_func:
            try:
                return self.filter_func(event)
            except Exception:
                return False
        
        return True
    
    def handle_event(self, event: CommunicationEvent) -> None:
        """Handle the event"""
        try:
            self.callback(event)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error handling event in {self.plugin_id}: {e}")


class PluginCommunicationBus(BaseManager):
    """
    Plugin Communication Bus
    
    Provides event-driven communication system for loose coupling between plugins.
    Integrates with the message bus and interface registry for comprehensive communication.
    """
    
    # Signals
    event_published = pyqtSignal(str, str)  # event_type, source_plugin
    subscription_added = pyqtSignal(str, str)  # plugin_id, event_type
    subscription_removed = pyqtSignal(str, str)  # plugin_id, event_type
    
    def __init__(self, config_manager=None, message_bus: Optional[PluginMessageBus] = None,
                 interface_registry: Optional[PluginInterfaceRegistry] = None):
        super().__init__(config_manager, "PluginCommunicationBus")
        
        # Core components
        self.message_bus = message_bus
        self.interface_registry = interface_registry
        
        # Event subscriptions
        self._subscriptions: Dict[EventType, List[EventSubscription]] = {}
        self._plugin_subscriptions: Dict[str, Set[str]] = {}  # plugin_id -> subscription_ids
        
        # Event history for debugging
        self._event_history: List[CommunicationEvent] = []
        self._max_history_size = 1000
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'events_published': 0,
            'events_delivered': 0,
            'subscriptions_active': 0
        }
        
        self.logger.info("Plugin Communication Bus initialized")
    
    def initialize(self) -> bool:
        """Initialize the communication bus"""
        try:
            # Set up core event handlers
            self._setup_core_event_handlers()
            
            self.logger.info("Plugin Communication Bus initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Plugin Communication Bus: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup communication bus resources"""
        try:
            with self._lock:
                self._subscriptions.clear()
                self._plugin_subscriptions.clear()
                self._event_history.clear()
            
            self.logger.info("Plugin Communication Bus cleaned up")
        except Exception as e:
            self.logger.error(f"Error during communication bus cleanup: {e}")
    
    def subscribe(self, plugin_id: str, event_type: EventType, callback: Callable[[CommunicationEvent], None],
                 filter_func: Optional[Callable[[CommunicationEvent], bool]] = None) -> str:
        """
        Subscribe to events
        
        Args:
            plugin_id: ID of the subscribing plugin
            event_type: Type of event to subscribe to
            callback: Callback function to handle events
            filter_func: Optional filter function for events
            
        Returns:
            Subscription ID
        """
        try:
            with self._lock:
                subscription = EventSubscription(plugin_id, event_type, callback, filter_func)
                
                # Add to subscriptions
                if event_type not in self._subscriptions:
                    self._subscriptions[event_type] = []
                self._subscriptions[event_type].append(subscription)
                
                # Track plugin subscriptions
                if plugin_id not in self._plugin_subscriptions:
                    self._plugin_subscriptions[plugin_id] = set()
                self._plugin_subscriptions[plugin_id].add(subscription.subscription_id)
                
                # Update statistics
                self._stats['subscriptions_active'] = self._stats.get('subscriptions_active', 0) + 1
                
                # Emit signal
                self.subscription_added.emit(plugin_id, event_type.value)
                
                self.logger.debug(f"Plugin {plugin_id} subscribed to {event_type.value}")
                return subscription.subscription_id
                
        except Exception as e:
            self.logger.error(f"Error subscribing to event: {e}")
            raise
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            True if unsubscribed successfully
        """
        try:
            with self._lock:
                # Find and remove subscription
                for event_type, subscriptions in self._subscriptions.items():
                    for i, subscription in enumerate(subscriptions):
                        if subscription.subscription_id == subscription_id:
                            # Remove subscription
                            del subscriptions[i]
                            
                            # Update plugin subscriptions
                            plugin_id = subscription.plugin_id
                            if plugin_id in self._plugin_subscriptions:
                                self._plugin_subscriptions[plugin_id].discard(subscription_id)
                                
                                # Clean up empty plugin entries
                                if not self._plugin_subscriptions[plugin_id]:
                                    del self._plugin_subscriptions[plugin_id]
                            
                            # Update statistics
                            self._stats['subscriptions_active'] = self._stats.get('subscriptions_active', 0) - 1
                            
                            # Emit signal
                            self.subscription_removed.emit(plugin_id, event_type.value)
                            
                            self.logger.debug(f"Unsubscribed: {subscription_id}")
                            return True
                
                self.logger.warning(f"Subscription not found: {subscription_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unsubscribing: {e}")
            return False
    
    def unsubscribe_plugin(self, plugin_id: str) -> int:
        """
        Unsubscribe all events for a plugin
        
        Args:
            plugin_id: ID of the plugin to unsubscribe
            
        Returns:
            Number of subscriptions removed
        """
        try:
            with self._lock:
                if plugin_id not in self._plugin_subscriptions:
                    return 0
                
                subscription_ids = list(self._plugin_subscriptions[plugin_id])
                removed_count = 0
                
                for subscription_id in subscription_ids:
                    if self.unsubscribe(subscription_id):
                        removed_count += 1
                
                self.logger.debug(f"Unsubscribed {removed_count} events for plugin {plugin_id}")
                return removed_count
                
        except Exception as e:
            self.logger.error(f"Error unsubscribing plugin: {e}")
            return 0
    
    def publish_event(self, event: CommunicationEvent) -> int:
        """
        Publish an event to subscribers
        
        Args:
            event: Event to publish
            
        Returns:
            Number of subscribers that received the event
        """
        try:
            with self._lock:
                # Add to history
                self._add_to_history(event)
                
                # Find matching subscriptions
                matching_subscriptions = self._find_matching_subscriptions(event)
                
                # Update statistics
                self._stats['events_published'] = self._stats.get('events_published', 0) + 1
                
                # Emit signal
                self.event_published.emit(event.event_type.value, event.source_plugin)
                
                # Deliver to subscribers (outside of lock to avoid deadlock)
                delivered_count = 0
                
            # Deliver events outside of lock
            for subscription in matching_subscriptions:
                try:
                    subscription.handle_event(event)
                    delivered_count += 1
                    self._stats['events_delivered'] = self._stats.get('events_delivered', 0) + 1
                except Exception as e:
                    self.logger.error(f"Error delivering event to {subscription.plugin_id}: {e}")
            
            # Also send through message bus if available
            if self.message_bus:
                self._send_via_message_bus(event)
            
            self.logger.debug(f"Event {event.event_type.value} delivered to {delivered_count} subscribers")
            return delivered_count
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}")
            return 0
    
    def publish_system_event(self, event_type: EventType, data: Any = None, metadata: Dict[str, Any] = None) -> int:
        """
        Publish a system event
        
        Args:
            event_type: Type of system event
            data: Event data
            metadata: Optional metadata
            
        Returns:
            Number of subscribers that received the event
        """
        event = CommunicationEvent(
            event_type=event_type,
            source_plugin="system",
            data=data,
            metadata=metadata or {}
        )
        
        return self.publish_event(event)
    
    def get_event_history(self, limit: int = 100) -> List[CommunicationEvent]:
        """Get recent event history"""
        with self._lock:
            return self._event_history[-limit:] if limit > 0 else self._event_history.copy()
    
    def get_plugin_subscriptions(self, plugin_id: str) -> List[str]:
        """Get all subscription IDs for a plugin"""
        with self._lock:
            return list(self._plugin_subscriptions.get(plugin_id, set()))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication bus statistics"""
        with self._lock:
            return {
                **self._stats,
                'active_subscriptions': sum(len(subs) for subs in self._subscriptions.values()),
                'subscribed_plugins': len(self._plugin_subscriptions),
                'event_types_subscribed': len(self._subscriptions),
                'history_size': len(self._event_history)
            }
    
    def _find_matching_subscriptions(self, event: CommunicationEvent) -> List[EventSubscription]:
        """Find subscriptions that match the event"""
        matching_subscriptions = []
        
        # Check direct event type matches
        if event.event_type in self._subscriptions:
            for subscription in self._subscriptions[event.event_type]:
                if subscription.should_handle(event):
                    # Check target filtering
                    if event.target_plugins is None or subscription.plugin_id in event.target_plugins:
                        matching_subscriptions.append(subscription)
        
        # Check custom event subscriptions
        if event.event_type == EventType.CUSTOM and EventType.CUSTOM in self._subscriptions:
            for subscription in self._subscriptions[EventType.CUSTOM]:
                if subscription.should_handle(event):
                    if event.target_plugins is None or
                        subscription.plugin_id in event.target_plugins):
                        matching_subscriptions.append(subscription)
        
        return matching_subscriptions
    
    def _add_to_history(self, event: CommunicationEvent) -> None:
        """Add event to history"""
        self._event_history.append(event)
        
        # Trim history if too large
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
    
    def _send_via_message_bus(self, event: CommunicationEvent) -> None:
        """Send event via message bus for cross-system communication"""
        try:
            if not self.message_bus:
                return
            
            message = Message(
                message_type=MessageType.EVENT,
                topic=f"event.{event.event_type.value}",
                sender_id=event.source_plugin,
                payload=event.data,
                priority=MessagePriority.NORMAL
            )
            
            # Add event metadata to message headers
            for key, value in event.metadata.items():
                message.add_header(key, value)
            
            self.message_bus.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending event via message bus: {e}")
    
    def _setup_core_event_handlers(self) -> None:
        """Set up core system event handlers"""
        try:
            # Handle interface registry events
            if self.interface_registry:
                self.interface_registry.service_registered.connect(
                    lambda name, provider: self.publish_system_event(
                        EventType.SERVICE_REGISTERED,
                        {"service_name": name, "provider_id": provider}
                    )
                )
                
                self.interface_registry.service_unregistered.connect(
                    lambda name, provider: self.publish_system_event(
                        EventType.SERVICE_UNREGISTERED,
                        {"service_name": name, "provider_id": provider}
                    )
                )
            
        except Exception as e:
            self.logger.error(f"Error setting up core event handlers: {e}")
