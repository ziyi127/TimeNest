"""
计划任务调度服务
提供跨平台的任务调度和执行功能
"""

import json
import os
import platform
import subprocess
import threading
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from models.scheduled_task import ScheduledTask, TaskSettings, OSType, TaskType
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("task_scheduler_service")


class TaskSchedulerService:
    """计划任务调度服务类"""
    
    def __init__(self):
        """初始化计划任务调度服务"""
        self.config_file = "./data/task_scheduler_config.json"
        self.data_file = "./data/task_scheduler_data.json"
        self.settings: Optional[TaskSettings] = None
        self.scheduled_tasks: List[ScheduledTask] = []
        self.running_tasks: Dict[str, subprocess.Popen] = {}
        self._ensure_data_directory()
        self._load_settings()
        self._load_scheduled_tasks()
        logger.info("TaskSchedulerService initialized")
    
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
        """加载任务调度设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = TaskSettings.from_dict(data)
                logger.debug("任务调度设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = TaskSettings()
                self._save_settings()
                logger.debug("创建默认任务调度设置")
        except Exception as e:
            logger.error(f"加载任务调度设置失败: {str(e)}")
            self.settings = TaskSettings()
    
    def _save_settings(self):
        """保存任务调度设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("任务调度设置保存成功")
        except Exception as e:
            logger.error(f"保存任务调度设置失败: {str(e)}")
            raise ValidationException("保存任务调度设置失败")
    
    def _load_scheduled_tasks(self):
        """加载计划任务数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.scheduled_tasks = [ScheduledTask.from_dict(item) for item in data]
                logger.debug(f"计划任务数据加载成功，共 {len(self.scheduled_tasks)} 个项目")
        except Exception as e:
            logger.error(f"加载计划任务数据失败: {str(e)}")
    
    def _save_scheduled_tasks(self):
        """保存计划任务数据"""
        try:
            # 确保数据目录存在
            self._ensure_data_directory()
            
            data = [item.to_dict() for item in self.scheduled_tasks]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("计划任务数据保存成功")
        except Exception as e:
            logger.error(f"保存计划任务数据失败: {str(e)}")
    
    def get_settings(self) -> TaskSettings:
        """
        获取任务调度设置
        
        Returns:
            TaskSettings: 任务调度设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or TaskSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新任务调度设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        logger.info("更新任务调度设置")
        
        try:
            if not self.settings:
                self.settings = TaskSettings()
            
            # 更新设置字段
            for key, value in settings_data.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            # 保存设置
            self._save_settings()
            
            logger.info("任务调度设置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新任务调度设置失败: {str(e)}")
            return False
    
    def get_scheduled_tasks(self) -> List[ScheduledTask]:
        """
        获取所有计划任务
        
        Returns:
            List[ScheduledTask]: 计划任务列表
        """
        return self.scheduled_tasks
    
    def get_scheduled_task(self, task_id: str) -> Optional[ScheduledTask]:
        """
        根据任务ID获取计划任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[ScheduledTask]: 计划任务
        """
        for task in self.scheduled_tasks:
            if task.id == task_id:
                return task
        return None
    
    def add_scheduled_task(self, task: ScheduledTask) -> bool:
        """
        添加计划任务
        
        Args:
            task: 计划任务
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查任务ID是否已存在
            if self.get_scheduled_task(task.id):
                logger.warning(f"计划任务已存在: {task.id}")
                return False
            
            self.scheduled_tasks.append(task)
            self._save_scheduled_tasks()
            logger.info(f"添加计划任务: {task.id} -> {task.name}")
            return True
        except Exception as e:
            logger.error(f"添加计划任务失败: {str(e)}")
            return False
    
    def update_scheduled_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        更新计划任务
        
        Args:
            task_id: 任务ID
            task_data: 任务数据字典
            
        Returns:
            bool: 是否更新成功
        """
        try:
            task = self.get_scheduled_task(task_id)
            if not task:
                logger.warning(f"计划任务未找到: {task_id}")
                return False
            
            # 更新任务字段
            for key, value in task_data.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            self._save_scheduled_tasks()
            logger.info(f"更新计划任务: {task.id} -> {task.name}")
            return True
        except Exception as e:
            logger.error(f"更新计划任务失败: {str(e)}")
            return False
    
    def remove_scheduled_task(self, task_id: str) -> bool:
        """
        删除计划任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            task = self.get_scheduled_task(task_id)
            if not task:
                logger.warning(f"计划任务未找到: {task_id}")
                return False
            
            self.scheduled_tasks.remove(task)
            self._save_scheduled_tasks()
            logger.info(f"删除计划任务: {task.id} -> {task.name}")
            return True
        except Exception as e:
            logger.error(f"删除计划任务失败: {str(e)}")
            return False
    
    def get_current_os(self) -> OSType:
        """
        获取当前操作系统类型
        
        Returns:
            OSType: 操作系统类型
        """
        system = platform.system().lower()
        if system == "windows":
            return OSType.WINDOWS
        elif system == "darwin":
            return OSType.MACOS
        elif system == "linux":
            return OSType.LINUX
        else:
            return OSType.UNKNOWN
    
    def get_os_specific_command(self, task: ScheduledTask) -> str:
        """
        获取特定操作系统的命令
        
        Args:
            task: 计划任务
            
        Returns:
            str: 操作系统特定的命令
        """
        current_os = self.get_current_os()
        
        # 如果任务定义了特定操作系统的命令，则使用该命令
        if current_os == OSType.WINDOWS and task.windows_command:
            return task.windows_command
        elif current_os == OSType.MACOS and task.mac_command:
            return task.mac_command
        elif current_os == OSType.LINUX and task.linux_command:
            return task.linux_command
        
        # 否则使用通用命令
        return task.command
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        执行计划任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            task = self.get_scheduled_task(task_id)
            if not task:
                logger.warning(f"计划任务未找到: {task_id}")
                return {
                    "success": False,
                    "message": "任务未找到",
                    "task_id": task_id
                }
            
            # 获取适用于当前操作系统的命令
            command = self.get_os_specific_command(task)
            if not command:
                logger.warning(f"任务命令为空: {task_id}")
                return {
                    "success": False,
                    "message": "任务命令为空",
                    "task_id": task_id
                }
            
            # 检查是否有相同任务正在运行
            if task_id in self.running_tasks:
                logger.warning(f"任务已在运行: {task_id}")
                return {
                    "success": False,
                    "message": "任务已在运行",
                    "task_id": task_id
                }
            
            # 执行命令
            logger.info(f"执行任务: {task_id} -> {command}")
            
            # 根据任务类型执行不同的命令
            if task.task_type == TaskType.PROGRAM:
                # 程序执行
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif task.task_type == TaskType.FILE:
                # 文件打开
                if self.get_current_os() == OSType.WINDOWS:
                    process = subprocess.Popen(
                        f'start "" "{command}"',
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                elif self.get_current_os() == OSType.MACOS:
                    process = subprocess.Popen(
                        f'open "{command}"',
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                elif self.get_current_os() == OSType.LINUX:
                    process = subprocess.Popen(
                        f'xdg-open "{command}"',
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                else:
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
            else:
                # 默认执行方式
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # 记录正在运行的任务
            self.running_tasks[task_id] = process
            
            # 异步等待任务完成
            def wait_for_completion():
                try:
                    stdout, stderr = process.communicate()
                    exit_code = process.returncode
                    
                    # 从运行中的任务中移除
                    if task_id in self.running_tasks:
                        del self.running_tasks[task_id]
                    
                    logger.info(f"任务执行完成: {task_id}, 退出码: {exit_code}")
                    
                    # 记录执行日志
                    self._log_task_execution(task_id, exit_code, stdout, stderr)
                except Exception as e:
                    logger.error(f"等待任务完成时出错: {str(e)}")
                    # 从运行中的任务中移除
                    if task_id in self.running_tasks:
                        del self.running_tasks[task_id]
            
            # 启动异步线程等待任务完成
            thread = threading.Thread(target=wait_for_completion)
            thread.daemon = True
            thread.start()
            
            return {
                "success": True,
                "message": "任务开始执行",
                "task_id": task_id
            }
        except Exception as e:
            logger.error(f"执行任务失败: {str(e)}")
            return {
                "success": False,
                "message": f"执行任务失败: {str(e)}",
                "task_id": task_id
            }
    
    def _log_task_execution(self, task_id: str, exit_code: int, stdout: str, stderr: str):
        """
        记录任务执行日志
        
        Args:
            task_id: 任务ID
            exit_code: 退出码
            stdout: 标准输出
            stderr: 错误输出
        """
        try:
            log_entry = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr
            }
            
            # 确保日志目录存在
            log_dir = "./logs"
            os.makedirs(log_dir, exist_ok=True)
            
            # 写入日志文件
            log_file = os.path.join(log_dir, f"task_{task_id}.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
            logger.debug(f"任务执行日志已记录: {task_id}")
        except Exception as e:
            logger.error(f"记录任务执行日志失败: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 任务状态
        """
        try:
            task = self.get_scheduled_task(task_id)
            if not task:
                return {
                    "task_id": task_id,
                    "exists": False,
                    "running": False,
                    "message": "任务未找到"
                }
            
            # 检查任务是否正在运行
            is_running = task_id in self.running_tasks
            
            return {
                "task_id": task_id,
                "exists": True,
                "running": is_running,
                "message": "任务正在运行" if is_running else "任务未运行"
            }
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            return {
                "task_id": task_id,
                "exists": False,
                "running": False,
                "message": f"获取任务状态失败: {str(e)}"
            }
    
    def stop_task(self, task_id: str) -> Dict[str, Any]:
        """
        停止正在运行的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 停止结果
        """
        try:
            if task_id not in self.running_tasks:
                return {
                    "success": False,
                    "message": "任务未在运行",
                    "task_id": task_id
                }
            
            process = self.running_tasks[task_id]
            process.terminate()  # 尝试优雅终止
            
            # 等待一段时间看是否终止
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果优雅终止失败，强制杀死进程
                process.kill()
                process.wait()
            
            # 从运行中的任务中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            logger.info(f"任务已停止: {task_id}")
            
            return {
                "success": True,
                "message": "任务已停止",
                "task_id": task_id
            }
        except Exception as e:
            logger.error(f"停止任务失败: {str(e)}")
            return {
                "success": False,
                "message": f"停止任务失败: {str(e)}",
                "task_id": task_id
            }
    
    def get_running_tasks(self) -> List[str]:
        """
        获取所有正在运行的任务ID列表
        
        Returns:
            List[str]: 正在运行的任务ID列表
        """
        return list(self.running_tasks.keys())
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False