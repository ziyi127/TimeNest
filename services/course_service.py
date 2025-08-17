"""
课程管理服务
提供课程相关的业务逻辑处理
"""

from typing import List, Optional
from models.class_item import ClassItem
from utils.validation_utils import validate_course_data
from utils.logger import get_service_logger
from utils.exceptions import ValidationException, NotFoundException, ConflictException
from data_access.json_data_access import JSONDataAccess

# 初始化日志记录器
logger = get_service_logger("course_service")


class CourseService:
    """课程管理服务类"""
    
    def __init__(self):
        """初始化课程服务"""
        self.data_access = JSONDataAccess()
        self.courses: List[ClassItem] = []
        self._load_courses()
        logger.info("CourseService initialized")
    
    def create_course(self, course: ClassItem) -> ClassItem:
        """
        创建课程
        
        Args:
            course: 课程对象
            
        Returns:
            创建的课程对象
            
        Raises:
            ValidationException: 数据验证失败
            ConflictException: 课程冲突
        """
        logger.info(f"Creating course: {course.id}")
        
        # 执行创建课程的步骤
        self._validate_and_check_course(course)
        self._ensure_course_id_unique(course.id)
        self._check_course_conflicts(course)
        self._add_course(course)
        
        logger.info(f"Course {course.id} created successfully")
        return course
    
    def _validate_and_check_course(self, course: ClassItem) -> None:
        """
        验证课程数据
        
        Args:
            course: 课程对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        is_valid, errors = validate_course_data(course)
        if not is_valid:
            logger.warning(f"Course validation failed: {errors}")
            raise ValidationException("课程数据验证失败", errors)
    
    def _ensure_course_id_unique(self, course_id: str) -> None:
        """
        确保课程ID唯一
        
        Args:
            course_id: 课程ID
            
        Raises:
            ConflictException: 课程ID已存在
        """
        if self.get_course_by_id(course_id):
            logger.warning(f"Course with id {course_id} already exists")
            raise ConflictException(f"课程ID {course_id} 已存在")
    
    def _add_course(self, course: ClassItem) -> None:
        """
        添加课程到列表
        
        Args:
            course: 要添加的课程
        """
        self.courses.append(course)
        self._save_courses()
    
    def update_course(self, course_id: str, updated_course: ClassItem) -> ClassItem:
        """
        更新课程
        
        Args:
            course_id: 课程ID
            updated_course: 更新的课程对象
            
        Returns:
            更新后的课程对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 课程未找到
            ConflictException: 课程冲突
        """
        logger.info(f"Updating course: {course_id}")
        
        # 执行更新课程的步骤
        self._validate_and_check_course(updated_course)
        course_index = self._find_course_index(course_id)
        self._ensure_course_exists(course_id, course_index)
        self._check_update_conflicts(updated_course, course_index)
        self._update_course_at_index(course_index, updated_course)
        
        logger.info(f"Course {course_id} updated successfully")
        return updated_course
    
    def _check_update_conflicts(self, updated_course: ClassItem, course_index: int) -> None:
        """
        检查更新时的课程冲突（排除自身）
        
        Args:
            updated_course: 更新的课程对象
            course_index: 要更新的课程索引
        """
        existing_courses = [c for i, c in enumerate(self.courses) if i != course_index]
        self._check_course_conflicts(updated_course, existing_courses)
    
    def delete_course(self, course_id: str) -> bool:
        """
        删除课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            是否删除成功
            
        Raises:
            NotFoundException: 课程未找到
        """
        logger.info(f"Deleting course: {course_id}")
        
        # 执行删除课程的步骤
        self._execute_delete_course_steps(course_id)
        
        logger.info(f"Course {course_id} deleted successfully")
        return True
    
    def _execute_delete_course_steps(self, course_id: str) -> None:
        """
        执行删除课程的步骤
        
        Args:
            course_id: 课程ID
            
        Raises:
            NotFoundException: 课程未找到
        """
        # 查找要删除的课程
        course_index = self._find_course_index(course_id)
        self._ensure_course_exists(course_id, course_index)
        
        # 删除课程
        self._remove_course_at_index(course_index)
    
    def get_course_by_id(self, course_id: str) -> Optional[ClassItem]:
        """
        根据ID获取课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程对象，如果未找到则返回None
        """
        logger.debug(f"Getting course by id: {course_id}")
        
        for course in self.courses:
            if course.id == course_id:
                logger.debug(f"Course {course_id} found")
                return course
        
        logger.debug(f"Course {course_id} not found")
        return None
    
    def get_all_courses(self) -> List[ClassItem]:
        """
        获取所有课程
        
        Returns:
            课程列表
        """
        logger.debug("Getting all courses")
        return self.courses.copy()
    
    def _find_course_index(self, course_id: str) -> int:
        """
        查找课程在列表中的索引
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程索引，如果未找到则返回-1
        """
        for i, course in enumerate(self.courses):
            if course.id == course_id:
                return i
        return -1
    
    def _is_time_conflict(self, course1: ClassItem, course2: ClassItem) -> bool:
        """
        检查两个课程的时间是否冲突
        
        Args:
            course1: 第一个课程
            course2: 第二个课程
            
        Returns:
            是否冲突
        """
        try:
            # 解析两个课程的时间
            start1_minutes = self._time_to_minutes(course1.duration.start_time)
            end1_minutes = self._time_to_minutes(course1.duration.end_time)
            start2_minutes = self._time_to_minutes(course2.duration.start_time)
            end2_minutes = self._time_to_minutes(course2.duration.end_time)
            
            # 检查是否有时间重叠
            return self._has_time_overlap(start1_minutes, end1_minutes, start2_minutes, end2_minutes)
            
        except Exception as e:
            logger.warning(f"时间冲突检测失败: {str(e)}")
            return False  # 如果解析失败，默认不冲突
    
    def _has_time_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """
        检查两个时间段是否有重叠
        
        Args:
            start1: 第一个时间段的开始时间(分钟)
            end1: 第一个时间段的结束时间(分钟)
            start2: 第二个时间段的开始时间(分钟)
            end2: 第二个时间段的结束时间(分钟)
            
        Returns:
            是否有时间重叠
        """
        return not (end1 <= start2 or end2 <= start1)
    
    def _time_to_minutes(self, time_str: str) -> int:
        """
        将时间字符串转换为分钟数
        
        Args:
            time_str: 时间字符串，格式为 "HH:MM"
            
        Returns:
            int: 总分钟数
            
        Raises:
            ValueError: 时间格式不正确时抛出异常
        """
        parts = time_str.split(':')
        if len(parts) != 2:
            raise ValueError(f"无效的时间格式: {time_str}")
        
        hour = int(parts[0])
        minute = int(parts[1])
        
        # 验证时间范围
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            raise ValueError(f"时间超出有效范围: {time_str}")
        
        return hour * 60 + minute
    
    def _check_course_conflicts(self, course: ClassItem, existing_courses: Optional[List[ClassItem]] = None) -> None:
        """
        检查课程冲突
        
        Args:
            course: 要检查的课程
            existing_courses: 已存在的课程列表，默认为所有课程
            
        Raises:
            ConflictException: 发现冲突
        """
        if existing_courses is None:
            existing_courses = self.courses
        
        conflicts: List[str] = []
        
        # 检查各类冲突
        conflicts.extend(self._check_teacher_conflict(course, existing_courses))
        conflicts.extend(self._check_location_conflict(course, existing_courses))
        conflicts.extend(self._check_time_conflict(course, existing_courses))
        
        if conflicts:
            logger.warning(f"Course conflicts found: {conflicts}")
            raise ConflictException("课程冲突检查失败", conflicts)
    
    def _check_teacher_conflict(self, course: ClassItem, existing_courses: List[ClassItem]) -> List[str]:
        """
        检查教师时间冲突
        
        Args:
            course: 要检查的课程
            existing_courses: 已存在的课程列表
            
        Returns:
            冲突信息列表
        """
        conflicts: List[str] = []
        
        for existing_course in existing_courses:
            # 检查教师冲突
            if self._is_teacher_conflict(course, existing_course):
                conflicts.append(f"教师 {course.teacher} 在 {course.duration.start_time}-{course.duration.end_time} 时间段已有课程")
        
        return conflicts
    
    def _is_teacher_conflict(self, course: ClassItem, existing_course: ClassItem) -> bool:
        """
        检查两个课程是否教师冲突
        
        Args:
            course: 要检查的课程
            existing_course: 已存在的课程
            
        Returns:
            是否教师冲突
        """
        return (existing_course.teacher == course.teacher and 
                existing_course.id != course.id and
                self._is_time_conflict(course, existing_course))
    
    def _check_location_conflict(self, course: ClassItem, existing_courses: List[ClassItem]) -> List[str]:
        """
        检查教室资源冲突
        
        Args:
            course: 要检查的课程
            existing_courses: 已存在的课程列表
            
        Returns:
            冲突信息列表
        """
        conflicts: List[str] = []
        
        for existing_course in existing_courses:
            # 检查教室冲突
            if self._is_location_conflict(course, existing_course):
                conflicts.append(f"教室 {course.location} 在 {course.duration.start_time}-{course.duration.end_time} 时间段已被占用")
        
        return conflicts
    
    def _is_location_conflict(self, course: ClassItem, existing_course: ClassItem) -> bool:
        """
        检查两个课程是否教室冲突
        
        Args:
            course: 要检查的课程
            existing_course: 已存在的课程
            
        Returns:
            是否教室冲突
        """
        return (existing_course.location == course.location and 
                existing_course.id != course.id and
                self._is_time_conflict(course, existing_course))
    
    def _check_time_conflict(self, course1: ClassItem, existing_courses: List[ClassItem]) -> List[str]:
        """
        检查课程时间冲突
        
        Args:
            course1: 要检查的课程
            existing_courses: 已存在的课程列表
            
        Returns:
            冲突信息列表
        """
        conflicts: List[str] = []
        
        for course2 in existing_courses:
            # 检查时间冲突
            if self._is_course_time_conflict(course1, course2):
                conflicts.append(f"课程时间 {course1.duration.start_time}-{course1.duration.end_time} 与课程 {course2.name} 冲突")
        
        return conflicts
    
    def _is_course_time_conflict(self, course1: ClassItem, course2: ClassItem) -> bool:
        """
        检查两个课程是否时间冲突
        
        Args:
            course1: 第一个课程
            course2: 第二个课程
            
        Returns:
            是否时间冲突
        """
        return (course1.id != course2.id and 
                self._is_time_conflict(course1, course2))
    
    def _validate_course_data(self, course: ClassItem) -> None:
        """
        验证课程数据
        
        Args:
            course: 要验证的课程
            
        Raises:
            ValidationException: 数据验证失败
        """
        is_valid, errors = validate_course_data(course)
        if not is_valid:
            logger.warning(f"Course validation failed: {errors}")
            raise ValidationException("课程数据验证失败", errors)
    
    def _ensure_course_exists(self, course_id: str, course_index: int) -> None:
        """
        确保课程存在
        
        Args:
            course_id: 课程ID
            course_index: 课程索引
            
        Raises:
            NotFoundException: 课程未找到
        """
        if course_index == -1:
            logger.warning(f"Course {course_id} not found")
            raise NotFoundException(f"课程 {course_id} 未找到")
    
    def _load_courses(self):
        """加载课程数据"""
        try:
            data = self.data_access.read_json("courses.json")
            if data and "courses" in data:
                self.courses = [
                    ClassItem.from_dict(course_data) 
                    for course_data in data["courses"]
                ]
            logger.info(f"加载了 {len(self.courses)} 门课程")
        except Exception as e:
            logger.error(f"加载课程数据失败: {str(e)}")
            self.courses = []
    
    def _save_courses(self):
        """保存课程数据"""
        try:
            data = {
                "courses": [course.to_dict() for course in self.courses]
            }
            self.data_access.write_json("courses.json", data)
            logger.debug("课程数据已保存")
        except Exception as e:
            logger.error(f"保存课程数据失败: {str(e)}")
            raise ValidationException("保存课程数据失败")
    
    def _update_course_at_index(self, index: int, course: ClassItem) -> None:
        """
        在指定索引处更新课程
        
        Args:
            index: 课程索引
            course: 新的课程对象
        """
        self.courses[index] = course
        self._save_courses()
    
    def _remove_course_at_index(self, index: int) -> None:
        """
        删除指定索引处的课程
        
        Args:
            index: 课程索引
        """
        del self.courses[index]
