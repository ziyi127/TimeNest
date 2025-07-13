#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PyQt6.QtCore import QObject
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    # 提供备用实现
    class QObject:
        def __init__(self, *args, **kwargs):
            pass

"""
PowerShell Executor for Plugin SDK
Provides secure PowerShell script execution during plugin installation/setup
"""

import logging
import subprocess
import tempfile
import os
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .security_validator import SecurityValidator, ValidationFlags, ValidationResult


class ExecutionPolicy(Enum):
    """PowerShell execution policies"""
    RESTRICTED = "Restricted"
    REMOTE_SIGNED = "RemoteSigned"
    UNRESTRICTED = "Unrestricted"
    BYPASS = "Bypass"


class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class PowerShellCommand:
    """PowerShell command definition"""
    id: str
    script_content: str
    description: str = ""
    timeout_seconds: int = 300  # 5 minutes default
    execution_policy: ExecutionPolicy = ExecutionPolicy.REMOTE_SIGNED
    working_directory: Optional[str] = None
    environment_variables: Dict[str, str] = field(default_factory=dict)
    requires_admin: bool = False
    validate_before_execution: bool = True
    
    def __post_init__(self):
        """Validate command after initialization"""
        if not self.script_content.strip():
            raise ValueError("Script content cannot be empty")
        
        
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")


@dataclass
class ExecutionResult:
    """PowerShell execution result"""
    command_id: str
    status: CommandStatus
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    error_message: str = ""
    validation_result: Optional[ValidationResult] = None


