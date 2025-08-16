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
            file_path = self._export_data_by_format(config, export_data, export_path)
            
            logger.info(f"数据导出成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            raise ValidationException(f"数据导出失败: {str(e)}")
    
    def _export_data_by_format(self, config: DataExportConfig, data: Dict[str, Any], export_path: str) -> str:
        """
        根据格式导出数据
        
        Args:
            config: 导出配置
            data: 要导出的数据
            export_path: 导出文件路径
            
        Returns:
            导出文件的完整路径
            
        Raises:
            ValidationException: 不支持的导出格式
        """
        format_handlers = {
            ExportFormat.JSON: self._export_json,
            ExportFormat.CSV: self._export_csv,
            ExportFormat.EXCEL: self._export_excel,
        }
        
        # 获取处理函数
        handler = format_handlers.get(config.format)
        if not handler:
            raise ValidationException(f"不支持的导出格式: {config.format}")
        
        return handler(data, export_path)
    
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
            self._ensure_import_file_exists(import_path)
            
            # 根据格式导入数据
            import_data = self._import_data_by_format(config, import_path)
            
            # 验证数据
            self._validate_import_data_if_needed(config, import_data)
            
            # 导入数据
            self._import_data_to_services(import_data, config.overwrite_existing)
            
            logger.info("数据导入成功")
            return True
            
        except Exception as e:
            logger.error(f"数据导入失败: {str(e)}")
            raise ValidationException(f"数据导入失败: {str(e)}")
    
    def _ensure_import_file_exists(self, import_path: str) -> None:
        """
        确保导入文件存在
        
        Args:
            import_path: 导入文件路径
            
        Raises:
            ValidationException: 文件不存在
        """
        if not os.path.exists(import_path):
            raise ValidationException(f"导入文件不存在: {import_path}")
    
    def _import_data_by_format(self, config: DataImportConfig, import_path: str) -> Dict[str, Any]:
        """
        根据格式导入数据
        
        Args:
            config: 导入配置
            import_path: 导入文件路径
            
        Returns:
            导入的数据字典
            
        Raises:
            ValidationException: 不支持的导入格式
        """
        format_handlers = {
            ExportFormat.JSON: self._import_json,
            ExportFormat.CSV: self._import_csv,
            ExportFormat.EXCEL: self._import_excel,
        }
        
        # 获取处理函数
        handler = format_handlers.get(config.format)
        if not handler:
            raise ValidationException(f"不支持的导入格式: {config.format}")
        
        return handler(import_path)
    
    def _validate_import_data_if_needed(self, config: DataImportConfig, data: Dict[str, Any]) -> None:
        """
        如果需要则验证导入的数据
        
        Args:
            config: 导入配置
            data: 要验证的数据
            
        Raises:
            ValidationException: 数据验证失败
        """
        if config.validate_data:
            self._validate_import_data(data)
    
    def _collect_export_data(self, config: DataExportConfig) -> Dict[str, Any]:
        """
        收集要导出的数据
        
        Args:
            config: 导出配置
            
        Returns:
            要导出的数据字典
        """
        logger.debug("收集导出数据")
        
        # 获取各服务实例
        services = self._get_services()
        
        export_data: Dict[str, Any] = {}
        
        # 收集各种数据类型
        self._collect_data_types(export_data, config, services)
        
        return export_data

    def _collect_data_types(self, export_data: Dict[str, Any], config: DataExportConfig, services: Dict[str, Any]) -> None:
        """
        收集各种数据类型
        
        Args:
            export_data: 导出数据字典
            config: 导出配置
            services: 服务实例字典
        """
        # 定义配置选项和收集函数的映射
        data_collection_mapping = {
            "include_courses": (self._collect_courses, "courses"),
            "include_schedules": (self._collect_schedules, "schedules"),
            "include_temp_changes": (self._collect_temp_changes, "temp_changes"),
            "include_cycle_schedules": (self._collect_cycle_schedules, "cycle_schedules")
        }
        
        # 收集每种数据类型
        for config_option, (collect_func, data_key) in data_collection_mapping.items():
            if getattr(config, config_option, False):
                export_data[data_key] = collect_func(services)

    def _collect_courses(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集课程数据
        
        Args:
            services: 服务实例字典
            
        Returns:
            课程数据列表
        """
        course_service = services["course_service"]
        courses = course_service.get_all_courses()
        return [course.to_dict() for course in courses]

    def _collect_schedules(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集课程表数据
        
        Args:
            services: 服务实例字典
            
        Returns:
            课程表数据列表
        """
        schedule_service = services["schedule_service"]
        schedules = schedule_service.get_all_schedules()
        return [schedule.to_dict() for schedule in schedules]

    def _collect_temp_changes(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集临时换课数据
        
        Args:
            services: 服务实例字典
            
        Returns:
            临时换课数据列表
        """
        temp_change_service = services["temp_change_service"]
        temp_changes = temp_change_service.get_all_temp_changes()
        return [temp_change.to_dict() for temp_change in temp_changes]

    def _collect_cycle_schedules(self, services: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        收集循环课程表数据
        
        Args:
            services: 服务实例字典
            
        Returns:
            循环课程表数据列表
        """
        cycle_schedule_service = services["cycle_schedule_service"]
        cycle_schedules = cycle_schedule_service.get_all_cycle_schedules()
        return [cycle_schedule.to_dict() for cycle_schedule in cycle_schedules]
    
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
        self._ensure_directory_exists(export_path)
        
        # 为每种数据类型创建单独的CSV文件
        base_path = export_path.rstrip(".csv") if export_path.endswith(".csv") else export_path
        
        # 导出各种数据类型
        self._export_data_types_to_csv(data, base_path)
        
        return f"{base_path}_courses.csv"  # 返回第一个文件路径作为代表
    
    def _ensure_directory_exists(self, file_path: str) -> None:
        """
        确保文件路径的目录存在
        
        Args:
            file_path: 文件路径
        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def _export_data_types_to_csv(self, data: Dict[str, Any], base_path: str) -> None:
        """
        将各种数据类型导出为CSV文件
        
        Args:
            data: 要导出的数据
            base_path: 基础文件路径
        """
        # 定义数据类型和对应文件名的映射
        data_type_mapping = {
            "courses": f"{base_path}_courses.csv",
            "schedules": f"{base_path}_schedules.csv",
            "temp_changes": f"{base_path}_temp_changes.csv",
            "cycle_schedules": f"{base_path}_cycle_schedules.csv"
        }
        
        # 导出每种数据类型
        for data_type, file_path in data_type_mapping.items():
            if data_type in data:
                self._write_csv_file(file_path, data[data_type])
    
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
        import_data: Dict[str, Any] = {}
        
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
        if not isinstance(data, dict):  # type: ignore
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
        from services.service_factory import ServiceFactory  # type: ignore
        
        # 获取各服务实例
        services = self._get_services()
        
        # 导入各种数据类型
        self._import_data_types(data, services, overwrite_existing)
        
        logger.debug("数据导入到服务完成")
    
    def _get_services(self) -> Dict[str, Any]:
        """
        获取所有需要的服务实例
        
        Returns:
            包含各服务实例的字典
        """
        from services.service_factory import ServiceFactory  # type: ignore
        
        return {
            "course_service": ServiceFactory.get_course_service(),
            "schedule_service": ServiceFactory.get_schedule_service(),
            "temp_change_service": ServiceFactory.get_temp_change_service(),
            "cycle_schedule_service": ServiceFactory.get_cycle_schedule_service()
        }
    
    def _import_data_types(self, data: Dict[str, Any], services: Dict[str, Any], overwrite_existing: bool) -> None:
        """
        导入各种数据类型
        
        Args:
            data: 要导入的数据
            services: 服务实例字典
            overwrite_existing: 是否覆盖现有数据
        """
        # 定义数据类型和处理函数的映射
        data_import_mapping: Dict[str, Any] = {
            "courses": self._import_courses,
            "schedules": self._import_schedules,
            "temp_changes": self._import_temp_changes,
            "cycle_schedules": self._import_cycle_schedules
        }
        
        # 导入每种数据类型
        for data_type, import_func in data_import_mapping.items():
            if data_type in data:
                try:
                    import_func(data[data_type], services, overwrite_existing)
                except Exception as e:
                    logger.warning(f"导入{data_type}数据失败: {str(e)}")
    
    def _import_courses(self, courses_data: List[Dict[str, Any]], services: Dict[str, Any], overwrite_existing: bool) -> None:
        """
        导入课程数据
        
        Args:
            courses_data: 课程数据列表
            services: 服务实例字典
            overwrite_existing: 是否覆盖现有数据
        """
        course_service = services["course_service"]
        for course_data in courses_data:
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
    
    def _import_schedules(self, schedules_data: List[Dict[str, Any]], services: Dict[str, Any], overwrite_existing: bool) -> None:
        """
        导入课程表数据
        
        Args:
            schedules_data: 课程表数据列表
            services: 服务实例字典
            overwrite_existing: 是否覆盖现有数据
        """
        schedule_service = services["schedule_service"]
        for schedule_data in schedules_data:
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
    
    def _import_temp_changes(self, temp_changes_data: List[Dict[str, Any]], services: Dict[str, Any], overwrite_existing: bool) -> None:
        """
        导入临时换课数据
        
        Args:
            temp_changes_data: 临时换课数据列表
            services: 服务实例字典
            overwrite_existing: 是否覆盖现有数据
        """
        temp_change_service = services["temp_change_service"]
        for temp_change_data in temp_changes_data:
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
    
    def _import_cycle_schedules(self, cycle_schedules_data: List[Dict[str, Any]], services: Dict[str, Any], overwrite_existing: bool) -> None:
        """
        导入循环课程表数据
        
        Args:
            cycle_schedules_data: 循环课程表数据列表
            services: 服务实例字典
            overwrite_existing: 是否覆盖现有数据
        """
        cycle_schedule_service = services["cycle_schedule_service"]
        for cycle_schedule_data in cycle_schedules_data:
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
