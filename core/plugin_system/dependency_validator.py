#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugin Dependency Validation System
Validates plugin compatibility and dependencies before loading
"""

import logging
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from packaging import version
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class DependencyType(Enum):
    """Types of dependencies"""
    PLUGIN = "plugin"
    SERVICE = "service"
    API = "api"
    SYSTEM = "system"
    PYTHON_PACKAGE = "python_package"


class CompatibilityLevel(Enum):
    """Compatibility levels"""
    COMPATIBLE = "compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass
class PluginDependency:
    """Plugin dependency definition"""
    name: str
    dependency_type: DependencyType
    version_constraint: str = "*"  # Semantic version constraint
    optional: bool = False
    description: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate dependency definition"""
        if not self.name:
            raise ValueError("Dependency name cannot be empty")
        
        # Validate version constraint format
        if not self._is_valid_version_constraint(self.version_constraint):
            raise ValueError(f"Invalid version constraint: {self.version_constraint}")
    
    def _is_valid_version_constraint(self, constraint: str) -> bool:
        """Validate version constraint format"""
        if constraint == "*":
            return True
        
        # Support common version constraint patterns
        patterns = [
            r"^\d+\.\d+\.\d+$",  # Exact version: 1.2.3
            r"^>=\d+\.\d+\.\d+$",  # Minimum version: >=1.2.3
            r"^<=\d+\.\d+\.\d+$",  # Maximum version: <=1.2.3
            r"^>\d+\.\d+\.\d+$",   # Greater than: >1.2.3
            r"^<\d+\.\d+\.\d+$",   # Less than: <1.2.3
            r"^~\d+\.\d+\.\d+$",   # Compatible release: ~1.2.3
            r"^\^\d+\.\d+\.\d+$",  # Caret range: ^1.2.3
        ]
        
        return any(re.match(pattern, constraint) for pattern in patterns)
    
    def is_satisfied_by(self, available_version: str) -> bool:
        """Check if dependency is satisfied by available version"""
        try:
            if self.version_constraint == "*":
                return True
            
            return self._check_version_constraint(available_version, self.version_constraint)
        except Exception:
            return False
    
    def _check_version_constraint(self, available: str, constraint: str) -> bool:
        """Check if available version satisfies constraint"""
        try:
            available_ver = version.parse(available)
            
            if constraint.startswith(">="):
                required_ver = version.parse(constraint[2:])
                return available_ver >= required_ver
            elif constraint.startswith("<="):
                required_ver = version.parse(constraint[2:])
                return available_ver <= required_ver
            elif constraint.startswith(">"):
                required_ver = version.parse(constraint[1:])
                return available_ver > required_ver
            elif constraint.startswith("<"):
                required_ver = version.parse(constraint[1:])
                return available_ver < required_ver
            elif constraint.startswith("~"):
                # Compatible release: ~1.2.3 means >=1.2.3, <1.3.0
                required_ver = version.parse(constraint[1:])
                next_minor = version.parse(f"{required_ver.major}.{required_ver.minor + 1}.0")
                return required_ver <= available_ver < next_minor
            elif constraint.startswith("^"):
                # Caret range: ^1.2.3 means >=1.2.3, <2.0.0
                required_ver = version.parse(constraint[1:])
                next_major = version.parse(f"{required_ver.major + 1}.0.0")
                return required_ver <= available_ver < next_major
            else:
                # Exact version
                required_ver = version.parse(constraint)
                return available_ver == required_ver
                
        except Exception:
            return False


