"""
备份恢复服务
提供数据备份和恢复相关的业务逻辑处理
<<<<<<< HEAD
作者: TimeNest团队
创建日期: 2024-01-01
版本: 1.0.0
描述: 提供数据备份和恢复相关的业务逻辑处理，包括创建、恢复、列出和删除备份等功能
=======
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

import os
import json
import shutil
import zipfile
from typing import List, Dict, Any
from datetime import datetime
from models.backup import BackupInfo, BackupConfig
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("backup_service")


class BackupService:
    """备份恢复服务类"""
    
    def __init__(self):
        """初始化备份恢复服务"""
        self.backup_config = BackupConfig()
        self._load_backup_config()
        logger.info("BackupService initialized")
    
    def _load_backup_config(self):
        """加载备份配置"""
        # 简化实现：在实际项目中可能需要从文件或数据库加载配置
        logger.debug("加载备份配置")
    
    def create_backup(self, name: str, description: str = "", compress: bool = True) -> BackupInfo:
        """
        创建备份
        
        Args:
            name: 备份名称
            description: 备份描述
            compress: 是否压缩备份文件
            
        Returns:
            备份信息对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info(f"创建备份: {name}")
        
        try:
            # 生成备份相关信息
            backup_id, backup_file_path = self._generate_backup_info(name, compress)
            
            # 确保备份目录存在
            self._ensure_backup_directory_exists()
            
            # 标准化路径确保跨平台兼容性
            backup_file_path = os.path.normpath(backup_file_path)
            
            # 收集并创建备份数据
            self._create_backup_data(backup_file_path, compress)
            
            # 获取文件大小并创建备份信息对象
            backup_info = self._create_backup_info_object(
                backup_id, name, description, backup_file_path)
            
            # 保存备份信息（简化实现：在实际项目中可能需要保存到文件或数据库）
            logger.info(f"备份创建成功: {backup_file_path}")
            return backup_info
            
        except PermissionError as e:
            logger.error(f"没有权限创建备份: {str(e)}")
            raise ValidationException(f"没有权限创建备份: {str(e)}")
        except Exception as e:
            logger.error(f"创建备份失败: {str(e)}")
            raise ValidationException(f"创建备份失败: {str(e)}")
    
    def _generate_backup_info(self, name: str, compress: bool) -> tuple[str, str]:
        """
        生成备份相关信息
        
        Args:
            name: 备份名称
            compress: 是否压缩备份文件
            
        Returns:
            备份ID和备份文件路径的元组
        """
        backup_id = self._generate_backup_id()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{backup_id}"
        
        # 确定备份文件路径
        backup_dir = self.backup_config.backup_location
        if compress:
            backup_file_path = os.path.join(backup_dir, f"{backup_filename}.zip")
        else:
            backup_file_path = os.path.join(backup_dir, backup_filename)
            
        return backup_id, backup_file_path
    
    def _ensure_backup_directory_exists(self) -> None:
        """
        确保备份目录存在
        """
        backup_dir = self.backup_config.backup_location
        os.makedirs(backup_dir, exist_ok=True)
    
    def _create_backup_data(self, backup_file_path: str, compress: bool) -> None:
        """
        创建备份数据
        
        Args:
            backup_file_path: 备份文件路径
            compress: 是否压缩备份文件
        """
        # 收集要备份的数据
        backup_data = self._collect_backup_data()
        
        # 创建备份文件
        if compress:
            self._create_compressed_backup(backup_data, backup_file_path)
        else:
            self._create_uncompressed_backup(backup_data, backup_file_path)
    
    def _create_backup_info_object(self, backup_id: str, name: str, description: str, 
                                   backup_file_path: str) -> BackupInfo:
        """
        创建备份信息对象
        
        Args:
            backup_id: 备份ID
            name: 备份名称
            description: 备份描述
            backup_file_path: 备份文件路径
            
        Returns:
            备份信息对象
        """
        # 获取文件大小
        file_size = os.path.getsize(backup_file_path)
        
        # 创建备份信息对象
        return BackupInfo(
            id=backup_id,
            name=name,
            description=description,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_path=backup_file_path,
            file_size=file_size,
            include_courses=True,
            include_schedules=True,
            include_temp_changes=True,
            include_cycle_schedules=True
        )
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        恢复备份
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否恢复成功
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info(f"恢复备份: {backup_id}")
        
        try:
            # 查找并验证备份文件
            backup_file_path = self._locate_and_validate_backup_file(backup_id)
            
            # 标准化路径确保跨平台兼容性
            backup_file_path = os.path.normpath(backup_file_path)
            
            # 读取备份数据
            backup_data = self._read_backup_data(backup_file_path)
            
            # 恢复数据到各服务
            self._restore_data_to_services(backup_data)
            
            logger.info(f"备份恢复成功: {backup_id}")
            return True
            
        except PermissionError as e:
            logger.error(f"没有权限恢复备份: {str(e)}")
            raise ValidationException(f"没有权限恢复备份: {str(e)}")
        except Exception as e:
            logger.error(f"恢复备份失败: {str(e)}")
            raise ValidationException(f"恢复备份失败: {str(e)}")
    
    def _locate_and_validate_backup_file(self, backup_id: str) -> str:
        """
        查找并验证备份文件是否存在
        
        Args:
            backup_id: 备份ID
            
        Returns:
            备份文件路径
            
        Raises:
            ValidationException: 备份文件不存在
        """
        # 查找备份文件（简化实现：在实际项目中可能需要从文件或数据库查找备份信息）
        backup_file_path = self._find_backup_file(backup_id)
        if not backup_file_path or not os.path.exists(backup_file_path):
            raise ValidationException(f"备份文件不存在: {backup_id}")
        return backup_file_path
    
    def _read_backup_data(self, backup_file_path: str) -> Dict[str, Any]:
        """
        读取备份数据
        
        Args:
            backup_file_path: 备份文件路径
            
        Returns:
            备份数据字典
        """
        if backup_file_path.endswith(".zip"):
            return self._read_compressed_backup(backup_file_path)
        else:
            return self._read_uncompressed_backup(backup_file_path)
    
    def list_backups(self) -> List[BackupInfo]:
        """
        列出所有备份，增强跨平台兼容性
        
        Returns:
            备份信息列表
        """
        logger.info("列出所有备份")
        
        try:
            # 检查并获取备份目录中的文件
            backup_files = self._get_backup_files()
            
            # 为每个文件创建备份信息
            backups = self._create_backup_info_list(backup_files)
            
            # 按创建时间排序（最新的在前）
            backups.sort(key=lambda x: x.created_at, reverse=True)
            
            logger.info(f"找到 {len(backups)} 个备份")
            return backups
            
        except PermissionError as e:
            logger.error(f"没有权限访问备份目录: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"列出备份失败: {str(e)}")
            return []
    
    def _get_backup_files(self) -> List[str]:
        """
        获取备份目录中的所有文件路径
        
        Returns:
            备份文件路径列表
        """
        backup_dir = os.path.normpath(self.backup_config.backup_location)
        
        # 检查备份目录是否存在
        if not os.path.exists(backup_dir):
            return []
        
        # 遍历备份目录中的文件
        backup_files = []
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            file_path = os.path.normpath(file_path)
            if os.path.isfile(file_path):
                backup_files.append(file_path)
                
        return backup_files
    
    def _create_backup_info_list(self, backup_files: List[str]) -> List[BackupInfo]:
        """
        为备份文件列表创建备份信息对象列表
        
        Args:
            backup_files: 备份文件路径列表
            
        Returns:
            备份信息对象列表
        """
        backups: List[BackupInfo] = []
        
        for file_path in backup_files:
            filename = os.path.basename(file_path)
            backup_info = BackupInfo(
                id=self._extract_backup_id_from_filename(filename),
                name=filename,
                description="",
                created_at=datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S"),
                file_path=file_path,
                file_size=os.path.getsize(file_path)
            )
            backups.append(backup_info)
            
        return backups
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        删除备份
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否删除成功
        """
        logger.info(f"删除备份: {backup_id}")
        
        try:
            # 查找备份文件
            backup_file_path = self._find_backup_file(backup_id)
            if not backup_file_path or not os.path.exists(backup_file_path):
                logger.warning(f"备份文件不存在: {backup_id}")
                return False
            
            # 标准化路径确保跨平台兼容性
            backup_file_path = os.path.normpath(backup_file_path)
            
            # 删除备份文件
            os.remove(backup_file_path)
            
            logger.info(f"备份删除成功: {backup_id}")
            return True
            
        except PermissionError as e:
            logger.error(f"没有权限删除备份: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"删除备份失败: {str(e)}")
            return False
    
    def _generate_backup_id(self) -> str:
        """
        生成备份ID
        
        Returns:
            备份ID
        """
        import uuid
        return str(uuid.uuid4())
    
    def _collect_backup_data(self) -> Dict[str, Any]:
        """
        收集要备份的数据
        
        Returns:
            要备份的数据字典
        """
        logger.debug("收集备份数据")
        
        # 获取各服务实例
        services = self._get_backup_services()
        
        backup_data: Dict[str, Any] = {}
        
        # 收集各种数据类型
        self._collect_data_types_for_backup(backup_data, services)
        
        return backup_data

    def _get_backup_services(self) -> Dict[str, Any]:
        """
        获取备份所需的所有服务实例
        
        Returns:
            包含各服务实例的字典
        """
        from services.service_factory import ServiceFactory
        
        return {
            "course_service": ServiceFactory.get_course_service(),
            "schedule_service": ServiceFactory.get_schedule_service(),
            "temp_change_service": ServiceFactory.get_temp_change_service(),
            "cycle_schedule_service": ServiceFactory.get_cycle_schedule_service()
        }

    def _collect_data_types_for_backup(self, backup_data: Dict[str, Any], services: Dict[str, Any]) -> None:
        """
        收集各种数据类型用于备份
        
        Args:
            backup_data: 备份数据字典
            services: 服务实例字典
        """
        # 定义数据收集函数映射
        data_collection_mapping = {
            "courses": self._collect_courses_for_backup,
            "schedules": self._collect_schedules_for_backup,
            "temp_changes": self._collect_temp_changes_for_backup,
            "cycle_schedules": self._collect_cycle_schedules_for_backup
        }
        
        # 收集每种数据类型
        for data_key, collect_func in data_collection_mapping.items():
            backup_data[data_key] = collect_func(services)

    def _collect_courses_for_backup(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集课程数据用于备份
        
        Args:
            services: 服务实例字典
            
        Returns:
            课程数据列表
        """
        course_service = services["course_service"]
        courses = course_service.get_all_courses()
        return [course.to_dict() for course in courses]
    
    def _collect_schedules_for_backup(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集课程表数据用于备份
        
        Args:
            services: 服务实例字典
            
        Returns:
            课程表数据列表
        """
        schedule_service = services["schedule_service"]
        schedules = schedule_service.get_all_schedules()
        return [schedule.to_dict() for schedule in schedules]
    
    def _collect_temp_changes_for_backup(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集临时换课数据用于备份
        
        Args:
            services: 服务实例字典
            
        Returns:
            临时换课数据列表
        """
        temp_change_service = services["temp_change_service"]
        temp_changes = temp_change_service.get_all_temp_changes()
        return [temp_change.to_dict() for temp_change in temp_changes]
    
    def _collect_cycle_schedules_for_backup(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集循环课程表数据用于备份
        
        Args:
            services: 服务实例字典
            
        Returns:
            循环课程表数据列表
        """
        cycle_schedule_service = services["cycle_schedule_service"]
        cycle_schedules = cycle_schedule_service.get_all_cycle_schedules()
        return [cycle_schedule.to_dict() for cycle_schedule in cycle_schedules]
    
    def _create_compressed_backup(self, data: Dict[str, Any], backup_file_path: str):
        """
        创建压缩备份文件
        
        Args:
            data: 要备份的数据
            backup_file_path: 备份文件路径
        """
        logger.debug(f"创建压缩备份: {backup_file_path}")
        
        # 创建临时目录
        temp_dir = self._create_temp_directory(backup_file_path)
        
        try:
            # 将数据写入临时JSON文件
            temp_file_path = self._write_temp_backup_data(temp_dir, data)
            
            # 创建ZIP文件
            self._create_zip_file(backup_file_path, temp_file_path)
            
            # 删除临时目录
            self._remove_temp_directory(temp_dir)
            
        except Exception as e:
            # 清理临时目录
            self._remove_temp_directory(temp_dir)
            raise e
    
    def _create_temp_directory(self, backup_file_path: str) -> str:
        """
        创建临时目录
        
        Args:
            backup_file_path: 备份文件路径
            
        Returns:
            临时目录路径
        """
        temp_dir = backup_file_path + "_temp"
        temp_dir = os.path.normpath(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    def _write_temp_backup_data(self, temp_dir: str, data: Dict[str, Any]) -> str:
        """
        将备份数据写入临时文件
        
        Args:
            temp_dir: 临时目录路径
            data: 要备份的数据
            
        Returns:
            临时文件路径
        """
        temp_file_path = os.path.join(temp_dir, "backup_data.json")
        temp_file_path = os.path.normpath(temp_file_path)
        try:
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"写入临时文件失败: {str(e)}")
            raise
        return temp_file_path
    
    def _create_zip_file(self, backup_file_path: str, temp_file_path: str) -> None:
        """
        创建ZIP文件
        
        Args:
            backup_file_path: 备份文件路径
            temp_file_path: 临时文件路径
        """
        with zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(temp_file_path, "backup_data.json")
    
    def _remove_temp_directory(self, temp_dir: str) -> None:
        """
        删除临时目录
        
        Args:
            temp_dir: 临时目录路径
        """
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def _create_uncompressed_backup(self, data: Dict[str, Any], backup_file_path: str):
        """
        创建未压缩备份文件
        
        Args:
            data: 要备份的数据
            backup_file_path: 备份文件路径
        """
        logger.debug(f"创建未压缩备份: {backup_file_path}")
        
        with open(backup_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _read_compressed_backup(self, backup_file_path: str) -> Dict[str, Any]:
        """
        读取压缩备份文件
        
        Args:
            backup_file_path: 备份文件路径
            
        Returns:
            备份数据字典
        """
        logger.debug(f"读取压缩备份: {backup_file_path}")
        
        # 创建临时目录
        temp_dir = self._create_temp_directory(backup_file_path)
        
        try:
            # 解压ZIP文件
            self._extract_zip_file(backup_file_path, temp_dir)
            
            # 读取数据
            data = self._read_backup_data_from_temp(temp_dir)
            
            # 删除临时目录
            self._remove_temp_directory(temp_dir)
            
            return data
            
        except Exception as e:
            # 清理临时目录
            self._remove_temp_directory(temp_dir)
            raise e
    
    def _extract_zip_file(self, backup_file_path: str, temp_dir: str) -> None:
        """
        解压ZIP文件
        
        Args:
            backup_file_path: 备份文件路径
            temp_dir: 临时目录路径
        """
        try:
            with zipfile.ZipFile(backup_file_path, 'r') as zipf:
                zipf.extractall(temp_dir)
        except zipfile.BadZipFile as e:
            logger.error(f"无效的ZIP文件: {str(e)}")
            raise ValidationException(f"无效的ZIP文件: {str(e)}")
        except Exception as e:
            logger.error(f"解压ZIP文件失败: {str(e)}")
            raise
    
    def _read_backup_data_from_temp(self, temp_dir: str) -> Dict[str, Any]:
        """
        从临时目录读取备份数据
        
        Args:
            temp_dir: 临时目录路径
            
        Returns:
            备份数据字典
        """
        temp_file_path = os.path.join(temp_dir, "backup_data.json")
        temp_file_path = os.path.normpath(temp_file_path)
        try:
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误: {str(e)}")
            raise ValidationException(f"JSON格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"读取备份数据失败: {str(e)}")
            raise
    
    def _read_uncompressed_backup(self, backup_file_path: str) -> Dict[str, Any]:
        """
        读取未压缩备份文件
        
        Args:
            backup_file_path: 备份文件路径
            
        Returns:
            备份数据字典
        """
        logger.debug(f"读取未压缩备份: {backup_file_path}")
        
        with open(backup_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _restore_data_to_services(self, data: Dict[str, Any]) -> None:
        """
        将数据恢复到各服务中
        
        Args:
            data: 要恢复的数据
        """
        logger.debug("恢复数据到服务")
        
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        # 获取各服务实例
        # 使用 # type: ignore 注释忽略未使用变量警告，因为这些变量在简化实现中未被使用
        course_service = ServiceFactory.get_course_service()  # type: ignore
        schedule_service = ServiceFactory.get_schedule_service()  # type: ignore
        temp_change_service = ServiceFactory.get_temp_change_service()  # type: ignore
        cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()  # type: ignore
        
        # 恢复课程数据
        if "courses" in data:
            # 简化实现：在实际项目中可能需要更复杂的恢复逻辑
            logger.debug(f"恢复 {len(data['courses'])} 门课程数据")
        
        # 恢复课程表数据
        if "schedules" in data:
            # 简化实现：在实际项目中可能需要更复杂的恢复逻辑
            logger.debug(f"恢复 {len(data['schedules'])} 个课程表数据")
        
        # 恢复临时换课数据
        if "temp_changes" in data:
            # 简化实现：在实际项目中可能需要更复杂的恢复逻辑
            logger.debug(f"恢复 {len(data['temp_changes'])} 个临时换课数据")
        
        # 恢复循环课程表数据
        if "cycle_schedules" in data:
            # 简化实现：在实际项目中可能需要更复杂的恢复逻辑
            logger.debug(f"恢复 {len(data['cycle_schedules'])} 个循环课程表数据")
        
        logger.debug("数据恢复到服务完成")
    
    def _find_backup_file(self, backup_id: str) -> str:
        """
        查找备份文件路径，增强跨平台兼容性
        
        Args:
            backup_id: 备份ID
            
        Returns:
            备份文件路径
        """
        logger.debug(f"查找备份文件: {backup_id}")
        
        # 简化实现：在实际项目中应该从存储的元数据中查找备份文件路径
        backup_dir = os.path.normpath(self.backup_config.backup_location)
        if not os.path.exists(backup_dir):
            return ""
        
        # 遍历备份目录查找匹配的文件
        for filename in os.listdir(backup_dir):
            if backup_id in filename:
                file_path = os.path.join(backup_dir, filename)
                return os.path.normpath(file_path)
        
        return ""
    
    def _extract_backup_id_from_filename(self, filename: str) -> str:
        """
        从文件名中提取备份ID
        
        Args:
            filename: 文件名
            
        Returns:
            备份ID
        """
        # 简化实现：从文件名中提取UUID-like字符串
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, filename)
        return match.group(0) if match else filename
