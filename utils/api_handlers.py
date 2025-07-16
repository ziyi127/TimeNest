#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API handlers and network utilities for TimeNest
Provides safe HTTP requests and API interaction utilities
"""

import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse

from utils.common_imports import requests
from utils.shared_utilities import retry_operation
from utils.config_constants import ERROR_MESSAGES, SUCCESS_MESSAGES

logger = logging.getLogger(__name__)

class APIClient:
    """Safe API client with error handling and retries"""
    
    def __init__(self, base_url: str = "", timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        self.requests_available = requests.available
        
        if self.requests_available:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'TimeNest/2.0.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make HTTP request with error handling"""
        if not self.requests_available:
            logger.error("requests module not available")
            return None
        
        try:
            url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
            
            kwargs.setdefault('timeout', self.timeout)
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {'content': response.text, 'status_code': response.status_code}
                
        except Exception as e:
            logger.error(f"API request failed: {method} {endpoint} - {e}")
            return None
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """GET request"""
        return retry_operation(
            lambda: self._make_request('GET', endpoint, params=params),
            max_retries=self.max_retries
        )
    
    def post(self, endpoint: str, data: Optional[Dict] = None, 
             json: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """POST request"""
        return retry_operation(
            lambda: self._make_request('POST', endpoint, data=data, json=json),
            max_retries=self.max_retries
        )
    
    def put(self, endpoint: str, data: Optional[Dict] = None, 
            json: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """PUT request"""
        return retry_operation(
            lambda: self._make_request('PUT', endpoint, data=data, json=json),
            max_retries=self.max_retries
        )
    
    def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """DELETE request"""
        return retry_operation(
            lambda: self._make_request('DELETE', endpoint),
            max_retries=self.max_retries
        )
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

class WeatherAPI:
    """Weather API handler"""
    
    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key
        self.client = APIClient(base_url)
    
    def get_current_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """Get current weather for a city"""
        if not self.api_key:
            logger.warning("Weather API key not configured")
            return self._get_fallback_weather()
        
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            result = self.client.get('/weather', params=params)
            if result:
                return self._format_weather_data(result)
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
        
        return self._get_fallback_weather()
    
    def _format_weather_data(self, data: Dict) -> Dict[str, Any]:
        """Format weather data"""
        try:
            return {
                'temperature': data.get('main', {}).get('temp', 0),
                'description': data.get('weather', [{}])[0].get('description', ''),
                'humidity': data.get('main', {}).get('humidity', 0),
                'pressure': data.get('main', {}).get('pressure', 0),
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'city': data.get('name', ''),
                'country': data.get('sys', {}).get('country', '')
            }
        except Exception as e:
            logger.error(f"Weather data formatting error: {e}")
            return self._get_fallback_weather()
    
    def _get_fallback_weather(self) -> Dict[str, Any]:
        """Get fallback weather data"""
        return {
            'temperature': 20,
            'description': '天气信息不可用',
            'humidity': 50,
            'pressure': 1013,
            'wind_speed': 0,
            'city': '未知',
            'country': 'CN'
        }

class UpdateChecker:
    """Application update checker"""
    
    def __init__(self, repo_url: str = ""):
        self.repo_url = repo_url
        self.client = APIClient()
    
    def check_for_updates(self, current_version: str) -> Optional[Dict[str, Any]]:
        """Check for application updates"""
        if not self.repo_url:
            logger.warning("Update repository URL not configured")
            return None
        
        try:
            result = self.client.get(f"{self.repo_url}/releases/latest")
            if result and 'tag_name' in result:
                latest_version = result['tag_name'].lstrip('v')
                
                if self._is_newer_version(current_version, latest_version):
                    return {
                        'available': True,
                        'version': latest_version,
                        'download_url': result.get('html_url', ''),
                        'release_notes': result.get('body', ''),
                        'published_at': result.get('published_at', '')
                    }
                else:
                    return {'available': False, 'message': 'Already up to date'}
            
        except Exception as e:
            logger.error(f"Update check error: {e}")
        
        return None
    
    def _is_newer_version(self, current: str, latest: str) -> bool:
        """Compare version strings"""
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            return latest_parts > current_parts
        except Exception as e:
            logger.error(f"Version comparison error: {e}")
            return False

class PluginRepository:
    """Plugin repository API handler"""
    
    def __init__(self, repo_url: str = ""):
        self.repo_url = repo_url
        self.client = APIClient(repo_url)
    
    def list_plugins(self, category: str = "", search: str = "") -> Optional[list]:
        """List available plugins"""
        try:
            params = {}
            if category:
                params['category'] = category
            if search:
                params['search'] = search
            
            result = self.client.get('/plugins', params=params)
            return result.get('plugins', []) if result else []
            
        except Exception as e:
            logger.error(f"Plugin list error: {e}")
            return []
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed plugin information"""
        try:
            result = self.client.get(f'/plugins/{plugin_id}')
            return result if result else None
            
        except Exception as e:
            logger.error(f"Plugin info error: {e}")
            return None
    
    def download_plugin(self, plugin_id: str, version: str = "latest") -> Optional[bytes]:
        """Download plugin package"""
        if not self.client.requests_available:
            logger.error("Cannot download plugin: requests not available")
            return None
        
        try:
            endpoint = f'/plugins/{plugin_id}/download'
            if version != "latest":
                endpoint += f'?version={version}'
            
            response = self.client.session.get(
                urljoin(self.repo_url + '/', endpoint.lstrip('/')),
                timeout=self.client.timeout
            )
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.error(f"Plugin download error: {e}")
            return None

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def safe_download(url: str, timeout: int = 30) -> Optional[bytes]:
    """Safely download content from URL"""
    if not requests.available:
        logger.error("requests module not available for download")
        return None
    
    if not validate_url(url):
        logger.error(f"Invalid URL: {url}")
        return None
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None