class PowerShellExecutor(QObject):
    """
    PowerShell Executor for Plugin SDK
    
    Provides secure PowerShell script execution during plugin installation/setup
    with proper sandboxing, validation, and monitoring capabilities.:
    """
    
    # Signals
    command_started = pyqtSignal(str)  # command_id
    command_completed = pyqtSignal(str, object)  # command_id, result
    command_failed = pyqtSignal(str, str)  # command_id, error_message
    output_received = pyqtSignal(str, str)  # command_id, output_line
    
    def __init__(self, security_validator: Optional[SecurityValidator] = None):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.PowerShellExecutor')
        
        # Security validator
        self.security_validator = security_validator or SecurityValidator(
            ValidationFlags.POWERSHELL_VALIDATION | ValidationFlags.CODE_SCANNING
        )
        
        # Execution tracking
        self._active_commands: Dict[str, subprocess.Popen] = {}
        self._command_results: Dict[str, ExecutionResult] = {}
        self._execution_lock = threading.RLock()
        
        # Configuration
        self.max_concurrent_commands = 3
        self.default_timeout = 300  # 5 minutes
        self.temp_script_dir = Path(tempfile.gettempdir()) / "timenest_ps_scripts"
        self.temp_script_dir.mkdir(exist_ok=True)
        
        # Monitoring
        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(self._monitor_commands)
        self._monitor_timer.start(1000)  # Check every second
        
        self.logger.info("PowerShell Executor initialized")
    
    def execute_command(self, command: PowerShellCommand) -> bool:
        """
        Execute a PowerShell command
        
        Args:
            command: PowerShell command to execute
            
        Returns:
            True if command was queued successfully
        """
        try:
            # Check concurrent limit
            with self._execution_lock:
                if len(self._active_commands) >= self.max_concurrent_commands:
                    self.logger.warning(f"Maximum concurrent commands reached: {self.max_concurrent_commands}")
                    return False
                
                # Check if command already exists
                if command.id in self._active_commands or command.id in self._command_results:
                    self.logger.warning(f"Command already exists: {command.id}")
                    return False
            
            # Validate command if required
            if command.validate_before_execution:
                validation_result = self._validate_command(command)
                if not validation_result.is_safe:
                    self.logger.error(f"Command validation failed: {command.id}")
                    self._create_failed_result(command, "Command validation failed", validation_result)
                    return False
            
            # Execute in background thread
            thread = threading.Thread(
                target=self._execute_command_thread,
                args=(command,),
                daemon=True
            )
            thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing command {command.id}: {e}")
            self._create_failed_result(command, str(e))
            return False
    
    def cancel_command(self, command_id: str) -> bool:
        """
        Cancel a running command
        
        Args:
            command_id: ID of the command to cancel
            
        Returns:
            True if command was cancelled successfully
        """
        try:
            with self._execution_lock:
                if command_id in self._active_commands:
                    process = self._active_commands[command_id]
                    process.terminate()
                    
                    # Wait a bit for graceful termination
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if necessary
                        process.kill()
                        process.wait()
                    
                    # Create cancelled result
                    result = ExecutionResult(
                        command_id=command_id,
                        status=CommandStatus.CANCELLED,
                        error_message="Command cancelled by user"
                    )
                    
                    self._command_results[command_id] = result
                    del self._active_commands[command_id]
                    
                    self.command_failed.emit(command_id, "Command cancelled")
                    
                    self.logger.info(f"Command cancelled: {command_id}")
                    return True
                else:
                    self.logger.warning(f"Command not found or not running: {command_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error cancelling command {command_id}: {e}")
            return False
    
    def get_command_result(self, command_id: str) -> Optional[ExecutionResult]:
        """Get command execution result"""
        return self._command_results.get(command_id)
    
    def get_active_commands(self) -> List[str]:
        """Get list of active command IDs"""
        with self._execution_lock:
            return list(self._active_commands.keys())
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        try:
            # Cancel all active commands
            with self._execution_lock:
                for command_id in list(self._active_commands.keys()):
                    self.cancel_command(command_id)
            
            # Stop monitoring
            self._monitor_timer.stop()
            
            # Clean up temp files
            try:
                import shutil
                if self.temp_script_dir.exists():
                    shutil.rmtree(self.temp_script_dir)
            except Exception as e:
                self.logger.warning(f"Error cleaning up temp directory: {e}")
            
            self.logger.info("PowerShell Executor cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _execute_command_thread(self, command: PowerShellCommand) -> None:
        """Execute command in background thread"""
        start_time = time.time()
        result = ExecutionResult(
            command_id=command.id,
            status=CommandStatus.RUNNING
        )
        
        try:
            # Create temporary script file
            script_file = self._create_temp_script(command)
            
            # Build PowerShell command
            ps_args = self._build_powershell_args(command, script_file)
            
            # Start process
            with self._execution_lock:
                if command.id in self._command_results:
                    # Command was cancelled before starting:
                    # Command was cancelled before starting
                    return
                
                process = subprocess.Popen(
                    ps_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=command.working_directory,
                    env=self._build_environment(command)
                )
                
                self._active_commands[command.id] = process
            
            # Emit started signal
            self.command_started.emit(command.id)
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=command.timeout_seconds)
                result.exit_code = process.returncode
                result.stdout = stdout
                result.stderr = stderr
                
                
                if process.returncode == 0:
                    result.status = CommandStatus.COMPLETED
                
                    result.status = CommandStatus.COMPLETED
                else:
                    result.status = CommandStatus.FAILED
                    result.error_message = f"Process exited with code {process.returncode}"
                
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                result.status = CommandStatus.TIMEOUT
                result.error_message = f"Command timed out after {command.timeout_seconds} seconds"
            
            # Calculate execution time
            result.execution_time = time.time() - start_time
            
            # Clean up
            with self._execution_lock:
                if command.id in self._active_commands:
                    del self._active_commands[command.id]
                self._command_results[command.id] = result
            
            # Clean up temp script
            try:
                script_file.unlink()
            except Exception:
                pass
            
            # Emit completion signal
            if result.status == CommandStatus.COMPLETED:
                self.command_completed.emit(command.id, result)
            else:
                self.command_failed.emit(command.id, result.error_message)
            
        except Exception as e:
            result.status = CommandStatus.FAILED
            result.error_message = str(e)
            result.execution_time = time.time() - start_time
            
            with self._execution_lock:
                if command.id in self._active_commands:
                    del self._active_commands[command.id]
                self._command_results[command.id] = result
            
            self.command_failed.emit(command.id, str(e))
            self.logger.error(f"Error executing command {command.id}: {e}")
    
    def _validate_command(self, command: PowerShellCommand) -> ValidationResult:
        """Validate PowerShell command"""
        try:
            # Create temporary script file for validation
            script_file = self._create_temp_script(command)
            
            # Validate using security validator
            validation_result = self.security_validator.validate_plugin(script_file)
            
            # Clean up temp file
            try:
                script_file.unlink()
            except Exception:
                pass
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating command: {e}")
            # Return a failed validation result
            from .security_validator import ValidationResult, SecurityLevel, SecurityIssue
            result = ValidationResult(is_safe=False, security_level=SecurityLevel.BLOCKED)
            result.add_issue(SecurityIssue(
                level=SecurityLevel.BLOCKED,
                category="validation_error",
                description=f"Validation failed: {e}"
            ))
            return result
    
    def _create_temp_script(self, command: PowerShellCommand) -> Path:
        """Create temporary script file"""
        script_file = self.temp_script_dir / f"{command.id}.ps1"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(command.script_content)
        
        return script_file
    
    def _build_powershell_args(self, command: PowerShellCommand, script_file: Path) -> List[str]:
        """Build PowerShell command arguments"""
        args = ["powershell.exe", "-NoProfile", "-NonInteractive"]
        
        # Set execution policy
        args.extend(["-ExecutionPolicy", command.execution_policy.value])
        
        # Add script file
        args.extend(["-File", str(script_file)])
        
        return args
    
    def _build_environment(self, command: PowerShellCommand) -> Dict[str, str]:
        """Build environment variables"""
        env = os.environ.copy()
        env.update(command.environment_variables)
        return env
    
    def _create_failed_result(self, command: PowerShellCommand, error_message: str, 
                            validation_result: Optional[ValidationResult] = None) -> None:
        """Create a failed execution result"""
        result = ExecutionResult(
            command_id=command.id,
            status=CommandStatus.FAILED,
            error_message=error_message,
            validation_result=validation_result
        )
        
        self._command_results[command.id] = result
        self.command_failed.emit(command.id, error_message)
    
    def _monitor_commands(self) -> None:
        """Monitor active commands for completion"""
        try:
            with self._execution_lock:
                completed_commands = []
                
                for command_id, process in self._active_commands.items():
                    if process.poll() is not None:
                        completed_commands.append(command_id)
                
                # Note: Actual completion handling is done in the execution thread
                # This is just for monitoring and cleanup
                
        except Exception as e:
            self.logger.error(f"Error monitoring commands: {e}")