@dataclass
class ValidationResult:
    """Dependency validation result"""
    is_valid: bool
    compatibility_level: CompatibilityLevel
    missing_dependencies: List[PluginDependency] = field(default_factory=list)
    version_conflicts: List[Tuple[PluginDependency, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        self.warnings.append(message)
    
    def add_error(self, message: str) -> None:
        """Add an error message"""
        self.errors.append(message)
        self.is_valid = False
    
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues that prevent loading"""
        return bool(self.errors or self.missing_dependencies or self.version_conflicts)


class DependencyValidator(BaseManager):
    """
    Plugin Dependency Validation System
    
    Validates plugin compatibility and dependencies before loading.
    Supports semantic versioning and complex dependency resolution.
    """
    
    # Signals
    validation_completed = pyqtSignal(str, bool)  # plugin_id, is_valid
    dependency_resolved = pyqtSignal(str, str)    # plugin_id, dependency_name
    validation_failed = pyqtSignal(str, str)      # plugin_id, error_message
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "DependencyValidator")
        
        # Available plugins and their versions
        self._available_plugins: Dict[str, str] = {}
        
        # Available services and their versions
        self._available_services: Dict[str, str] = {}
        
        # System capabilities
        self._system_capabilities: Dict[str, str] = {}
        
        # Validation cache
        self._validation_cache: Dict[str, ValidationResult] = {}
        
        # Dependency graph for circular dependency detection
        self._dependency_graph: Dict[str, Set[str]] = {}
        
        self.logger.info("Dependency Validator initialized")
    
    def initialize(self) -> bool:
        """Initialize the dependency validator"""
        try:
            self._detect_system_capabilities()
            self.logger.info("Dependency Validator initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Dependency Validator: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup validator resources"""
        try:
            self._validation_cache.clear()
            self._dependency_graph.clear()
            self.logger.info("Dependency Validator cleaned up")
        except Exception as e:
            self.logger.error(f"Error during validator cleanup: {e}")
    
    def register_plugin(self, plugin_id: str, plugin_version: str) -> None:
        """Register an available plugin"""
        self._available_plugins[plugin_id] = plugin_version
        self.logger.debug(f"Registered plugin: {plugin_id} v{plugin_version}")
    
    def register_service(self, service_name: str, service_version: str) -> None:
        """Register an available service"""
        self._available_services[service_name] = service_version
        self.logger.debug(f"Registered service: {service_name} v{service_version}")
    
    def validate_dependencies(self, plugin_id: str, dependencies: List[PluginDependency]) -> ValidationResult:
        """
        Validate plugin dependencies
        
        Args:
            plugin_id: ID of the plugin being validated
            dependencies: List of plugin dependencies
            
        Returns:
            ValidationResult with validation details
        """
        try:
            # Check cache first
            cache_key = f"{plugin_id}:{hash(tuple(dep.name for dep in dependencies))}"
            if cache_key in self._validation_cache:
                return self._validation_cache[cache_key]
            
            result = ValidationResult(is_valid=True, compatibility_level=CompatibilityLevel.COMPATIBLE)
            
            # Validate each dependency
            for dependency in dependencies:
                self._validate_single_dependency(dependency, result)
            
            # Check for circular dependencies
            self._check_circular_dependencies(plugin_id, dependencies, result)
            
            # Determine overall compatibility level
            self._determine_compatibility_level(result)
            
            # Cache result
            self._validation_cache[cache_key] = result
            
            # Emit signal
            self.validation_completed.emit(plugin_id, result.is_valid)
            
            if not result.is_valid:
                error_msg = "; ".join(result.errors)
                self.validation_failed.emit(plugin_id, error_msg)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating dependencies for {plugin_id}: {e}")
            result = ValidationResult(is_valid=False, compatibility_level=CompatibilityLevel.UNKNOWN)
            result.add_error(f"Validation error: {e}")
            return result
    
    def _validate_single_dependency(self, dependency: PluginDependency, result: ValidationResult) -> None:
        """Validate a single dependency"""
        try:
            if dependency.dependency_type == DependencyType.PLUGIN:
                self._validate_plugin_dependency(dependency, result)
            elif dependency.dependency_type == DependencyType.SERVICE:
                self._validate_service_dependency(dependency, result)
            elif dependency.dependency_type == DependencyType.SYSTEM:
                self._validate_system_dependency(dependency, result)
            elif dependency.dependency_type == DependencyType.API:
                self._validate_api_dependency(dependency, result)
            elif dependency.dependency_type == DependencyType.PYTHON_PACKAGE:
                self._validate_python_package_dependency(dependency, result)
            else:
                result.add_warning(f"Unknown dependency type: {dependency.dependency_type}")
                
        except Exception as e:
            if dependency.optional:
                result.add_warning(f"Optional dependency validation failed: {dependency.name} - {e}")
            else:
                result.add_error(f"Required dependency validation failed: {dependency.name} - {e}")
    
    def _validate_plugin_dependency(self, dependency: PluginDependency, result: ValidationResult) -> None:
        """Validate plugin dependency"""
        if dependency.name not in self._available_plugins:
            if dependency.optional:
                result.add_warning(f"Optional plugin dependency not found: {dependency.name}")
            else:
                result.missing_dependencies.append(dependency)
                result.add_error(f"Required plugin dependency not found: {dependency.name}")
            return
        
        available_version = self._available_plugins[dependency.name]
        if not dependency.is_satisfied_by(available_version):
            result.version_conflicts.append((dependency, available_version))
            result.add_error(
                f"Plugin version conflict: {dependency.name} requires {dependency.version_constraint}, "
                f"but {available_version} is available"
            )
    
    def _validate_service_dependency(self, dependency: PluginDependency, result: ValidationResult) -> None:
        """Validate service dependency"""
        if dependency.name not in self._available_services:
            if dependency.optional:
                result.add_warning(f"Optional service dependency not found: {dependency.name}")
            else:
                result.missing_dependencies.append(dependency)
                result.add_error(f"Required service dependency not found: {dependency.name}")
            return
        
        available_version = self._available_services[dependency.name]
        if not dependency.is_satisfied_by(available_version):
            result.version_conflicts.append((dependency, available_version))
            result.add_error(
                f"Service version conflict: {dependency.name} requires {dependency.version_constraint}, "
                f"but {available_version} is available"
            )

    def _validate_system_dependency(self, dependency: PluginDependency, result: ValidationResult) -> None:
        """Validate system dependency"""
        if dependency.name not in self._system_capabilities:
            if dependency.optional:
                result.add_warning(f"Optional system dependency not found: {dependency.name}")
            else:
                result.missing_dependencies.append(dependency)
                result.add_error(f"Required system capability not found: {dependency.name}")
            return

        available_version = self._system_capabilities[dependency.name]
        if not dependency.is_satisfied_by(available_version):
            result.version_conflicts.append((dependency, available_version))
            result.add_error(
                f"System capability version conflict: {dependency.name} requires {dependency.version_constraint}, "
                f"but {available_version} is available"
            )

    def _validate_api_dependency(self, dependency: PluginDependency, result: ValidationResult) -> None:
        """Validate API dependency"""
        # For now, assume all API dependencies are satisfied
        # This can be enhanced to check actual API availability
        result.add_warning(f"API dependency validation not fully implemented: {dependency.name}")

    def _validate_python_package_dependency(self, dependency: PluginDependency, result: ValidationResult) -> None:
        """Validate Python package dependency"""
        try:
            import importlib
            importlib.import_module(dependency.name)
            # Package is available, but we can't easily check version without additional logic
            result.add_warning(f"Python package dependency found but version not verified: {dependency.name}")
        except ImportError:
            if dependency.optional:
                result.add_warning(f"Optional Python package not found: {dependency.name}")
            else:
                result.missing_dependencies.append(dependency)
                result.add_error(f"Required Python package not found: {dependency.name}")

    def _check_circular_dependencies(self, plugin_id: str, dependencies: List[PluginDependency], result: ValidationResult) -> None:
        """Check for circular dependencies"""
        try:
            # Build dependency graph for this plugin
            plugin_deps = set()
            for dep in dependencies:
                if dep.dependency_type == DependencyType.PLUGIN:
                    plugin_deps.add(dep.name)

            self._dependency_graph[plugin_id] = plugin_deps

            # Check for cycles using DFS
            visited = set()
            rec_stack = set()

            def has_cycle(node: str) -> bool:
                if node in rec_stack:
                    return True
                if node in visited:
                    return False

                visited.add(node)
                rec_stack.add(node)

                for neighbor in self._dependency_graph.get(node, set()):
                    if has_cycle(neighbor):
                        return True

                rec_stack.remove(node)
                return False

            if has_cycle(plugin_id):
                result.add_error(f"Circular dependency detected involving plugin: {plugin_id}")

        except Exception as e:
            result.add_warning(f"Error checking circular dependencies: {e}")

    def _determine_compatibility_level(self, result: ValidationResult) -> None:
        """Determine overall compatibility level"""
        if result.errors or result.missing_dependencies:
            result.compatibility_level = CompatibilityLevel.INCOMPATIBLE
        elif result.version_conflicts:
            result.compatibility_level = CompatibilityLevel.PARTIALLY_COMPATIBLE
        elif result.warnings:
            result.compatibility_level = CompatibilityLevel.PARTIALLY_COMPATIBLE
        else:
            result.compatibility_level = CompatibilityLevel.COMPATIBLE

    def _detect_system_capabilities(self) -> None:
        """Detect available system capabilities"""
        try:
            import sys
            import platform

            # Python version
            self._system_capabilities["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

            # Operating system
            self._system_capabilities["os"] = platform.system().lower()
            self._system_capabilities["os_version"] = platform.release()

            # Architecture
            self._system_capabilities["arch"] = platform.machine()

            # Qt version (if available)
            try:
                from PyQt6.QtCore import QT_VERSION_STR
                self._system_capabilities["qt"] = QT_VERSION_STR
            except ImportError:
                pass

            self.logger.debug(f"Detected system capabilities: {self._system_capabilities}")

        except Exception as e:
            self.logger.error(f"Error detecting system capabilities: {e}")

    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get the current dependency graph"""
        return self._dependency_graph.copy()

    def clear_validation_cache(self) -> None:
        """Clear the validation cache"""
        self._validation_cache.clear()
        self.logger.debug("Validation cache cleared")

    def get_validation_statistics(self) -> Dict[str, int]:
        """Get validation statistics"""
        return {
            "total_validations": len(self._validation_cache),
            "available_plugins": len(self._available_plugins),
            "available_services": len(self._available_services),
            "system_capabilities": len(self._system_capabilities)
        }
