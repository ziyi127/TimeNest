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
Plugin Store Client
Fetches plugin metadata from the TimeNest plugin store
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl

from core.base_manager import BaseManager


@dataclass
class PluginStoreMetadata:
    """Plugin metadata from the store"""
    id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    download_count: int = 0
    star_rating: float = 0.0
    review_count: int = 0
    compatibility_status: str = "unknown"
    last_updated: str = ""
    tags: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    changelog: str = ""
    homepage: str = ""
    repository: str = ""
    license: str = ""
    file_size: int = 0
    download_url: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginStoreMetadata':
        """Create instance from dictionary"""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            author=data.get('author', ''),
            download_count=data.get('download_count', 0),
            star_rating=data.get('star_rating', 0.0),
            review_count=data.get('review_count', 0),
            compatibility_status=data.get('compatibility_status', 'unknown'),
            last_updated=data.get('last_updated', ''),
            tags=data.get('tags', []),
            screenshots=data.get('screenshots', []),
            changelog=data.get('changelog', ''),
            homepage=data.get('homepage', ''),
            repository=data.get('repository', ''),
            license=data.get('license', ''),
            file_size=data.get('file_size', 0),
            download_url=data.get('download_url', '')
        )


@dataclass
class PluginReview:
    """Plugin review data"""
    reviewer: str
    rating: int
    comment: str
    date: str
    helpful_count: int = 0


