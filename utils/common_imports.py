#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Common imports and optional module handling
Provides safe imports for optional dependencies
"""

import logging
import sys
from typing import Any, Optional, Dict, Callable

logger = logging.getLogger(__name__)

class OptionalModule:
    """Wrapper for optional modules with fallback behavior"""
    
    def __init__(self, module_name: str, fallback_value: Any = None):
        self.module_name = module_name
        self.fallback_value = fallback_value
        self.module = None
        self.available = False
        self._load_module()
    
    def _load_module(self):
        """Load the module if available"""
        try:
            self.module = __import__(self.module_name)
            self.available = True
        except ImportError:
            logger.error(f"Optional module '{self.module_name}' not available")
            self.module = self.fallback_value
            self.available = False
    
    def __getattr__(self, name):
        if self.available and hasattr(self.module, name):
            return getattr(self.module, name)
        return self.fallback_value
    
    def __bool__(self):
        return self.available

def safe_import(module_name: str, fallback: Any = None) -> OptionalModule:
    """Safely import a module with fallback"""
    return OptionalModule(module_name, fallback)

try:
    from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer, Qt, QTranslator, QLocale
    from PySide6.QtWidgets import QApplication, QWidget, QFrame, QVBoxLayout, QSystemTrayIcon
    from PySide6.QtGui import QIcon
    from PySide6.QtQml import qmlRegisterType
    PYSIDE6_AVAILABLE = True
except ImportError:
    logger.error("PySide6 not available - using fallback implementations")
    PYSIDE6_AVAILABLE = False
    
    class QObject:
        def __init__(self, *args, **kwargs):
            pass
    
    class Signal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass
        def connect(self, *args):
            pass
    
    class Slot:
        def __init__(self, *args):
            pass
        def __call__(self, func):
            return func
    
    class Property:
        def __init__(self, *args):
            pass
        def __call__(self, func):
            return func
    
    class QTimer:
        def __init__(self):
            pass
        def start(self, *args):
            pass
        def stop(self):
            pass
        def timeout(self):
            return Signal()

    class QSystemTrayIcon:
        def __init__(self, *args):
            pass
        def show(self):
            pass
        def hide(self):
            pass
        def setIcon(self, *args):
            pass
        def setToolTip(self, *args):
            pass
        def activated(self):
            return Signal()
        def messageClicked(self):
            return Signal()
        def showMessage(self, *args):
            pass
        def isSystemTrayAvailable(self):
            return False

    class Qt:
        class WindowType:
            WindowStaysOnTopHint = None
            FramelessWindowHint = None
            Tool = None
        class AlignmentFlag:
            AlignCenter = None
            AlignLeft = None
            AlignRight = None
        class Key:
            Key_Escape = None
        class MouseButton:
            LeftButton = None
            RightButton = None

    class QTranslator:
        def __init__(self):
            pass
        def load(self, *args):
            return False

    class QLocale:
        def __init__(self):
            pass
        @staticmethod
        def system():
            return QLocale()
        def name(self):
            return "en_US"

    def qmlRegisterType(*args, **kwargs):
        """Fallback QML register type function"""
        pass

    # Don't override the fallback classes with None - keep the class definitions above
    QApplication = QWidget = QFrame = QVBoxLayout = QIcon = None

psutil = safe_import('psutil')
requests = safe_import('requests')
openpyxl = safe_import('openpyxl')
yaml = safe_import('yaml')
pandas = safe_import('pandas')
numpy = safe_import('numpy')
PIL = safe_import('PIL')
plyer = safe_import('plyer')
cryptography = safe_import('cryptography')
coloredlogs = safe_import('coloredlogs')
jsonschema = safe_import('jsonschema')
packaging = safe_import('packaging')
sentry_sdk = safe_import('sentry_sdk')

OPTIONAL_MODULES = {
    'psutil': psutil,
    'requests': requests,
    'openpyxl': openpyxl,
    'yaml': yaml,
    'pandas': pandas,
    'numpy': numpy,
    'PIL': PIL,
    'plyer': plyer,
    'cryptography': cryptography,
    'coloredlogs': coloredlogs,
    'jsonschema': jsonschema,
    'packaging': packaging,
    'sentry_sdk': sentry_sdk
}

def check_module_availability() -> Dict[str, bool]:
    """Check availability of all optional modules"""
    return {name: module.available for name, module in OPTIONAL_MODULES.items()}

def get_available_modules() -> list:
    """Get list of available optional modules"""
    return [name for name, module in OPTIONAL_MODULES.items() if module.available]

def get_missing_modules() -> list:
    """Get list of missing optional modules"""
    return [name for name, module in OPTIONAL_MODULES.items() if not module.available]

# Explicit exports for all PySide6 components
__all__ = [
    'PYSIDE6_AVAILABLE',
    'QObject', 'Signal', 'Slot', 'Property', 'QTimer', 'Qt', 'QTranslator', 'QLocale',
    'QApplication', 'QWidget', 'QFrame', 'QVBoxLayout', 'QSystemTrayIcon',
    'QIcon', 'qmlRegisterType',
    'psutil', 'requests', 'openpyxl', 'yaml', 'pandas', 'numpy', 'PIL', 'plyer', 'cryptography',
    'safe_import', 'OptionalModule', 'get_available_modules', 'get_missing_modules'
]
