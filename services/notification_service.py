"""
通知服务
提供通知管理相关的业务逻辑处理
<<<<<<< HEAD
作者: TimeNest团队
创建日期: 2024-01-01
版本: 1.0.0
描述: 提供通知管理相关的业务逻辑处理，包括创建、更新、删除、查询通知等功能
=======
>>>>>>> 3ebc1a0d5b5d68fcc8be71ad4e1441605fb57214
"""

import uuid
import datetime
from typing import List, Optional
from models.notification import Notification
from utils.logger import get_service_logger
from utils.exceptions import ValidationException, NotFoundException
from data_access.json_data_access import JSONDataAccess

# 初始化日志记录器
logger = get_service_logger("notification_service")


class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        """初始化通知服务"""
        self.data_access = JSONDataAccess()
        self.notifications: List[Notification] = []
        self._load_notifications()
        logger.info("NotificationService initialized")
    
    def _load_notifications(self):
        """加载通知数据"""
        try:
            data = self.data_access.read_json("notifications.json")
            if data and "notifications" in data:
                self.notifications = [
                    Notification.from_dict(notification_data) 
                    for notification_data in data["notifications"]
                ]
            logger.info(f"加载了 {len(self.notifications)} 条通知")
        except Exception as e:
            logger.error(f"加载通知数据失败: {str(e)}")
            self.notifications = []
    
    def _save_notifications(self):
        """保存通知数据"""
        try:
            data = {
                "notifications": [notification.to_dict() for notification in self.notifications]
            }
            self.data_access.write_json("notifications.json", data)
            logger.debug("通知数据已保存")
        except Exception as e:
            logger.error(f"保存通知数据失败: {str(e)}")
            raise ValidationException("保存通知数据失败")
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())
    
    def create_notification(self, title: str, content: str, priority: str = "normal", 
                          category: str = "general", target_users: Optional[List[str]] = None) -> Notification:
        """
        创建通知
        
        Args:
            title: 通知标题
            content: 通知内容
            priority: 通知优先级 ("low", "normal", "high")
            category: 通知分类
            target_users: 目标用户列表，空列表表示所有用户
            
        Returns:
            创建的通知对象
            
        Raises:
            ValidationException: 数据验证失败
        """
        logger.info(f"创建通知: {title}")
        
        # 验证数据
        if not title or not isinstance(title, str) or len(title.strip()) == 0:
            logger.warning("通知标题不能为空")
            raise ValidationException("通知标题不能为空")
        
        if not content or not isinstance(content, str) or len(content.strip()) == 0:
            logger.warning("通知内容不能为空")
            raise ValidationException("通知内容不能为空")
        
        if priority not in ["low", "normal", "high"]:
            logger.warning(f"无效的通知优先级: {priority}")
            raise ValidationException("通知优先级必须是 'low', 'normal' 或 'high'")
        
        # 创建通知对象
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        notification = Notification(
            id=self._generate_id(),
            title=title.strip(),
            content=content.strip(),
            created_at=current_time,
            priority=priority,
            category=category,
            target_users=target_users or []
        )
        
        # 添加到通知列表
        self.notifications.append(notification)
        
        # 保存数据
        self._save_notifications()
        
        logger.info(f"通知 {notification.id} 创建成功")
        return notification
    
    def update_notification(self, notification_id: str, title: Optional[str] = None, content: Optional[str] = None,
                          priority: Optional[str] = None, category: Optional[str] = None, is_read: Optional[bool] = None) -> Notification:
        """
        更新通知
        
        Args:
            notification_id: 通知ID
            title: 通知标题（可选）
            content: 通知内容（可选）
            priority: 通知优先级（可选）
            category: 通知分类（可选）
            is_read: 是否已读（可选）
            
        Returns:
            更新后的通知对象
            
        Raises:
            ValidationException: 数据验证失败
            NotFoundException: 通知未找到
        """
        logger.info(f"更新通知: {notification_id}")
        
        # 查找通知
        notification = self.get_notification_by_id(notification_id)
        if not notification:
            logger.warning(f"通知 {notification_id} 未找到")
            raise NotFoundException(f"通知 {notification_id} 未找到")
        
        # 更新字段
        if title is not None:
            if not isinstance(title, str) or len(title.strip()) == 0:
                logger.warning("通知标题不能为空")
                raise ValidationException("通知标题不能为空")
            notification.title = title.strip()
        
        if content is not None:
            if not isinstance(content, str) or len(content.strip()) == 0:
                logger.warning("通知内容不能为空")
                raise ValidationException("通知内容不能为空")
            notification.content = content.strip()
        
        if priority is not None:
            if priority not in ["low", "normal", "high"]:
                logger.warning(f"无效的通知优先级: {priority}")
                raise ValidationException("通知优先级必须是 'low', 'normal' 或 'high'")
            notification.priority = priority
        
        if category is not None:
            notification.category = category
        
        if is_read is not None:
            notification.is_read = is_read
        
        # 保存数据
        self._save_notifications()
        
        logger.info(f"通知 {notification_id} 更新成功")
        return notification
    
    def delete_notification(self, notification_id: str) -> bool:
        """
        删除通知
        
        Args:
            notification_id: 通知ID
            
        Returns:
            是否删除成功
            
        Raises:
            NotFoundException: 通知未找到
        """
        logger.info(f"删除通知: {notification_id}")
        
        # 查找通知索引
        notification_index = self._find_notification_index(notification_id)
        if notification_index == -1:
            logger.warning(f"通知 {notification_id} 未找到")
            raise NotFoundException(f"通知 {notification_id} 未找到")
        
        # 删除通知
        del self.notifications[notification_index]
        
        # 保存数据
        self._save_notifications()
        
        logger.info(f"通知 {notification_id} 删除成功")
        return True
    
    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """
        根据ID获取通知
        
        Args:
            notification_id: 通知ID
            
        Returns:
            通知对象，如果未找到则返回None
        """
        logger.debug(f"获取通知: {notification_id}")
        
        for notification in self.notifications:
            if notification.id == notification_id:
                logger.debug(f"找到通知: {notification_id}")
                return notification
        
        logger.debug(f"未找到通知: {notification_id}")
        return None
    
    def get_all_notifications(self) -> List[Notification]:
        """
        获取所有通知
        
        Returns:
            通知列表
        """
        logger.debug("获取所有通知")
        return self.notifications.copy()
    
    def get_unread_notifications(self) -> List[Notification]:
        """
        获取未读通知
        
        Returns:
            未读通知列表
        """
        logger.debug("获取未读通知")
        return [notification for notification in self.notifications if not notification.is_read]
    
    def get_notifications_by_category(self, category: str) -> List[Notification]:
        """
        根据分类获取通知
        
        Args:
            category: 通知分类
            
        Returns:
            指定分类的通知列表
        """
        logger.debug(f"获取分类通知: {category}")
        return [notification for notification in self.notifications if notification.category == category]
    
    def mark_as_read(self, notification_id: str) -> Notification:
        """
        标记通知为已读
        
        Args:
            notification_id: 通知ID
            
        Returns:
            更新后的通知对象
            
        Raises:
            NotFoundException: 通知未找到
        """
        logger.info(f"标记通知为已读: {notification_id}")
        return self.update_notification(notification_id, is_read=True)
    
    def mark_all_as_read(self) -> int:
        """
        标记所有通知为已读
        
        Returns:
            更新的通知数量
        """
        logger.info("标记所有通知为已读")
        
        count = 0
        for notification in self.notifications:
            if not notification.is_read:
                notification.is_read = True
                count += 1
        
        if count > 0:
            # 保存数据
            self._save_notifications()
            logger.info(f"标记了 {count} 条通知为已读")
        
        return count
    
    def _find_notification_index(self, notification_id: str) -> int:
        """
        查找通知在列表中的索引
        
        Args:
            notification_id: 通知ID
            
        Returns:
            通知索引，如果未找到则返回-1
        """
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                return i
        return -1