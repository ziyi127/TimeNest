"""
课程简称服务
提供课程名称简称管理和生成功能
"""

import json
import os
import re
from typing import List, Optional, Dict, Any
from models.course_alias import CourseAlias, CourseAliasSettings
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("course_alias_service")


class CourseAliasService:
    """课程简称服务类"""
    
    def __init__(self):
        """初始化课程简称服务"""
        self.config_file = "./data/course_alias_config.json"
        self.data_file = "./data/course_alias_data.json"
        self.settings: Optional[CourseAliasSettings] = None
        self.course_aliases: List[CourseAlias] = []
        self._ensure_data_directory()
        self._load_settings()
        self._load_course_alias_data()
        logger.info("CourseAliasService initialized")
    
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
        """加载课程简称设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = CourseAliasSettings.from_dict(data)
                logger.debug("课程简称设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = CourseAliasSettings()
                self._save_settings()
                logger.debug("创建默认课程简称设置")
        except Exception as e:
            logger.error(f"加载课程简称设置失败: {str(e)}")
            self.settings = CourseAliasSettings()
    
    def _save_settings(self):
        """保存课程简称设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("课程简称设置保存成功")
        except Exception as e:
            logger.error(f"保存课程简称设置失败: {str(e)}")
            raise ValidationException("保存课程简称设置失败")
    
    def _load_course_alias_data(self):
        """加载课程简称数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.course_aliases = [CourseAlias.from_dict(item) for item in data]
                logger.debug(f"课程简称数据加载成功，共 {len(self.course_aliases)} 个项目")
        except Exception as e:
            logger.error(f"加载课程简称数据失败: {str(e)}")
    
    def _save_course_alias_data(self):
        """保存课程简称数据"""
        try:
            # 确保数据目录存在
            self._ensure_data_directory()
            
            data = [item.to_dict() for item in self.course_aliases]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("课程简称数据保存成功")
        except Exception as e:
            logger.error(f"保存课程简称数据失败: {str(e)}")
    
    def get_settings(self) -> CourseAliasSettings:
        """
        获取课程简称设置
        
        Returns:
            CourseAliasSettings: 课程简称设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or CourseAliasSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新课程简称设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        logger.info("更新课程简称设置")
        
        try:
            # 确保设置对象存在
            self._ensure_settings_exists()
            
            # 更新设置字段
            self._update_settings_fields(settings_data)
            
            # 保存设置
            self._save_settings()
            
            logger.info("课程简称设置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新课程简称设置失败: {str(e)}")
            return False
    
    def _ensure_settings_exists(self) -> None:
        """
        确保设置对象存在
        """
        if not self.settings:
            self.settings = CourseAliasSettings()
    
    def _update_settings_fields(self, settings_data: Dict[str, Any]) -> None:
        """
        更新设置字段
        
        Args:
            settings_data: 设置数据字典
        """
        for key, value in settings_data.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
    
    def get_course_aliases(self) -> List[CourseAlias]:
        """
        获取所有课程简称
        
        Returns:
            List[CourseAlias]: 课程简称列表
        """
        return self.course_aliases
    
    def get_course_alias(self, course_id: str) -> Optional[CourseAlias]:
        """
        根据课程ID获取课程简称
        
        Args:
            course_id: 课程ID
            
        Returns:
            Optional[CourseAlias]: 课程简称
        """
        for alias in self.course_aliases:
            if alias.course_id == course_id:
                return alias
        return None
    
    def get_alias_by_course_id(self, course_id: str) -> str:
        """
        根据课程ID获取简称
        
        Args:
            course_id: 课程ID
            
        Returns:
            str: 课程简称，如果未找到则返回空字符串
        """
        alias = self.get_course_alias(course_id)
        return alias.alias if alias else ""
    
    def add_course_alias(self, alias: CourseAlias) -> bool:
        """
        添加课程简称
        
        Args:
            alias: 课程简称
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查课程ID是否已存在
            if self._is_course_alias_exists(alias.course_id):
                logger.warning(f"课程简称已存在: {alias.course_id}")
                return False
            
            # 添加并保存课程简称
            self._add_and_save_course_alias(alias)
            
            logger.info(f"添加课程简称: {alias.course_id} -> {alias.alias}")
            return True
        except Exception as e:
            logger.error(f"添加课程简称失败: {str(e)}")
            return False
    
    def _is_course_alias_exists(self, course_id: str) -> bool:
        """
        检查课程简称是否存在
        
        Args:
            course_id: 课程ID
            
        Returns:
            bool: 课程简称是否存在
        """
        return self.get_course_alias(course_id) is not None
    
    def _add_and_save_course_alias(self, alias: CourseAlias) -> None:
        """
        添加并保存课程简称
        
        Args:
            alias: 课程简称
        """
        self.course_aliases.append(alias)
        self._save_course_alias_data()
    
    def update_course_alias(self, course_id: str, alias_data: Dict[str, Any]) -> bool:
        """
        更新课程简称
        
        Args:
            course_id: 课程ID
            alias_data: 简称数据字典
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 查找并验证课程简称
            alias = self._get_and_validate_course_alias(course_id)
            if not alias:
                return False
            
            # 更新简称字段并保存
            self._update_alias_fields_and_save(alias, alias_data)
            
            logger.info(f"更新课程简称: {alias.course_id} -> {alias.alias}")
            return True
        except Exception as e:
            logger.error(f"更新课程简称失败: {str(e)}")
            return False
    
    def _get_and_validate_course_alias(self, course_id: str):
        """
        获取并验证课程简称是否存在
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程简称对象或None
        """
        alias = self.get_course_alias(course_id)
        if not alias:
            logger.warning(f"课程简称未找到: {course_id}")
            return None
        return alias
    
    def _update_alias_fields_and_save(self, alias, alias_data: Dict[str, Any]) -> None:
        """
        更新简称字段并保存
        
        Args:
            alias: 课程简称对象
            alias_data: 简称数据字典
        """
        # 更新简称字段
        for key, value in alias_data.items():
            if hasattr(alias, key):
                setattr(alias, key, value)
        
        self._save_course_alias_data()
    
    def remove_course_alias(self, course_id: str) -> bool:
        """
        删除课程简称
        
        Args:
            course_id: 课程ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 查找并验证课程简称
            alias = self._get_and_validate_course_alias(course_id)
            if not alias:
                return False
            
            # 删除并保存课程简称
            self._remove_and_save_course_alias(alias)
            
            logger.info(f"删除课程简称: {alias.course_id} -> {alias.alias}")
            return True
        except Exception as e:
            logger.error(f"删除课程简称失败: {str(e)}")
            return False
    
    def _remove_and_save_course_alias(self, alias: CourseAlias) -> None:
        """
        删除并保存课程简称
        
        Args:
            alias: 课程简称对象
        """
        self.course_aliases.remove(alias)
        self._save_course_alias_data()
    
    def _clean_course_name(self, course_name: str) -> str:
        """
        清理课程名称，只保留中文、英文和数字
        
        Args:
            course_name: 原始课程名称
            
        Returns:
            str: 清理后的课程名称
        """
        return re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', course_name)
    
    def _get_max_alias_length(self) -> int:
        """
        获取最大简称长度设置
        
        Returns:
            int: 最大简称长度
        """
        return self.settings.max_alias_length if self.settings else 10
    
    def _generate_chinese_alias(self, clean_name: str) -> str:
        """
        生成中文课程简称
        
        Args:
            clean_name: 清理后的课程名称
            
        Returns:
            str: 中文课程简称
        """
        return clean_name[:self._get_max_alias_length()]
    
    def _generate_english_alias(self, clean_name: str) -> str:
        """
        生成英文课程简称
        
        Args:
            clean_name: 清理后的课程名称
            
        Returns:
            str: 英文课程简称
        """
        words = clean_name.split()
        if len(words) > 1:
            # 取每个单词的首字母
            acronym = ''.join([word[0] for word in words if word])
            return acronym[:self._get_max_alias_length()]
        else:
            # 取前几个字符
            return clean_name[:self._get_max_alias_length()]
    
    def generate_alias(self, course_name: str) -> str:
        """
        自动生成课程简称
        
        Args:
            course_name: 课程名称
            
        Returns:
            str: 生成的简称
        """
        if not self.settings or not self.settings.auto_generate:
            return course_name
        
        try:
            # 清理和预处理课程名称
            clean_name = self._clean_course_name(course_name)
            
            # 处理特殊情况
            if self._is_empty_or_invalid_name(clean_name, course_name):
                return self._handle_empty_or_invalid_name(clean_name, course_name)
            
            # 如果名称长度小于等于最大长度，直接返回
            if len(clean_name) <= self._get_max_alias_length():
                return clean_name
            
            # 根据语言类型生成简称
            return self._generate_alias_by_language_type(clean_name)
        except Exception as e:
            logger.error(f"生成课程简称失败: {str(e)}")
            return course_name[:self._get_max_alias_length()]
    
    def _is_empty_or_invalid_name(self, clean_name: str, original_name: str) -> bool:
        """
        检查名称是否为空或无效
        
        Args:
            clean_name: 清理后的名称
            original_name: 原始名称
            
        Returns:
            bool: 是否为空或无效
        """
        return not clean_name
    
    def _handle_empty_or_invalid_name(self, clean_name: str, original_name: str) -> str:
        """
        处理空或无效名称
        
        Args:
            clean_name: 清理后的名称
            original_name: 原始名称
            
        Returns:
            str: 处理后的名称
        """
        return original_name[:self._get_max_alias_length()]
    
    def _generate_alias_by_language_type(self, clean_name: str) -> str:
        """
        根据语言类型生成简称
        
        Args:
            clean_name: 清理后的课程名称
            
        Returns:
            str: 生成的简称
        """
        # 对于中文，取前几个字符
        if re.search(r'[\u4e00-\u9fa5]', clean_name):
            return self._generate_chinese_alias(clean_name)
        
        # 对于英文，尝试提取首字母
        return self._generate_english_alias(clean_name)
    
    def _get_course_alias_with_fallback(self, course_id: str, course_name: str) -> str:
        """
        获取课程简称，如果未找到且启用了自动生成，则生成简称
        
        Args:
            course_id: 课程ID
            course_name: 课程名称
            
        Returns:
            str: 课程简称
        """
        alias = self.get_alias_by_course_id(course_id)
        if not alias and self.settings and self.settings.auto_generate:
            alias = self.generate_alias(course_name)
        return alias
    
    def get_course_with_alias(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        获取带简称的课程信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            Optional[Dict[str, Any]]: 课程信息字典
        """
        try:
            # 获取课程
            course = self._get_course_by_id(course_id)
            if not course:
                return None
            
            # 获取简称并构建课程数据
            course_data = self._build_course_data_with_alias(course)
            
            return course_data
        except Exception as e:
            logger.error(f"获取带简称的课程信息失败: {str(e)}")
            return None
    def _get_course_by_id(self, course_id: str):
        """
        根据ID获取课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程对象或None
        """
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        # 获取课程服务
        course_service = ServiceFactory.get_course_service()
        return course_service.get_course_by_id(course_id)
    def _build_course_data_with_alias(self, course) -> Dict[str, Any]:
        """
        构建带简称的课程数据
        
        Args:
            course: 课程对象
            
        Returns:
            Dict[str, Any]: 课程数据字典
        """
        # 获取简称
        alias = self._get_course_alias_with_fallback(course.id, course.name)
        
        # 构建返回数据
        return self._build_course_data(course, alias)
    
    def _build_course_data(self, course, alias: str) -> Dict[str, Any]:
        """
        构建课程数据字典
        
        Args:
            course: 课程对象
            alias: 课程简称
            
        Returns:
            Dict[str, Any]: 课程数据字典
        """
        return {
            "id": course.id,
            "name": course.name,
            "alias": alias,
            "teacher": course.teacher,
            "location": course.location,
            "color": getattr(course, 'color', '')
        }
    
    def get_all_courses_with_aliases(self) -> List[Dict[str, Any]]:
        """
        获取所有带简称的课程信息
        
        Returns:
            List[Dict[str, Any]]: 课程信息列表
        """
        try:
            # 获取课程服务和所有课程
            course_service = self._get_course_service()
            courses = course_service.get_all_courses()
            
            # 为每个课程生成带简称的信息
            courses_with_aliases = self._build_courses_with_aliases_list(courses)
            
            return courses_with_aliases
        except Exception as e:
            logger.error(f"获取所有带简称的课程信息失败: {str(e)}")
            return []
    
    def _get_course_service(self):
        """
        获取课程服务实例
        
        Returns:
            课程服务实例
        """
        # 延迟导入ServiceFactory以避免循环导入
        from services.service_factory import ServiceFactory
        
        return ServiceFactory.get_course_service()
    
    def _build_courses_with_aliases_list(self, courses: List) -> List[Dict[str, Any]]:
        """
        构建带简称的课程信息列表
        
        Args:
            courses: 课程列表
            
        Returns:
            List[Dict[str, Any]]: 带简称的课程信息列表
        """
        courses_with_aliases: List[Dict[str, Any]] = []
        for course in courses:
            # 获取简称
            alias = self._get_course_alias_with_fallback(course.id, course.name)
            
            # 构建返回数据
            course_data = self._build_course_data(course, alias)
            courses_with_aliases.append(course_data)
            
        return courses_with_aliases
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False