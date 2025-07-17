#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Central configuration constants and default values
"""

from pathlib import Path
from typing import Dict, Any

APP_NAME = "TimeNest"
APP_VERSION = "2.2.0 Release"
ORGANIZATION_NAME = "TimeNest Team"
ORGANIZATION_DOMAIN = "timenest.app"

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = Path.home() / '.timenest'
LOG_DIR = DATA_DIR / 'logs'
CONFIG_DIR = DATA_DIR / 'config'
CACHE_DIR = DATA_DIR / 'cache'
BACKUP_DIR = DATA_DIR / 'backups'

DEFAULT_DIRS = [DATA_DIR, LOG_DIR, CONFIG_DIR, CACHE_DIR, BACKUP_DIR]

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

PYINSTALLER_HIDDEN_IMPORTS = [
    "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets",
    "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtSql",
    "sqlite3", "json", "datetime", "pathlib", "logging",
    "configparser", "openpyxl", "requests"
]

PYINSTALLER_EXCLUDES = [
    "tkinter", "matplotlib", "numpy", "pandas", "scipy",
    "PIL", "cv2", "tensorflow", "torch"
]

DEFAULT_THEME_SETTINGS = {
    'theme_mode': 'auto',
    'primary_color': '#2196F3',
    'accent_color': '#FF9800',
    'background_color': '#FFFFFF',
    'text_color': '#000000',
    'font_family': 'MiSans-Light',
    'font_size': 14
}

DEFAULT_NOTIFICATION_SETTINGS = {
    'enabled': True,
    'sound_enabled': True,
    'desktop_notifications': True,
    'system_tray_notifications': True,
    'duration': 5000,
    'position': 'top_right',
    'max_notifications': 5,
    'do_not_disturb': {
        'enabled': False,
        'start_time': '22:00',
        'end_time': '07:00',
        'allow_urgent': True,
        'weekends_only': False
    },
    'smart_features': {
        'duplicate_detection': True,
        'auto_retry': True,
        'retry_count': 3,
        'retry_interval': 5,
        'priority_queue': True,
        'batch_processing': True
    }
}

DEFAULT_FLOATING_WINDOW_SETTINGS = {
    'enabled': True,
    'always_on_top': True,
    'auto_hide': False,
    'opacity': 0.9,
    'width': 300,
    'height': 200,
    'position': {'x': 100, 'y': 100},
    'update_interval': 1000
}

DEFAULT_PERFORMANCE_SETTINGS = {
    'monitoring_enabled': True,
    'monitoring_interval': 60,
    'memory_threshold': 95,
    'cpu_threshold': 95,
    'disk_threshold': 95,
    'silent_mode': True,
    'auto_cleanup': True,
    'cache_size_limit': 100 * 1024 * 1024  # 100MB
}

DEFAULT_PLUGIN_SETTINGS = {
    'enabled': True,
    'auto_load': True,
    'security_check': True,
    'sandbox_mode': True,
    'max_plugins': 50,
    'plugin_timeout': 30
}

DEFAULT_SCHEDULE_SETTINGS = {
    'auto_refresh': True,
    'refresh_interval': 300,  # 5 minutes
    'show_past_events': False,
    'default_duration': 90,  # minutes
    'week_start': 'monday',
    'time_format': '24h'
}

DEFAULT_TASK_SETTINGS = {
    'auto_save': True,
    'save_interval': 60,  # seconds
    'max_tasks': 1000,
    'default_priority': 'medium',
    'completion_sound': True,
    'reminder_enabled': True
}

RECOVERY_STRATEGIES = {
    "pip_install_failed": {
        "mirrors": [
            "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "https://mirrors.aliyun.com/pypi/simple/",
            "https://pypi.douban.com/simple/"
        ],
        "retry_count": 3,
        "timeout": 120
    },
    "venv_creation_failed": {
        "cleanup_on_failure": True,
        "use_virtualenv_fallback": True,
        "retry_count": 2
    },
    "permission_denied": {
        "use_user_install": True,
        "create_user_dirs": True
    },
    "network_error": {
        "retry_count": 5,
        "retry_delay": 10,
        "offline_mode": False
    },
    "dependency_conflict": {
        "force_reinstall": True,
        "ignore_dependencies": False
    }
}

ENVIRONMENT_PRESETS = {
    "windows_standard": {
        "python_executable": "python",
        "pip_args": ["--user"],
        "system_packages": [],
        "env_vars": {}
    },
    "windows_conda": {
        "python_executable": "python",
        "pip_args": [],
        "system_packages": [],
        "env_vars": {"CONDA_DEFAULT_ENV": "base"}
    },
    "linux_standard": {
        "python_executable": "python3",
        "pip_args": [],
        "system_packages": ["python3-tk", "python3-dev"],
        "env_vars": {"QT_QPA_PLATFORM": "xcb"}
    },
    "wsl": {
        "python_executable": "python3",
        "pip_args": [],
        "system_packages": ["python3-tk", "python3-dev", "x11-apps"],
        "env_vars": {
            "DISPLAY": ":0",
            "QT_QPA_PLATFORM": "xcb"
        }
    },
    "macos": {
        "python_executable": "python3",
        "pip_args": [],
        "system_packages": [],
        "env_vars": {}
    }
}

ERROR_MESSAGES = {
    'module_not_found': "Required module '{}' not found. Please install it using: pip install {}",
    'config_load_failed': "Failed to load configuration from '{}'. Using default settings.",
    'permission_denied': "Permission denied accessing '{}'. Please check file permissions.",
    'network_error': "Network error occurred: {}. Please check your internet connection.",
    'file_not_found': "File not found: '{}'. Please check the file path.",
    'invalid_format': "Invalid format in file '{}': {}",
    'initialization_failed': "Failed to initialize component '{}': {}"
}

SUCCESS_MESSAGES = {
    'module_loaded': "Successfully loaded module '{}'",
    'config_loaded': "Configuration loaded from '{}'",
    'component_initialized': "Component '{}' initialized successfully",
    'operation_completed': "Operation '{}' completed successfully"
}

def get_default_config() -> Dict[str, Any]:
    """Get complete default configuration"""
    return {
        'app': {
            'name': APP_NAME,
            'version': APP_VERSION,
            'organization': ORGANIZATION_NAME,
            'domain': ORGANIZATION_DOMAIN
        },
        'theme': DEFAULT_THEME_SETTINGS,
        'notifications': DEFAULT_NOTIFICATION_SETTINGS,
        'floating_window': DEFAULT_FLOATING_WINDOW_SETTINGS,
        'performance': DEFAULT_PERFORMANCE_SETTINGS,
        'plugins': DEFAULT_PLUGIN_SETTINGS,
        'schedule': DEFAULT_SCHEDULE_SETTINGS,
        'tasks': DEFAULT_TASK_SETTINGS
    }
