#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System integration utilities for TimeNest
Provides cross-platform system interaction capabilities
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from utils.shared_utilities import safe_execute_command
from utils.common_imports import psutil

logger = logging.getLogger(__name__)

class SystemInfo:
    """System information collector"""
    
    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """Get platform information"""
        try:
            return {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'python_version': platform.python_version(),
                'platform': platform.platform()
            }
        except Exception as e:
            logger.error(f"Failed to get platform info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_hardware_info() -> Dict[str, Any]:
        """Get hardware information"""
        info = {}
        
        try:
            if psutil.available:
                info.update({
                    'cpu_count': psutil.cpu_count(),
                    'cpu_count_logical': psutil.cpu_count(logical=True),
                    'memory_total': psutil.virtual_memory().total,
                    'memory_available': psutil.virtual_memory().available,
                    'disk_usage': {
                        'total': psutil.disk_usage('/').total,
                        'used': psutil.disk_usage('/').used,
                        'free': psutil.disk_usage('/').free
                    }
                })
            else:
                info['psutil_unavailable'] = True
        except Exception as e:
            logger.error(f"Failed to get hardware info: {e}")
            info['error'] = str(e)
        
        return info
    
    @staticmethod
    def get_environment_info() -> Dict[str, str]:
        """Get environment information"""
        try:
            return {
                'user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
                'home': str(Path.home()),
                'cwd': str(Path.cwd()),
                'path': os.getenv('PATH', ''),
                'python_path': sys.executable,
                'display': os.getenv('DISPLAY', 'not_set'),
                'lang': os.getenv('LANG', 'not_set'),
                'shell': os.getenv('SHELL', 'not_set')
            }
        except Exception as e:
            logger.error(f"Failed to get environment info: {e}")
            return {'error': str(e)}

class NotificationSender:
    """Cross-platform notification sender"""
    
    @staticmethod
    def send_notification(title: str, message: str, icon: Optional[str] = None) -> bool:
        """Send system notification"""
        try:
            system = platform.system().lower()
            
            if system == 'linux':
                return NotificationSender._send_linux_notification(title, message, icon)
            elif system == 'darwin':
                return NotificationSender._send_macos_notification(title, message)
            elif system == 'windows':
                return NotificationSender._send_windows_notification(title, message)
            else:
                logger.warning(f"Notifications not supported on {system}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    @staticmethod
    def _send_linux_notification(title: str, message: str, icon: Optional[str] = None) -> bool:
        """Send Linux notification using notify-send"""
        cmd = ['notify-send', title, message]
        if icon:
            cmd.extend(['--icon', icon])
        
        return safe_execute_command(cmd, timeout=5)
    
    @staticmethod
    def _send_macos_notification(title: str, message: str) -> bool:
        """Send macOS notification using osascript"""
        script = f'display notification "{message}" with title "{title}"'
        cmd = ['osascript', '-e', script]
        
        return safe_execute_command(cmd, timeout=5)
    
    @staticmethod
    def _send_windows_notification(title: str, message: str) -> bool:
        """Send Windows notification using PowerShell"""
        try:
            from utils.common_imports import plyer
            if plyer.available:
                plyer.notification.notify(
                    title=title,
                    message=message,
                    timeout=5
                )
                return True
        except Exception as e:
            logger.debug(f"Plyer notification failed: {e}")
        
        script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $notification = New-Object System.Windows.Forms.NotifyIcon
        $notification.Icon = [System.Drawing.SystemIcons]::Information
        $notification.BalloonTipTitle = "{title}"
        $notification.BalloonTipText = "{message}"
        $notification.Visible = $true
        $notification.ShowBalloonTip(5000)
        '''
        
        cmd = ['powershell', '-Command', script]
        return safe_execute_command(cmd, timeout=10)

class FileAssociation:
    """File association management"""
    
    @staticmethod
    def register_file_type(extension: str, app_path: str, description: str = "") -> bool:
        """Register file type association"""
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                return FileAssociation._register_windows_file_type(extension, app_path, description)
            elif system == 'linux':
                return FileAssociation._register_linux_file_type(extension, app_path, description)
            elif system == 'darwin':
                return FileAssociation._register_macos_file_type(extension, app_path, description)
            else:
                logger.warning(f"File association not supported on {system}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register file type: {e}")
            return False
    
    @staticmethod
    def _register_windows_file_type(extension: str, app_path: str, description: str) -> bool:
        """Register Windows file type"""
        try:
            import winreg
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\.{extension}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f"TimeNest.{extension}")
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\TimeNest.{extension}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, description)
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\TimeNest.{extension}\\shell\\open\\command") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f'"{app_path}" "%1"')
            
            return True
        except ImportError:
            logger.error("winreg not available")
            return False
        except Exception as e:
            logger.error(f"Windows file association failed: {e}")
            return False
    
    @staticmethod
    def _register_linux_file_type(extension: str, app_path: str, description: str) -> bool:
        """Register Linux file type using xdg-mime"""
        try:
            desktop_file = f"""[Desktop Entry]
Name=TimeNest
Comment={description}
Exec={app_path} %f
Icon=timenest
Terminal=false
Type=Application
MimeType=application/x-timenest-{extension};
"""
            
            desktop_path = Path.home() / ".local/share/applications/timenest.desktop"
            desktop_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(desktop_path, 'w') as f:
                f.write(desktop_file)
            
            mime_cmd = ['xdg-mime', 'default', 'timenest.desktop', f'application/x-timenest-{extension}']
            return safe_execute_command(mime_cmd, timeout=10)
            
        except Exception as e:
            logger.error(f"Linux file association failed: {e}")
            return False
    
    @staticmethod
    def _register_macos_file_type(extension: str, app_path: str, description: str) -> bool:
        """Register macOS file type"""
        logger.warning("macOS file association not implemented")
        return False

class AutoStart:
    """Auto-start management"""
    
    @staticmethod
    def enable_autostart(app_name: str, app_path: str) -> bool:
        """Enable application auto-start"""
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                return AutoStart._enable_windows_autostart(app_name, app_path)
            elif system == 'linux':
                return AutoStart._enable_linux_autostart(app_name, app_path)
            elif system == 'darwin':
                return AutoStart._enable_macos_autostart(app_name, app_path)
            else:
                logger.warning(f"Auto-start not supported on {system}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to enable auto-start: {e}")
            return False
    
    @staticmethod
    def _enable_windows_autostart(app_name: str, app_path: str) -> bool:
        """Enable Windows auto-start via registry"""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            
            return True
        except ImportError:
            logger.error("winreg not available")
            return False
        except Exception as e:
            logger.error(f"Windows auto-start failed: {e}")
            return False
    
    @staticmethod
    def _enable_linux_autostart(app_name: str, app_path: str) -> bool:
        """Enable Linux auto-start via .desktop file"""
        try:
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec={app_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
            
            autostart_dir = Path.home() / ".config/autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = autostart_dir / f"{app_name.lower()}.desktop"
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            return True
        except Exception as e:
            logger.error(f"Linux auto-start failed: {e}")
            return False
    
    @staticmethod
    def _enable_macos_autostart(app_name: str, app_path: str) -> bool:
        """Enable macOS auto-start via launchd"""
        logger.warning("macOS auto-start not implemented")
        return False

def get_system_capabilities() -> Dict[str, bool]:
    """Get available system capabilities"""
    return {
        'notifications': NotificationSender.send_notification("Test", "Test") if platform.system() in ['Linux', 'Darwin', 'Windows'] else False,
        'file_associations': platform.system() in ['Linux', 'Windows'],
        'auto_start': platform.system() in ['Linux', 'Windows'],
        'system_tray': platform.system() in ['Linux', 'Windows', 'Darwin'],
        'psutil_available': psutil.available
    }
