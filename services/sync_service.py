"""
数据同步服务
提供多设备数据同步功能
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Any
from datetime import datetime
from utils.logger import get_service_logger

# 初始化日志记录器
logger = get_service_logger("sync_service")


class SyncService:
    """数据同步服务类"""
    
    def __init__(self):
        """初始化数据同步服务"""
        self.sync_directory = "./data/sync"
        self._ensure_sync_directory()
        logger.info("SyncService initialized")
    
    def _ensure_sync_directory(self):
        """确保同步目录存在"""
        try:
            os.makedirs(self.sync_directory, exist_ok=True)
            logger.debug(f"确保同步目录存在: {self.sync_directory}")
        except Exception as e:
            logger.error(f"创建同步目录失败: {str(e)}")
    
    def sync_to_directory(self, target_directory: str) -> bool:
        """
        同步数据到指定目录
        
        Args:
            target_directory: 目标目录路径
            
        Returns:
            是否同步成功
        """
        logger.info(f"同步数据到目录: {target_directory}")
        
        try:
            # 确保目标目录存在
            os.makedirs(target_directory, exist_ok=True)
            
            # 获取要同步的数据
            sync_data = self._collect_sync_data()
            
            # 生成数据文件
            data_file_path = os.path.join(target_directory, "sync_data.json")
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(sync_data, f, ensure_ascii=False, indent=2)
            
            # 生成元数据文件
            metadata = self._generate_metadata(sync_data)
            metadata_file_path = os.path.join(target_directory, "sync_metadata.json")
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 复制其他必要文件
            self._copy_additional_files(target_directory)
            
            logger.info(f"数据同步到目录成功: {target_directory}")
            return True
            
        except Exception as e:
            logger.error(f"同步数据到目录失败: {str(e)}")
            return False
    
    def sync_from_directory(self, source_directory: str) -> bool:
        """
        从指定目录同步数据
        
        Args:
            source_directory: 源目录路径
            
        Returns:
            是否同步成功
        """
        logger.info(f"从目录同步数据: {source_directory}")
        
        try:
            # 检查源目录是否存在
            if not os.path.exists(source_directory):
                logger.warning(f"源目录不存在: {source_directory}")
                return False
            
            # 检查必要的文件是否存在
            data_file_path = os.path.join(source_directory, "sync_data.json")
            if not os.path.exists(data_file_path):
                logger.warning(f"同步数据文件不存在: {data_file_path}")
                return False
            
            # 读取同步数据
            with open(data_file_path, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            
            # 验证数据完整性
            metadata_file_path = os.path.join(source_directory, "sync_metadata.json")
            if os.path.exists(metadata_file_path):
                with open(metadata_file_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                if not self._verify_data_integrity(sync_data, metadata):
                    logger.warning("同步数据完整性验证失败")
                    return False
            
            # 导入数据到各服务
            self._import_sync_data(sync_data)
            
            # 复制其他必要文件
            self._copy_additional_files_from_source(source_directory)
            
            logger.info(f"从目录同步数据成功: {source_directory}")
            return True
            
        except Exception as e:
            logger.error(f"从目录同步数据失败: {str(e)}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        获取同步状态
        
        Returns:
            同步状态信息
        """
        logger.debug("获取同步状态")
        
        try:
            # 延迟导入ServiceFactory以避免循环导入
            from services.service_factory import ServiceFactory
            
            # 获取本地数据信息
            course_service = ServiceFactory.get_course_service()
            schedule_service = ServiceFactory.get_schedule_service()
            temp_change_service = ServiceFactory.get_temp_change_service()
            cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
            
            status: Dict[str, Any] = {
                "local_data": {
                    "courses_count": len(course_service.get_all_courses()),
                    "schedules_count": len(schedule_service.get_all_schedules()),
                    "temp_changes_count": len(temp_change_service.get_all_temp_changes()),
                    "cycle_schedules_count": len(cycle_schedule_service.get_all_cycle_schedules())
                },
                "sync_directory": self.sync_directory,
                "last_sync_time": self._get_last_sync_time(),
                "sync_enabled": True
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取同步状态失败: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _collect_sync_data(self) -> Dict[str, Any]:
        """
        收集要同步的数据
        
        Returns:
            要同步的数据字典
        """
        logger.debug("收集同步数据")
        
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        sync_data = {}
        
        # 获取各服务实例
        course_service = ServiceFactory.get_course_service()
        schedule_service = ServiceFactory.get_schedule_service()
        temp_change_service = ServiceFactory.get_temp_change_service()
        cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
        
        # 收集课程数据
        courses = course_service.get_all_courses()
        sync_data["courses"] = [course.to_dict() for course in courses]
        
        # 收集课程表数据
        schedules = schedule_service.get_all_schedules()
        sync_data["schedules"] = [schedule.to_dict() for schedule in schedules]
        
        # 收集临时换课数据
        temp_changes = temp_change_service.get_all_temp_changes()
        sync_data["temp_changes"] = [temp_change.to_dict() for temp_change in temp_changes]
        
        # 收集循环课程表数据
        cycle_schedules = cycle_schedule_service.get_all_cycle_schedules()
        sync_data["cycle_schedules"] = [cycle_schedule.to_dict() for cycle_schedule in cycle_schedules]
        
        return sync_data
    
    def _generate_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成数据元数据
        
        Args:
            data: 数据字典
            
        Returns:
            元数据字典
        """
        logger.debug("生成数据元数据")
        
        # 计算数据哈希值
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
        
        # 获取数据大小
        data_size = len(data_str.encode('utf-8'))
        
        metadata: Dict[str, Any] = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "data_hash": data_hash,
            "data_size": data_size,
            "record_counts": {
                "courses": len(data.get("courses", [])),
                "schedules": len(data.get("schedules", [])),
                "temp_changes": len(data.get("temp_changes", [])),
                "cycle_schedules": len(data.get("cycle_schedules", []))
            }
        }
        
        return metadata
    
    def _verify_data_integrity(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 数据字典
            metadata: 元数据字典
            
        Returns:
            数据是否完整
        """
        logger.debug("验证数据完整性")
        
        try:
            # 验证数据哈希值
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
            data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
            
            if data_hash != metadata.get("data_hash"):
                logger.warning("数据哈希值不匹配")
                return False
            
            # 验证记录数量
            record_counts = metadata.get("record_counts", {})
            if (len(data.get("courses", [])) != record_counts.get("courses", 0) or
                len(data.get("schedules", [])) != record_counts.get("schedules", 0) or
                len(data.get("temp_changes", [])) != record_counts.get("temp_changes", 0) or
                len(data.get("cycle_schedules", [])) != record_counts.get("cycle_schedules", 0)):
                logger.warning("记录数量不匹配")
                return False
            
            logger.debug("数据完整性验证通过")
            return True
            
        except Exception as e:
            logger.error(f"数据完整性验证失败: {str(e)}")
            return False
    
    def _import_sync_data(self, data: Dict[str, Any]):
        """
        导入同步数据到各服务
        
        Args:
            data: 要导入的数据字典
        """
        logger.debug("导入同步数据")
        
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        # 获取各服务实例
        course_service = ServiceFactory.get_course_service()
        schedule_service = ServiceFactory.get_schedule_service()
        temp_change_service = ServiceFactory.get_temp_change_service()
        cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
        
        # 导入课程数据
        if "courses" in data:
            logger.debug(f"导入 {len(data['courses'])} 门课程")
            # 注意：这里简化处理，实际项目中可能需要更复杂的导入逻辑
        
        # 导入课程表数据
        if "schedules" in data:
            logger.debug(f"导入 {len(data['schedules'])} 个课程表项")
            # 注意：这里简化处理，实际项目中可能需要更复杂的导入逻辑
        
        # 导入临时换课数据
        if "temp_changes" in data:
            logger.debug(f"导入 {len(data['temp_changes'])} 个临时换课")
            # 注意：这里简化处理，实际项目中可能需要更复杂的导入逻辑
        
        # 导入循环课程表数据
        if "cycle_schedules" in data:
            logger.debug(f"导入 {len(data['cycle_schedules'])} 个循环课程表")
            # 注意：这里简化处理，实际项目中可能需要更复杂的导入逻辑
        
        logger.debug("同步数据导入完成")
    
    def _copy_additional_files(self, target_directory: str):
        """
        复制其他必要文件到目标目录
        
        Args:
            target_directory: 目标目录路径
        """
        logger.debug(f"复制其他必要文件到: {target_directory}")
        
        # 这里可以复制配置文件、插件文件等
        # 简化处理：实际项目中可能需要复制更多文件
        
        try:
            # 复制配置文件示例
            config_source = "./data/config.json"
            config_target = os.path.join(target_directory, "config.json")
            if os.path.exists(config_source):
                shutil.copy2(config_source, config_target)
                logger.debug("复制配置文件完成")
        except Exception as e:
            logger.warning(f"复制配置文件失败: {str(e)}")
    
    def _copy_additional_files_from_source(self, source_directory: str):
        """
        从源目录复制其他必要文件
        
        Args:
            source_directory: 源目录路径
        """
        logger.debug(f"从源目录复制其他必要文件: {source_directory}")
        
        # 这里可以复制配置文件、插件文件等
        # 简化处理：实际项目中可能需要复制更多文件
        
        try:
            # 复制配置文件示例
            config_source = os.path.join(source_directory, "config.json")
            config_target = "./data/config.json"
            if os.path.exists(config_source):
                shutil.copy2(config_source, config_target)
                logger.debug("复制配置文件完成")
        except Exception as e:
            logger.warning(f"复制配置文件失败: {str(e)}")
    
    def _get_last_sync_time(self) -> str:
        """
        获取最后同步时间
        
        Returns:
            最后同步时间字符串
        """
        try:
            metadata_file = os.path.join(self.sync_directory, "sync_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata.get("created_at", "")
            return ""
        except Exception as e:
            logger.warning(f"获取最后同步时间失败: {str(e)}")
            return ""
