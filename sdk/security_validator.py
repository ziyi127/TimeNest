#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Validator for Plugin SDK
Provides security validation with optional MD5 bypass for development builds
"""

import logging
import hashlib
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from pathlib import Path


class ValidationFlags(Flag):
    """Security validation flags"""
    NONE = 0
    MD5_VALIDATION = auto()
    CODE_SCANNING = auto()
    PERMISSION_CHECK = auto()
    SANDBOX_VALIDATION = auto()
    POWERSHELL_VALIDATION = auto()
    DEVELOPMENT_BYPASS = auto()
    
    # Preset combinations
    STRICT = MD5_VALIDATION | CODE_SCANNING | PERMISSION_CHECK | SANDBOX_VALIDATION | POWERSHELL_VALIDATION
    NORMAL = MD5_VALIDATION | CODE_SCANNING | PERMISSION_CHECK
    DEVELOPMENT = CODE_SCANNING | PERMISSION_CHECK | DEVELOPMENT_BYPASS


class SecurityLevel(Enum):
    """Security levels"""
    SAFE = "safe"
    WARNING = "warning"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"


@dataclass
class SecurityIssue:
    """Security issue description"""
    level: SecurityLevel
    category: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: str = ""


@dataclass
class ValidationResult:
    """Security validation result"""
    is_safe: bool
    security_level: SecurityLevel
    issues: List[SecurityIssue] = field(default_factory=list)
    bypassed_checks: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_issue(self, issue: SecurityIssue) -> None:
        """Add a security issue"""
        self.issues.append(issue)
        
        # Update overall security level
        if issue.level == SecurityLevel.BLOCKED:
            self.security_level = SecurityLevel.BLOCKED
            self.is_safe = False
        elif issue.level == SecurityLevel.DANGEROUS and self.security_level != SecurityLevel.BLOCKED:
            self.security_level = SecurityLevel.DANGEROUS
            self.is_safe = False
        elif issue.level == SecurityLevel.WARNING and self.security_level in [SecurityLevel.SAFE]:
            self.security_level = SecurityLevel.WARNING


class SecurityValidator:
    """
    Security Validator for Plugin SDK
    
    Provides comprehensive security validation for plugins including:
    - MD5 hash validation with development bypass
    - Code scanning for dangerous patterns
    - Permission validation
    - Sandbox compatibility checks
    - PowerShell script validation
    """
    
    def __init__(self, validation_flags: ValidationFlags = ValidationFlags.NORMAL):
        self.validation_flags = validation_flags
        self.logger = logging.getLogger(f'{__name__}.SecurityValidator')
        
        # Dangerous patterns to scan for
        self.dangerous_patterns = {
            'file_operations': [
                r'os\.remove\(',
                r'os\.rmdir\(',
                r'shutil\.rmtree\(',
                r'open\([^)]*["\']w.get("\')',
                r'pathlib\.Path\([^)]*\)\.unlink\(',
            ],
            'network_operations': [
                r'urllib\.request\.',
                r'requests\.',
                r'socket\.',
                r'http\.client\.',
            ],
            'system_operations': [
                r'subprocess\.',
                r'os\.system\(',
                r'os\.popen\(',
                r'eval\(',
                r'exec\(',
                r'__import__\(',
            ],
            'registry_operations': [
                r'winreg\.',
                r'_winreg\.',
            ]
        }
        
        # Trusted MD5 hashes (for known safe plugins)
        self.trusted_hashes: Set[str] = set()
        
        self.logger.info(f"Security Validator initialized with flags: {validation_flags}")
    
    def validate_plugin(self, plugin_path: Path, expected_md5: Optional[str] = None) -> ValidationResult:
        """
        Validate plugin security
        
        Args:
            plugin_path: Path to plugin directory or file
            expected_md5: Expected MD5 hash (optional)
            
        Returns:
            ValidationResult with security assessment
        """
        result = ValidationResult(is_safe=True, security_level=SecurityLevel.SAFE)
        
        try:
            # MD5 validation
            if ValidationFlags.MD5_VALIDATION in self.validation_flags:
                self._validate_md5(plugin_path, expected_md5, result)
            
            # Code scanning
            if ValidationFlags.CODE_SCANNING in self.validation_flags:
                self._scan_code(plugin_path, result)
            
            # Permission check
            if ValidationFlags.PERMISSION_CHECK in self.validation_flags:
                self._check_permissions(plugin_path, result)
            
            # Sandbox validation
            if ValidationFlags.SANDBOX_VALIDATION in self.validation_flags:
                self._validate_sandbox_compatibility(plugin_path, result)
            
            # PowerShell validation
            if ValidationFlags.POWERSHELL_VALIDATION in self.validation_flags:
                self._validate_powershell_scripts(plugin_path, result)
            
            self.logger.info(f"Plugin validation completed: {result.security_level.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during plugin validation: {e}")
            result.add_issue(SecurityIssue(
                level=SecurityLevel.BLOCKED,
                category="validation_error",
                description=f"Validation failed: {e}",
                recommendation="Contact plugin developer"
            ))
            return result
    
    def _validate_md5(self, plugin_path: Path, expected_md5: Optional[str], result: ValidationResult) -> None:
        """Validate MD5 hash"""
        try:
            # Check for development bypass
            if ValidationFlags.DEVELOPMENT_BYPASS in self.validation_flags:
                result.bypassed_checks.add("md5_validation")
                self.logger.debug("MD5 validation bypassed (development mode)")
                return
            
            # Calculate actual MD5
            actual_md5 = self._calculate_md5(plugin_path)
            result.metadata['calculated_md5'] = actual_md5
            
            # Check against expected hash
            if expected_md5:
                if actual_md5 != expected_md5.lower():
                    result.add_issue(SecurityIssue(
                        level=SecurityLevel.DANGEROUS,
                        category="integrity",
                        description=f"MD5 hash mismatch: expected {expected_md5}, got {actual_md5}",
                        recommendation="Verify plugin source and re-download"
                    ))
                    return
            
            # Check against trusted hashes
            if actual_md5 in self.trusted_hashes:
                result.metadata['trusted_plugin'] = True
                self.logger.debug(f"Plugin verified as trusted: {actual_md5}")
            else:
                result.add_issue(SecurityIssue(
                    level=SecurityLevel.WARNING,
                    category="trust",
                    description="Plugin not in trusted hash database",
                    recommendation="Verify plugin source before installation"
                ))
                
        except Exception as e:
            result.add_issue(SecurityIssue(
                level=SecurityLevel.WARNING,
                category="md5_validation",
                description=f"MD5 validation failed: {e}",
                recommendation="Manual verification recommended"
            ))
    
    def _scan_code(self, plugin_path: Path, result: ValidationResult) -> None:
        """Scan code for dangerous patterns"""
        try:
            python_files = []
            
            if plugin_path.is_file() and plugin_path.suffix == '.py':
                python_files = [plugin_path]
            elif plugin_path.is_dir():
                python_files = list(plugin_path.rglob('*.py'))
            
            for file_path in python_files:
                self._scan_file(file_path, result)
                
        except Exception as e:
            result.add_issue(SecurityIssue(
                level=SecurityLevel.WARNING,
                category="code_scanning",
                description=f"Code scanning failed: {e}",
                recommendation="Manual code review recommended"
            ))
    
    def _scan_file(self, file_path: Path, result: ValidationResult) -> None:
        """Scan a single file for dangerous patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for category, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    import re
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Determine severity based on category
                        if category in ['system_operations', 'registry_operations']:
                            level = SecurityLevel.DANGEROUS
                        else:
                            level = SecurityLevel.WARNING
                        
                        result.add_issue(SecurityIssue(
                            level=level,
                            category=category,
                            description=f"Potentially dangerous operation: {match.group()}",
                            file_path=str(file_path),
                            line_number=line_num,
                            recommendation=f"Review {category} usage for security implications"
                        ))
                        
        except Exception as e:
            self.logger.warning(f"Error scanning file {file_path}: {e}")
    
    def _check_permissions(self, plugin_path: Path, result: ValidationResult) -> None:
        """Check file permissions"""
        try:
            if not plugin_path.exists():
                result.add_issue(SecurityIssue(
                    level=SecurityLevel.BLOCKED,
                    category="permissions",
                    description="Plugin path does not exist",
                    recommendation="Verify plugin installation"
                ))
                return
            
            # Check if files are readable
            if plugin_path.is_file():
                if not os.access(plugin_path, os.R_OK):
                    result.add_issue(SecurityIssue(
                        level=SecurityLevel.BLOCKED,
                        category="permissions",
                        description="Plugin file is not readable",
                        recommendation="Check file permissions"
                    ))
            elif plugin_path.is_dir():
                for file_path in plugin_path.rglob('*'):
                    if file_path.is_file() and not os.access(file_path, os.R_OK):
                        result.add_issue(SecurityIssue(
                            level=SecurityLevel.WARNING,
                            category="permissions",
                            description=f"File not readable: {file_path}",
                            recommendation="Check file permissions"
                        ))
                        
        except Exception as e:
            result.add_issue(SecurityIssue(
                level=SecurityLevel.WARNING,
                category="permissions",
                description=f"Permission check failed: {e}",
                recommendation="Manual permission verification recommended"
            ))
    
    def _validate_sandbox_compatibility(self, plugin_path: Path, result: ValidationResult) -> None:
        """Validate sandbox compatibility"""
        try:
            # Check for sandbox-incompatible operations
            incompatible_imports = [
                'ctypes',
                'subprocess',
                'multiprocessing',
                'threading',
                'asyncio'
            ]
            
            
            if plugin_path.is_dir():
                python_files = list(plugin_path.rglob('*.py'))
            
                python_files = list(plugin_path.rglob('*.py'))
            else:
                python_files = [plugin_path] if plugin_path.suffix == '.py' else []
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for import_name in incompatible_imports:
                        if f'import {import_name}' in content or f'from {import_name}' in content:
                            result.add_issue(SecurityIssue(
                                level=SecurityLevel.WARNING,
                                category="sandbox",
                                description=f"Sandbox-incompatible import: {import_name}",
                                file_path=str(file_path),
                                recommendation="Plugin may not work in sandboxed environment"
                            ))
                            
                except Exception as e:
                    self.logger.warning(f"Error checking sandbox compatibility for {file_path}: {e}")
                    
        except Exception as e:
            result.add_issue(SecurityIssue(
                level=SecurityLevel.WARNING,
                category="sandbox",
                description=f"Sandbox validation failed: {e}",
                recommendation="Manual sandbox compatibility check recommended"
            ))
    
    def _validate_powershell_scripts(self, plugin_path: Path, result: ValidationResult) -> None:
        """Validate PowerShell scripts"""
        try:
            ps_files = []
            
            
            if plugin_path.is_dir():
                ps_files = list(plugin_path.rglob('*.ps1'))
            
                ps_files = list(plugin_path.rglob('*.ps1'))
            elif plugin_path.suffix == '.ps1':
                ps_files = [plugin_path]
            
            for ps_file in ps_files:
                self._validate_powershell_file(ps_file, result)
                
        except Exception as e:
            result.add_issue(SecurityIssue(
                level=SecurityLevel.WARNING,
                category="powershell",
                description=f"PowerShell validation failed: {e}",
                recommendation="Manual PowerShell script review recommended"
            ))
    
    def _validate_powershell_file(self, ps_file: Path, result: ValidationResult) -> None:
        """Validate a single PowerShell file"""
        try:
            with open(ps_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for dangerous PowerShell patterns
            dangerous_ps_patterns = [
                r'Invoke-Expression',
                r'IEX\s',
                r'Start-Process',
                r'New-Object\s+System\.Net\.WebClient',
                r'DownloadString',
                r'DownloadFile',
                r'Remove-Item.*-Recurse',
                r'Set-ExecutionPolicy',
            ]
            
            import re
            for pattern in dangerous_ps_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    result.add_issue(SecurityIssue(
                        level=SecurityLevel.DANGEROUS,
                        category="powershell",
                        description=f"Dangerous PowerShell operation: {match.group()}",
                        file_path=str(ps_file),
                        line_number=line_num,
                        recommendation="Review PowerShell script for security implications"
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error validating PowerShell file {ps_file}: {e}")
    
    def _calculate_md5(self, path: Path) -> str:
        """Calculate MD5 hash of file or directory"""
        md5_hash = hashlib.md5()
        
        
        if path.is_file():
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
        elif path.is_dir():
            # Hash all files in directory
            for file_path in sorted(path.rglob('*')):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
    def add_trusted_hash(self, md5_hash: str) -> None:
        """Add a trusted MD5 hash"""
        self.trusted_hashes.add(md5_hash.lower())
        self.logger.debug(f"Added trusted hash: {md5_hash}")
    
    def remove_trusted_hash(self, md5_hash: str) -> None:
        """Remove a trusted MD5 hash"""
        self.trusted_hashes.discard(md5_hash.lower())
        self.logger.debug(f"Removed trusted hash: {md5_hash}")
    
    def get_trusted_hashes(self) -> Set[str]:
        """Get all trusted hashes"""
        return self.trusted_hashes.copy()
