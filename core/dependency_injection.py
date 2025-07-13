#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 依赖注入容器
提供完整的依赖注入和控制反转功能

该模块提供了完整的依赖注入功能，包括：
- 服务注册和解析
- 生命周期管理（单例、瞬态、作用域）
- 循环依赖检测和解决
- 接口绑定和实现
- 装饰器支持
- 配置驱动的依赖注入
"""

import logging
import threading
import inspect
from typing import Dict, Any, Optional, Type, TypeVar, Callable, List, Union, Protocol
from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
from weakref import WeakValueDictionary

T = TypeVar('T')


class ServiceLifetime(Enum):
    """服务生命周期"""
    SINGLETON = auto()  # 单例模式
    TRANSIENT = auto()  # 瞬态模式（每次创建新实例）
    SCOPED = auto()     # 作用域模式（在特定作用域内单例）


@dataclass
class ServiceDescriptor:
    """
    服务描述符
    
    Attributes:
        service_type: 服务类型（接口或类）
        implementation_type: 实现类型
        lifetime: 生命周期
        factory: 工厂函数
        instance: 单例实例
        dependencies: 依赖列表
    """
    service_type: Type
    implementation_type: Optional[Type] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    dependencies: List[Type] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class CircularDependencyError(Exception):
    """循环依赖错误"""
    pass


class ServiceNotFoundError(Exception):
    """服务未找到错误"""
    pass


class DependencyInjectionContainer:
    """
    依赖注入容器
    
    提供完整的依赖注入功能，支持多种生命周期管理和循环依赖检测。
    """
    
    def __init__(self):
        """初始化依赖注入容器"""
        self.logger = logging.getLogger(f'{__name__}.DependencyInjectionContainer')
        
        # 服务注册表
        self._services: Dict[Type, ServiceDescriptor] = {}
        
        # 单例实例缓存
        self._singletons: Dict[Type, Any] = {}
        
        # 作用域实例缓存
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        
        # 当前作用域
        self._current_scope: Optional[str] = None
        
        # 线程锁
        self._lock = threading.RLock()
        
        # 解析栈（用于循环依赖检测）
        self._resolution_stack: List[Type] = []
        
        # 弱引用缓存（避免内存泄漏）
        self._weak_cache: WeakValueDictionary = WeakValueDictionary()
        
        self.logger.info("依赖注入容器初始化完成")
    
    def register_singleton(self, service_type: Type[T], implementation_type: Optional[Type[T]] = None) -> 'DependencyInjectionContainer':
        """
        注册单例服务
        
        Args:
            service_type: 服务类型
            implementation_type: 实现类型，如果为None则使用service_type
            
        Returns:
            容器实例（支持链式调用）
        """
        return self._register_service(service_type, implementation_type, ServiceLifetime.SINGLETON)
    
    def register_transient(self, service_type: Type[T], implementation_type: Optional[Type[T]] = None) -> 'DependencyInjectionContainer':
        """
        注册瞬态服务
        
        Args:
            service_type: 服务类型
            implementation_type: 实现类型，如果为None则使用service_type
            
        Returns:
            容器实例（支持链式调用）
        """
        return self._register_service(service_type, implementation_type, ServiceLifetime.TRANSIENT)
    
    def register_scoped(self, service_type: Type[T], implementation_type: Optional[Type[T]] = None) -> 'DependencyInjectionContainer':
        """
        注册作用域服务
        
        Args:
            service_type: 服务类型
            implementation_type: 实现类型，如果为None则使用service_type
            
        Returns:
            容器实例（支持链式调用）
        """
        return self._register_service(service_type, implementation_type, ServiceLifetime.SCOPED)
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T], lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> 'DependencyInjectionContainer':
        """
        注册工厂函数
        
        Args:
            service_type: 服务类型
            factory: 工厂函数
            lifetime: 生命周期
            
        Returns:
            容器实例（支持链式调用）
        """
        with self._lock:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                factory=factory,
                lifetime=lifetime
            )
            self._services[service_type] = descriptor
            
            self.logger.debug(f"注册工厂服务: {service_type.__name__} ({lifetime.name})")
            return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'DependencyInjectionContainer':
        """
        注册实例
        
        Args:
            service_type: 服务类型
            instance: 实例对象
            
        Returns:
            容器实例（支持链式调用）
        """
        with self._lock:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                instance=instance,
                lifetime=ServiceLifetime.SINGLETON
            )
            self._services[service_type] = descriptor
            self._singletons[service_type] = instance
            
            self.logger.debug(f"注册实例: {service_type.__name__}")
            return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        解析服务
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
            
        Raises:
            ServiceNotFoundError: 服务未找到
            CircularDependencyError: 循环依赖
        """
        with self._lock:
            try:
                # 检查循环依赖
                if service_type in self._resolution_stack:
                    cycle = " -> ".join([t.__name__ for t in self._resolution_stack[self._resolution_stack.index(service_type):]])
                    raise CircularDependencyError(f"检测到循环依赖: {cycle} -> {service_type.__name__}")
                
                self._resolution_stack.append(service_type)
                
                # 解析服务
                instance = self._resolve_service(service_type)
                
                return instance
                
            finally:
                # 清理解析栈
                if service_type in self._resolution_stack:
                    self._resolution_stack.remove(service_type)
    
    def try_resolve(self, service_type: Type[T]) -> Optional[T]:
        """
        尝试解析服务（不抛出异常）
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例或None
        """
        try:
            return self.resolve(service_type)
        except (ServiceNotFoundError, CircularDependencyError) as e:
            self.logger.debug(f"解析服务失败: {service_type.__name__} - {e}")
            return None
    
    def is_registered(self, service_type: Type) -> bool:
        """
        检查服务是否已注册
        
        Args:
            service_type: 服务类型
            
        Returns:
            是否已注册
        """
        return service_type in self._services
    
    def create_scope(self, scope_name: str) -> 'ServiceScope':
        """
        创建服务作用域
        
        Args:
            scope_name: 作用域名称
            
        Returns:
            服务作用域实例
        """
        return ServiceScope(self, scope_name)
    
    def _register_service(self, service_type: Type[T], implementation_type: Optional[Type[T]], lifetime: ServiceLifetime) -> 'DependencyInjectionContainer':
        """内部服务注册方法"""
        with self._lock:
            impl_type = implementation_type or service_type
            
            # 分析依赖
            dependencies = self._analyze_dependencies(impl_type)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifetime=lifetime,
                dependencies=dependencies
            )
            
            self._services[service_type] = descriptor
            
            self.logger.debug(f"注册服务: {service_type.__name__} -> {impl_type.__name__} ({lifetime.name})")
            return self
    
    def _resolve_service(self, service_type: Type[T]) -> T:
        """内部服务解析方法"""
        # 检查是否已注册
        if service_type not in self._services:
            raise ServiceNotFoundError(f"服务未注册: {service_type.__name__}")
        
        descriptor = self._services[service_type]
        
        # 处理已有实例
        if descriptor.instance is not None:
            return descriptor.instance
        
        # 处理单例
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
        
        # 处理作用域
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            if self._current_scope and self._current_scope in self._scoped_instances:
                scoped_cache = self._scoped_instances[self._current_scope]
                if service_type in scoped_cache:
                    return scoped_cache[service_type]
        
        # 创建实例
        instance = self._create_instance(descriptor)
        
        # 缓存实例
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            self._singletons[service_type] = instance
        elif descriptor.lifetime == ServiceLifetime.SCOPED and self._current_scope:
            if self._current_scope not in self._scoped_instances:
                self._scoped_instances[self._current_scope] = {}
            self._scoped_instances[self._current_scope][service_type] = instance
        
        return instance
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        try:
            # 使用工厂函数
            if descriptor.factory:
                return descriptor.factory()
            
            # 使用构造函数
            if descriptor.implementation_type:
                # 解析构造函数依赖:
                # 解析构造函数依赖
                constructor_args = self._resolve_constructor_dependencies(descriptor.implementation_type)
                return descriptor.implementation_type(*constructor_args)
            
            raise ValueError(f"无法创建实例: {descriptor.service_type.__name__}")
            
        except Exception as e:
            self.logger.error(f"创建实例失败: {descriptor.service_type.__name__} - {e}")
            raise
    
    def _analyze_dependencies(self, implementation_type: Type) -> List[Type]:
        """分析类型的依赖"""
        dependencies = []
        
        try:
            # 获取构造函数签名
            signature = inspect.signature(implementation_type.__init__)
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                # 获取类型注解
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
            
        except Exception as e:
            self.logger.debug(f"分析依赖失败: {implementation_type.__name__} - {e}")
        
        return dependencies
    
    def _resolve_constructor_dependencies(self, implementation_type: Type) -> List[Any]:
        """解析构造函数依赖"""
        args = []
        
        try:
            signature = inspect.signature(implementation_type.__init__)
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                # 解析依赖
                if param.annotation != inspect.Parameter.empty:
                    dependency = self.resolve(param.annotation)
                    args.append(dependency)
                elif param.default != inspect.Parameter.empty:
                    # 使用默认值
                    args.append(param.default)
                else:
                    # 尝试按名称解析
                    self.logger.warning(f"无法解析参数: {param_name} in {implementation_type.__name__}")
            
        except Exception as e:
            self.logger.error(f"解析构造函数依赖失败: {implementation_type.__name__} - {e}")
        
        return args
    
    def cleanup(self) -> None:
        """清理容器资源"""
        with self._lock:
            # 清理单例实例
            for instance in self._singletons.values():
                if hasattr(instance, 'cleanup'):
                    try:
                        instance.cleanup()
                    except Exception as e:
                        self.logger.error(f"清理实例失败: {e}")
            
            # 清理作用域实例
            for scope_instances in self._scoped_instances.values():
                for instance in scope_instances.values():
                    if hasattr(instance, 'cleanup'):
                        try:
                            instance.cleanup()
                        except Exception as e:
                            self.logger.error(f"清理作用域实例失败: {e}")
            
            # 清空缓存
            self._services.clear()
            self._singletons.clear()
            self._scoped_instances.clear()
            self._weak_cache.clear()
            
            self.logger.info("依赖注入容器清理完成")


