继续继续"""
倒计时服务
提供特定日期倒计时计算和管理功能
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.countdown import CountdownItem, CountdownSettings
from utils.logger import get_service_logger
from utils.exceptions import ValidationException

# 初始化日志记录器
logger = get_service_logger("countdown_service")


class CountdownService:
    """倒计时服务类"""
    
    def __init__(self):
        """初始化倒计时服务"""
        self.config_file = "./data/countdown_config.json"
        self.data_file = "./data/countdown_data.json"
        self.settings: Optional[CountdownSettings] = None
        self.countdown_items: List[CountdownItem] = []
        self._ensure_data_directory()
        self._load_settings()
        self._load_countdown_data()
        logger.info("CountdownService initialized")
    
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
        """加载倒计时设置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = CountdownSettings.from_dict(data)
                logger.debug("倒计时设置加载成功")
            else:
                # 如果配置文件不存在，创建默认设置
                self.settings = CountdownSettings()
                self._save_settings()
                logger.debug("创建默认倒计时设置")
        except Exception as e:
            logger.error(f"加载倒计时设置失败: {str(e)}")
            self.settings = CountdownSettings()
    
    def _save_settings(self):
        """保存倒计时设置"""
        try:
            if self.settings:
                # 确保数据目录存在
                self._ensure_data_directory()
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
                logger.debug("倒计时设置保存成功")
        except Exception as e:
            logger.error(f"保存倒计时设置失败: {str(e)}")
            raise ValidationException("保存倒计时设置失败")
    
    def _load_countdown_data(self):
        """加载倒计时数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.countdown_items = [CountdownItem.from_dict(item) for item in data]
                logger.debug(f"倒计时数据加载成功，共 {len(self.countdown_items)} 个项目")
        except Exception as e:
            logger.error(f"加载倒计时数据失败: {str(e)}")
    
    def _save_countdown_data(self):
        """保存倒计时数据"""
        try:
            # 确保数据目录存在
            self._ensure_data_directory()
            
            data = [item.to_dict() for item in self.countdown_items]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("倒计时数据保存成功")
        except Exception as e:
            logger.error(f"保存倒计时数据失败: {str(e)}")
    
    def get_settings(self) -> CountdownSettings:
        """
        获取倒计时设置
        
        Returns:
            CountdownSettings: 倒计时设置
        """
        if not self.settings:
            self._load_settings()
        return self.settings or CountdownSettings()
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """
        更新倒计时设置
        
        Args:
            settings_data: 设置数据字典
            
        Returns:
            bool: 是否更新成功
        """
        logger.info("更新倒计时设置")
        
        try:
            # 确保设置对象存在
            self._ensure_settings_exists()
            
            # 更新设置字段
            self._update_settings_fields(settings_data)
            
            # 保存设置
            self._save_settings()
            
            logger.info("倒计时设置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新倒计时设置失败: {str(e)}")
            return False
    
    def _ensure_settings_exists(self) -> None:
        """
        确保设置对象存在
        """
        if not self.settings:
            self.settings = CountdownSettings()
    
    def _update_settings_fields(self, settings_data: Dict[str, Any]) -> None:
        """
        更新设置字段
        
        Args:
            settings_data: 设置数据字典
        """
        for key, value in settings_data.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
    
    def get_countdown_items(self) -> List[CountdownItem]:
        """
        获取所有倒计时项目
        
        Returns:
            List[CountdownItem]: 倒计时项目列表
        """
        return self.countdown_items
    
    def get_countdown_item(self, item_id: str) -> Optional[CountdownItem]:
        """
        根据ID获取倒计时项目
        
        Args:
            item_id: 项目ID
            
        Returns:
            Optional[CountdownItem]: 倒计时项目
        """
        for item in self.countdown_items:
            if item.id == item_id:
                return item
        return None
    
    def add_countdown_item(self, item: CountdownItem) -> bool:
        """
        添加倒计时项目
        
        Args:
            item: 倒计时项目
            
        Returns:
            bool: 是否添加成功
        """
        try:
            # 检查ID是否已存在
            if self._is_countdown_item_exists(item.id):
                logger.warning(f"倒计时项目ID已存在: {item.id}")
                return False
            
            # 添加并保存倒计时项目
            self._add_and_save_countdown_item(item)
            
            logger.info(f"添加倒计时项目: {item.name}")
            return True
        except Exception as e:
            logger.error(f"添加倒计时项目失败: {str(e)}")
            return False
    
    def _is_countdown_item_exists(self, item_id: str) -> bool:
        """
        检查倒计时项目是否存在
        
        Args:
            item_id: 项目ID
            
        Returns:
            bool: 倒计时项目是否存在
        """
        return self.get_countdown_item(item_id) is not None
    
    def _add_and_save_countdown_item(self, item: CountdownItem) -> None:
        """
        添加并保存倒计时项目
        
        Args:
            item: 倒计时项目
        """
        self.countdown_items.append(item)
        self._save_countdown_data()
    
    def update_countdown_item(self, item_id: str, item_data: Dict[str, Any]) -> bool:
        """
        更新倒计时项目
        
        Args:
            item_id: 项目ID
            item_data: 项目数据字典
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 查找并验证倒计时项目
            item = self._get_and_validate_countdown_item(item_id)
            if not item:
                return False
            
            # 更新项目字段并保存
            self._update_item_fields_and_save(item, item_data)
            
            logger.info(f"更新倒计时项目: {item.name}")
            return True
        except Exception as e:
            logger.error(f"更新倒计时项目失败: {str(e)}")
            return False
    
    def _get_and_validate_countdown_item(self, item_id: str):
        """
        获取并验证倒计时项目是否存在
        
        Args:
            item_id: 项目ID
            
        Returns:
            倒计时项目对象或None
        """
        item = self.get_countdown_item(item_id)
        if not item:
            logger.warning(f"倒计时项目未找到: {item_id}")
            return None
        return item
    
    def _update_item_fields_and_save(self, item, item_data: Dict[str, Any]) -> None:
        """
        更新项目字段并保存
        
        Args:
            item: 倒计时项目对象
            item_data: 项目数据字典
        """
        # 更新项目字段
        for key, value in item_data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        self._save_countdown_data()
    
    def remove_countdown_item(self, item_id: str) -> bool:
        """
        删除倒计时项目
        
        Args:
            item_id: 项目ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 查找并验证倒计时项目
            item = self._get_and_validate_countdown_item(item_id)
            if not item:
                return False
            
            # 删除并保存倒计时项目
            self._remove_and_save_countdown_item(item)
            
            logger.info(f"删除倒计时项目: {item.name}")
            return True
        except Exception as e:
            logger.error(f"删除倒计时项目失败: {str(e)}")
            return False
    
    def _remove_and_save_countdown_item(self, item) -> None:
        """
        删除并保存倒计时项目
        
        Args:
            item: 倒计时项目对象
        """
        self.countdown_items.remove(item)
        self._save_countdown_data()
    
    def calculate_countdown(self, target_date_str: str) -> Dict[str, Any]:
        """
        计算倒计时
        
        Args:
            target_date_str: 目标日期字符串 (YYYY-MM-DD)
            
        Returns:
            Dict[str, Any]: 倒计时信息
        """
        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            # 计算时间差
            time_diff = target_date - current_date
            
            # 根据时间差计算倒计时信息
            return self._build_countdown_info(time_diff)
        except Exception as e:
            logger.error(f"计算倒计时失败: {str(e)}")
            return self._get_error_countdown_info()
    
    def _build_countdown_info(self, time_diff) -> Dict[str, Any]:
        """
        构建倒计时信息
        
        Args:
            time_diff: 时间差对象
            
        Returns:
            Dict[str, Any]: 倒计时信息
        """
        # 如果目标日期已过，则返回负数
        if time_diff.total_seconds() < 0:
            return self._build_past_countdown_info(time_diff)
        else:
            return self._build_future_countdown_info(time_diff)
    
    def _build_past_countdown_info(self, time_diff) -> Dict[str, Any]:
        """
        构建过去时间的倒计时信息
        
        Args:
            time_diff: 时间差对象
            
        Returns:
            Dict[str, Any]: 倒计时信息
        """
        days = time_diff.days
        hours, remainder = divmod(abs(time_diff.seconds), 3600)
        minutes, _ = divmod(remainder, 60)
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "is_past": True,
            "message": f"已过期 {-days} 天"
        }
    
    def _build_future_countdown_info(self, time_diff) -> Dict[str, Any]:
        """
        构建未来时间的倒计时信息
        
        Args:
            time_diff: 时间差对象
            
        Returns:
            Dict[str, Any]: 倒计时信息
        """
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "is_past": False,
            "message": f"还有 {days} 天 {hours} 小时 {minutes} 分钟"
        }
    
    def _get_error_countdown_info(self) -> Dict[str, Any]:
        """
        获取错误情况下的倒计时信息
        
        Returns:
            Dict[str, Any]: 倒计时信息
        """
        return {
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "is_past": False,
            "message": "计算失败"
        }
    
    def get_all_countdowns(self) -> List[Dict[str, Any]]:
        """
        获取所有倒计时信息
        
        Returns:
            List[Dict[str, Any]]: 倒计时信息列表
        """
        return self._build_all_countdowns_list()
    
    def _build_all_countdowns_list(self) -> List[Dict[str, Any]]:
        """
        构建所有倒计时信息列表
        
        Returns:
            List[Dict[str, Any]]: 倒计时信息列表
        """
        countdowns = []
        for item in self.countdown_items:
            countdown_info = self._build_enhanced_countdown_info(item)
            countdowns.append(countdown_info)
        return countdowns
    
    def _build_enhanced_countdown_info(self, item: CountdownItem) -> Dict[str, Any]:
        """
        构建增强的倒计时信息
        
        Args:
            item: 倒计时项目
            
        Returns:
            Dict[str, Any]: 增强的倒计时信息
        """
        countdown_info = self.calculate_countdown(item.target_date)
        countdown_info["id"] = item.id
        countdown_info["name"] = item.name
        countdown_info["target_date"] = item.target_date
        countdown_info["description"] = item.description
        countdown_info["is_important"] = item.is_important
        return countdown_info
    
    def get_important_countdowns(self) -> List[Dict[str, Any]]:
        """
        获取重要倒计时信息
        
        Returns:
            List[Dict[str, Any]]: 重要倒计时信息列表
        """
        return self._build_important_countdowns_list()
    
    def _build_important_countdowns_list(self) -> List[Dict[str, Any]]:
        """
        构建重要倒计时信息列表
        
        Returns:
            List[Dict[str, Any]]: 重要倒计时信息列表
        """
        important_countdowns = []
        for item in self.countdown_items:
            if item.is_important:
                countdown_info = self._build_enhanced_countdown_info(item)
                important_countdowns.append(countdown_info)
        return important_countdowns
    
    def is_service_enabled(self) -> bool:
        """
        检查服务是否启用
        
        Returns:
            bool: 服务是否启用
        """
        return self.settings.enabled if self.settings else False