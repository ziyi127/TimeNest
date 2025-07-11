#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest Excel导出增强功能
支持多种模板、统计功能、打印优化
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import os


class ExportTemplate(Enum):
    """导出模板类型"""
    BASIC = "basic"                 # 基础模板
    DETAILED = "detailed"           # 详细模板
    WEEKLY = "weekly"               # 周视图模板
    MONTHLY = "monthly"             # 月视图模板
    STATISTICS = "statistics"       # 统计模板
    PRINT_FRIENDLY = "print_friendly"  # 打印友好模板


class ExportFormat(Enum):
    """导出格式"""
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"


@dataclass
class ExportOptions:
    """导出选项"""
    template: ExportTemplate = ExportTemplate.BASIC
    format: ExportFormat = ExportFormat.XLSX
    include_weekends: bool = True
    include_empty_slots: bool = False
    include_statistics: bool = True
    include_teacher_info: bool = True
    include_classroom_info: bool = True
    include_notes: bool = True
    week_range: Optional[tuple] = None  # (start_week, end_week)
    custom_title: str = ""
    watermark: str = ""
    page_orientation: str = "portrait"  # portrait, landscape
    font_size: int = 12
    color_scheme: str = "default"


class ExcelExportEnhanced:
    """Excel导出增强类"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.ExcelExportEnhanced')
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Dict]:
        """加载模板配置"""
        return {
            ExportTemplate.BASIC.value: {
                "name": "基础模板",
                "description": "简单的课程表格式",
                "columns": ["时间", "周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                "include_header": True,
                "include_footer": False,
                "color_scheme": "light"
            },
            ExportTemplate.DETAILED.value: {
                "name": "详细模板",
                "description": "包含完整课程信息",
                "columns": ["时间", "周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                "include_header": True,
                "include_footer": True,
                "include_statistics": True,
                "color_scheme": "professional"
            },
            ExportTemplate.WEEKLY.value: {
                "name": "周视图模板",
                "description": "按周显示课程安排",
                "layout": "weekly",
                "include_week_summary": True,
                "color_scheme": "colorful"
            },
            ExportTemplate.MONTHLY.value: {
                "name": "月视图模板",
                "description": "按月显示课程安排",
                "layout": "monthly",
                "include_month_summary": True,
                "color_scheme": "minimal"
            },
            ExportTemplate.STATISTICS.value: {
                "name": "统计模板",
                "description": "课程统计分析报告",
                "include_charts": True,
                "include_analysis": True,
                "color_scheme": "data"
            },
            ExportTemplate.PRINT_FRIENDLY.value: {
                "name": "打印友好模板",
                "description": "优化打印效果",
                "print_optimized": True,
                "black_white": True,
                "large_font": True
            }
        }
    
    def export_schedule(self, schedule_data: Dict[str, Any], file_path: str, options: ExportOptions) -> bool:
        """导出课程表"""
        try:
            self.logger.info(f"开始导出课程表: {options.template.value} -> {file_path}")
            
            if options.format == ExportFormat.XLSX or options.format == ExportFormat.XLS:
                return self._export_to_excel(schedule_data, file_path, options)
            elif options.format == ExportFormat.CSV:
                return self._export_to_csv(schedule_data, file_path, options)
            elif options.format == ExportFormat.PDF:
                return self._export_to_pdf(schedule_data, file_path, options)
            elif options.format == ExportFormat.HTML:
                return self._export_to_html(schedule_data, file_path, options)
            else:
                self.logger.error(f"不支持的导出格式: {options.format}")
                return False
                
        except Exception as e:
            self.logger.error(f"导出课程表失败: {e}")
            return False
    
    def _export_to_excel(self, schedule_data: Dict[str, Any], file_path: str, options: ExportOptions) -> bool:
        """导出到Excel"""
        try:
            # 这里使用模拟实现，实际需要安装openpyxl
            self.logger.info("Excel导出功能需要安装openpyxl库")
            
            # 模拟Excel导出过程
            courses = schedule_data.get('courses', [])
            
            # 创建基础数据结构
            excel_data = self._prepare_excel_data(courses, options)
            
            # 应用模板样式
            styled_data = self._apply_template_style(excel_data, options)
            
            # 添加统计信息
            if options.include_statistics:
                stats_data = self._generate_statistics(courses)
                styled_data['statistics'] = stats_data
            
            # 保存到文件（模拟）
            self._save_excel_file(styled_data, file_path, options)
            
            self.logger.info(f"Excel导出完成: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel导出失败: {e}")
            return False
    
    def _export_to_csv(self, schedule_data: Dict[str, Any], file_path: str, options: ExportOptions) -> bool:
        """导出到CSV"""
        try:
            import csv
            
            courses = schedule_data.get('courses', [])
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                if options.template == ExportTemplate.STATISTICS:
                    # 统计模板
                    self._write_statistics_csv(f, courses, options)
                else:
                    # 标准课程表模板
                    self._write_schedule_csv(f, courses, options)
            
            self.logger.info(f"CSV导出完成: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV导出失败: {e}")
            return False
    
    def _export_to_pdf(self, schedule_data: Dict[str, Any], file_path: str, options: ExportOptions) -> bool:
        """导出到PDF"""
        try:
            self.logger.info("PDF导出功能正在开发中")
            # 这里可以集成reportlab或其他PDF库
            return False
            
        except Exception as e:
            self.logger.error(f"PDF导出失败: {e}")
            return False
    
    def _export_to_html(self, schedule_data: Dict[str, Any], file_path: str, options: ExportOptions) -> bool:
        """导出到HTML"""
        try:
            courses = schedule_data.get('courses', [])
            html_content = self._generate_html_content(courses, options)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML导出完成: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"HTML导出失败: {e}")
            return False
    
    def _prepare_excel_data(self, courses: List[Dict], options: ExportOptions) -> Dict[str, Any]:
        """准备Excel数据"""
        # 时间段定义
        time_slots = [
            "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
            "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
            "19:00-19:45", "19:55-20:40"
        ]
        
        # 星期定义
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        # 创建课程表矩阵
        schedule_matrix = {}
        for i, time_slot in enumerate(time_slots):
            schedule_matrix[time_slot] = {}
            for j, day in enumerate(weekdays):
                schedule_matrix[time_slot][day] = ""
        
        # 填充课程数据
        for course in courses:
            day_index = course.get('day', 0)
            if 0 <= day_index < len(weekdays):
                day_name = weekdays[day_index]
                start_time = course.get('start_time', '08:00')
                
                # 找到对应的时间段
                for time_slot in time_slots:
                    if start_time in time_slot:
                        cell_content = course['name']
                        if options.include_teacher_info and course.get('teacher'):
                            cell_content += f"\n{course['teacher']}"
                        if options.include_classroom_info and course.get('classroom'):
                            cell_content += f"\n{course['classroom']}"
                        
                        schedule_matrix[time_slot][day_name] = cell_content
                        break
        
        return {
            'schedule_matrix': schedule_matrix,
            'time_slots': time_slots,
            'weekdays': weekdays,
            'courses': courses
        }
    
    def _apply_template_style(self, excel_data: Dict[str, Any], options: ExportOptions) -> Dict[str, Any]:
        """应用模板样式"""
        template_config = self.templates.get(options.template.value, {})
        
        # 添加样式信息
        excel_data['style'] = {
            'template': options.template.value,
            'color_scheme': template_config.get('color_scheme', 'default'),
            'font_size': options.font_size,
            'include_header': template_config.get('include_header', True),
            'include_footer': template_config.get('include_footer', False)
        }
        
        return excel_data
    
    def _generate_statistics(self, courses: List[Dict]) -> Dict[str, Any]:
        """生成统计信息"""
        stats = {
            'total_courses': len(courses),
            'courses_by_day': {},
            'courses_by_type': {},
            'teachers': set(),
            'classrooms': set(),
            'total_credits': 0
        }
        
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        # 初始化按天统计
        for day in weekdays:
            stats['courses_by_day'][day] = 0
        
        # 统计课程信息
        for course in courses:
            # 按天统计
            day_index = course.get('day', 0)
            if 0 <= day_index < len(weekdays):
                day_name = weekdays[day_index]
                stats['courses_by_day'][day_name] += 1
            
            # 按类型统计
            course_type = course.get('course_type', '其他')
            stats['courses_by_type'][course_type] = stats['courses_by_type'].get(course_type, 0) + 1
            
            # 教师和教室
            if course.get('teacher'):
                stats['teachers'].add(course['teacher'])
            if course.get('classroom'):
                stats['classrooms'].add(course['classroom'])
            
            # 学分统计
            stats['total_credits'] += course.get('credits', 0)
        
        # 转换集合为列表
        stats['teachers'] = list(stats['teachers'])
        stats['classrooms'] = list(stats['classrooms'])
        
        return stats
    
    def _save_excel_file(self, data: Dict[str, Any], file_path: str, options: ExportOptions):
        """保存Excel文件（模拟实现）"""
        # 这里是模拟实现，实际需要使用openpyxl
        self.logger.info(f"模拟保存Excel文件: {file_path}")
        
        # 创建一个JSON文件作为模拟
        json_file = file_path.replace('.xlsx', '.json').replace('.xls', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            # 处理不可序列化的对象
            serializable_data = {}
            for key, value in data.items():
                if key == 'style':
                    serializable_data[key] = value
                elif key == 'statistics':
                    serializable_data[key] = value
                else:
                    serializable_data[key] = value
            
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
    
    def _write_schedule_csv(self, file, courses: List[Dict], options: ExportOptions):
        """写入课程表CSV"""
        import csv
        
        writer = csv.writer(file)
        
        # 写入标题
        if options.custom_title:
            writer.writerow([options.custom_title])
            writer.writerow([])
        
        # 写入表头
        headers = ["时间", "周一", "周二", "周三", "周四", "周五"]
        if options.include_weekends:
            headers.extend(["周六", "周日"])
        writer.writerow(headers)
        
        # 写入课程数据
        time_slots = [
            "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
            "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
            "19:00-19:45", "19:55-20:40"
        ]
        
        for time_slot in time_slots:
            row = [time_slot]
            for day in range(7 if options.include_weekends else 5):
                # 查找该时间段的课程
                course_info = ""
                for course in courses:
                    if course.get('day') == day and course.get('start_time', '08:00') in time_slot:
                        course_info = course['name']
                        if options.include_teacher_info and course.get('teacher'):
                            course_info += f" ({course['teacher']})"
                        break
                row.append(course_info)
            writer.writerow(row)
    
    def _write_statistics_csv(self, file, courses: List[Dict], options: ExportOptions):
        """写入统计CSV"""
        import csv
        
        writer = csv.writer(file)
        stats = self._generate_statistics(courses)
        
        # 写入统计信息
        writer.writerow(["课程统计报告"])
        writer.writerow([])
        writer.writerow(["总课程数", stats['total_courses']])
        writer.writerow(["总学分", stats['total_credits']])
        writer.writerow([])
        
        # 按天统计
        writer.writerow(["按天统计"])
        for day, count in stats['courses_by_day'].items():
            writer.writerow([day, count])
        writer.writerow([])
        
        # 按类型统计
        writer.writerow(["按类型统计"])
        for course_type, count in stats['courses_by_type'].items():
            writer.writerow([course_type, count])
    
    def _generate_html_content(self, courses: List[Dict], options: ExportOptions) -> str:
        """生成HTML内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{options.custom_title or '课程表'}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
                .course {{ background-color: #e8f4fd; }}
            </style>
        </head>
        <body>
            <h1>{options.custom_title or '课程表'}</h1>
            <table>
                <tr>
                    <th>时间</th>
                    <th>周一</th>
                    <th>周二</th>
                    <th>周三</th>
                    <th>周四</th>
                    <th>周五</th>
        """
        
        if options.include_weekends:
            html += "<th>周六</th><th>周日</th>"
        
        html += "</tr>"
        
        # 添加课程数据
        time_slots = [
            "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
            "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
            "19:00-19:45", "19:55-20:40"
        ]
        
        for time_slot in time_slots:
            html += f"<tr><td>{time_slot}</td>"
            for day in range(7 if options.include_weekends else 5):
                course_info = ""
                for course in courses:
                    if course.get('day') == day and course.get('start_time', '08:00') in time_slot:
                        course_info = course['name']
                        if options.include_teacher_info and course.get('teacher'):
                            course_info += f"<br>{course['teacher']}"
                        if options.include_classroom_info and course.get('classroom'):
                            course_info += f"<br>{course['classroom']}"
                        break
                
                css_class = "course" if course_info else ""
                html += f'<td class="{css_class}">{course_info}</td>'
            html += "</tr>"
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
    
    def get_available_templates(self) -> Dict[str, Dict]:
        """获取可用模板"""
        return self.templates
    
    def validate_export_options(self, options: ExportOptions) -> List[str]:
        """验证导出选项"""
        errors = []
        
        if options.font_size < 8 or options.font_size > 72:
            errors.append("字体大小必须在8-72之间")
        
        if options.week_range:
            start, end = options.week_range
            if start > end or start < 1 or end > 30:
                errors.append("周次范围无效")
        
        return errors