class ServiceScope:
    """
    服务作用域
    
    用于管理作用域内的服务实例生命周期。
    """
    
    def __init__(self, container: DependencyInjectionContainer, scope_name: str):
        """
        初始化服务作用域
        
        Args:
            container: 依赖注入容器
            scope_name: 作用域名称
        """
        self.container = container
        self.scope_name = scope_name
        self._previous_scope = None
    
    def __enter__(self) -> 'ServiceScope':
        """进入作用域"""
        self._previous_scope = self.container._current_scope
        self.container._current_scope = self.scope_name
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出作用域"""
        # 清理作用域实例
        if self.scope_name in self.container._scoped_instances:
            scope_instances = self.container._scoped_instances[self.scope_name]
            for instance in scope_instances.values():
                if hasattr(instance, 'cleanup'):
                    try:
                        instance.cleanup()
                    except Exception as e:
                        self.container.logger.error(f"清理作用域实例失败: {e}")
            
            del self.container._scoped_instances[self.scope_name]
        
        # 恢复之前的作用域
        self.container._current_scope = self._previous_scope


# 全局容器实例
_global_container = DependencyInjectionContainer()


def get_container() -> DependencyInjectionContainer:
    """获取全局依赖注入容器"""
    return _global_container


def inject(service_type: Type[T]) -> T:
    """
    依赖注入装饰器辅助函数
    
    Args:
        service_type: 服务类型
        
    Returns:
        服务实例
    """
    return _global_container.resolve(service_type)


def injectable(cls: Type[T]) -> Type[T]:
    """
    可注入类装饰器
    
    Args:
        cls: 要装饰的类
        
    Returns:
        装饰后的类
    """
    # 自动注册为瞬态服务
    _global_container.register_transient(cls)
    return cls
