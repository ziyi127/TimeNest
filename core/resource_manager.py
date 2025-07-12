#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 学习资源管理器
管理学习资料、笔记、文档和在线资源
"""

import logging
import os
import hashlib
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class ResourceType(Enum):
    """资源类型"""
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    LINK = "link"
    NOTE = "note"
    BOOK = "book"
    EXERCISE = "exercise"


class ResourceStatus(Enum):
    """资源状态"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    BROKEN = "broken"


@dataclass
class ResourceTag:
    """资源标签"""
    name: str
    color: str = "#007ACC"
    description: str = ""


@dataclass
class StudyResource:
    """学习资源"""
    id: str
    title: str
    resource_type: ResourceType
    subject: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    file_size: int = 0  # 字节
    file_hash: Optional[str] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    rating: int = 0  # 1-5星评分
    notes: str = ""
    related_resources: Set[str] = field(default_factory=set)


@dataclass
class ResourceCollection:
    """资源集合"""
    id: str
    name: str
    description: str
    subject: str
    resource_ids: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    is_public: bool = False


@dataclass
class StudyNote:
    """学习笔记"""
    id: str
    title: str
    content: str
    subject: str
    resource_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    word_count: int = 0
    is_favorite: bool = False


class ResourceManager(BaseManager):
    """学习资源管理器"""
    
    # 信号定义
    resource_added = pyqtSignal(str)  # 资源ID
    resource_updated = pyqtSignal(str)
    resource_accessed = pyqtSignal(str)
    collection_created = pyqtSignal(str)  # 集合ID
    note_created = pyqtSignal(str)  # 笔记ID
    resource_broken = pyqtSignal(str, str)  # 资源ID, 错误信息
    
    def __init__(self, config_manager=None):
        super().__init__("ResourceManager", config_manager)
        
        # 数据存储
        self.resources: Dict[str, StudyResource] = {}
        self.collections: Dict[str, ResourceCollection] = {}
        self.notes: Dict[str, StudyNote] = {}
        self.tags: Dict[str, ResourceTag] = {}
        
        # 资源目录
        self.resource_base_path = Path("resources")
        self.resource_base_path.mkdir(exist_ok=True)
        
        # 支持的文件类型
        self.supported_extensions = {
            ResourceType.DOCUMENT: {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'},
            ResourceType.VIDEO: {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'},
            ResourceType.AUDIO: {'.mp3', '.wav', '.flac', '.aac', '.ogg'},
            ResourceType.IMAGE: {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'}
        }
        
        # 初始化默认标签
        self._init_default_tags()
        
        self.logger.info("学习资源管理器初始化完成")
    
    def _init_default_tags(self):
        """初始化默认标签"""
        try:
            default_tags = [
                ResourceTag("重要", "#FF4444", "重要的学习资源"),
                ResourceTag("复习", "#44FF44", "用于复习的资源"),
                ResourceTag("练习", "#4444FF", "练习题和习题"),
                ResourceTag("参考", "#FFAA44", "参考资料"),
                ResourceTag("笔记", "#AA44FF", "个人笔记"),
                ResourceTag("视频", "#44AAFF", "视频教程"),
                ResourceTag("文档", "#AAAA44", "文档资料")
            ]
            
            for tag in default_tags:
                self.tags[tag.name] = tag
                
        except Exception as e:
            self.logger.error(f"初始化默认标签失败: {e}")
    
    def add_resource(self, title: str, resource_type: ResourceType, subject: str,
                    file_path: str = None, url: str = None, description: str = "",
                    tags: Set[str] = None) -> str:
        """添加学习资源"""
        try:
            resource_id = f"res_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 验证资源
            if file_path:
                file_path = Path(file_path)
                if not file_path.exists():
                    raise FileNotFoundError(f"文件不存在: {file_path}")
                
                # 计算文件哈希
                file_hash = self._calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
                
                # 检查重复文件
                existing_resource = self._find_resource_by_hash(file_hash)
                if existing_resource:
                    self.logger.warning(f"文件已存在: {existing_resource.title}")
                    return existing_resource.id
            else:
                file_hash = None
                file_size = 0
            
            # 创建资源
            resource = StudyResource(
                id=resource_id,
                title=title,
                resource_type=resource_type,
                subject=subject,
                file_path=str(file_path) if file_path else None,
                url=url,
                description=description,
                tags=tags or set(),
                file_size=file_size,
                file_hash=file_hash
            )
            
            self.resources[resource_id] = resource
            self.resource_added.emit(resource_id)
            
            self.logger.info(f"学习资源已添加: {title}")
            return resource_id
            
        except Exception as e:
            self.logger.error(f"添加学习资源失败: {e}")
            return ""
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            self.logger.error(f"计算文件哈希失败: {e}")
            return ""
    
    def _find_resource_by_hash(self, file_hash: str) -> Optional[StudyResource]:
        """根据哈希值查找资源"""
        try:
            for resource in self.resources.values():
                if resource.file_hash == file_hash:
                    return resource
            return None
            
        except Exception as e:
            self.logger.error(f"查找资源失败: {e}")
            return None
    
    def access_resource(self, resource_id: str) -> bool:
        """访问资源"""
        try:
            if resource_id not in self.resources:
                return False
            
            resource = self.resources[resource_id]
            
            # 检查资源可用性
            if resource.file_path:
                if not Path(resource.file_path).exists():
                    resource.status = ResourceStatus.BROKEN
                    self.resource_broken.emit(resource_id, "文件不存在")
                    return False
            
            # 更新访问记录
            resource.access_count += 1
            resource.last_accessed = datetime.now()
            resource.status = ResourceStatus.IN_USE
            
            self.resource_accessed.emit(resource_id)
            self.logger.info(f"资源已访问: {resource.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"访问资源失败: {e}")
            return False
    
    def create_collection(self, name: str, description: str, subject: str,
                         resource_ids: Set[str] = None, tags: Set[str] = None) -> str:
        """创建资源集合"""
        try:
            collection_id = f"col_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            collection = ResourceCollection(
                id=collection_id,
                name=name,
                description=description,
                subject=subject,
                resource_ids=resource_ids or set(),
                tags=tags or set()
            )
            
            self.collections[collection_id] = collection
            self.collection_created.emit(collection_id)
            
            self.logger.info(f"资源集合已创建: {name}")
            return collection_id
            
        except Exception as e:
            self.logger.error(f"创建资源集合失败: {e}")
            return ""
    
    def add_note(self, title: str, content: str, subject: str,
                resource_id: str = None, tags: Set[str] = None) -> str:
        """添加学习笔记"""
        try:
            note_id = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 计算字数
            word_count = len(content.split())
            
            note = StudyNote(
                id=note_id,
                title=title,
                content=content,
                subject=subject,
                resource_id=resource_id,
                tags=tags or set(),
                word_count=word_count
            )
            
            self.notes[note_id] = note
            self.note_created.emit(note_id)
            
            self.logger.info(f"学习笔记已添加: {title}")
            return note_id
            
        except Exception as e:
            self.logger.error(f"添加学习笔记失败: {e}")
            return ""
    
    def search_resources(self, query: str, resource_type: ResourceType = None,
                        subject: str = None, tags: Set[str] = None) -> List[StudyResource]:
        """搜索学习资源"""
        try:
            results = []
            query_lower = query.lower()
            
            for resource in self.resources.values():
                # 检查类型过滤
                if resource_type and resource.resource_type != resource_type:
                    continue
                
                # 检查科目过滤
                if subject and resource.subject != subject:
                    continue
                
                # 检查标签过滤
                if tags and not tags.intersection(resource.tags):
                    continue
                
                # 检查关键词匹配
                if (query_lower in resource.title.lower() or
                    query_lower in resource.description.lower() or
                    any(query_lower in tag.lower() for tag in resource.tags)):
                    results.append(resource)
            
            # 按相关性排序（简单实现）
            results.sort(key=lambda r: (
                r.rating,  # 评分
                r.access_count,  # 访问次数
                -abs((datetime.now() - r.created_at).days)  # 创建时间
            ), reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"搜索学习资源失败: {e}")
            return []
    
    def get_resource_recommendations(self, subject: str = None,
                                   current_resource_id: str = None) -> List[StudyResource]:
        """获取资源推荐"""
        try:
            recommendations = []
            
            # 基于科目推荐
            if subject:
                subject_resources = [r for r in self.resources.values() 
                                   if r.subject == subject and r.rating >= 3]
                recommendations.extend(subject_resources[:5])
            
            # 基于当前资源推荐相关资源
            if current_resource_id and current_resource_id in self.resources:
                current_resource = self.resources[current_resource_id]
                
                # 查找相关资源
                for resource_id in current_resource.related_resources:
                    if resource_id in self.resources:
                        recommendations.append(self.resources[resource_id])
                
                # 基于标签推荐
                for resource in self.resources.values():
                    if (resource.id != current_resource_id and
                        resource.tags.intersection(current_resource.tags)):
                        recommendations.append(resource)
            
            # 去重并排序
            unique_recommendations = list({r.id: r for r in recommendations}.values())
            unique_recommendations.sort(key=lambda r: (r.rating, r.access_count), reverse=True)
            
            return unique_recommendations[:10]
            
        except Exception as e:
            self.logger.error(f"获取资源推荐失败: {e}")
            return []
    
    def get_resource_statistics(self) -> Dict[str, Any]:
        """获取资源统计信息"""
        try:
            # 基本统计
            total_resources = len(self.resources)
            total_collections = len(self.collections)
            total_notes = len(self.notes)
            
            # 类型分布
            type_distribution = {}
            for resource in self.resources.values():
                type_name = resource.resource_type.value
                type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
            
            # 科目分布
            subject_distribution = {}
            for resource in self.resources.values():
                subject = resource.subject
                subject_distribution[subject] = subject_distribution.get(subject, 0) + 1
            
            # 状态分布
            status_distribution = {}
            for resource in self.resources.values():
                status = resource.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # 访问统计
            total_accesses = sum(r.access_count for r in self.resources.values())
            most_accessed = max(self.resources.values(), key=lambda r: r.access_count, default=None)
            
            # 评分统计
            rated_resources = [r for r in self.resources.values() if r.rating > 0]
            avg_rating = sum(r.rating for r in rated_resources) / len(rated_resources) if rated_resources else 0
            
            # 存储统计
            total_file_size = sum(r.file_size for r in self.resources.values() if r.file_size)
            
            return {
                'total_resources': total_resources,
                'total_collections': total_collections,
                'total_notes': total_notes,
                'type_distribution': type_distribution,
                'subject_distribution': subject_distribution,
                'status_distribution': status_distribution,
                'total_accesses': total_accesses,
                'most_accessed': most_accessed.title if most_accessed else None,
                'average_rating': round(avg_rating, 2),
                'total_file_size_mb': round(total_file_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.error(f"获取资源统计失败: {e}")
            return {}
    
    def organize_resources(self) -> Dict[str, Any]:
        """整理资源"""
        try:
            organized = 0
            issues_found = []
            
            for resource in self.resources.values():
                # 检查文件完整性
                if resource.file_path:
                    file_path = Path(resource.file_path)
                    if not file_path.exists():
                        resource.status = ResourceStatus.BROKEN
                        issues_found.append(f"文件不存在: {resource.title}")
                    elif resource.file_hash:
                        # 验证文件哈希
                        current_hash = self._calculate_file_hash(file_path)
                        if current_hash != resource.file_hash:
                            issues_found.append(f"文件已修改: {resource.title}")
                
                # 更新状态
                if resource.status == ResourceStatus.IN_USE:
                    # 如果长时间未访问，改为可用状态
                    if (resource.last_accessed and 
                        datetime.now() - resource.last_accessed > timedelta(hours=1)):
                        resource.status = ResourceStatus.AVAILABLE
                        organized += 1
            
            return {
                'organized_count': organized,
                'issues_found': issues_found,
                'total_checked': len(self.resources)
            }
            
        except Exception as e:
            self.logger.error(f"整理资源失败: {e}")
            return {'error': str(e)}
    
    def export_resource_list(self, format_type: str = "json") -> str:
        """导出资源列表"""
        try:
            import json
            
            export_data = {
                'resources': [],
                'collections': [],
                'notes': [],
                'export_time': datetime.now().isoformat()
            }
            
            # 导出资源
            for resource in self.resources.values():
                export_data['resources'].append({
                    'id': resource.id,
                    'title': resource.title,
                    'type': resource.resource_type.value,
                    'subject': resource.subject,
                    'description': resource.description,
                    'tags': list(resource.tags),
                    'rating': resource.rating,
                    'access_count': resource.access_count,
                    'created_at': resource.created_at.isoformat()
                })
            
            # 导出集合
            for collection in self.collections.values():
                export_data['collections'].append({
                    'id': collection.id,
                    'name': collection.name,
                    'description': collection.description,
                    'subject': collection.subject,
                    'resource_count': len(collection.resource_ids),
                    'created_at': collection.created_at.isoformat()
                })
            
            # 导出笔记
            for note in self.notes.values():
                export_data['notes'].append({
                    'id': note.id,
                    'title': note.title,
                    'subject': note.subject,
                    'word_count': note.word_count,
                    'tags': list(note.tags),
                    'created_at': note.created_at.isoformat()
                })
            
            # 保存到文件
            export_file = f"resource_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"资源列表已导出: {export_file}")
            return export_file
            
        except Exception as e:
            self.logger.error(f"导出资源列表失败: {e}")
            return ""
    
    def cleanup(self):
        """清理资源"""
        try:
            super().cleanup()
            self.logger.info("学习资源管理器已清理")
            
        except Exception as e:
            self.logger.error(f"清理学习资源管理器失败: {e}")
