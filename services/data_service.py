"""
数据导入导出服务
提供数据导入导出相关的业务逻辑处理
"""

import os
import json
import csv
from typing import Dict, List, Any
from models.data_export import DataExportConfig, DataImportConfig, ExportFormat
from models.class_item import ClassItem
from models.class_plan import ClassPlan
from models.temp_change import TempChange
from models.cycle_schedule import CycleSchedule
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("data_service")


class DataService:
    """数据导入导出服务类"""
    
    def __init__(self):
        """初始化数据导入导出服务"""
        logger.info("DataService initialized")
    
    def export_data(self, config: DataExportConfig, export_path: str) -> str:
        """
        导出数据
        
        Args:
            config: 导出配置
            export_path: 导出文件路径
            
        Returns:
            导出文件的完整路径
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info(f"导出数据到: {export_path}")
        
        try:
            # 获取要导出的数据
            export_data = self._collect_export_data(config)
            
            # 根据格式导出数据
            if config.format == ExportFormat.JSON:
                file_path = self._export_json(export_data, export_path)
            elif config.format == ExportFormat.CSV:
                file_path = self._export_csv(export_data, export_path)
            elif config.format == ExportFormat.EXCEL:
                file_path = self._export_excel(export_data, export_path)
            else:
                raise ValidationException(f"不支持的导出格式: {config.format}")
            
            logger.info(f"数据导出成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            raise ValidationException(f"数据导出失败: {str(e)}")
    
    def import_data(self, config: DataImportConfig, import_path: str) -> bool:
        """
        导入数据
        
        Args:
            config: 导入配置
            import_path: 导入文件路径
            
        Returns:
            是否导入成功
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info(f"从 {import_path} 导入数据")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(import_path):
                raise ValidationException(f"导入文件不存在: {import_path}")
            
            # 根据格式导入数据
            if config.format == ExportFormat.JSON:
                import_data = self._import_json(import_path)
            elif config.format == ExportFormat.CSV:
                import_data = self._import_csv(import_path)
            elif config.format == ExportFormat.EXCEL:
                import_data = self._import_excel(import_path)
            else:
                raise ValidationException(f"不支持的导入格式: {config.format}")
            
            # 验证数据
            if config.validate_data:
                self._validate_import_data(import_data)
            
            # 导入数据
            self._import_data_to_services(import_data, config.overwrite_existing)
            
            logger.info("数据导入成功")
            return True
            
        except Exception as e:
            logger.error(f"数据导入失败: {str(e)}")
            raise ValidationException(f"数据导入失败: {str(e)}")
    
    def _collect_export_data(self, config: DataExportConfig) -> Dict[str, Any]:
        """
        收集要导出的数据
        
        Args:
            config: 导出配置
            
        Returns:
            要导出的数据字典
        """
        logger.debug("收集导出数据")
        
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        export_data: Dict[str, Any] = {}
        
        # 获取各服务实例
        course_service = ServiceFactory.get_course_service()
        schedule_service = ServiceFactory.get_schedule_service()
        temp_change_service = ServiceFactory.get_temp_change_service()
        cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
        
        # 导出课程数据
        if config.include_courses:
            courses = course_service.get_all_courses()
            export_data["courses"] = [course.to_dict() for course in courses]
        
        # 导出课程表数据
        if config.include_schedules:
            schedules = schedule_service.get_all_schedules()
            export_data["schedules"] = [schedule.to_dict() for schedule in schedules]
        
        # 导出临时换课数据
        if config.include_temp_changes:
            temp_changes = temp_change_service.get_all_temp_changes()
            export_data["temp_changes"] = [temp_change.to_dict() for temp_change in temp_changes]
        
        # 导出循环课程表数据
        if config.include_cycle_schedules:
            cycle_schedules = cycle_schedule_service.get_all_cycle_schedules()
            export_data["cycle_schedules"] = [cycle_schedule.to_dict() for cycle_schedule in cycle_schedules]
        
        return export_data
    
    def _export_json(self, data: Dict[str, Any], export_path: str) -> str:
        """
        导出JSON格式数据
        
        Args:
            data: 要导出的数据
            export_path: 导出文件路径
            
        Returns:
            导出文件的完整路径
        """
        logger.debug("导出JSON数据")
        
        # 确保文件扩展名正确
        if not export_path.endswith(".json"):
            export_path += ".json"
        
        # 写入JSON文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return export_path
    
    def _export_csv(self, data: Dict[str, Any], export_path: str) -> str:
        """
        导出CSV格式数据
        
        Args:
            data: 要导出的数据
            export_path: 导出文件路径
            
        Returns:
            导出文件的完整路径
        """
        logger.debug("导出CSV数据")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(export_path) if os.path.dirname(export_path) else ".", exist_ok=True)
        
        # 为每种数据类型创建单独的CSV文件
        base_path = export_path.rstrip(".csv") if export_path.endswith(".csv") else export_path
        
        # 导出课程数据
        if "courses" in data:
            courses_path = f"{base_path}_courses.csv"
            self._write_csv_file(courses_path, data["courses"])
        
        # 导出课程表数据
        if "schedules" in data:
            schedules_path = f"{base_path}_schedules.csv"
            self._write_csv_file(schedules_path, data["schedules"])
        
        # 导出临时换课数据
        if "temp_changes" in data:
            temp_changes_path = f"{base_path}_temp_changes.csv"
            self._write_csv_file(temp_changes_path, data["temp_changes"])
        
        # 导出循环课程表数据
        if "cycle_schedules" in data:
            cycle_schedules_path = f"{base_path}_cycle_schedules.csv"
            self._write_csv_file(cycle_schedules_path, data["cycle_schedules"])
        
        return f"{base_path}_courses.csv"  # 返回第一个文件路径作为代表
    
    def _write_csv_file(self, file_path: str, data: List[Dict[str, Any]]):
        """
        写入CSV文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
        """
        if not data:
            # 如果没有数据，创建空文件
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                pass
            return
        
        # 获取所有字段名
        fieldnames: set[str] = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))  # type: ignore
        
        # 写入CSV文件
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def _export_excel(self, data: Dict[str, Any], export_path: str) -> str:
        """
        导出Excel格式数据（简化实现，实际项目中可能需要使用pandas或openpyxl等库）
        
        Args:
            data: 要导出的数据
            export_path: 导出文件路径
            
        Returns:
            导出文件的完整路径
        """
        logger.debug("导出Excel数据（简化实现）")
        
        # 简化实现：将Excel导出为JSON格式
        if not export_path.endswith(".xlsx"):
            export_path = export_path.rstrip(".xlsx") + ".xlsx"
        
        # 实际项目中这里应该使用pandas或openpyxl等库来创建真正的Excel文件
        # 这里为了简化，我们仍然导出为JSON格式，但文件名使用.xlsx扩展名
        json_export_path = export_path.replace(".xlsx", ".json")
        self._export_json(data, json_export_path)
        
        return json_export_path
    
    def _import_json(self, import_path: str) -> Dict[str, Any]:
        """
        导入JSON格式数据
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            导入的数据字典
        """
        logger.debug("导入JSON数据")
        
        with open(import_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _import_csv(self, import_path: str) -> Dict[str, Any]:
        """
        导入CSV格式数据（简化实现）
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            导入的数据字典
        """
        logger.debug("导入CSV数据（简化实现）")
        
        # 简化实现：假设只有一个CSV文件包含所有数据
        # 实际项目中可能需要处理多个CSV文件
        import_data = {}
        
        with open(import_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            data_list = list(reader)
            # 简化处理：假设文件名可以指示数据类型
            file_name = os.path.basename(import_path)
            if "course" in file_name:
                import_data["courses"] = data_list
            elif "schedule" in file_name:
                import_data["schedules"] = data_list
            elif "temp_change" in file_name:
                import_data["temp_changes"] = data_list
            elif "cycle_schedule" in file_name:
                import_data["cycle_schedules"] = data_list
            else:
                # 默认处理
                import_data["data"] = data_list
        
        return import_data
    
    def _import_excel(self, import_path: str) -> Dict[str, Any]:
        """
        导入Excel格式数据（简化实现）
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            导入的数据字典
        """
        logger.debug("导入Excel数据（简化实现）")
        
        # 简化实现：假设Excel文件实际上是JSON格式
        # 实际项目中这里应该使用pandas或openpyxl等库来读取真正的Excel文件
        return self._import_json(import_path.replace(".xlsx", ".json"))
    
    def _validate_import_data(self, data: Dict[str, Any]) -> None:
        """
        验证导入的数据
        
        Args:
            data: 要验证的数据
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.debug("验证导入数据")
        
        # 检查必需的数据结构
        if not isinstance(data, dict):
            raise ValidationException("导入数据格式不正确，应为字典类型")
        
        # 验证各数据类型的结构
        data_types = ["courses", "schedules", "temp_changes", "cycle_schedules"]
        for data_type in data_types:
            if data_type in data and data[data_type] is not None:
                if not isinstance(data[data_type], list):
                    raise ValidationException(f"{data_type}数据格式不正确，应为列表类型")
        
        logger.debug("数据验证通过")
    
    def _import_data_to_services(self, data: Dict[str, Any], overwrite_existing: bool):
        """
        将数据导入到各服务中
        
        Args:
            data: 要导入的数据
            overwrite_existing: 是否覆盖现有数据
        """
        logger.debug("导入数据到服务")
        
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        # 获取各服务实例
        course_service = ServiceFactory.get_course_service()
        schedule_service = ServiceFactory.get_schedule_service()
        temp_change_service = ServiceFactory.get_temp_change_service()
        cycle_schedule_service = ServiceFactory.get_cycle_schedule_service()
        
        # 导入课程数据
        if "courses" in data:
            for course_data in data["courses"]:
                try:
                    course = ClassItem.from_dict(course_data)
                    if overwrite_existing or not course_service.get_course_by_id(course.id):
                        if course_service.get_course_by_id(course.id):
                            course_service.update_course(course.id, course)
                        else:
                            # 这里需要处理创建课程的逻辑，但课程服务可能不允许直接创建
                            # 实际项目中可能需要修改服务层来支持批量导入
                            pass
                except Exception as e:
                    logger.warning(f"导入课程数据失败: {str(e)}")
        
        # 导入课程表数据
        if "schedules" in data:
            for schedule_data in data["schedules"]:
                try:
                    schedule = ClassPlan.from_dict(schedule_data)
                    if overwrite_existing or not schedule_service.get_schedule_by_id(schedule.id):
                        if schedule_service.get_schedule_by_id(schedule.id):
                            schedule_service.update_schedule(schedule.id, schedule)
                        else:
                            # 这里需要处理创建课程表的逻辑
                            pass
                except Exception as e:
                    logger.warning(f"导入课程表数据失败: {str(e)}")
        
        # 导入临时换课数据
        if "temp_changes" in data:
            for temp_change_data in data["temp_changes"]:
                try:
                    temp_change = TempChange.from_dict(temp_change_data)
                    if overwrite_existing or not temp_change_service.get_temp_change_by_id(temp_change.id):
                        if temp_change_service.get_temp_change_by_id(temp_change.id):
                            temp_change_service.update_temp_change(temp_change.id, temp_change)
                        else:
                            # 这里需要处理创建临时换课的逻辑
                            pass
                except Exception as e:
                    logger.warning(f"导入临时换课数据失败: {str(e)}")
        
        # 导入循环课程表数据
        if "cycle_schedules" in data:
            for cycle_schedule_data in data["cycle_schedules"]:
                try:
                    cycle_schedule = CycleSchedule.from_dict(cycle_schedule_data)
                    if overwrite_existing or not cycle_schedule_service.get_cycle_schedule_by_id(cycle_schedule.id):
                        if cycle_schedule_service.get_cycle_schedule_by_id(cycle_schedule.id):
                            cycle_schedule_service.update_cycle_schedule(cycle_schedule.id, cycle_schedule)
                        else:
                            # 这里需要处理创建循环课程表的逻辑
                            pass
                except Exception as e:
                    logger.warning(f"导入循环课程表数据失败: {str(e)}")
        
        logger.debug("数据导入到服务完成")
