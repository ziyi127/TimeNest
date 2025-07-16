#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Centralized recovery system for handling various failure scenarios
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from utils.config_constants import RECOVERY_STRATEGIES
from utils.shared_utilities import safe_execute_command, retry_operation

logger = logging.getLogger(__name__)

class RecoveryStrategy:
    """Base class for recovery strategies"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"recovery.{name}")
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute the recovery strategy"""
        raise NotImplementedError

class PipInstallRecovery(RecoveryStrategy):
    """Recovery strategy for pip installation failures"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        package = context.get("package", "")
        if not package:
            return False
        
        mirrors = self.config.get("mirrors", [])
        retry_count = self.config.get("retry_count", 3)
        timeout = self.config.get("timeout", 120)
        
        for mirror in mirrors:
            self.logger.info(f"Trying mirror: {mirror}")
            cmd = [sys.executable, "-m", "pip", "install", "-i", mirror, package]
            
            for attempt in range(retry_count):
                try:
                    subprocess.run(cmd, check=True, timeout=timeout, 
                                 capture_output=True, text=True)
                    self.logger.info(f"Successfully installed {package} using {mirror}")
                    return True
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < retry_count - 1:
                        time.sleep(2 ** attempt)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Timeout on attempt {attempt + 1}")
        
        return False

class VenvCreationRecovery(RecoveryStrategy):
    """Recovery strategy for virtual environment creation failures"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        venv_path = context.get("venv_path")
        if not venv_path:
            return False
        
        venv_path = Path(venv_path)
        
        if self.config.get("cleanup_on_failure", True) and venv_path.exists():
            try:
                import shutil
                shutil.rmtree(venv_path)
                self.logger.info(f"Cleaned up failed venv: {venv_path}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup venv: {e}")
        
        if self.config.get("use_virtualenv_fallback", True):
            try:
                cmd = [sys.executable, "-m", "virtualenv", str(venv_path)]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                self.logger.info("Successfully created venv using virtualenv")
                return True
            except Exception as e:
                self.logger.error(f"Virtualenv fallback failed: {e}")
        
        return False

class PermissionRecovery(RecoveryStrategy):
    """Recovery strategy for permission denied errors"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        if self.config.get("use_user_install", True):
            package = context.get("package", "")
            if package:
                cmd = [sys.executable, "-m", "pip", "install", "--user", package]
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    self.logger.info(f"Successfully installed {package} with --user")
                    return True
                except Exception as e:
                    self.logger.error(f"User install failed: {e}")
        
        if self.config.get("create_user_dirs", True):
            try:
                user_dirs = [
                    Path.home() / '.local' / 'bin',
                    Path.home() / '.local' / 'lib',
                    Path.home() / '.config'
                ]
                for dir_path in user_dirs:
                    dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.info("Created user directories")
                return True
            except Exception as e:
                self.logger.error(f"Failed to create user dirs: {e}")
        
        return False

class NetworkRecovery(RecoveryStrategy):
    """Recovery strategy for network errors"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        retry_count = self.config.get("retry_count", 5)
        retry_delay = self.config.get("retry_delay", 10)
        
        for attempt in range(retry_count):
            try:
                import requests
                response = requests.get("https://pypi.org", timeout=10)
                if response.status_code == 200:
                    self.logger.info("Network connectivity restored")
                    return True
            except Exception:
                pass
            
            if attempt < retry_count - 1:
                self.logger.info(f"Network check failed, retrying in {retry_delay}s")
                time.sleep(retry_delay)
        
        if self.config.get("offline_mode", False):
            self.logger.info("Switching to offline mode")
            return True
        
        return False

class DependencyConflictRecovery(RecoveryStrategy):
    """Recovery strategy for dependency conflicts"""
    
    def execute(self, context: Dict[str, Any]) -> bool:
        package = context.get("package", "")
        if not package:
            return False
        
        if self.config.get("force_reinstall", True):
            cmd = [sys.executable, "-m", "pip", "install", 
                   "--force-reinstall", "--no-deps", package]
            try:
                subprocess.run(cmd, check=True, timeout=120, 
                             capture_output=True, text=True)
                self.logger.info(f"Force reinstalled {package}")
                return True
            except Exception as e:
                self.logger.error(f"Force reinstall failed: {e}")
        
        return False

class AutoRecoverySystem:
    """Centralized auto-recovery system"""
    
    def __init__(self):
        self.strategies = {
            "pip_install_failed": PipInstallRecovery(
                "pip_install_failed", 
                RECOVERY_STRATEGIES["pip_install_failed"]
            ),
            "venv_creation_failed": VenvCreationRecovery(
                "venv_creation_failed",
                RECOVERY_STRATEGIES["venv_creation_failed"]
            ),
            "permission_denied": PermissionRecovery(
                "permission_denied",
                RECOVERY_STRATEGIES["permission_denied"]
            ),
            "network_error": NetworkRecovery(
                "network_error",
                RECOVERY_STRATEGIES["network_error"]
            ),
            "dependency_conflict": DependencyConflictRecovery(
                "dependency_conflict",
                RECOVERY_STRATEGIES["dependency_conflict"]
            )
        }
        self.logger = logging.getLogger("auto_recovery")
    
    def attempt_recovery(self, error_type: str, context: Dict[str, Any]) -> bool:
        """Attempt to recover from an error"""
        strategy = self.strategies.get(error_type)
        if not strategy:
            self.logger.warning(f"No recovery strategy for error type: {error_type}")
            return False
        
        try:
            self.logger.info(f"Attempting recovery for: {error_type}")
            success = strategy.execute(context)
            if success:
                self.logger.info(f"Recovery successful for: {error_type}")
            else:
                self.logger.warning(f"Recovery failed for: {error_type}")
            return success
        except Exception as e:
            self.logger.error(f"Recovery strategy failed: {e}")
            return False
    
    def register_strategy(self, error_type: str, strategy: RecoveryStrategy):
        """Register a custom recovery strategy"""
        self.strategies[error_type] = strategy
        self.logger.info(f"Registered recovery strategy for: {error_type}")

_global_recovery_system = AutoRecoverySystem()

def get_recovery_system() -> AutoRecoverySystem:
    """Get the global recovery system instance"""
    return _global_recovery_system

def attempt_recovery(error_type: str, context: Dict[str, Any]) -> bool:
    """Convenience function to attempt recovery"""
    return _global_recovery_system.attempt_recovery(error_type, context)
