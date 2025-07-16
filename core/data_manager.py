#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.common_imports import QObject, Signal

"""
TimeNest 数据管理器
负责应用程序的数据存储、备份和管理功能
"""

import logging
import os
import json
import yaml
import sqlite3
import shutil
import zipfile
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from PySide6.QtCore import QObject, Signal, QTimer, QThread, Slot
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlError


class DataBackupWorker(QThread):
    """
    数据备份工作线程
    """
    
    backup_progress = Signal(int)  # 备份进度
    backup_finished = Signal(bool, str)  # 备份完成, 成功状态, 消息
    
    def __init__(self, data_manager, backup_path: str, include_files: List[str]):
        super().__init__()
        self.data_manager = data_manager
        self.backup_path = backup_path
        self.include_files = include_files
        self.logger = logging.getLogger(f'{__name__}.DataBackupWorker')
    
    def run(self):
        """
        执行备份任务
        """
        try:
            self.logger.info(f"开始数据备份到: {self.backup_path}")
            
            backup_path = Path(self.backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            total_files = len(self.include_files)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(self.include_files):
                    try:
                        file_path = Path(file_path)
                        if file_path.exists():
                            rel_path = file_path.relative_to(self.data_manager.data_dir)
                            zipf.write(file_path, rel_path)

                            progress = int((i + 1) / total_files * 100)
                            self.backup_progress.emit(progress)

                            self.logger.debug(f"已备份文件: {rel_path}")
                        
                    except Exception as e:
                        self.logger.warning(f"备份文件失败 {file_path}: {e}")
                        continue
            
            self.backup_finished.emit(True, f"备份完成: {backup_path}")
            self.logger.info("数据备份完成")
            
        except Exception as e:
            error_msg = f"数据备份失败: {e}"
            self.logger.error(error_msg)
            self.backup_finished.emit(False, error_msg)


class DataRestoreWorker(QThread):
    """
    数据恢复工作线程
    """
    
    restore_progress = Signal(int)  # 恢复进度
    restore_finished = Signal(bool, str)  # 恢复完成, 成功状态, 消息
    
    def __init__(self, data_manager, backup_path: str, restore_dir: str):
        super().__init__()
        self.data_manager = data_manager
        self.backup_path = backup_path
        self.restore_dir = restore_dir
        self.logger = logging.getLogger(f'{__name__}.DataRestoreWorker')
    
    def run(self):
        """
        执行恢复任务
        """
        try:
            self.logger.info(f"开始数据恢复从: {self.backup_path}")
            
            backup_path = Path(self.backup_path)
            restore_dir = Path(self.restore_dir)
            
            
            if not backup_path.exists():
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
                raise FileNotFoundError(f"备份文件不存在: {backup_path}")
            
            restore_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                file_list = zipf.namelist()
                total_files = len(file_list)
                
                for i, file_name in enumerate(file_list):
                    try:
                        zipf.extract(file_name, restore_dir)
                        
                        # 更新进度
                        progress = int((i + 1) / total_files * 100)
                        self.restore_progress.emit(progress)
                        
                        self.logger.debug(f"已恢复文件: {file_name}")
                        
                    except Exception as e:
                        self.logger.warning(f"恢复文件失败 {file_name}: {e}")
                        continue
            
            self.restore_finished.emit(True, f"恢复完成到: {restore_dir}")
            self.logger.info("数据恢复完成")
            
        except Exception as e:
            error_msg = f"数据恢复失败: {e}"
            self.logger.error(error_msg)
            self.restore_finished.emit(False, error_msg)


class DataManager(QObject):
    """
    数据管理器
    
    负责应用程序数据的存储、备份、恢复和管理
    """
    
    # 信号定义
    data_saved = Signal(str, str)  # 数据类型, 文件路径
    data_loaded = Signal(str, str)  # 数据类型, 文件路径
    data_deleted = Signal(str, str)  # 数据类型, 文件路径
    backup_started = Signal(str)  # 备份路径
    backup_progress = Signal(int)  # 备份进度
    backup_finished = Signal(bool, str)  # 备份完成, 成功状态, 消息
    restore_started = Signal(str)  # 恢复路径
    restore_progress = Signal(int)  # 恢复进度
    restore_finished = Signal(bool, str)  # 恢复完成, 成功状态, 消息
    cleanup_finished = Signal(int, int)  # 清理完成, 删除文件数, 释放空间(MB)
    database_error = Signal(str)  # 数据库错误
    
    def __init__(self, data_dir: str = None, config_manager=None, parent=None):
        """
        初始化数据管理器
        
        Args:
            data_dir: 数据目录路径
            config_manager: 配置管理器
            parent: 父对象
        """
        super().__init__(parent)
        
        # 设置日志
        self.logger = logging.getLogger(f'{__name__}.DataManager')
        
        # 配置管理器
        self.config_manager = config_manager
        
        # 数据目录
        if data_dir is None:
            if config_manager:
                data_dir = config_manager.get('data.data_dir', 'data')
                if not os.path.isabs(data_dir):
                    data_dir = config_manager.config_dir / data_dir
            else:
                data_dir = Path.home() / ".timenest" / "data"
        
        self.data_dir = Path(data_dir)
        
        # 子目录
        self.schedules_dir = self.data_dir / "schedules"
        self.logs_dir = self.data_dir / "logs"
        self.cache_dir = self.data_dir / "cache"
        self.temp_dir = self.data_dir / "temp"
        self.exports_dir = self.data_dir / "exports"
        self.backups_dir = self.data_dir / "backups"
        self.plugins_dir = self.data_dir / "plugins"
        self.user_data_dir = self.data_dir / "user_data"
        
        # 数据库
        self.db_file = self.data_dir / "timenest.db"
        self.db_connection = None
        
        # 备份和恢复工作线程
        self.backup_worker = None
        self.restore_worker = None
        
        # 自动清理定时器
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._auto_cleanup)
        
        # 初始化
        self._ensure_directories()
        self._init_database()
        self._start_auto_cleanup()
        
        self.logger.info(f"数据管理器初始化完成，数据目录: {self.data_dir}")
    
    def _ensure_directories(self):
        """
        确保所有必要的目录存在
        """
        try:
            directories = [
                self.data_dir,
                self.schedules_dir,
                self.logs_dir,
                self.cache_dir,
                self.temp_dir,
                self.exports_dir,
                self.backups_dir,
                self.plugins_dir,
                self.user_data_dir
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"目录已创建: {directory}")
            
        except Exception as e:
            self.logger.error(f"创建目录失败: {e}")
            raise
    
    def _init_database(self):
        """
        初始化数据库
        """
        try:
            # 创建数据库连接
            self.db_connection = QSqlDatabase.addDatabase("QSQLITE", "timenest_main")
            self.db_connection.setDatabaseName(str(self.db_file))
            
            
            if not self.db_connection.open():
                error = self.db_connection.lastError()
            
                error = self.db_connection.lastError()
                raise Exception(f"无法打开数据库: {error.text()}")
            
            # 创建表
            self._create_tables()
            
            self.logger.info(f"数据库初始化完成: {self.db_file}")
            
        except Exception as e:
            self.logger.error(f"初始化数据库失败: {e}")
            self.database_error.emit(str(e))
    
    def _create_tables(self):
        """
        创建数据库表
        """
        try:
            query = QSqlQuery(self.db_connection)
            
            # 用户数据表
            query.exec("""
                CREATE TABLE IF NOT EXISTS user_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    data_type TEXT DEFAULT 'string',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 应用日志表
            query.exec("""
                CREATE TABLE IF NOT EXISTS app_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    function TEXT,
                    line_number INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 操作历史表
            query.exec("""
                CREATE TABLE IF NOT EXISTS operation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    operation_data TEXT,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 文件元数据表
            query.exec("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_type TEXT,
                    file_size INTEGER,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 备份记录表
            query.exec("""
                CREATE TABLE IF NOT EXISTS backup_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_name TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    backup_size INTEGER,
                    backup_type TEXT DEFAULT 'full',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            query.exec("CREATE INDEX IF NOT EXISTS idx_user_data_key ON user_data(key)")
            query.exec("CREATE INDEX IF NOT EXISTS idx_app_logs_timestamp ON app_logs(timestamp)")
            query.exec("CREATE INDEX IF NOT EXISTS idx_operation_history_timestamp ON operation_history(timestamp)")
            query.exec("CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata(file_path)")
            query.exec("CREATE INDEX IF NOT EXISTS idx_backup_records_created ON backup_records(created_at)")
            
            self.logger.debug("数据库表创建完成")
            
        except Exception as e:
            self.logger.error(f"创建数据库表失败: {e}")
            raise
    
    def _start_auto_cleanup(self):
        """
        启动自动清理
        """
        try:
            if self.config_manager:
                auto_cleanup = self.config_manager.get('data.auto_cleanup', True)
                if auto_cleanup:
                    # 每天执行一次清理:
                    # 每天执行一次清理
                    self.cleanup_timer.start(24 * 60 * 60 * 1000)
                    self.logger.info("自动清理已启动")
            
        except Exception as e:
            self.logger.error(f"启动自动清理失败: {e}")
    
    def save_data(self, data_type: str, data: Any, file_name: str = None,
                  format: str = 'json', subdir: str = None) -> Optional[str]:
        """
        保存数据到文件
        
        Args:
            data_type: 数据类型
            data: 要保存的数据
            file_name: 文件名
            format: 保存格式 ('json', 'yaml', 'txt')
            subdir: 子目录
            
        Returns:
            保存的文件路径
        """
        try:
            # 确定保存目录
            if subdir:
                save_dir = self.data_dir / subdir
            elif data_type == 'schedule':
                save_dir = self.schedules_dir
            elif data_type == 'export':
                save_dir = self.exports_dir
            elif data_type == 'user_data':
                save_dir = self.user_data_dir
            else:
                save_dir = self.data_dir
            
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 确定文件名
            if file_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{data_type}_{timestamp}"
            
            # 确定文件扩展名
            if format == 'yaml':
                file_ext = '.yaml'
            elif format == 'txt':
                file_ext = '.txt'
            else:
                file_ext = '.json'
            
            
            if not file_name.endswith(file_ext):
                file_name += file_ext
            
            file_path = save_dir / file_name
            
            # 保存数据
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == 'yaml':
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                elif format == 'txt':
                    if isinstance(data, str):
                        f.write(data)
                    else:
                        f.write(str(data))
                else:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # 更新文件元数据
            self._update_file_metadata(file_path)
            
            # 发出信号
            self.data_saved.emit(data_type, str(file_path))
            
            self.logger.info(f"数据已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            return None
    
    def load_data(self, file_path: str, format: str = None) -> Optional[Any]:
        """
        从文件加载数据
        
        Args:
            file_path: 文件路径
            format: 文件格式 ('json', 'yaml', 'txt')
            
        Returns:
            加载的数据
        """
        try:
            file_path = Path(file_path)
            
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
            
                self.logger.warning(f"文件不存在: {file_path}")
                return None
            
            # 自动检测格式
            if format is None:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    format = 'yaml'
                elif file_path.suffix.lower() == '.txt':
                    format = 'txt'
                else:
                    format = 'json'
            
            # 加载数据
            with open(file_path, 'r', encoding='utf-8') as f:
                if format == 'yaml':
                    data = yaml.safe_load(f)
                elif format == 'txt':
                    data = f.read()
                else:
                    data = json.load(f)
            
            # 更新访问时间
            self._update_file_access_time(file_path)
            
            # 发出信号
            data_type = self._get_data_type_from_path(file_path)
            self.data_loaded.emit(data_type, str(file_path))
            
            self.logger.debug(f"数据已加载: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            return None
    
    def delete_data(self, file_path: str) -> bool:
        """
        删除数据文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            file_path = Path(file_path)
            
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
            
                self.logger.warning(f"文件不存在: {file_path}")
                return False
            
            # 删除文件
            file_path.unlink()
            
            # 删除文件元数据
            self._delete_file_metadata(file_path)
            
            # 发出信号
            data_type = self._get_data_type_from_path(file_path)
            self.data_deleted.emit(data_type, str(file_path))
            
            self.logger.info(f"数据已删除: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除数据失败: {e}")
            return False
    
    def list_data_files(self, data_type: str = None, subdir: str = None) -> List[Dict[str, Any]]:
        """
        列出数据文件
        
        Args:
            data_type: 数据类型过滤
            subdir: 子目录
            
        Returns:
            文件信息列表
        """
        try:
            # 确定搜索目录
            if subdir:
                search_dir = self.data_dir / subdir
            elif data_type == 'schedule':
                search_dir = self.schedules_dir
            elif data_type == 'export':
                search_dir = self.exports_dir
            elif data_type == 'user_data':
                search_dir = self.user_data_dir
            else:
                search_dir = self.data_dir
            
            
            if not search_dir.exists():
                return []
            
                return []
            
            files = []
            for file_path in search_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        file_info = {
                            'path': str(file_path),
                            'name': file_path.name,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_ctime),
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'accessed': datetime.fromtimestamp(stat.st_atime),
                            'type': self._get_data_type_from_path(file_path),
                            'format': file_path.suffix.lower().lstrip('.')
                        }
                        files.append(file_info)
                        
                    except Exception as e:
                        self.logger.warning(f"获取文件信息失败 {file_path}: {e}")
                        continue
            
            # 按修改时间排序
            files.sort(key=lambda x: x.get('modified'), reverse=True)
            
            return files
            
        except Exception as e:
            self.logger.error(f"列出数据文件失败: {e}")
            return []
    
    def _get_data_type_from_path(self, file_path: Path) -> str:
        """
        从文件路径推断数据类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            数据类型
        """
        try:
            if self.schedules_dir in file_path.parents:
                return 'schedule'
            elif self.exports_dir in file_path.parents:
                return 'export'
            elif self.user_data_dir in file_path.parents:
                return 'user_data'
            elif self.logs_dir in file_path.parents:
                return 'log'
            elif self.cache_dir in file_path.parents:
                return 'cache'
            elif self.temp_dir in file_path.parents:
                return 'temp'
            elif self.backups_dir in file_path.parents:
                return 'backup'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    def _update_file_metadata(self, file_path: Path):
        """
        更新文件元数据
        
        Args:
            file_path: 文件路径
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return
            
            stat = file_path.stat()
            file_type = self._get_data_type_from_path(file_path)
            
            # 计算文件校验和
            import hashlib
            with open(file_path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            
            query = QSqlQuery(self.db_connection)
            query.prepare("""
                INSERT OR REPLACE INTO file_metadata 
                (file_path, file_type, file_size, checksum, updated_at, accessed_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            
            query.addBindValue(str(file_path))
            query.addBindValue(file_type)
            query.addBindValue(stat.st_size)
            query.addBindValue(checksum)
            
            
            if not query.exec():
                error = query.lastError()
            
                error = query.lastError()
                self.logger.warning(f"更新文件元数据失败: {error.text()}")
            
        except Exception as e:
            self.logger.warning(f"更新文件元数据失败: {e}")
    
    def _update_file_access_time(self, file_path: Path):
        """
        更新文件访问时间
        
        Args:
            file_path: 文件路径
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return
            
            query = QSqlQuery(self.db_connection)
            query.prepare("""
                UPDATE file_metadata 
                SET accessed_at = CURRENT_TIMESTAMP 
                WHERE file_path = ?
            """)
            
            query.addBindValue(str(file_path))
            
            
            if not query.exec():
                error = query.lastError()
            
                error = query.lastError()
                self.logger.warning(f"更新文件访问时间失败: {error.text()}")
            
        except Exception as e:
            self.logger.warning(f"更新文件访问时间失败: {e}")
    
    def _delete_file_metadata(self, file_path: Path):
        """
        删除文件元数据
        
        Args:
            file_path: 文件路径
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return
            
            query = QSqlQuery(self.db_connection)
            query.prepare("DELETE FROM file_metadata WHERE file_path = ?")
            query.addBindValue(str(file_path))
            
            
            if not query.exec():
                error = query.lastError()
            
                error = query.lastError()
                self.logger.warning(f"删除文件元数据失败: {error.text()}")
            
        except Exception as e:
            self.logger.warning(f"删除文件元数据失败: {e}")
    
    def create_backup(self, backup_name: str = None, backup_type: str = 'full', 
                     description: str = None, include_files: List[str] = None) -> bool:
        """
        创建数据备份
        
        Args:
            backup_name: 备份名称
            backup_type: 备份类型 ('full', 'incremental')
            description: 备份描述
            include_files: 包含的文件列表
            
        Returns:
            是否成功启动备份
        """
        try:
            if self.backup_worker and self.backup_worker.isRunning():
                self.logger.warning("备份任务正在进行中")
                return False
            
            # 生成备份名称
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.backups_dir / f"{backup_name}.zip"
            
            # 确定要备份的文件
            if include_files is None:
                include_files = self._get_backup_files(backup_type)
            
            # 记录备份信息
            self._record_backup(backup_name, str(backup_path), backup_type, description)
            
            # 启动备份工作线程
            self.backup_worker = DataBackupWorker(self, str(backup_path), include_files)
            self.backup_worker.backup_progress.connect(self.backup_progress)
            self.backup_worker.backup_finished.connect(self._on_backup_finished)
            
            self.backup_worker.start()
            
            self.backup_started.emit(str(backup_path))
            self.logger.info(f"备份任务已启动: {backup_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return False
    
    def _get_backup_files(self, backup_type: str) -> List[str]:
        """
        获取要备份的文件列表
        
        Args:
            backup_type: 备份类型
            
        Returns:
            文件路径列表
        """
        files = []
        
        try:
            if backup_type == 'full':
                # 完整备份：包含所有数据文件:
                # 完整备份：包含所有数据文件
                for directory in [self.schedules_dir, self.user_data_dir, self.exports_dir]:
                    if directory.exists():
                        for file_path in directory.rglob('*'):
                            if file_path.is_file():
                                files.append(str(file_path))
                
                # 包含数据库文件
                if self.db_file.exists():
                    files.append(str(self.db_file))
                
            elif backup_type == 'incremental':
                # 增量备份：只包含最近修改的文件
                cutoff_time = datetime.now() - timedelta(days=1)
                
                for directory in [self.schedules_dir, self.user_data_dir, self.exports_dir]:
                    if directory.exists():
                        for file_path in directory.rglob('*'):
                            if file_path.is_file():
                                stat = file_path.stat()
                                if datetime.fromtimestamp(stat.st_mtime) > cutoff_time:
                                    files.append(str(file_path))
            
            self.logger.debug(f"备份文件列表生成完成，共 {len(files)} 个文件")
            
        except Exception as e:
            self.logger.error(f"生成备份文件列表失败: {e}")
        
        return files
    
    def _record_backup(self, backup_name: str, backup_path: str, 
                      backup_type: str, description: str):
        """
        记录备份信息
        
        Args:
            backup_name: 备份名称
            backup_path: 备份路径
            backup_type: 备份类型
            description: 备份描述
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return
            
            query = QSqlQuery(self.db_connection)
            query.prepare("""
                INSERT INTO backup_records 
                (backup_name, backup_path, backup_type, description)
                VALUES (?, ?, ?, ?)
            """)
            
            query.addBindValue(backup_name)
            query.addBindValue(backup_path)
            query.addBindValue(backup_type)
            query.addBindValue(description or '')
            
            
            if not query.exec():
                error = query.lastError()
            
                error = query.lastError()
                self.logger.warning(f"记录备份信息失败: {error.text()}")
            
        except Exception as e:
            self.logger.warning(f"记录备份信息失败: {e}")
    
    @Slot(bool, str)
    def _on_backup_finished(self, success: bool, message: str):
        """
        备份完成回调
        
        Args:
            success: 是否成功
            message: 消息
        """
        try:
            if success and self.backup_worker:
                # 更新备份大小:
                # 更新备份大小
                backup_path = Path(self.backup_worker.backup_path)
                if backup_path.exists():
                    backup_size = backup_path.stat().st_size
                    self._update_backup_size(str(backup_path), backup_size)
            
            self.backup_finished.emit(success, message)
            
            # 清理工作线程
            if self.backup_worker:
                self.backup_worker.deleteLater()
                self.backup_worker = None
            
        except Exception as e:
            self.logger.error(f"处理备份完成事件失败: {e}")
    
    def _update_backup_size(self, backup_path: str, backup_size: int):
        """
        更新备份大小
        
        Args:
            backup_path: 备份路径
            backup_size: 备份大小
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return
            
            query = QSqlQuery(self.db_connection)
            query.prepare("""
                UPDATE backup_records 
                SET backup_size = ? 
                WHERE backup_path = ?
            """)
            
            query.addBindValue(backup_size)
            query.addBindValue(backup_path)
            
            
            if not query.exec():
                error = query.lastError()
            
                error = query.lastError()
                self.logger.warning(f"更新备份大小失败: {error.text()}")
            
        except Exception as e:
            self.logger.warning(f"更新备份大小失败: {e}")
    
    def restore_backup(self, backup_path: str, restore_dir: str = None) -> bool:
        """
        恢复数据备份
        
        Args:
            backup_path: 备份文件路径
            restore_dir: 恢复目录
            
        Returns:
            是否成功启动恢复
        """
        try:
            if self.restore_worker and self.restore_worker.isRunning():
                self.logger.warning("恢复任务正在进行中")
                return False
            
            
            if restore_dir is None:
                restore_dir = str(self.data_dir)
            
                restore_dir = str(self.data_dir)
            
            # 启动恢复工作线程
            self.restore_worker = DataRestoreWorker(self, backup_path, restore_dir)
            self.restore_worker.restore_progress.connect(self.restore_progress)
            self.restore_worker.restore_finished.connect(self._on_restore_finished)
            
            self.restore_worker.start()
            
            self.restore_started.emit(backup_path)
            self.logger.info(f"恢复任务已启动: {backup_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"恢复备份失败: {e}")
            return False
    
    @Slot(bool, str)
    def _on_restore_finished(self, success: bool, message: str):
        """
        恢复完成回调
        
        Args:
            success: 是否成功
            message: 消息
        """
        try:
            self.restore_finished.emit(success, message)
            
            # 清理工作线程
            if self.restore_worker:
                self.restore_worker.deleteLater()
                self.restore_worker = None
            
        except Exception as e:
            self.logger.error(f"处理恢复完成事件失败: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份
        
        Returns:
            备份信息列表
        """
        try:
            backups = []
            
            
            if not self.db_connection or not self.db_connection.isOpen():
                return backups
            
                return backups
            
            query = QSqlQuery(self.db_connection)
            query.exec("""
                SELECT backup_name, backup_path, backup_size, backup_type, 
                       description, created_at
                FROM backup_records 
                ORDER BY created_at DESC
            """)
            
            while query.next():
                backup_info = {
                    'name': query.value(0),
                    'path': query.value(1),
                    'size': query.value(2) or 0,
                    'type': query.value(3),
                    'description': query.value(4),
                    'created_at': query.value(5)
                }
                
                # 检查文件是否存在
                backup_path = Path(backup_info.get('path'))
                backup_info['exists'] = backup_path.exists()
                
                
                if backup_info.get('exists') and backup_info['size'] == 0:
                    # 更新文件大小:
                
                    # 更新文件大小
                    backup_info['size'] = backup_path.stat().st_size
                    self._update_backup_size(backup_info.get('path'), backup_info.get('size'))
                
                backups.append(backup_info)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"列出备份失败: {e}")
            return []
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        删除备份
        
        Args:
            backup_path: 备份路径
            
        Returns:
            是否删除成功
        """
        try:
            backup_path = Path(backup_path)
            
            # 删除文件
            if backup_path.exists():
                backup_path.unlink()
            
            # 删除数据库记录
            if self.db_connection and self.db_connection.isOpen():
                query = QSqlQuery(self.db_connection)
                query.prepare("DELETE FROM backup_records WHERE backup_path = ?")
                query.addBindValue(str(backup_path))
                
                
                if not query.exec():
                    error = query.lastError()
                
                    error = query.lastError()
                    self.logger.warning(f"删除备份记录失败: {error.text()}")
            
            self.logger.info(f"备份已删除: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除备份失败: {e}")
            return False
    
    @Slot()
    def _auto_cleanup(self):
        """
        自动清理
        """
        try:
            self.logger.info("开始自动清理")
            
            deleted_files = 0
            freed_space = 0
            
            
            if self.config_manager:
                cleanup_days = self.config_manager.get('data.cleanup_days', 30)
            
                cleanup_days = self.config_manager.get('data.cleanup_days', 30)
            else:
                cleanup_days = 30
            
            cutoff_time = datetime.now() - timedelta(days=cleanup_days)
            
            # 清理临时文件
            if self.temp_dir.exists():
                for file_path in self.temp_dir.rglob('*'):
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            if datetime.fromtimestamp(stat.st_mtime) < cutoff_time:
                                freed_space += stat.st_size
                                file_path.unlink()
                                deleted_files += 1
                        except Exception as e:
                            self.logger.warning(f"清理临时文件失败 {file_path}: {e}")
            
            # 清理缓存文件
            if self.cache_dir.exists():
                for file_path in self.cache_dir.rglob('*'):
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            if datetime.fromtimestamp(stat.st_atime) < cutoff_time:
                                freed_space += stat.st_size
                                file_path.unlink()
                                deleted_files += 1
                        except Exception as e:
                            self.logger.warning(f"清理缓存文件失败 {file_path}: {e}")
            
            # 清理旧日志
            self._cleanup_old_logs(cutoff_time)
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            freed_space_mb = freed_space // (1024 * 1024)
            self.cleanup_finished.emit(deleted_files, freed_space_mb)
            
            self.logger.info(f"自动清理完成，删除 {deleted_files} 个文件，释放 {freed_space_mb} MB 空间")
            
        except Exception as e:
            self.logger.error(f"自动清理失败: {e}")
    
    def _cleanup_old_logs(self, cutoff_time: datetime):
        """
        清理旧日志
        
        Args:
            cutoff_time: 截止时间
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return
            
            query = QSqlQuery(self.db_connection)
            query.prepare("DELETE FROM app_logs WHERE timestamp < ?")
            query.addBindValue(cutoff_time.isoformat())
            
            
            if query.exec():
                deleted_count = query.numRowsAffected()
            
                deleted_count = query.numRowsAffected()
                if deleted_count > 0:
                    self.logger.debug(f"清理旧日志记录: {deleted_count} 条")
            else:
                error = query.lastError()
                self.logger.warning(f"清理旧日志失败: {error.text()}")
            
        except Exception as e:
            self.logger.warning(f"清理旧日志失败: {e}")
    
    def _cleanup_old_backups(self):
        """
        清理旧备份
        """
        try:
            if self.config_manager:
                max_backups = self.config_manager.get('schedule.max_backups', 10)
            else:
                max_backups = 10
            
            backups = self.list_backups()
            
            
            if len(backups) > max_backups:
                # 删除最旧的备份:
            
                # 删除最旧的备份
                old_backups = backups[max_backups:]
                for backup in old_backups:
                    self.delete_backup(backup.get('path'))
                
                self.logger.debug(f"清理旧备份: {len(old_backups)} 个")
            
        except Exception as e:
            self.logger.warning(f"清理旧备份失败: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储信息
        
        Returns:
            存储信息字典
        """
        try:
            info = {
                'data_dir': str(self.data_dir),
                'total_size': 0,
                'file_count': 0,
                'directories': {}
            }
            
            # 统计各目录的大小和文件数
            directories = {
                'schedules': self.schedules_dir,
                'logs': self.logs_dir,
                'cache': self.cache_dir,
                'temp': self.temp_dir,
                'exports': self.exports_dir,
                'backups': self.backups_dir,
                'user_data': self.user_data_dir
            }
            
            for dir_name, dir_path in directories.items():
                if dir_path.exists():
                    dir_size = 0
                    dir_files = 0
                    
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file():
                            try:
                                file_size = file_path.stat().st_size
                                dir_size += file_size
                                dir_files += 1
                            except Exception:
                                continue
                    
                    info.get('directories')[dir_name] = {
                        'size': dir_size,
                        'size_mb': dir_size // (1024 * 1024),
                        'file_count': dir_files
                    }
                    
                    info['total_size'] = info.get('total_size', 0) + dir_size
                    info['file_count'] = info.get('file_count', 0) + dir_files
                else:
                    info.get('directories')[dir_name] = {
                        'size': 0,
                        'size_mb': 0,
                        'file_count': 0
                    }
            
            info['total_size_mb'] = info.get('total_size') // (1024 * 1024)
            
            return info
            
        except Exception as e:
            self.logger.error(f"获取存储信息失败: {e}")
            return {}

    def save_setting(self, key: str, value: Any) -> bool:
        """
        保存设置（优化版本）

        Args:
            key: 设置键
            value: 设置值

        Returns:
            是否保存成功
        """
        # 输入验证
        if not key or not isinstance(key, str) or key.strip() == "":
            self.logger.error("设置键不能为空")
            return False

        try:
            if not self.db_connection or not self.db_connection.isOpen():
                self.logger.error("数据库连接不可用")
                return False

            # 开始事务以确保数据一致性
            if not self.db_connection.transaction():
                self.logger.error("无法开始事务")
                return False

            try:
                # 优化的数据类型检测和序列化
                if isinstance(value, bool):
                    data_type = 'bool'
                    value_str = str(value).lower()
                elif isinstance(value, int):
                    data_type = 'int'
                    value_str = str(value)
                elif isinstance(value, float):
                    data_type = 'float'
                    value_str = str(value)
                elif isinstance(value, (list, dict, tuple)):
                    data_type = 'json'
                    try:
                        value_str = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
                    except (TypeError, ValueError) as e:
                        self.logger.error(f"JSON序列化失败: {e}")
                        self.db_connection.rollback()
                        return False
                elif value is None:
                    data_type = 'null'
                    value_str = 'null'
                else:
                    data_type = 'string'
                    value_str = str(value)

                # 使用预编译语句提高性能
                query = QSqlQuery(self.db_connection)
                query.prepare("""
                    INSERT OR REPLACE INTO user_data
                    (key, value, data_type, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """)

                query.addBindValue(key.strip())
                query.addBindValue(value_str)
                query.addBindValue(data_type)

                if not query.exec():
                    error = query.lastError()
                    self.logger.error(f"保存设置失败: {error.text()}")
                    self.db_connection.rollback()
                    return False

                # 提交事务
                if not self.db_connection.commit():
                    self.logger.error("提交事务失败")
                    return False

                self.logger.debug(f"设置已保存: {key} = {value} (类型: {data_type})")
                return True

            except Exception as e:
                self.db_connection.rollback()
                raise e

        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False

    def load_setting(self, key: str, default_value: Any = None) -> Any:
        """
        加载设置

        Args:
            key: 设置键
            default_value: 默认值

        Returns:
            设置值
        """
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return default_value

            query = QSqlQuery(self.db_connection)
            query.prepare("SELECT value, data_type FROM user_data WHERE key = ?")
            query.addBindValue(key)

            if not query.exec():
                error = query.lastError()
                self.logger.error(f"加载设置失败: {error.text()}")
                return default_value

            if query.next():
                value_str = query.value(0)
                data_type = query.value(1)

                # 根据数据类型转换值
                if data_type == 'bool':
                    return value_str.lower() == 'true'
                elif data_type == 'int':
                    return int(value_str)
                elif data_type == 'float':
                    return float(value_str)
                elif data_type == 'json':
                    return json.loads(value_str)
                else:
                    return value_str

            return default_value

        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            return default_value

    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """
        获取设置（load_setting的别名）

        Args:
            key: 设置键
            default_value: 默认值

        Returns:
            设置值
        """
        return self.load_setting(key, default_value)

    def cleanup(self):
        """
        清理资源
        """
        try:
            # 停止定时器
            if self.cleanup_timer.isActive():
                self.cleanup_timer.stop()
            
            # 停止工作线程
            if self.backup_worker and self.backup_worker.isRunning():
                self.backup_worker.terminate()
                self.backup_worker.wait()
            
            
            if self.restore_worker and self.restore_worker.isRunning():
                self.restore_worker.terminate()
            
                self.restore_worker.terminate()
                self.restore_worker.wait()
            
            # 关闭数据库连接
            if self.db_connection and self.db_connection.isOpen():
                self.db_connection.close()
            
            self.logger.info("数据管理器资源已清理")
            
        except Exception as e:
            self.logger.error(f"清理数据管理器失败: {e}")

    def import_data(self, file_path: str) -> bool:
        """导入数据"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"导入文件不存在: {file_path}")
                return False

            # 根据文件扩展名选择导入方式
            if file_path.suffix.lower() == '.json':
                return self._import_json_data(file_path)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                return self._import_yaml_data(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                return self._import_excel_data(file_path)
            else:
                self.logger.error(f"不支持的文件格式: {file_path.suffix}")
                return False

        except Exception as e:
            self.logger.error(f"导入数据失败: {e}")
            return False

    def export_data(self, file_path: str) -> bool:
        """导出数据"""
        try:
            file_path = Path(file_path)

            # 根据文件扩展名选择导出方式
            if file_path.suffix.lower() == '.json':
                return self._export_json_data(file_path)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                return self._export_yaml_data(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                return self._export_excel_data(file_path)
            else:
                self.logger.error(f"不支持的文件格式: {file_path.suffix}")
                return False

        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            return False

    def backup_data(self) -> bool:
        """备份数据"""
        try:
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"timenest_backup_{timestamp}.zip"

            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 备份数据库文件
                if self.db_path.exists():
                    zipf.write(self.db_path, "database.db")

                # 备份配置文件
                config_files = [
                    self.data_dir / "config.json",
                    self.data_dir / "settings.json",
                    self.data_dir / "themes.json"
                ]

                for config_file in config_files:
                    if config_file.exists():
                        zipf.write(config_file, config_file.name)

                # 备份插件数据
                plugins_dir = self.data_dir / "plugins"
                if plugins_dir.exists():
                    for plugin_file in plugins_dir.rglob("*"):
                        if plugin_file.is_file():
                            arcname = f"plugins/{plugin_file.relative_to(plugins_dir)}"
                            zipf.write(plugin_file, arcname)

            self.logger.info(f"数据备份成功: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"数据备份失败: {e}")
            return False

    def restore_data(self) -> bool:
        """恢复数据"""
        try:
            backup_dir = self.data_dir / "backups"
            if not backup_dir.exists():
                self.logger.error("备份目录不存在")
                return False

            # 找到最新的备份文件
            backup_files = list(backup_dir.glob("timenest_backup_*.zip"))
            if not backup_files:
                self.logger.error("没有找到备份文件")
                return False

            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)

            # 创建临时恢复目录
            temp_dir = self.data_dir / "temp_restore"
            temp_dir.mkdir(exist_ok=True)

            try:
                with zipfile.ZipFile(latest_backup, 'r') as zipf:
                    zipf.extractall(temp_dir)

                # 恢复数据库
                temp_db = temp_dir / "database.db"
                if temp_db.exists():
                    # 关闭当前数据库连接
                    if self.db_connection and self.db_connection.isOpen():
                        self.db_connection.close()

                    # 备份当前数据库
                    if self.db_path.exists():
                        backup_current = self.db_path.with_suffix('.db.backup')
                        shutil.copy2(self.db_path, backup_current)

                    # 恢复数据库
                    shutil.copy2(temp_db, self.db_path)

                    # 重新初始化数据库连接
                    self._init_database()

                # 恢复配置文件
                config_files = ["config.json", "settings.json", "themes.json"]
                for config_file in config_files:
                    temp_config = temp_dir / config_file
                    if temp_config.exists():
                        target_config = self.data_dir / config_file
                        shutil.copy2(temp_config, target_config)

                # 恢复插件数据
                temp_plugins = temp_dir / "plugins"
                if temp_plugins.exists():
                    target_plugins = self.data_dir / "plugins"
                    if target_plugins.exists():
                        shutil.rmtree(target_plugins)
                    shutil.copytree(temp_plugins, target_plugins)

                self.logger.info(f"数据恢复成功: {latest_backup}")
                return True

            finally:
                # 清理临时目录
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

        except Exception as e:
            self.logger.error(f"数据恢复失败: {e}")
            return False

    def _import_json_data(self, file_path: Path) -> bool:
        """导入JSON数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 导入课程数据
            if 'courses' in data:
                self._import_courses_data(data['courses'])

            # 导入任务数据
            if 'tasks' in data:
                self._import_tasks_data(data['tasks'])

            # 导入设置数据
            if 'settings' in data:
                self._import_settings_data(data['settings'])

            self.logger.info(f"JSON数据导入成功: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"导入JSON数据失败: {e}")
            return False

    def _import_yaml_data(self, file_path: Path) -> bool:
        """导入YAML数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # 导入课程数据
            if 'courses' in data:
                self._import_courses_data(data['courses'])

            # 导入任务数据
            if 'tasks' in data:
                self._import_tasks_data(data['tasks'])

            # 导入设置数据
            if 'settings' in data:
                self._import_settings_data(data['settings'])

            self.logger.info(f"YAML数据导入成功: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"导入YAML数据失败: {e}")
            return False

    def _import_excel_data(self, file_path: Path) -> bool:
        """导入Excel数据"""
        try:
            from core.excel_schedule_manager import ExcelScheduleManager
            excel_manager = ExcelScheduleManager()

            courses = excel_manager.import_from_excel(str(file_path))
            if courses:
                self._import_courses_data(courses)
                self.logger.info(f"Excel数据导入成功: {file_path}")
                return True
            else:
                self.logger.error("Excel文件中没有有效的课程数据")
                return False

        except Exception as e:
            self.logger.error(f"导入Excel数据失败: {e}")
            return False

    def _export_json_data(self, file_path: Path) -> bool:
        """导出JSON数据"""
        try:
            data = {
                'courses': self._export_courses_data(),
                'tasks': self._export_tasks_data(),
                'settings': self._export_settings_data(),
                'export_time': datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"JSON数据导出成功: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"导出JSON数据失败: {e}")
            return False

    def _export_yaml_data(self, file_path: Path) -> bool:
        """导出YAML数据"""
        try:
            data = {
                'courses': self._export_courses_data(),
                'tasks': self._export_tasks_data(),
                'settings': self._export_settings_data(),
                'export_time': datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"YAML数据导出成功: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"导出YAML数据失败: {e}")
            return False

    def _export_excel_data(self, file_path: Path) -> bool:
        """导出Excel数据"""
        try:
            from core.excel_schedule_manager import ExcelScheduleManager
            excel_manager = ExcelScheduleManager()

            courses = self._export_courses_data()
            if excel_manager.export_to_excel(courses, str(file_path)):
                self.logger.info(f"Excel数据导出成功: {file_path}")
                return True
            else:
                self.logger.error("Excel数据导出失败")
                return False

        except Exception as e:
            self.logger.error(f"导出Excel数据失败: {e}")
            return False

    def _import_courses_data(self, courses_data: List[Dict]) -> None:
        """导入课程数据到数据库"""
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return

            query = QSqlQuery(self.db_connection)
            query.prepare("""
                INSERT OR REPLACE INTO courses
                (name, teacher, location, time, weekday, start_week, end_week)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """)

            for course in courses_data:
                query.addBindValue(course.get('name', ''))
                query.addBindValue(course.get('teacher', ''))
                query.addBindValue(course.get('location', ''))
                query.addBindValue(course.get('time', ''))
                query.addBindValue(course.get('weekday', ''))
                query.addBindValue(course.get('start_week', 1))
                query.addBindValue(course.get('end_week', 16))

                if not query.exec():
                    self.logger.error(f"导入课程失败: {query.lastError().text()}")

        except Exception as e:
            self.logger.error(f"导入课程数据失败: {e}")

    def _import_tasks_data(self, tasks_data: List[Dict]) -> None:
        """导入任务数据到数据库"""
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return

            query = QSqlQuery(self.db_connection)
            query.prepare("""
                INSERT OR REPLACE INTO tasks
                (title, description, priority, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """)

            for task in tasks_data:
                query.addBindValue(task.get('title', ''))
                query.addBindValue(task.get('description', ''))
                query.addBindValue(task.get('priority', 'medium'))
                query.addBindValue(task.get('due_date', ''))
                query.addBindValue(task.get('status', 'pending'))

                if not query.exec():
                    self.logger.error(f"导入任务失败: {query.lastError().text()}")

        except Exception as e:
            self.logger.error(f"导入任务数据失败: {e}")

    def _import_settings_data(self, settings_data: Dict) -> None:
        """导入设置数据"""
        try:
            settings_file = self.data_dir / "settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"导入设置数据失败: {e}")

    def _export_courses_data(self) -> List[Dict]:
        """导出课程数据"""
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return []

            query = QSqlQuery("SELECT * FROM courses", self.db_connection)
            courses = []

            while query.next():
                course = {
                    'name': query.value('name'),
                    'teacher': query.value('teacher'),
                    'location': query.value('location'),
                    'time': query.value('time'),
                    'weekday': query.value('weekday'),
                    'start_week': query.value('start_week'),
                    'end_week': query.value('end_week')
                }
                courses.append(course)

            return courses

        except Exception as e:
            self.logger.error(f"导出课程数据失败: {e}")
            return []

    def _export_tasks_data(self) -> List[Dict]:
        """导出任务数据"""
        try:
            if not self.db_connection or not self.db_connection.isOpen():
                return []

            query = QSqlQuery("SELECT * FROM tasks", self.db_connection)
            tasks = []

            while query.next():
                task = {
                    'title': query.value('title'),
                    'description': query.value('description'),
                    'priority': query.value('priority'),
                    'due_date': query.value('due_date'),
                    'status': query.value('status')
                }
                tasks.append(task)

            return tasks

        except Exception as e:
            self.logger.error(f"导出任务数据失败: {e}")
            return []

    def _export_settings_data(self) -> Dict:
        """导出设置数据"""
        try:
            settings_file = self.data_dir / "settings.json"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"导出设置数据失败: {e}")
            return {}

    def save_all_data(self) -> bool:
        """保存所有数据"""
        try:
            # 确保数据库事务提交
            if self.db_connection and self.db_connection.isOpen():
                self.db_connection.commit()

            self.logger.info("所有数据已保存")
            return True

        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            return False

    def __del__(self):
        """
        析构函数
        """
        self.cleanup()