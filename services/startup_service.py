"""
开机启动服务
提供应用程序开机自启配置功能
"""

import json
import os
import platform
import subprocess
from typing import List, Optional, Dict, Any
from models.startup_config import StartupItem, StartupSettings
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("startup_service")


class StartupService:
    """开机启动服务类"""
    
    def __init__(self):
        """初始化开机启动服务"""
        self.config_file = "./data/startup_config.json"
        self.data_file = "./data/startup_data.json"
        self.settings: Optional[StartupSettings] = None
        self.startup_items: List[StartupItem] = []
        self._ensure_data_directory()
        self._load_settings()
        self._load_startup_data()
        logger.info("StartupService initialized")
    
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
        """加载开机启动设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = StartupSettings.from_dict(data)
                logger.debug("开机启动设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = StartupSettings()
                self._save_settings()
                logger.debug("创建默认开机启动设置")
        except Exception as e:
            logger.error(f"加载开机启动设置失败: {str(e)}")
            self.settings = StartupSettings()
    
    def _save_settings(self):
        """保存开机启动设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("开机启动设置保存成功")
        except Exception as e:
            logger.error(f"保存开机启动设置失败: {str(e)}")
            raise ValidationException("保存开机启动设置失败")
    
    def _load_startup_data(self):
        """加载开机启动项数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.startup_items = [StartupItem.from_dict(item) for item in data]
                logger.debug(f"开机启动项数据加载成功，共 {len(self.startup_items)} 个项目")
        except Exception as e:
            logger.error(f"加载开机启动项数据失败: {str(e)}")
    
    def _save_startup_data(self):
        """保存开机启动项数据"""
        try:
            # 确保数据目录存在
            self._ensure_data_directory()
            
            data = [item.to_dict() for item in self.startup_items]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("开机启动项数据保存成功")
        except Exception as e:
            logger.error(f"保存开机启动项数据失败: {str(e)}")
    
    def get_settings(self) -> StartupSettings:
        """
        获取开机启动设置
        
        Returns:
            StartupSettings: 开机启动设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or StartupSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新开机启动设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        logger.info("更新开机启动设置")
        
        try:
            if not self.settings:
                self.settings = StartupSettings()
            
            # 更新设置字段
            for key, value in settings_data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # 保存设置
            self._save_settings()
            
            logger.info("开机启动设置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新开机启动设置失败: {str(e)}")
            return False
    
    def get_startup_items(self) -> List[StartupItem]:
        """
        获取所有开机启动项
        
        Returns:
            List[StartupItem]: 开机启动项列表
        """
        return self.startup_items
    
    def get_startup_item(self, item_id: str) -> Optional[StartupItem]:
        """
        根据ID获取开机启动项
        
        Args:
            item_id: 启动项ID
            
        Returns:
            Optional[StartupItem]: 开机启动项
        """
        for item in self.startup_items:
            if item.id == item_id:
                return item
        return None
    
    def add_startup_item(self, item: StartupItem) -> bool:
        """
        添加开机启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查启动项ID是否已存在
            if self.get_startup_item(item.id):
                logger.warning(f"开机启动项已存在: {item.id}")
                return False
            
            self.startup_items.append(item)
            self._save_startup_data()
            logger.info(f"添加开机启动项: {item.id} -> {item.name}")
            
            # 如果启用自动配置，则应用到系统
            if self.settings and self.settings.auto_configure:
                self._apply_startup_item(item)
            
            return True
        except Exception as e:
            logger.error(f"添加开机启动项失败: {str(e)}")
            return False
    
    def update_startup_item(self, item_id: str, item_data: Dict[str, Any]) -> bool:
        """
        更新开机启动项
        
        Args:
            item_id: 启动项ID
            item_data: 启动项数据字典
            
        Returns:
            bool: 是否更新成功
        """
        try:
            item = self.get_startup_item(item_id)
            if not item:
                logger.warning(f"开机启动项未找到: {item_id}")
                return False
            
            # 更新启动项字段
            for key, value in item_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            self._save_startup_data()
            logger.info(f"更新开机启动项: {item.id} -> {item.name}")
            
            # 如果启用自动配置，则应用到系统
            if self.settings and self.settings.auto_configure:
                self._apply_startup_item(item)
            
            return True
        except Exception as e:
            logger.error(f"更新开机启动项失败: {str(e)}")
            return False
    
    def remove_startup_item(self, item_id: str) -> bool:
        """
        删除开机启动项
        
        Args:
            item_id: 启动项ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            item = self.get_startup_item(item_id)
            if not item:
                logger.warning(f"开机启动项未找到: {item_id}")
                return False
            
            # 如果启用自动配置，则从系统中移除
            if self.settings and self.settings.auto_configure:
                self._remove_startup_item_from_system(item)
            
            self.startup_items.remove(item)
            self._save_startup_data()
            logger.info(f"删除开机启动项: {item.id} -> {item.name}")
            return True
        except Exception as e:
            logger.error(f"删除开机启动项失败: {str(e)}")
            return False
    
    def _apply_startup_item(self, item: StartupItem) -> bool:
        """
        将启动项应用到系统
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否应用成功
        """
        try:
            system = platform.system().lower()
            
            if system == "windows":
                return self._apply_startup_item_windows(item)
            elif system == "darwin":  # macOS
                return self._apply_startup_item_macos(item)
            elif system == "linux":
                return self._apply_startup_item_linux(item)
            else:
                logger.warning(f"不支持的操作系统: {system}")
                return False
        except Exception as e:
            logger.error(f"应用启动项到系统失败: {str(e)}")
            return False
    
    def _apply_startup_item_windows(self, item: StartupItem) -> bool:
        """
        在Windows系统上应用启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否应用成功
        """
        try:
            # 使用注册表方式添加启动项
            import winreg
            
            # 打开启动项注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            # 设置启动项
            winreg.SetValueEx(key, item.name, 0, winreg.REG_SZ, item.executable_path)
            winreg.CloseKey(key)
            
            logger.info(f"Windows启动项已应用: {item.name}")
            return True
        except ImportError:
            # 如果无法导入winreg模块，使用另一种方式
            try:
                # 创建启动目录快捷方式
                startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
                shortcut_path = os.path.join(startup_dir, f"{item.name}.lnk")
                
                # 使用PowerShell创建快捷方式
                ps_command = f"""
                $WshShell = New-Object -comObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
                $Shortcut.TargetPath = '{item.executable_path}'
                $Shortcut.Save()
                """
                
                subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True)
                
                logger.info(f"Windows启动项快捷方式已创建: {item.name}")
                return True
            except Exception as e:
                logger.error(f"创建Windows启动项快捷方式失败: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"应用Windows启动项失败: {str(e)}")
            return False
    
    def _apply_startup_item_macos(self, item: StartupItem) -> bool:
        """
        在macOS系统上应用启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否应用成功
        """
        try:
            # 创建plist文件
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{item.id}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{item.executable_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
            
            # plist文件路径
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{item.id}.plist")
            
            # 写入plist文件
            with open(plist_path, 'w', encoding='utf-8') as f:
                f.write(plist_content)
            
            # 加载plist文件
            subprocess.run(["launchctl", "load", plist_path], check=True, capture_output=True)
            
            logger.info(f"macOS启动项已应用: {item.name}")
            return True
        except Exception as e:
            logger.error(f"应用macOS启动项失败: {str(e)}")
            return False
    
    def _apply_startup_item_linux(self, item: StartupItem) -> bool:
        """
        在Linux系统上应用启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否应用成功
        """
        try:
            # 创建.desktop文件
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={item.name}
Exec={item.executable_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true"""
            
            # .desktop文件路径
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = os.path.join(autostart_dir, f"{item.id}.desktop")
            
            # 写入.desktop文件
            with open(desktop_path, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            
            logger.info(f"Linux启动项已应用: {item.name}")
            return True
        except Exception as e:
            logger.error(f"应用Linux启动项失败: {str(e)}")
            return False
    
    def _remove_startup_item_from_system(self, item: StartupItem) -> bool:
        """
        从系统中移除启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否移除成功
        """
        try:
            system = platform.system().lower()
            
            if system == "windows":
                return self._remove_startup_item_windows(item)
            elif system == "darwin":  # macOS
                return self._remove_startup_item_macos(item)
            elif system == "linux":
                return self._remove_startup_item_linux(item)
            else:
                logger.warning(f"不支持的操作系统: {system}")
                return False
        except Exception as e:
            logger.error(f"从系统中移除启动项失败: {str(e)}")
            return False
    
    def _remove_startup_item_windows(self, item: StartupItem) -> bool:
        """
        在Windows系统上移除启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否移除成功
        """
        try:
            # 使用注册表方式移除启动项
            import winreg
            
            # 打开启动项注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            # 删除启动项
            winreg.DeleteValue(key, item.name)
            winreg.CloseKey(key)
            
            logger.info(f"Windows启动项已移除: {item.name}")
            return True
        except ImportError:
            # 如果无法导入winreg模块，使用另一种方式
            try:
                # 删除启动目录快捷方式
                startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
                shortcut_path = os.path.join(startup_dir, f"{item.name}.lnk")
                
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                    logger.info(f"Windows启动项快捷方式已删除: {item.name}")
                
                return True
            except Exception as e:
                logger.error(f"删除Windows启动项快捷方式失败: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"移除Windows启动项失败: {str(e)}")
            return False
    
    def _remove_startup_item_macos(self, item: StartupItem) -> bool:
        """
        在macOS系统上移除启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否移除成功
        """
        try:
            # plist文件路径
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{item.id}.plist")
            
            # 卸载plist文件
            subprocess.run(["launchctl", "unload", plist_path], check=True, capture_output=True)
            
            # 删除plist文件
            if os.path.exists(plist_path):
                os.remove(plist_path)
            
            logger.info(f"macOS启动项已移除: {item.name}")
            return True
        except Exception as e:
            logger.error(f"移除macOS启动项失败: {str(e)}")
            return False
    
    def _remove_startup_item_linux(self, item: StartupItem) -> bool:
        """
        在Linux系统上移除启动项
        
        Args:
            item: 开机启动项
            
        Returns:
            bool: 是否移除成功
        """
        try:
            # .desktop文件路径
            autostart_dir = os.path.expanduser("~/.config/autostart")
            desktop_path = os.path.join(autostart_dir, f"{item.id}.desktop")
            
            # 删除.desktop文件
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
            
            logger.info(f"Linux启动项已移除: {item.name}")
            return True
        except Exception as e:
            logger.error(f"移除Linux启动项失败: {str(e)}")
            return False
    
    def apply_all_startup_items(self) -> Dict[str, Any]:
        """
        应用所有启动项到系统
        
        Returns:
            Dict[str, Any]: 应用结果
        """
        try:
            success_count = 0
            failed_items = []
            
            for item in self.startup_items:
                if self._apply_startup_item(item):
                    success_count += 1
                else:
                    failed_items.append(item.id)
            
            return {
                "success": True,
                "message": f"已应用 {success_count} 个启动项，失败 {len(failed_items)} 个",
                "success_count": success_count,
                "failed_count": len(failed_items),
                "failed_items": failed_items
            }
        except Exception as e:
            logger.error(f"应用所有启动项失败: {str(e)}")
            return {
                "success": False,
                "message": f"应用所有启动项失败: {str(e)}",
                "success_count": 0,
                "failed_count": len(self.startup_items),
                "failed_items": [item.id for item in self.startup_items]
            }
    
    def remove_all_startup_items(self) -> Dict[str, Any]:
        """
        从系统中移除所有启动项
        
        Returns:
            Dict[str, Any]: 移除结果
        """
        try:
            success_count = 0
            failed_items = []
            
            for item in self.startup_items:
                if self._remove_startup_item_from_system(item):
                    success_count += 1
                else:
                    failed_items.append(item.id)
            
            return {
                "success": True,
                "message": f"已移除 {success_count} 个启动项，失败 {len(failed_items)} 个",
                "success_count": success_count,
                "failed_count": len(failed_items),
                "failed_items": failed_items
            }
        except Exception as e:
            logger.error(f"移除所有启动项失败: {str(e)}")
            return {
                "success": False,
                "message": f"移除所有启动项失败: {str(e)}",
                "success_count": 0,
                "failed_count": len(self.startup_items),
                "failed_items": [item.id for item in self.startup_items]
            }
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False