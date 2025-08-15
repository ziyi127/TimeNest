"""
JSON数据访问层实现
提供JSON文件的读写、序列化/反序列化、数据验证、备份和恢复功能
支持跨平台兼容性和增强的错误处理
"""

import json
import os
import shutil
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONDataAccess:
    """JSON数据访问类"""
    
    def __init__(self, data_dir: str = "./data"):
        """
        初始化JSON数据访问对象
        
        Args:
            data_dir: 数据存储目录路径
        """
        self.data_dir = os.path.normpath(data_dir)
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        self.backup_dir = os.path.join(self.data_dir, "backups")
        self.backup_dir = os.path.normpath(self.backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _get_file_path(self, filename: str) -> str:
        """
        获取文件完整路径，确保跨平台兼容性
        
        Args:
            filename: 文件名
            
        Returns:
            文件完整路径
        """
        return os.path.normpath(os.path.join(self.data_dir, filename))
    
    def read_json(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        读取JSON文件，增强错误处理和跨平台兼容性
        
        Args:
            filename: 文件名
            
        Returns:
            JSON数据字典，如果文件不存在或读取失败则返回None
        """
        file_path = self._get_file_path(filename)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning(f"文件 {file_path} 不存在")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"解析JSON文件 {file_path} 失败: {e}")
            return None
        except PermissionError as e:
            logger.error(f"没有权限访问文件 {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"读取文件 {file_path} 失败: {e}")
            return None
    
    def write_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """
        写入JSON文件，增强错误处理和跨平台兼容性
        
        Args:
            filename: 文件名
            data: 要写入的数据
            
        Returns:
            写入成功返回True，否则返回False
        """
        file_path = self._get_file_path(filename)
        
        try:
            # 确保数据目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 创建临时文件以确保原子写入
            temp_file_path = file_path + ".tmp"
            
            with open(temp_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            
            # 原子性地替换原文件
            shutil.move(temp_file_path, file_path)
            return True
        except PermissionError as e:
            logger.error(f"没有权限写入文件 {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"写入文件 {file_path} 失败: {e}")
            return False
    
    def validate_data(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        验证数据是否符合指定的模式
        
        Args:
            data: 要验证的数据
            schema: 数据模式定义
            
        Returns:
            验证通过返回True，否则返回False
        """
        # 简单的数据验证实现
        try:
            for key, expected_type in schema.items():
                if key not in data:
                    logger.warning(f"数据缺少必需字段: {key}")
                    return False
                
                if not isinstance(data[key], expected_type):
                    logger.warning(f"字段 {key} 类型不匹配，期望 {expected_type}，实际 {type(data[key])}")
                    return False
            return True
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return False
    
    def backup_data(self, filename: str) -> bool:
        """
        备份指定的数据文件，增强跨平台兼容性
        
        Args:
            filename: 要备份的文件名
            
        Returns:
            备份成功返回True，否则返回False
        """
        try:
            source_path = self._get_file_path(filename)
            if not os.path.exists(source_path):
                logger.warning(f"源文件 {source_path} 不存在，无法备份")
                return False
            
            # 生成备份文件名，包含时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filename}.backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            backup_path = os.path.normpath(backup_path)
            
            # 复制文件到备份目录
            shutil.copy2(source_path, backup_path)
            logger.info(f"文件 {filename} 已备份到 {backup_path}")
            return True
        except PermissionError as e:
            logger.error(f"没有权限创建备份文件: {e}")
            return False
        except Exception as e:
            logger.error(f"备份文件 {filename} 失败: {e}")
            return False
    
    def restore_data(self, filename: str, backup_filename: str) -> bool:
        """
        从备份文件恢复数据，增强跨平台兼容性
        
        Args:
            filename: 要恢复的文件名
            backup_filename: 备份文件名
            
        Returns:
            恢复成功返回True，否则返回False
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            backup_path = os.path.normpath(backup_path)
            if not os.path.exists(backup_path):
                logger.warning(f"备份文件 {backup_path} 不存在")
                return False
            
            target_path = self._get_file_path(filename)
            
            # 复制备份文件到目标位置
            shutil.copy2(backup_path, target_path)
            logger.info(f"已从 {backup_filename} 恢复文件 {filename}")
            return True
        except PermissionError as e:
            logger.error(f"没有权限恢复文件: {e}")
            return False
        except Exception as e:
            logger.error(f"从备份 {backup_filename} 恢复文件 {filename} 失败: {e}")
            return False
    
    def list_backups(self, filename: str) -> List[str]:
        """
        列出指定文件的所有备份，增强跨平台兼容性
        
        Args:
            filename: 文件名
            
        Returns:
            备份文件名列表
        """
        backups: List[str] = []
        try:
            # 查找匹配的备份文件
            prefix = f"{filename}.backup_"
            for file in os.listdir(self.backup_dir):
                if file.startswith(prefix):
                    backups.append(os.path.normpath(file))
            # 按时间戳排序，最新的在前
            backups.sort(reverse=True)
        except PermissionError as e:
            logger.error(f"没有权限访问备份目录: {e}")
        except Exception as e:
            logger.error(f"列出 {filename} 的备份文件失败: {e}")
        
        return backups