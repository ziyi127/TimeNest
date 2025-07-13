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
Plugin Message Bus with Type Safety
Provides type-safe message passing between plugins with delivery guarantees
"""

import logging
import threading
import uuid
import time
from typing import Dict, List, Any, Optional, Callable, Type, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.base_manager import BaseManager

T = TypeVar('T')


class MessageType(Enum):
    """Message types for categorization"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    NOTIFICATION = "notification"
    COMMAND = "command"
    QUERY = "query"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class DeliveryMode(Enum):
    """Message delivery modes"""
    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    REQUEST_RESPONSE = "request_response"


@dataclass
class Message(Generic[T]):
    """Type-safe message container"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.EVENT
    topic: str = ""
    sender_id: str = ""
    recipient_id: Optional[str] = None  # None for broadcast
    payload: T = None
    priority: MessagePriority = MessagePriority.NORMAL
    delivery_mode: DeliveryMode = DeliveryMode.FIRE_AND_FORGET
    timestamp: float = field(default_factory=time.time)
    expiry_time: Optional[float] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.expiry_time is None:
            return False
        return time.time() > self.expiry_time
    
    def add_header(self, key: str, value: Any) -> None:
        """Add a header to the message"""
        self.headers[key] = value
    
    def get_header(self, key: str, default: Any = None) -> Any:
        """Get a header value"""
        return self.headers.get(key, default)


@dataclass
class MessageHandler:
    """Message handler registration"""
    handler_id: str
    plugin_id: str
    topic: str
    callback: Callable[[Message], None]
    message_type: Optional[MessageType] = None
    priority_filter: Optional[MessagePriority] = None
    
    def can_handle(self, message: Message) -> bool:
        """Check if this handler can handle the message"""
        # Check topic
        if not self._topic_matches(message.topic):
            return False
        
        # Check message type
        if self.message_type and message.message_type != self.message_type:
            return False
        
        # Check priority filter
        if self.priority_filter and message.priority.value < self.priority_filter.value:
            return False
        
        return True
    
    def _topic_matches(self, message_topic: str) -> bool:
        """Check if topic matches with wildcard support"""
        if self.topic == "*":
            return True
        
        
        if self.topic.endswith("*"):
            prefix = self.topic[:-1]
            return message_topic.startswith(prefix)
        
        return self.topic == message_topic


class IMessageFilter(ABC):
    """Interface for message filters"""
    
    @abstractmethod
    def should_process(self, message: Message) -> bool:
        """Determine if message should be processed"""
        pass


class MessageDeliveryTracker:
    """Tracks message delivery status"""
    
    def __init__(self):
        self._delivery_status: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def track_message(self, message: Message, recipients: List[str]) -> None:
        """Start tracking a message"""
        with self._lock:
            self._delivery_status[message.id] = {
                'message': message,
                'recipients': set(recipients),
                'delivered': set(),
                'failed': set(),
                'timestamp': time.time()
            }
    
    def mark_delivered(self, message_id: str, recipient_id: str) -> None:
        """Mark message as delivered to recipient"""
        with self._lock:
            if message_id in self._delivery_status:
                status = self._delivery_status[message_id]
                status.get('delivered').add(recipient_id)
                status.get('failed').discard(recipient_id)
    
    def mark_failed(self, message_id: str, recipient_id: str) -> None:
        """Mark message delivery as failed"""
        with self._lock:
            if message_id in self._delivery_status:
                status = self._delivery_status[message_id]
                status.get('failed').add(recipient_id)
    
    def is_fully_delivered(self, message_id: str) -> bool:
        """Check if message is fully delivered"""
        with self._lock:
            if message_id not in self._delivery_status:
                return False
            
            status = self._delivery_status[message_id]
            return status['delivered'] == status.get('recipients')
    
    def get_delivery_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get delivery status for a message"""
        with self._lock:
            return self._delivery_status.get(message_id)
    
    def cleanup_old_entries(self, max_age_seconds: int = 3600) -> None:
        """Clean up old tracking entries"""
        with self._lock:
            current_time = time.time()
            expired_ids = [
                msg_id for msg_id, status in self._delivery_status.items()
                if current_time - status.get('timestamp') > max_age_seconds:
            ]
            
            for msg_id in expired_ids:
                del self._delivery_status[msg_id]