class PluginStoreClient(BaseManager):
    """
    Plugin Store Client
    
    Fetches plugin metadata, ratings, and reviews from the TimeNest plugin store.
    Provides caching and offline support.
    """
    
    # Signals
    metadata_fetched = pyqtSignal(str, object)  # plugin_id, metadata
    reviews_fetched = pyqtSignal(str, list)     # plugin_id, reviews
    fetch_error = pyqtSignal(str, str)          # plugin_id, error_message
    store_status_changed = pyqtSignal(bool)     # is_online
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "PluginStoreClient")
        
        # Store configuration
        self.store_base_url = "https://raw.githubusercontent.com/ziyi127/TimeNest-Store/main"
        self.api_timeout = 10  # seconds
        
        # Network manager
        self.network_manager = QNetworkAccessManager()
        
        # Cache
        self._metadata_cache: Dict[str, PluginStoreMetadata] = {}
        self._reviews_cache: Dict[str, List[PluginReview]] = {}
        self._cache_expiry = 3600  # 1 hour
        self._last_fetch_time: Dict[str, float] = {}
        
        # Store status
        self._is_online = False
        
        # Status check timer
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_store_status)
        self._status_timer.start(60000)  # Check every minute
        
        self.logger.info("Plugin Store Client initialized")
    
    def initialize(self) -> bool:
        """Initialize the store client"""
        try:
            # Check initial store status
            self._check_store_status()
            
            self.logger.info("Plugin Store Client initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Plugin Store Client: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup store client resources"""
        try:
            self._status_timer.stop()
            self._metadata_cache.clear()
            self._reviews_cache.clear()
            self.logger.info("Plugin Store Client cleaned up")
        except Exception as e:
            self.logger.error(f"Error during store client cleanup: {e}")
    
    def fetch_plugin_metadata(self, plugin_id: str, force_refresh: bool = False) -> None:
        """
        Fetch plugin metadata from store
        
        Args:
            plugin_id: ID of the plugin
            force_refresh: Force refresh from server
        """
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid(plugin_id):
                cached_metadata = self._metadata_cache.get(plugin_id)
                if cached_metadata and hasattr(self, "metadata_fetched"):
                    self.metadata_fetched.emit(plugin_id, cached_metadata)
                    return
            
            # Fetch from server
            self._fetch_from_server(plugin_id, "metadata")
            
        except Exception as e:
            self.logger.error(f"Error fetching metadata for {plugin_id}: {e}")
            self.fetch_error.emit(plugin_id, str(e))
    
    def fetch_plugin_reviews(self, plugin_id: str, force_refresh: bool = False) -> None:
        """
        Fetch plugin reviews from store
        
        Args:
            plugin_id: ID of the plugin
            force_refresh: Force refresh from server
        """
        try:
            # Check cache first
            if not force_refresh and self._is_cache_valid(plugin_id, "reviews"):
                cached_reviews = self._reviews_cache.get(plugin_id)
                if cached_reviews and hasattr(self, "reviews_fetched"):
                    self.reviews_fetched.emit(plugin_id, cached_reviews)
                    return
            
            # Fetch from server
            self._fetch_from_server(plugin_id, "reviews")
            
        except Exception as e:
            self.logger.error(f"Error fetching reviews for {plugin_id}: {e}")
            self.fetch_error.emit(plugin_id, str(e))
    
    def get_cached_metadata(self, plugin_id: str) -> Optional[PluginStoreMetadata]:
        """Get cached metadata for a plugin"""
        return self._metadata_cache.get(plugin_id)
    
    def get_cached_reviews(self, plugin_id: str) -> List[PluginReview]:
        """Get cached reviews for a plugin"""
        return self._reviews_cache.get(plugin_id, [])
    
    def is_store_online(self) -> bool:
        """Check if the plugin store is online"""
        return self._is_online
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._metadata_cache.clear()
        self._reviews_cache.clear()
        self._last_fetch_time.clear()
        self.logger.debug("Plugin store cache cleared")
    
    def _fetch_from_server(self, plugin_id: str, data_type: str) -> None:
        """Fetch data from server"""
        try:
            if data_type == "metadata":
                url = f"{self.store_base_url}/plugins/{plugin_id}/metadata.json"
            elif data_type == "reviews":
                url = f"{self.store_base_url}/plugins/{plugin_id}/reviews.json"
            else:
                raise ValueError(f"Unknown data type: {data_type}")
            
            # Create network request
            request = QNetworkRequest(QUrl(url))
            request.setRawHeader(b"User-Agent", b"TimeNest/1.0")
            
            # Send request
            reply = self.network_manager.get(request)
            
            # Connect response handler
            reply.finished.connect(
                lambda: self._handle_network_response(reply, plugin_id, data_type)
            )
            
        except Exception as e:
            self.logger.error(f"Error creating network request: {e}")
            self.fetch_error.emit(plugin_id, str(e))
    
    def _handle_network_response(self, reply: QNetworkReply, plugin_id: str, data_type: str) -> None:
        """Handle network response"""
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                error_msg = reply.errorString()
                self.logger.error(f"Network error fetching {data_type} for {plugin_id}: {error_msg}")
                self.fetch_error.emit(plugin_id, error_msg)
                return
            
            # Read response data
            data = reply.readAll().data().decode('utf-8')
            json_data = json.loads(data)
            
            # Process response
            if data_type == "metadata":
                self._process_metadata_response(plugin_id, json_data)
            elif data_type == "reviews":
                self._process_reviews_response(plugin_id, json_data)
            
            # Update fetch time
            import time
            self._last_fetch_time[f"{plugin_id}_{data_type}"] = time.time()
            
        except Exception as e:
            self.logger.error(f"Error processing response for {plugin_id}: {e}")
            self.fetch_error.emit(plugin_id, str(e))
        finally:
            reply.deleteLater()
    
    def _process_metadata_response(self, plugin_id: str, data: Dict[str, Any]) -> None:
        """Process metadata response"""
        try:
            metadata = PluginStoreMetadata.from_dict(data)
            self._metadata_cache[plugin_id] = metadata
            self.metadata_fetched.emit(plugin_id, metadata)
            
        except Exception as e:
            self.logger.error(f"Error processing metadata response: {e}")
            self.fetch_error.emit(plugin_id, str(e))
    
    def _process_reviews_response(self, plugin_id: str, data: Dict[str, Any]) -> None:
        """Process reviews response"""
        try:
            reviews = []
            for review_data in data.get('reviews', []):
                review = PluginReview(
                    reviewer=review_data.get('reviewer', ''),
                    rating=review_data.get('rating', 0),
                    comment=review_data.get('comment', ''),
                    date=review_data.get('date', ''),
                    helpful_count=review_data.get('helpful_count', 0)
                )
                reviews.append(review)
            
            self._reviews_cache[plugin_id] = reviews
            self.reviews_fetched.emit(plugin_id, reviews)
            
        except Exception as e:
            self.logger.error(f"Error processing reviews response: {e}")
            self.fetch_error.emit(plugin_id, str(e))
    
    def _is_cache_valid(self, plugin_id: str, data_type: str = "metadata") -> bool:
        """Check if cached data is still valid"""
        import time
        cache_key = f"{plugin_id}_{data_type}"
        
        
        if cache_key not in self._last_fetch_time:
            return False
        
        elapsed = time.time() - self._last_fetch_time[cache_key]
        return elapsed < self._cache_expiry
    
    def _check_store_status(self) -> None:
        """Check if the plugin store is accessible"""
        try:
            # Simple ping to check store availability
            url = f"{self.store_base_url}/status.json"
            request = QNetworkRequest(QUrl(url))
            request.setRawHeader(b"User-Agent", b"TimeNest/1.0")
            
            reply = self.network_manager.get(request)
            reply.finished.connect(lambda: self._handle_status_response(reply))
            
        except Exception as e:
            self.logger.debug(f"Error checking store status: {e}")
            self._update_store_status(False)
    
    def _handle_status_response(self, reply: QNetworkReply) -> None:
        """Handle store status response"""
        try:
            is_online = reply.error() == QNetworkReply.NetworkError.NoError
            self._update_store_status(is_online)
        except Exception:
            self._update_store_status(False)
        finally:
            reply.deleteLater()
    
    def _update_store_status(self, is_online: bool) -> None:
        """Update store online status"""
        if self._is_online != is_online:
            self._is_online = is_online
            self.store_status_changed.emit(is_online)
            self.logger.debug(f"Plugin store status: {'online' if is_online else 'offline'}")
