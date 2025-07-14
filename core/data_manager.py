#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

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
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlError


class DataBackupWorker(QThread):
    """
    数据备份工作线程
    """
    
    backup_progress = pyqtSignal(int)  # 备份进度
    backup_finished = pyqtSignal(bool, str)  # 备份完成, 成功状态, 消息
    
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
                            # 计算相对路径:
                            # 计算相对路径
                            rel_path = file_path.relative_to(self.data_manager.data_dir)
                            zipf.write(file_path, rel_path)
                            
                            # 更新进度
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
    
    restore_progress = pyqtSignal(int)  # 恢复进度
    restore_finished = pyqtSignal(bool, str)  # 恢复完成, 成功状态, 消息
    
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
    data_saved = pyqtSignal(str, str)  # 数据类型, 文件路径
    data_loaded = pyqtSignal(str, str)  # 数据类型, 文件路径
    data_deleted = pyqtSignal(str, str)  # 数据类型, 文件路径
    backup_started = pyqtSignal(str)  # 备份路径
    backup_progress = pyqtSignal(int)  # 备份进度
    backup_finished = pyqtSignal(bool, str)  # 备份完成, 成功状态, 消息
    restore_started = pyqtSignal(str)  # 恢复路径
    restore_progress = pyqtSignal(int)  # 恢复进度
    restore_finished = pyqtSignal(bool, str)  # 恢复完成, 成功状态, 消息
    cleanup_finished = pyqtSignal(int, int)  # 清理完成, 删除文件数, 释放空间(MB)
    database_error = pyqtSignal(str)  # 数据库错误
    
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
    
    @pyqtSlot(bool, str)
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
    
    @pyqtSlot(bool, str)
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
    
    @pyqtSlot()
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
    
    def __del__(self):
        """
        析构函数
        """
        self.cleanup()