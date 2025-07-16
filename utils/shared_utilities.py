#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared utility functions used across multiple modules
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def setup_encoding():
    """Setup UTF-8 encoding for stdout/stderr"""
    for stream in [sys.stdout, sys.stderr]:
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')

def safe_execute_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 30) -> bool:
    """Safely execute a command with error handling"""
    try:
        subprocess.run(cmd, cwd=cwd, check=True, timeout=timeout, 
                      capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)} - {e}")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"Command timeout: {' '.join(cmd)}")
        return False
    except Exception as e:
        logger.error(f"Command error: {e}")
        return False

def retry_operation(func: Callable, max_retries: int = 3, delay: float = 1.0, 
                   backoff: float = 2.0) -> Any:
    """Retry an operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Operation failed after {max_retries} attempts: {e}")
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
            time.sleep(delay)
            delay *= backoff

def safe_dict_get(data: Dict, key: str, default: Any = None, 
                 expected_type: Optional[type] = None) -> Any:
    """Safely get value from dictionary with type checking"""
    try:
        value = data.get(key, default)
        if expected_type and value is not None and not isinstance(value, expected_type):
            logger.warning(f"Type mismatch for key '{key}': expected {expected_type}, got {type(value)}")
            return default
        return value
    except Exception as e:
        logger.error(f"Error getting key '{key}': {e}")
        return default

def validate_path(path: Union[str, Path], must_exist: bool = False, 
                 create_if_missing: bool = False) -> Optional[Path]:
    """Validate and optionally create a path"""
    try:
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            if create_if_missing:
                if path_obj.suffix:
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                    path_obj.touch()
                else:
                    path_obj.mkdir(parents=True, exist_ok=True)
            else:
                logger.error(f"Required path does not exist: {path}")
                return None
        
        return path_obj
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return None

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def cleanup_timers(*timers) -> None:
    """Cleanup multiple timers safely"""
    for timer in timers:
        if timer and hasattr(timer, 'stop'):
            try:
                timer.stop()
            except Exception as e:
                logger.debug(f"Timer cleanup error: {e}")

def merge_configs(base_config: Dict, override_config: Dict) -> Dict:
    """Merge two configuration dictionaries recursively"""
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def get_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """Get formatted timestamp string"""
    return datetime.now().strftime(format_str)

def is_within_time_range(start_time: str, end_time: str, 
                        current_time: Optional[datetime] = None) -> bool:
    """Check if current time is within specified range"""
    try:
        if current_time is None:
            current_time = datetime.now()
        
        current_time_str = current_time.strftime("%H:%M")
        
        if start_time <= end_time:
            return start_time <= current_time_str <= end_time
        else:
            return current_time_str >= start_time or current_time_str <= end_time
    except Exception as e:
        logger.error(f"Time range check error: {e}")
        return False

def debounce(wait_time: float):
    """Debounce decorator to limit function call frequency"""
    def decorator(func):
        last_called = [0.0]
        
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait_time:
                last_called[0] = now
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def create_backup_filename(original_path: Path, suffix: str = "backup") -> Path:
    """Create a backup filename with timestamp"""
    timestamp = get_timestamp()
    stem = original_path.stem
    extension = original_path.suffix
    return original_path.parent / f"{stem}_{suffix}_{timestamp}{extension}"
