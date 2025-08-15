"""
系统时间同步服务
提供系统时间自动同步功能
"""

import json
import os
import platform
import subprocess
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any
from models.time_sync import TimeSyncSettings
from utils.logger import get_service_logger

# 初始化日志记录器
logger = get_service_logger("time_sync_service")


class TimeSyncService:
    """系统时间同步服务类"""
    
    def __init__(self):
        """初始化系统时间同步服务"""
        self.config_file = "./data/time_sync_config.json"
        self.settings: Optional[TimeSyncSettings] = None
        self.sync_thread: Optional[threading.Thread] = None
        self.is_running = False
        self._ensure_data_directory()
        self._load_settings()
        self._start_auto_sync_if_enabled()
        logger.info("TimeSyncService initialized")
    
    def _ensure_data_directory(self):
        """确保数据目录存在"""
        try:
            data_dir = os.path.dirname(self.config_file)
            if data_dir:
                os.makedirs(data_dir, exist_ok=True)
                logger.debug(f"确保数据目录存在: {data_dir}")
        except Exception as e:
            logger.error(f"创建数据目录失败: {str(e)}")
    
    def _load_settings(self):
        """加载时间同步设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = TimeSyncSettings.from_dict(data)
                logger.debug("时间同步设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = TimeSyncSettings()
                self._save_settings()
                logger.debug("创建默认时间同步设置")
        except Exception as e:
            logger.error(f"加载时间同步设置失败: {str(e)}")
            self.settings = TimeSyncSettings()
    
    def _save_settings(self):
        """保存时间同步设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("时间同步设置保存成功")
        except Exception as e:
            logger.error(f"保存时间同步设置失败: {str(e)}")
            raise Exception("保存时间同步设置失败")
    
    def get_settings(self) -> TimeSyncSettings:
        """
        获取时间同步设置
        
        Returns:
            TimeSyncSettings: 时间同步设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or TimeSyncSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新时间同步设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        logger.info("更新时间同步设置")
        
        try:
            if not self.settings:
                self.settings = TimeSyncSettings()
            
            # 更新设置字段
            for key, value in settings_data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # 保存设置
            self._save_settings()
            
            # 如果启用了自动同步，启动同步线程
            if self.settings.enabled:
                self._start_auto_sync_if_enabled()
            else:
                # 如果禁用了自动同步，停止同步线程
                self._stop_auto_sync()
            
            logger.info("时间同步设置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新时间同步设置失败: {str(e)}")
            return False
    
    def _start_auto_sync_if_enabled(self):
        """如果启用了自动同步，则启动同步线程"""
        try:
            if self.settings and self.settings.enabled and not self.is_running:
                self.is_running = True
                self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
                self.sync_thread.start()
                logger.info("时间自动同步线程已启动")
        except Exception as e:
            logger.error(f"启动时间自动同步线程失败: {str(e)}")
    
    def _stop_auto_sync(self):
        """停止自动同步"""
        try:
            self.is_running = False
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5)  # 等待最多5秒
                logger.info("时间自动同步线程已停止")
        except Exception as e:
            logger.error(f"停止时间自动同步线程失败: {str(e)}")
    
    def _sync_worker(self):
        """时间同步工作线程"""
        try:
            while self.is_running and self.settings and self.settings.enabled:
                # 执行时间同步
                self.sync_time()
                
                # 等待下次同步间隔
                interval = self.settings.sync_interval if self.settings else 3600
                for _ in range(interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
        except Exception as e:
            logger.error(f"时间同步工作线程出错: {str(e)}")
        finally:
            self.is_running = False
            logger.info("时间同步工作线程已结束")
    
    def sync_time(self) -> Dict[str, Any]:
        """
        同步系统时间
        
        Returns:
            Dict[str, Any]: 同步结果
        """
        try:
            logger.info("开始同步系统时间")
            
            # 记录同步前的时间
            before_sync = datetime.now()
            
            # 根据操作系统执行不同的时间同步命令
            system = platform.system().lower()
            ntp_server = self.settings.ntp_server if self.settings else "pool.ntp.org"
            
            if system == "windows":
                result = self._sync_time_windows(ntp_server)
            elif system == "darwin":  # macOS
                result = self._sync_time_macos(ntp_server)
            elif system == "linux":
                result = self._sync_time_linux(ntp_server)
            else:
                logger.warning(f"不支持的操作系统: {system}")
                return {
                    "success": False,
                    "message": f"不支持的操作系统: {system}",
                    "before_sync": before_sync.isoformat()
                }
            
            # 记录同步后的时间
            after_sync = datetime.now()
            
            # 添加时间信息到结果中
            result["before_sync"] = before_sync.isoformat()
            result["after_sync"] = after_sync.isoformat()
            
            logger.info(f"系统时间同步完成: {result['message']}")
            return result
        except Exception as e:
            logger.error(f"同步系统时间失败: {str(e)}")
            return {
                "success": False,
                "message": f"同步系统时间失败: {str(e)}",
                "before_sync": datetime.now().isoformat()
            }
    
    def _sync_time_windows(self, ntp_server: str) -> Dict[str, Any]:
        """
        在Windows系统上同步时间
        
        Args:
            ntp_server: NTP服务器地址
            
        Returns:
            Dict[str, Any]: 同步结果
        """
        try:
            # 使用w32tm命令同步时间
            # 首先停止Windows时间服务
            subprocess.run(["net", "stop", "w32time"], check=True, capture_output=True)
            
            # 配置NTP服务器
            subprocess.run(["w32tm", "/config", f"/manualpeerlist:{ntp_server}", "/syncfromflags:manual", "/reliable:yes", "/update"], 
                          check=True, capture_output=True)
            
            # 启动Windows时间服务
            subprocess.run(["net", "start", "w32time"], check=True, capture_output=True)
            
            # 立即同步时间
            result = subprocess.run(["w32tm", "/resync"], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Windows系统时间同步成功",
                    "command_output": result.stdout.strip()
                }
            else:
                return {
                    "success": False,
                    "message": "Windows系统时间同步失败",
                    "command_output": result.stderr.strip()
                }
        except Exception as e:
            logger.error(f"Windows时间同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"Windows时间同步失败: {str(e)}"
            }
    
    def _sync_time_macos(self, ntp_server: str) -> Dict[str, Any]:
        """
        在macOS系统上同步时间
        
        Args:
            ntp_server: NTP服务器地址
            
        Returns:
            Dict[str, Any]: 同步结果
        """
        try:
            # 使用ntpdate命令同步时间（需要sudo权限）
            result = subprocess.run(["sudo", "ntpdate", "-s", ntp_server], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "macOS系统时间同步成功",
                    "command_output": result.stdout.strip()
                }
            else:
                # 如果ntpdate不可用，尝试使用sntp
                result = subprocess.run(["sudo", "sntp", "-sS", ntp_server], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "macOS系统时间同步成功",
                        "command_output": result.stdout.strip()
                    }
                else:
                    return {
                        "success": False,
                        "message": "macOS系统时间同步失败",
                        "command_output": result.stderr.strip()
                    }
        except Exception as e:
            logger.error(f"macOS时间同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"macOS时间同步失败: {str(e)}"
            }
    
    def _sync_time_linux(self, ntp_server: str) -> Dict[str, Any]:
        """
        在Linux系统上同步时间
        
        Args:
            ntp_server: NTP服务器地址
            
        Returns:
            Dict[str, Any]: 同步结果
        """
        try:
            # 尝试使用timedatectl命令同步时间（较新的系统）
            result = subprocess.run(["sudo", "timedatectl", "set-ntp", "true"], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 等待同步完成
                time.sleep(2)
                return {
                    "success": True,
                    "message": "Linux系统时间同步成功",
                    "command_output": "使用timedatectl同步时间"
                }
            else:
                # 如果timedatectl不可用，尝试使用ntpdate
                result = subprocess.run(["sudo", "ntpdate", ntp_server], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Linux系统时间同步成功",
                        "command_output": result.stdout.strip()
                    }
                else:
                    # 如果ntpdate也不可用，尝试使用chrony
                    result = subprocess.run(["sudo", "chrony", "sources"], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "message": "Linux系统时间同步成功",
                            "command_output": "使用chrony同步时间"
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Linux系统时间同步失败",
                            "command_output": result.stderr.strip()
                        }
        except Exception as e:
            logger.error(f"Linux时间同步失败: {str(e)}")
            return {
                "success": False,
                "message": f"Linux时间同步失败: {str(e)}"
            }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        获取时间同步状态
        
        Returns:
            Dict[str, Any]: 同步状态信息
        """
        try:
            return {
                "enabled": self.settings.enabled if self.settings else False,
                "ntp_server": self.settings.ntp_server if self.settings else "pool.ntp.org",
                "sync_interval": self.settings.sync_interval if self.settings else 3600,
                "is_running": self.is_running,
                "last_sync": getattr(self, '_last_sync', None)
            }
        except Exception as e:
            logger.error(f"获取时间同步状态失败: {str(e)}")
            return {
                "enabled": False,
                "ntp_server": "pool.ntp.org",
                "sync_interval": 3600,
                "is_running": False,
                "last_sync": None
            }
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False