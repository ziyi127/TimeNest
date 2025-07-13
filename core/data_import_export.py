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
TimeNest 数据导入导出管理器
支持多种格式的课程表数据导入导出
"""

import json
import yaml
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, time, date
from PyQt6.QtCore import QObject, pyqtSignal, QThread

from models.schedule import Schedule, Subject, TimeSlot, ClassItem, TimeLayout, TimeLayoutItem, ClassPlan


class DataImportExportManager(QObject):
    """数据导入导出管理器"""
    
    # 信号定义
    import_started = pyqtSignal(str)  # 文件路径
    import_progress = pyqtSignal(int)  # 进度百分比
    import_completed = pyqtSignal(bool, str)  # 成功状态, 消息
    export_started = pyqtSignal(str)  # 文件路径
    export_progress = pyqtSignal(int)  # 进度百分比
    export_completed = pyqtSignal(bool, str)  # 成功状态, 消息
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.DataImportExportManager')
        
        # 支持的格式
        self.supported_import_formats = ['.json', '.yaml', '.yml', '.xlsx', '.xls']
        self.supported_export_formats = ['.json', '.yaml', '.yml', '.xlsx']
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """获取支持的格式"""
        return {
            'import': self.supported_import_formats,
            'export': self.supported_export_formats
        }
    
    def import_schedule(self, file_path: str) -> Optional[Schedule]:
        """
        导入课程表数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Schedule对象，失败返回None
        """
        try:
            self.import_started.emit(file_path)
            self.logger.info(f"开始导入课程表: {file_path}")
            
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 根据文件扩展名选择导入方法
            extension = file_path.suffix.lower()
            
            
            if extension == '.json':
                schedule = self._import_from_json(file_path)
            
                schedule = self._import_from_json(file_path)
            elif extension in ['.yaml', '.yml']:
                schedule = self._import_from_yaml(file_path)
            elif extension in ['.xlsx', '.xls']:
                schedule = self._import_from_excel(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {extension}")
            
            self.import_completed.emit(True, f"成功导入课程表: {schedule.name}")
            self.logger.info(f"课程表导入完成: {schedule.name}")
            return schedule
            
        except Exception as e:
            error_msg = f"导入课程表失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.import_completed.emit(False, error_msg)
            return None
    
    def export_schedule(self, schedule: Schedule, file_path: str, format_type: str = None) -> bool
        """
        导出课程表数据
        
        Args:
            schedule: 课程表对象
            file_path: 导出文件路径
            format_type: 格式类型，如果为None则根据文件扩展名判断
            
        Returns:
            是否成功
        """
        try:
            self.export_started.emit(file_path)
            self.logger.info(f"开始导出课程表: {file_path}")
            
            file_path = Path(file_path)
            
            # 确定格式
            if format_type:
                extension = f".{format_type.lower()}"
            else:
                extension = file_path.suffix.lower()
            
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 根据格式选择导出方法
            if extension == '.json':
                success = self._export_to_json(schedule, file_path)
            elif extension in ['.yaml', '.yml']:
                success = self._export_to_yaml(schedule, file_path)
            elif extension == '.xlsx':
                success = self._export_to_excel(schedule, file_path)
            else:
                raise ValueError(f"不支持的导出格式: {extension}")
            
            
            if success and hasattr(success, "self.export_completed"):
    self.export_completed.emit(True, f"成功导出课程表到: {file_path}")
            
                self.export_completed.emit(True, f"成功导出课程表到: {file_path}")
                self.logger.info(f"课程表导出完成: {file_path}")
            else:
                self.export_completed.emit(False, "导出失败")
            
            return success
            
        except Exception as e:
            error_msg = f"导出课程表失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.export_completed.emit(False, error_msg)
            return False
    
    def _import_from_json(self, file_path: Path) -> Schedule:
        """从JSON文件导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.import_progress.emit(50)
            
            # 验证数据格式
            if not isinstance(data, dict):
                raise ValueError("JSON数据格式错误：根对象必须是字典")
            
            # 创建Schedule对象
            schedule = Schedule.from_dict(data)
            
            self.import_progress.emit(100)
            return schedule
            
        except Exception as e:
            raise Exception(f"JSON导入失败: {str(e)}")
    
    def _import_from_yaml(self, file_path: Path) -> Schedule:
        """从YAML文件导入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.import_progress.emit(50)
            
            # 验证数据格式
            if not isinstance(data, dict):
                raise ValueError("YAML数据格式错误：根对象必须是字典")
            
            # 创建Schedule对象
            schedule = Schedule.from_dict(data)
            
            self.import_progress.emit(100)
            return schedule
            
        except Exception as e:
            raise Exception(f"YAML导入失败: {str(e)}")
    
    def _import_from_excel(self, file_path: Path) -> Schedule:
        """从Excel文件导入"""
        try:
            # 读取Excel文件
            excel_data = pd.read_excel(file_path, sheet_name=None)
            
            self.import_progress.emit(30)
            
            # 获取第一个工作表作为课程表数据
            if not excel_data:
                raise ValueError("Excel文件为空")
            
            sheet_name = list(excel_data.keys())[0]
            df = excel_data[sheet_name]
            
            self.import_progress.emit(60)
            
            # 解析Excel数据为Schedule对象
            schedule = self._parse_excel_to_schedule(df, sheet_name)
            
            self.import_progress.emit(100)
            return schedule
            
        except Exception as e:
            raise Exception(f"Excel导入失败: {str(e)}")
    
    def _parse_excel_to_schedule(self, df: pd.DataFrame, sheet_name: str) -> Schedule:
        """解析Excel数据为Schedule对象"""
        try:
            # 创建基本的Schedule对象
            schedule = Schedule(name=sheet_name or "导入的课程表")
            
            # 解析时间段（从第一列）
            time_slots = []
            for i, row_name in enumerate(df.index):
                if pd.notna(row_name) and str(row_name).strip():
                    # 尝试解析时间格式:
                    # 尝试解析时间格式
                    time_slot = TimeSlot(
                        id=f"slot_{i}",
                        name=str(row_name),
                        start_time=time(8 + i, 0),  # 默认从8点开始
                        end_time=time(8 + i + 1, 0)  # 每节课1小时
                    )
                    time_slots.append(time_slot)
                    schedule.add_time_slot(time_slot)
            
            # 解析科目和课程（从列数据）
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            subjects_dict = {}
            
            for col_idx, col_name in enumerate(df.columns):
                if col_idx >= len(weekdays):
                    break:
                    break
                
                weekday = weekdays[col_idx]
                
                for row_idx, cell_value in enumerate(df.iloc[:, col_idx]):
                    if pd.notna(cell_value) and str(cell_value).strip():
                        subject_name = str(cell_value).strip()
                        
                        # 创建或获取科目
                        if subject_name not in subjects_dict:
                            subject = Subject(
                                id=f"subject_{len(subjects_dict)}",
                                name=subject_name
                            )
                            subjects_dict[subject_name] = subject
                            schedule.add_subject(subject)
                        else:
                            subject = subjects_dict[subject_name]
                        
                        # 创建课程项
                        if row_idx < len(time_slots):
                            class_item = ClassItem(
                                id=f"class_{weekday}_{row_idx}",
                                subject_id=subject.id,
                                time_slot_id=time_slots[row_idx].id,
                                weekday=weekday
                            )
                            schedule.add_class(class_item)
            
            return schedule
            
        except Exception as e:
            raise Exception(f"解析Excel数据失败: {str(e)}")
    
    def _export_to_json(self, schedule: Schedule, file_path: Path) -> bool:
        """导出到JSON文件"""
        try:
            data = schedule.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"JSON导出失败: {e}")
            return False
    
    def _export_to_yaml(self, schedule: Schedule, file_path: Path) -> bool:
        """导出到YAML文件"""
        try:
            data = schedule.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"YAML导出失败: {e}")
            return False
    
    def _export_to_excel(self, schedule: Schedule, file_path: Path) -> bool:
        """导出到Excel文件"""
        try:
            # 使用现有的ExcelExporter
            from utils.excel_exporter import ExcelExporter
            
            exporter = ExcelExporter()
            return exporter.export_schedule(schedule, str(file_path))
            
        except Exception as e:
            self.logger.error(f"Excel导出失败: {e}")
            return False

    def import_from_classisland(self, file_path: str) -> Optional[Schedule]:
        """
        从ClassIsland格式导入课程表数据

        Args:
            file_path: ClassIsland数据文件路径

        Returns:
            Schedule对象，失败返回None
        """
        try:
            self.import_started.emit(file_path)
            self.logger.info(f"开始从ClassIsland导入: {file_path}")

            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 读取ClassIsland数据文件
            with open(file_path, 'r', encoding='utf-8') as f:
                classisland_data = json.load(f)

            self.import_progress.emit(30)

            # 转换ClassIsland数据格式到TimeNest格式
            schedule = self._convert_classisland_to_timenest(classisland_data)

            self.import_progress.emit(100)
            self.import_completed.emit(True, f"成功从ClassIsland导入课程表: {schedule.name}")
            self.logger.info(f"ClassIsland数据导入完成: {schedule.name}")
            return schedule

        except Exception as e:
            error_msg = f"ClassIsland导入失败: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.import_completed.emit(False, error_msg)
            return None

    def _convert_classisland_to_timenest(self, classisland_data: Dict[str, Any]) -> Schedule:
        """
        将ClassIsland数据格式转换为TimeNest格式

        Args:
            classisland_data: ClassIsland数据

        Returns:
            Schedule对象
        """
        try:
            # 创建Schedule对象
            schedule_name = classisland_data.get('Name', '从ClassIsland导入的课程表')
            schedule = Schedule(name=schedule_name)

            # 转换时间布局
            time_layout = classisland_data.get('TimeLayout', {})
            time_layout_items = time_layout.get('TimeLayoutItems', [])

            for i, item in enumerate(time_layout_items):
                # ClassIsland的时间格式转换
                start_time_str = item.get('StartSecond', '0')
                end_time_str = item.get('EndSecond', '0')

                # 将秒数转换为时间
                start_seconds = int(start_time_str)
                end_seconds = int(end_time_str)

                start_time = time(
                    hour=start_seconds // 3600,
                    minute=(start_seconds % 3600) // 60,
                    second=start_seconds % 60
                )
                end_time = time(
                    hour=end_seconds // 3600,
                    minute=(end_seconds % 3600) // 60,
                    second=end_seconds % 60
                )

                time_slot = TimeSlot(
                    id=f"slot_{i}",
                    name=f"第{i+1}节",
                    start_time=start_time,
                    end_time=end_time
                )
                schedule.add_time_slot(time_slot)

            self.import_progress.emit(60)

            # 转换科目
            subjects = classisland_data.get('Subjects', [])
            subject_mapping = {}

            for subject_data in subjects:
                subject = Subject(
                    id=subject_data.get('Id', ''),
                    name=subject_data.get('Name', ''),
                    color=subject_data.get('Color', '#2196F3'),
                    teacher=subject_data.get('Teacher', '')
                )
                schedule.add_subject(subject)
                subject_mapping[subject.id] = subject

            self.import_progress.emit(80)

            # 转换课程安排
            classes = classisland_data.get('Classes', [])
            weekday_mapping = {
                0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
                4: 'friday', 5: 'saturday', 6: 'sunday'
            }

            for class_data in classes:
                weekday_index = class_data.get('DayOfWeek', 0)
                weekday = weekday_mapping.get(weekday_index, 'monday')

                time_slot_index = class_data.get('TimeLayoutItem', 0)
                time_slot_id = f"slot_{time_slot_index}" if time_slot_index < len(schedule.time_slots) else None


                if time_slot_id:
                    class_item = ClassItem(

                    class_item = ClassItem(
                        id=f"class_{weekday}_{time_slot_index}",
                        subject_id=class_data.get('Subject', ''),
                        time_slot_id=time_slot_id,
                        weekday=weekday,
                        classroom=class_data.get('Classroom', ''),
                        teacher=class_data.get('Teacher', '')
                    )
                    schedule.add_class(class_item)

            return schedule

        except Exception as e:
            raise Exception(f"ClassIsland数据转换失败: {str(e)}")

    def export_for_backup(self, schedule: Schedule, backup_dir: str) -> bool:
        """
        导出课程表用于备份

        Args:
            schedule: 课程表对象
            backup_dir: 备份目录

        Returns:
            是否成功
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)

            # 生成备份文件名（包含时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"schedule_backup_{timestamp}.json"

            # 导出为JSON格式
            success = self._export_to_json(schedule, backup_file)


            if success and hasattr(success, "self.logger"):
    self.logger.info(f"课程表备份完成: {backup_file}")

                self.logger.info(f"课程表备份完成: {backup_file}")

            return success

        except Exception as e:
            self.logger.error(f"备份失败: {e}")
            return False

    def restore_from_backup(self, backup_file: str) -> Optional[Schedule]:
        """
        从备份文件恢复课程表

        Args:
            backup_file: 备份文件路径

        Returns:
            Schedule对象，失败返回None
        """
        try:
            return self.import_schedule(backup_file)

        except Exception as e:
            self.logger.error(f"恢复备份失败: {e}")
            return None