class PluginMessageBus(BaseManager):
    """
    Plugin Message Bus with Type Safety
    
    Provides type-safe message passing between plugins with delivery guarantees,
    priority handling, and comprehensive routing capabilities.
    """
    
    # Signals
    message_sent = pyqtSignal(str, str)      # message_id, topic
    message_delivered = pyqtSignal(str, str)  # message_id, recipient_id
    message_failed = pyqtSignal(str, str, str)  # message_id, recipient_id, error
    handler_registered = pyqtSignal(str, str)   # handler_id, topic
    handler_unregistered = pyqtSignal(str)      # handler_id
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "PluginMessageBus")
        
        # Message handlers
        self._handlers: Dict[str, MessageHandler] = {}
        self._topic_handlers: Dict[str, List[str]] = {}  # topic -> handler_ids
        
        # Message filters
        self._filters: List[IMessageFilter] = []
        
        # Delivery tracking
        self._delivery_tracker = MessageDeliveryTracker()
        
        # Message queue for async processing
        self._message_queue: List[Message] = []
        self._processing_queue = False
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'messages_sent': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'handlers_registered': 0
        }
        
        # Cleanup timer
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._cleanup_expired_messages)
        self._cleanup_timer.start(60000)  # Cleanup every minute
        
        self.logger.info("Plugin Message Bus initialized")
    
    def initialize(self) -> bool:
        """Initialize the message bus"""
        try:
            self._start_message_processing()
            self.logger.info("Plugin Message Bus initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Plugin Message Bus: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup message bus resources"""
        try:
            self._cleanup_timer.stop()
            self._handlers.clear()
            self._topic_handlers.clear()
            self._message_queue.clear()
            self._filters.clear()
            self.logger.info("Plugin Message Bus cleaned up")
        except Exception as e:
            self.logger.error(f"Error during message bus cleanup: {e}")
    
    def register_handler(self, plugin_id: str, topic: str, callback: Callable[[Message], None],
                        message_type: Optional[MessageType] = None,
                        priority_filter: Optional[MessagePriority] = None) -> str:
        """
        Register a message handler
        
        Args:
            plugin_id: ID of the plugin registering the handler
            topic: Topic to handle (supports wildcards)
            callback: Handler callback function
            message_type: Optional message type filter
            priority_filter: Optional minimum priority filter
            
        Returns:
            Handler ID
        """
        try:
            with self._lock:
                handler_id = f"{plugin_id}_{topic}_{uuid.uuid4().hex[:8]}"
                
                handler = MessageHandler(
                    handler_id=handler_id,
                    plugin_id=plugin_id,
                    topic=topic,
                    callback=callback,
                    message_type=message_type,
                    priority_filter=priority_filter
                )
                
                self._handlers[handler_id] = handler
                
                # Update topic index
                if topic not in self._topic_handlers:
                    self._topic_handlers[topic] = []
                self._topic_handlers[topic].append(handler_id)
                
                # Update statistics
                self._stats['handlers_registered'] = self._stats.get('handlers_registered', 0) + 1
                
                # Emit signal
                self.handler_registered.emit(handler_id, topic)
                
                self.logger.debug(f"Handler registered: {handler_id} for topic {topic}")
                return handler_id

        except Exception as e:
            self.logger.error(f"Error registering handler: {e}")
            raise

    def unregister_handler(self, handler_id: str) -> bool:
        """
        Unregister a message handler

        Args:
            handler_id: ID of the handler to unregister

        Returns:
            True if handler was unregistered successfully
        """
        try:
            with self._lock:
                if handler_id not in self._handlers:
                    self.logger.warning(f"Handler not found: {handler_id}")
                    return False

                handler = self._handlers[handler_id]

                # Remove from handlers
                del self._handlers[handler_id]

                # Update topic index
                if handler.topic in self._topic_handlers:
                    if handler_id in self._topic_handlers[handler.topic]:
                        self._topic_handlers[handler.topic].remove(handler_id)

                    # Clean up empty topic entries
                    if not self._topic_handlers[handler.topic]:
                        del self._topic_handlers[handler.topic]

                # Emit signal
                self.handler_unregistered.emit(handler_id)

                self.logger.debug(f"Handler unregistered: {handler_id}")
                return True

        except Exception as e:
            self.logger.error(f"Error unregistering handler: {e}")
            return False

    def send_message(self, message: Message) -> bool:
        """
        Send a message through the bus

        Args:
            message: Message to send

        Returns:
            True if message was queued successfully
        """
        try:
            # Validate message
            if not self._validate_message(message):
                self.logger.error(f"Invalid message: {message.id}")
                return False

            # Apply filters
            if not self._apply_filters(message):
                self.logger.debug(f"Message filtered out: {message.id}")
                return False

            # Check expiry
            if message.is_expired():
                self.logger.warning(f"Message expired: {message.id}")
                return False

            with self._lock:
                # Add to queue for processing
                self._message_queue.append(message)

                # Update statistics
                self._stats['messages_sent'] = _stats.get('messages_sent', 0) + 1

                # Emit signal
                self.message_sent.emit(message.id, message.topic)

                # Start processing if not already running
                if not self._processing_queue:
                    self._start_message_processing()

                self.logger.debug(f"Message queued: {message.id} for topic {message.topic}")
                return True

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False

    def send_request(self, topic: str, payload: Any, sender_id: str,
                    timeout_seconds: float = 30.0) -> Optional[Message]:
        """
        Send a request and wait for response

        Args:
            topic: Request topic
            payload: Request payload
            sender_id: ID of the sender
            timeout_seconds: Timeout for response

        Returns:
            Response message or None if timeout
        """
        try:
            # Create request message
            request = Message(
                message_type=MessageType.REQUEST,
                topic=topic,
                sender_id=sender_id,
                payload=payload,
                delivery_mode=DeliveryMode.REQUEST_RESPONSE,
                correlation_id=str(uuid.uuid4())
            )

            # Set up response handler
            response_received = threading.Event()
            response_message = None

            def response_handler(msg: Message):
                nonlocal response_message
                if (msg.message_type == MessageType.RESPONSE and:
                    msg.correlation_id == request.correlation_id):
                    response_message = msg
                    response_received.set()

            # Register temporary response handler
            response_topic = f"response.{request.correlation_id}"
            handler_id = self.register_handler(
                sender_id, response_topic, response_handler, MessageType.RESPONSE
            )

            try:
                # Send request
                if not self.send_message(request):
                    return None

                # Wait for response
                if response_received.wait(timeout_seconds):
                    return response_message
                else:
                    self.logger.warning(f"Request timeout: {request.id}")
                    return None

            finally:
                # Cleanup response handler
                self.unregister_handler(handler_id)

        except Exception as e:
            self.logger.error(f"Error sending request: {e}")
            return None

    def add_filter(self, filter_instance: IMessageFilter) -> None:
        """Add a message filter"""
        with self._lock:
            self._filters.append(filter_instance)

    def remove_filter(self, filter_instance: IMessageFilter) -> bool:
        """Remove a message filter"""
        with self._lock:
            if filter_instance in self._filters:
                self._filters.remove(filter_instance)
                return True
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        with self._lock:
            return {
                **self._stats,
                'active_handlers': len(self._handlers),
                'topics_registered': len(self._topic_handlers),
                'queued_messages': len(self._message_queue),
                'active_filters': len(self._filters)
            }

    def _validate_message(self, message: Message) -> bool:
        """Validate message before sending"""
        if not message.topic:
            return False
        if not message.sender_id:
            return False
        return True

    def _apply_filters(self, message: Message) -> bool:
        """Apply message filters"""
        for filter_instance in self._filters:
            try:
                if not filter_instance.should_process(message):
                    return False
            except Exception as e:
                self.logger.error(f"Error in message filter: {e}")
        return True

    def _start_message_processing(self) -> None:
        """Start processing queued messages"""
        if self._processing_queue:
            return

        self._processing_queue = True

        # Process messages in a separate thread to avoid blocking
        def process_messages():
            try:
                while True:
                    with self._lock:
                        if not self._message_queue:
                            self._processing_queue = False
                            break

                        message = self._message_queue.pop(0)

                    # Process message outside of lock
                    self._process_message(message)

            except Exception as e:
                self.logger.error(f"Error processing messages: {e}")
                self._processing_queue = False

        threading.Thread(target=process_messages, daemon=True).start()

    def _process_message(self, message: Message) -> None:
        """Process a single message"""
        try:
            # Find matching handlers
            matching_handlers = self._find_matching_handlers(message)


            if not matching_handlers:
                self.logger.debug(f"No handlers found for message: {message.id} topic: {message.topic}")
                return

            # Track delivery if needed
            if message.delivery_mode != DeliveryMode.FIRE_AND_FORGET:
                recipient_ids = [h.plugin_id for h in matching_handlers]
                self._delivery_tracker.track_message(message, recipient_ids)

            # Deliver to handlers
            for handler in matching_handlers:
                self._deliver_to_handler(message, handler)

        except Exception as e:
            self.logger.error(f"Error processing message {message.id}: {e}")

    def _find_matching_handlers(self, message: Message) -> List[MessageHandler]:
        """Find handlers that match the message"""
        matching_handlers = []

        with self._lock:
            # Check direct topic matches
            if message.topic in self._topic_handlers:
                for handler_id in self._topic_handlers[message.topic]:
                    handler = self._handlers.get(handler_id)
                    if handler and handler.can_handle(message):
                        matching_handlers.append(handler)

            # Check wildcard matches
            for topic, handler_ids in self._topic_handlers.items():
                if topic != message.topic and ("*" in topic):
                    for handler_id in handler_ids:
                        handler = self._handlers.get(handler_id)
                        if handler and handler.can_handle(message):
                            matching_handlers.append(handler)

        # Sort by priority (higher priority first)
        matching_handlers.sort(
            key=lambda h: h.priority_filter.value if h.priority_filter else 0,
            reverse=True
        )

        return matching_handlers

    def _deliver_to_handler(self, message: Message, handler: MessageHandler) -> None:
        """Deliver message to a specific handler"""
        try:
            handler.callback(message)

            # Track successful delivery
            if message.delivery_mode != DeliveryMode.FIRE_AND_FORGET:
                self._delivery_tracker.mark_delivered(message.id, handler.plugin_id)

            # Update statistics
            self._stats['messages_delivered'] = _stats.get('messages_delivered', 0) + 1

            # Emit signal
            self.message_delivered.emit(message.id, handler.plugin_id)

        except Exception as e:
            self.logger.error(f"Error delivering message to handler {handler.handler_id}: {e}")

            # Track failed delivery
            if message.delivery_mode != DeliveryMode.FIRE_AND_FORGET:
                self._delivery_tracker.mark_failed(message.id, handler.plugin_id)

            # Update statistics
            self._stats['messages_failed'] = _stats.get('messages_failed', 0) + 1

            # Emit signal
            self.message_failed.emit(message.id, handler.plugin_id, str(e))

    def _cleanup_expired_messages(self) -> None:
        """Clean up expired messages and tracking data"""
        try:
            self._delivery_tracker.cleanup_old_entries()

            # Remove expired messages from queue
            with self._lock:
                self._message_queue = [msg for msg in self._message_queue if not msg.is_expired()]

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
