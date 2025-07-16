"""
Excel课程表管理器
支持从Excel文件导入和导出课程表
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils.common_imports import pandas
from utils.shared_utilities import validate_path
from utils.data_processing import safe_json_save, validate_course_data


class ExcelScheduleManager:
    """Excel课程表管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.ExcelScheduleManager')
        self.template_path = "schedule_template.xlsx"
        self.config_path = "schedule_config.md"
        self.pandas_available = pandas.available
        
    def create_template(self) -> bool:
        """创建Excel课程表模板"""
        if not self.pandas_available:
            self.logger.error("pandas不可用，无法创建Excel模板")
            return False

        try:
            time_slots = [
                "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
                "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
                "19:00-19:45", "19:55-20:40", "20:50-21:35"
            ]

            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

            schedule_data = {"时间": time_slots}

            for day in weekdays:
                schedule_data[day] = [""] * len(time_slots)

            schedule_data["周一"][0] = "高等数学;张教授;教学楼A101;1-16周"
            schedule_data["周一"][1] = "线性代数;李教授;教学楼B203;1-8周;10-16周"
            schedule_data["周二"][2] = "大学英语;王教授;外语楼301;1-16周"
            schedule_data["周三"][0] = "计算机程序设计;赵教授;实验楼501;2-16周"
            schedule_data["周四"][3] = "大学物理;陈教授;理科楼201;1-12周"
            schedule_data["周五"][1] = "体育;刘教练;体育馆;1-16周"

            df = pandas.DataFrame(schedule_data)
            
            # 保存到Excel文件
            with pd.ExcelWriter(self.template_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='课程表', index=False)
                
                # 获取工作表对象进行格式化
                worksheet = writer.sheets['课程表']
                
                # 设置列宽
                worksheet.column_dimensions['A'].width = 15  # 时间列
                for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H']:
                    worksheet.column_dimensions[col].width = 25  # 星期列
                
                # 设置行高
                for row in range(1, len(time_slots) + 2):
                    worksheet.row_dimensions[row].height = 30
                
                # 添加边框和对齐
                from openpyxl.styles import Border, Side, Alignment
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = center_alignment
            
            self.logger.info(f"Excel课程表模板已创建: {self.template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建Excel模板失败: {e}")
            return False
    
    def create_config_file(self) -> bool:
        """创建配置说明文件"""
        try:
            config_content = """# TimeNest 课程表Excel配置说明

## 📋 Excel课程表格式说明

### 🕐 时间格式
- 使用24小时制，格式：`HH:MM-HH:MM`
- 示例：`08:00-08:45`, `14:00-14:45`

### 📅 星期格式
- 使用中文：周一、周二、周三、周四、周五、周六、周日
- 英文也支持：Monday、Tuesday、Wednesday、Thursday、Friday、Saturday、Sunday

### 📚 课程信息格式
每个单元格中的课程信息使用分号(;)分隔，格式为：
```
课程名称;教师姓名;上课地点;周次信息
```

#### 示例：
- `高等数学;张教授;教学楼A101;1-16周`
- `线性代数;李教授;教学楼B203;1-8周`
- `大学英语;王教授;外语楼301;1-16周`

### 🔄 多轮回课程（重要）
对于多周轮回的课程，在同一个单元格中使用分号(;)分隔不同的轮回：

#### 格式：
```
课程名称;教师;地点;周次1;课程名称;教师;地点;周次2
```

#### 示例：
```
线性代数;李教授;教学楼B203;1-8周;概率论;李教授;教学楼B203;10-16周
```

这表示：
- 第1-8周：线性代数，李教授，教学楼B203
- 第10-16周：概率论，李教授，教学楼B203
- 第9周：无课

### 📝 周次格式说明

#### 连续周次：
- `1-16周`：第1周到第16周
- `3-8周`：第3周到第8周

#### 单独周次：
- `1周`：仅第1周
- `5周`：仅第5周

#### 多个不连续周次：
- `1,3,5,7周`：第1、3、5、7周
- `1-4,8-12周`：第1-4周和第8-12周

#### 单双周：
- `1-16周(单)`：第1-16周的单数周
- `2-16周(双)`：第2-16周的双数周

### 🎯 完整示例

| 时间 | 周一 | 周二 | 周三 | 周四 | 周五 |
|------|------|------|------|------|------|
| 08:00-08:45 | 高等数学;张教授;教学楼A101;1-16周 | | 计算机程序设计;赵教授;实验楼501;2-16周 | | |
| 08:55-09:40 | 线性代数;李教授;教学楼B203;1-8周;概率论;李教授;教学楼B203;10-16周 | | | | 体育;刘教练;体育馆;1-16周 |
| 10:00-10:45 | | 大学英语;王教授;外语楼301;1-16周 | | | |
| 11:00-11:45 | | | | 大学物理;陈教授;理科楼201;1-12周 | |

### ⚠️ 注意事项

1. **分隔符**：必须使用英文分号(;)，不能使用中文分号(；)
2. **空单元格**：没有课程的时间段请保持单元格为空
3. **编码格式**：Excel文件请保存为UTF-8编码
4. **文件格式**：支持.xlsx和.xls格式
5. **工作表名称**：默认读取第一个工作表，建议命名为"课程表"

### 🔧 导入导出功能

#### 导入Excel课程表：
1. 按照上述格式编辑Excel文件
2. 在TimeNest中选择"导入课程表"
3. 选择您的Excel文件
4. 系统自动解析并导入课程信息

#### 导出Excel课程表：
1. 在TimeNest中选择"导出课程表"
2. 选择保存位置
3. 系统生成标准格式的Excel文件

### 📞 技术支持
如果在使用过程中遇到问题，请检查：
1. Excel格式是否正确
2. 分隔符是否使用英文分号
3. 周次格式是否符合规范
4. 文件编码是否为UTF-8

---
*TimeNest - 让时间管理更简单*
"""
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.logger.info(f"配置说明文件已创建: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建配置文件失败: {e}")
            return False
    
    def parse_course_cell(self, cell_content: str) -> List[Dict[str, Any]]:
        """解析课程单元格内容"""
        if not cell_content or cell_content.strip() == "":
            return []
        
        courses = []
        try:
            # 按分号分割，每4个元素为一组课程信息
            parts = [part.strip() for part in cell_content.split(';') if part.strip()]
            
            # 每4个元素组成一个课程：课程名;教师;地点;周次
            for i in range(0, len(parts), 4):
                if i + 3 < len(parts):
                    course = {
                        'name': parts[i],
                        'teacher': parts[i + 1],
                        'location': parts[i + 2],
                        'weeks': parts[i + 3]
                    }
                    courses.append(course)
                elif i + 2 < len(parts):
                    # 兼容只有3个元素的情况（没有周次信息）
                    course = {
                        'name': parts[i],
                        'teacher': parts[i + 1],
                        'location': parts[i + 2],
                        'weeks': '1-16周'  # 默认周次
                    }
                    courses.append(course)
            
        except Exception as e:
            self.logger.error(f"解析课程单元格失败: {e}, 内容: {cell_content}")
        
        return courses
    
    def parse_weeks(self, weeks_str: str) -> List[int]:
        """解析周次字符串，返回周次列表"""
        weeks = []
        try:
            # 移除"周"字
            weeks_str = weeks_str.replace('周', '').strip()
            
            # 处理单双周
            is_odd = '(单)' in weeks_str
            is_even = '(双)' in weeks_str
            weeks_str = weeks_str.replace('(单)', '').replace('(双)', '')
            
            # 按逗号分割不同的周次段
            segments = weeks_str.split(',')
            
            for segment in segments:
                segment = segment.strip()
                if '-' in segment:
                    # 连续周次
                    start, end = map(int, segment.split('-'))
                    week_range = list(range(start, end + 1))
                    
                    # 应用单双周过滤
                    if is_odd:
                        week_range = [w for w in week_range if w % 2 == 1]
                    elif is_even:
                        week_range = [w for w in week_range if w % 2 == 0]
                    
                    weeks.extend(week_range)
                else:
                    # 单独周次
                    week = int(segment)
                    if not is_odd and not is_even:
                        weeks.append(week)
                    elif is_odd and week % 2 == 1:
                        weeks.append(week)
                    elif is_even and week % 2 == 0:
                        weeks.append(week)
            
        except Exception as e:
            self.logger.error(f"解析周次失败: {e}, 周次字符串: {weeks_str}")
            # 默认返回1-16周
            weeks = list(range(1, 17))
        
        return sorted(list(set(weeks)))  # 去重并排序

    def import_from_excel(self, file_path: str, progress_callback=None) -> List[Dict[str, Any]]:
        """从Excel文件导入课程表"""
        if not self.pandas_available:
            self.logger.error("pandas不可用，无法导入Excel文件")
            if progress_callback:
                progress_callback(0, "pandas不可用，无法导入Excel文件")
            return []

        courses = []
        try:
            if progress_callback:
                progress_callback(10, "正在读取Excel文件...")

            validated_path = validate_path(file_path, must_exist=True)
            if not validated_path:
                self.logger.error(f"Excel文件不存在: {file_path}")
                if progress_callback:
                    progress_callback(0, f"文件不存在: {file_path}")
                return []

            df = pandas.read_excel(str(validated_path), sheet_name=0)

            if progress_callback:
                progress_callback(20, "正在解析Excel结构...")

            # 验证Excel结构
            if df.empty:
                raise ValueError("Excel文件为空")

            if df.shape[1] < 2:
                raise ValueError("Excel文件至少需要2列（时间列和至少一个星期列）")

            # 获取时间列
            time_column = df.iloc[:, 0].tolist()

            # 获取星期列（从第二列开始）
            weekdays = df.columns[1:].tolist()

            if progress_callback:
                progress_callback(30, f"发现 {len(weekdays)} 个星期列，{len(time_column)} 个时间段")

            total_cells = len(time_column) * len(weekdays)
            processed_cells = 0

            # 遍历每个时间段和星期
            for row_idx, time_slot in enumerate(time_column):
                if pandas.isna(time_slot) or str(time_slot).strip() == "":
                    processed_cells += len(weekdays)
                    continue

                for col_idx, weekday in enumerate(weekdays):
                    processed_cells += 1

                    if progress_callback and processed_cells % 10 == 0:
                        progress = 30 + int((processed_cells / total_cells) * 50)
                        progress_callback(progress, f"正在解析课程数据... ({processed_cells}/{total_cells})")

                    cell_content = df.iloc[row_idx, col_idx + 1]

                    if pandas.isna(cell_content) or str(cell_content).strip() == "":
                        continue

                    try:
                        # 解析单元格中的课程信息
                        cell_courses = self.parse_course_cell(str(cell_content))

                        for course in cell_courses:
                            # 解析周次
                            weeks = self.parse_weeks(course['weeks'])

                            # 创建单个课程记录，包含周次范围
                            course_record = {
                                'name': course['name'],
                                'teacher': course['teacher'],
                                'location': course['location'],
                                'weekday': self.normalize_weekday(weekday),
                                'time': str(time_slot),
                                'start_week': min(weeks) if weeks else 1,
                                'end_week': max(weeks) if weeks else 16,
                                'weeks': weeks  # 保留完整的周次列表用于调试
                            }
                            courses.append(course_record)
                    except Exception as e:
                        self.logger.warning(f"解析单元格失败 [{row_idx+1}, {col_idx+2}]: {e}")
                        continue

            if progress_callback:
                progress_callback(90, f"导入完成，共解析 {len(courses)} 条课程记录")

            # 数据去重和验证
            courses = self._validate_and_deduplicate_courses(courses)

            if progress_callback:
                progress_callback(100, f"成功导入 {len(courses)} 条有效课程记录")

            self.logger.info(f"成功从Excel导入 {len(courses)} 条课程记录")
            return courses

        except Exception as e:
            error_msg = f"从Excel导入课程表失败: {e}"
            self.logger.error(error_msg)
            if progress_callback:
                progress_callback(0, error_msg)
            raise Exception(error_msg)

    def _validate_and_deduplicate_courses(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证和去重课程数据"""
        valid_courses = []
        seen_courses = set()

        for course in courses:
            # 验证必要字段
            if not course.get('name') or not course.get('name').strip():
                self.logger.warning(f"跳过无效课程：缺少课程名称 - {course}")
                continue

            if not course.get('weekday'):
                self.logger.warning(f"跳过无效课程：缺少星期信息 - {course}")
                continue

            if not course.get('time'):
                self.logger.warning(f"跳过无效课程：缺少时间信息 - {course}")
                continue

            # 创建唯一标识符用于去重
            course_key = (
                course['name'].strip(),
                course['weekday'],
                course['time'],
                course.get('start_week', 1),
                course.get('end_week', 16)
            )

            if course_key not in seen_courses:
                seen_courses.add(course_key)

                # 清理和标准化数据
                cleaned_course = {
                    'name': course['name'].strip(),
                    'teacher': course.get('teacher', '').strip(),
                    'location': course.get('location', '').strip(),
                    'weekday': course['weekday'],
                    'time': course['time'],
                    'start_week': course.get('start_week', 1),
                    'end_week': course.get('end_week', 16)
                }
                valid_courses.append(cleaned_course)

        self.logger.info(f"数据验证完成：原始 {len(courses)} 条，有效 {len(valid_courses)} 条")
        return valid_courses

    def export_to_excel(self, courses: List[Dict[str, Any]], file_path: str) -> bool:
        """导出课程表到Excel文件"""
        try:
            # 创建时间段列表
            time_slots = [
                "08:00-08:45", "08:55-09:40", "10:00-10:45", "10:55-11:40",
                "14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40",
                "19:00-19:45", "19:55-20:40", "20:50-21:35"
            ]

            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

            # 创建课程表数据结构
            schedule_data = {}
            schedule_data["时间"] = time_slots

            for day in weekdays:
                schedule_data[day] = [""] * len(time_slots)

            # 按时间段和星期组织课程数据
            course_grid = {}
            for course in courses:
                time = course.get('time', '')
                weekday = self.normalize_weekday(course.get('weekday', ''))

                if time not in course_grid:
                    course_grid[time] = {}
                if weekday not in course_grid[time]:
                    course_grid[time][weekday] = []

                course_grid[time][weekday].append(course)

            # 填充课程表数据
            for time_idx, time_slot in enumerate(time_slots):
                for day in weekdays:
                    if time_slot in course_grid and day in course_grid[time_slot]:
                        courses_in_slot = course_grid[time_slot][day]

                        # 按周次分组课程
                        week_groups = {}
                        for course in courses_in_slot:
                            weeks_key = f"{course.get('start_week', 1)}-{course.get('end_week', 16)}"
                            if weeks_key not in week_groups:
                                week_groups[weeks_key] = []
                            week_groups[weeks_key].append(course)

                        # 构建单元格内容
                        cell_parts = []
                        for weeks_key, group_courses in week_groups.items():
                            if group_courses:
                                course = group_courses[0]  # 取第一个课程作为代表
                                cell_parts.extend([
                                    course.get('name', ''),
                                    course.get('teacher', ''),
                                    course.get('location', ''),
                                    f"{weeks_key}周"
                                ])

                        schedule_data[day][time_idx] = ';'.join(cell_parts)

            # 创建DataFrame并保存
            df = pd.DataFrame(schedule_data)

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='课程表', index=False)

                # 格式化工作表
                worksheet = writer.sheets['课程表']

                # 设置列宽
                worksheet.column_dimensions['A'].width = 15
                for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H']:
                    worksheet.column_dimensions[col].width = 25

                # 设置行高和样式
                from openpyxl.styles import Border, Side, Alignment
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )

                center_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = center_alignment
                        worksheet.row_dimensions[cell.row].height = 30

            self.logger.info(f"成功导出课程表到Excel: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"导出课程表到Excel失败: {e}")
            return False

    def normalize_weekday(self, weekday: str) -> str:
        """标准化星期格式"""
        weekday_map = {
            'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
            'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日',
            '星期一': '周一', '星期二': '周二', '星期三': '周三',
            '星期四': '周四', '星期五': '周五', '星期六': '周六', '星期日': '周日'
        }

        return weekday_map.get(weekday, weekday)

    def validate_excel_format(self, file_path: str) -> tuple[bool, str]:
        """验证Excel文件格式"""
        try:
            df = pd.read_excel(file_path, sheet_name=0)

            # 检查是否有时间列
            if df.shape[1] < 2:
                return False, "Excel文件至少需要2列（时间列和至少一个星期列）"

            # 检查时间列格式
            time_column = df.iloc[:, 0].tolist()
            valid_times = 0
            for time_slot in time_column:
                if pd.isna(time_slot):
                    continue
                time_str = str(time_slot).strip()
                if ':' in time_str and '-' in time_str:
                    valid_times += 1

            if valid_times == 0:
                return False, "时间列格式不正确，应为 HH:MM-HH:MM 格式"

            return True, "Excel格式验证通过"

        except Exception as e:
            return False, f"Excel文件读取失败: {e}"
