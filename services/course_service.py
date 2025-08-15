"""
课程管理服务
提供课程相关的业务逻辑处理
"""

from typing import List, Optional
from models.class_item import ClassItem
from utils.validation_utils import validate_course_data
from utils.logger import get_service_logger
from utils.exceptions import ValidationException, NotFoundException, ConflictException

# 初始化日志记录器
logger = get_service_logger("course_service")


class CourseService:
    """课程管理服务类"""
    
    def __init__(self):
        """初始化课程服务"""
        self.courses: List[ClassItem] = []
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
        
        # 验证课程数据
        is_valid, errors = validate_course_data(course)
        if not is_valid:
            logger.warning(f"Course validation failed: {errors}")
            raise ValidationException("课程数据验证失败", errors)
        
        # 检查课程ID是否已存在
        if self.get_course_by_id(course.id):
            logger.warning(f"Course with id {course.id} already exists")
            raise ConflictException(f"课程ID {course.id} 已存在")
        
        # 检查时间、教师、教室冲突
        self._check_course_conflicts(course)
        
        # 添加课程
        self.courses.append(course)
        logger.info(f"Course {course.id} created successfully")
        return course
    
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
        
        # 验证课程数据
        is_valid, errors = validate_course_data(updated_course)
        if not is_valid:
            logger.warning(f"Course validation failed: {errors}")
            raise ValidationException("课程数据验证失败", errors)
        
        # 查找要更新的课程
        course_index = self._find_course_index(course_id)
        if course_index == -1:
            logger.warning(f"Course {course_id} not found")
            raise NotFoundException(f"课程 {course_id} 未找到")
        
        # 检查时间、教师、教室冲突（排除自身）
        existing_courses = [c for i, c in enumerate(self.courses) if i != course_index]
        self._check_course_conflicts(updated_course, existing_courses)
        
        # 更新课程
        self.courses[course_index] = updated_course
        logger.info(f"Course {course_id} updated successfully")
        return updated_course
    
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
        
        # 查找要删除的课程
        course_index = self._find_course_index(course_id)
        if course_index == -1:
            logger.warning(f"Course {course_id} not found")
            raise NotFoundException(f"课程 {course_id} 未找到")
        
        # 删除课程
        del self.courses[course_index]
        logger.info(f"Course {course_id} deleted successfully")
        return True
    
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
        
        # 检查教师时间冲突
        teacher_conflicts = self._check_teacher_conflict(course, existing_courses)
        conflicts.extend(teacher_conflicts)
        
        # 检查教室资源冲突
        location_conflicts = self._check_location_conflict(course, existing_courses)
        conflicts.extend(location_conflicts)
        
        # 检查课程时间冲突
        time_conflicts = self._check_time_conflict(course, existing_courses)
        conflicts.extend(time_conflicts)
        
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
            # 如果是同一个教师且时间冲突
            if (existing_course.teacher == course.teacher and 
                existing_course.id != course.id and
                self._is_time_conflict(course, existing_course)):
                conflicts.append(f"教师 {course.teacher} 在 {course.duration.start_time}-{course.duration.end_time} 时间段已有课程")
        
        return conflicts
    
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
            # 如果是同一个教室且时间冲突
            if (existing_course.location == course.location and 
                existing_course.id != course.id and
                self._is_time_conflict(course, existing_course)):
                conflicts.append(f"教室 {course.location} 在 {course.duration.start_time}-{course.duration.end_time} 时间段已被占用")
        
        return conflicts
    
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
            # 如果时间冲突
            if (course1.id != course2.id and 
                self._is_time_conflict(course1, course2)):
                conflicts.append(f"课程时间 {course1.duration.start_time}-{course1.duration.end_time} 与课程 {course2.name} 冲突")
        
        return conflicts
    
    def _is_time_conflict(self, course1: ClassItem, course2: ClassItem) -> bool:
        """
        检查两个课程的时间是否冲突
        
        Args:
            course1: 第一个课程
            course2: 第二个课程
            
        Returns:
            是否冲突
        """
        # 检查时间是否冲突
        start1_h, start1_m = map(int, course1.duration.start_time.split(':'))
        end1_h, end1_m = map(int, course1.duration.end_time.split(':'))
        start2_h, start2_m = map(int, course2.duration.start_time.split(':'))
        end2_h, end2_m = map(int, course2.duration.end_time.split(':'))
        
        # 转换为分钟进行比较
        start1_minutes = start1_h * 60 + start1_m
        end1_minutes = end1_h * 60 + end1_m
        start2_minutes = start2_h * 60 + start2_m
        end2_minutes = end2_h * 60 + end2_m
        
        # 检查是否有时间重叠
        return not (end1_minutes <= start2_minutes or end2_minutes <= start1_minutes)