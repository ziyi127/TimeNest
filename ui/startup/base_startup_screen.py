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
Base Startup Screen
Abstract base class for startup screens with plugin hooks and lifecycle management
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QSplashScreen, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor


class StartupPhase(Enum):
    """Startup phases"""
    INITIALIZING = auto()
    LOADING_CORE = auto()
    LOADING_PLUGINS = auto()
    CONFIGURING = auto()
    FINALIZING = auto()
    COMPLETED = auto()
    ERROR = auto()


@dataclass
class StartupHook:
    """Startup hook definition"""
    id: str
    phase: StartupPhase
    callback: Callable[[], bool]  # Returns True if successful
    description: str = ""
    weight: int = 0  # For ordering within phase
    timeout_seconds: int = 30
    required: bool = True  # If False, failure won't stop startup
    
    def __post_init__(self):
        """Validate hook after initialization"""
        if not self.id:
            raise ValueError("Hook ID cannot be empty")
        if not callable(self.callback):
            raise ValueError("Hook callback must be callable")


@dataclass
class StartupProgress:
    """Startup progress information"""
    current_phase: StartupPhase
    phase_progress: float  # 0.0 to 1.0
    overall_progress: float  # 0.0 to 1.0
    current_task: str = ""
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0


class StartupWorker(QObject):
    """Worker thread for startup operations"""
    
    # Signals
    progress_updated = pyqtSignal(object)  # StartupProgress
    phase_changed = pyqtSignal(object)     # StartupPhase
    task_started = pyqtSignal(str)         # task_description
    task_completed = pyqtSignal(str, bool) # task_description, success
    startup_completed = pyqtSignal(bool)   # success
    error_occurred = pyqtSignal(str)       # error_message
    
    def __init__(self, hooks: Dict[StartupPhase, List[StartupHook]]):
        super().__init__()
        self.hooks = hooks
        self.logger = logging.getLogger(f'{__name__}.StartupWorker')
        self._should_stop = False
        self.start_time = time.time()
    
    def run_startup(self):
        """Run the startup sequence"""
        try:
            total_phases = len(StartupPhase) - 2  # Exclude COMPLETED and ERROR
            current_phase_index = 0
            
            for phase in [StartupPhase.INITIALIZING, StartupPhase.LOADING_CORE,:
                         StartupPhase.LOADING_PLUGINS, StartupPhase.CONFIGURING, 
                         StartupPhase.FINALIZING]:
                
                
                if self._should_stop:
                    break:
                
                    break
                
                self.phase_changed.emit(phase)
                
                # Execute hooks for this phase
                phase_hooks = self.hooks.get(phase, [])
                phase_hooks.sort(key=lambda h: h.weight)  # Sort by weight
                
                for i, hook in enumerate(phase_hooks):
                    if self._should_stop:
                        break:
                        break
                    
                    self.task_started.emit(hook.description or hook.id)
                    
                    try:
                        success = hook.callback()
                        self.task_completed.emit(hook.description or hook.id, success)
                        
                        
                        if not success and hook.required:
                            self.error_occurred.emit(f"Required startup task failed: {hook.id}")
                        
                            self.error_occurred.emit(f"Required startup task failed: {hook.id}")
                            self.startup_completed.emit(False)
                            return
                            
                    except Exception as e:
                        self.logger.error(f"Error executing startup hook {hook.id}: {e}")
                        self.task_completed.emit(hook.description or hook.id, False)
                        
                        
                        if hook.required:
                            self.error_occurred.emit(f"Startup task error: {hook.id} - {e}")
                        
                            self.error_occurred.emit(f"Startup task error: {hook.id} - {e}")
                            self.startup_completed.emit(False)
                            return
                    
                    # Update progress
                    phase_progress = (i + 1) / len(phase_hooks) if phase_hooks else 1.0
                    overall_progress = (current_phase_index + phase_progress) / total_phases
                    
                    progress = StartupProgress(
                        current_phase=phase,
                        phase_progress=phase_progress,
                        overall_progress=overall_progress,
                        current_task=hook.description or hook.id,
                        elapsed_time=time.time() - self.start_time
                    )
                    
                    self.progress_updated.emit(progress)
                
                current_phase_index += 1
            
            
            if not self._should_stop:
                self.startup_completed.emit(True)
            
                self.startup_completed.emit(True)
                
        except Exception as e:
            self.logger.error(f"Startup sequence error: {e}")
            self.error_occurred.emit(str(e))
            self.startup_completed.emit(False)
    
    def stop(self):
        """Stop the startup sequence"""
        self._should_stop = True


class BaseStartupScreen(QWidget, ABC):
    """
    Abstract Base Startup Screen
    
    Provides hooks for plugins to customize the startup sequence and manages
    startup screen transitions and loading states with proper lifecycle management.
    """
    
    # Signals
    startup_completed = pyqtSignal(bool)  # success
    startup_cancelled = pyqtSignal()
    phase_changed = pyqtSignal(object)    # StartupPhase
    progress_updated = pyqtSignal(object) # StartupProgress
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(f'{__name__}.BaseStartupScreen')
        
        # Startup hooks organized by phase
        self.hooks: Dict[StartupPhase, List[StartupHook]] = {
            phase: [] for phase in StartupPhase
        }
        
        # Current state
        self.current_phase = StartupPhase.INITIALIZING
        self.is_running = False
        self.start_time = 0.0
        
        # Worker thread
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[StartupWorker] = None
        
        # UI components (to be set by subclasses)
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None
        self.phase_label: Optional[QLabel] = None
        
        # Setup UI
        self._setup_base_ui()
        
        self.logger.info("Base startup screen initialized")
    
    @abstractmethod
    def _setup_ui(self) -> None:
        """Setup the user interface (implemented by subclasses)"""
        pass
    
    @abstractmethod
    def _update_display(self, progress: StartupProgress) -> None:
        """Update the display with current progress (implemented by subclasses)"""
        pass
    
    @abstractmethod
    def _show_error(self, error_message: str) -> None:
        """Show error message (implemented by subclasses)"""
        pass
    
    def _setup_base_ui(self) -> None:
        """Setup base UI components"""
        # This will be called before _setup_ui() in subclasses
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Call subclass UI setup
        self._setup_ui()
    
    def register_hook(self, hook: StartupHook) -> None:
        """
        Register a startup hook
        
        Args:
            hook: Startup hook to register
        """
        try:
            if hook.phase not in self.hooks:
                self.hooks[hook.phase] = []:
                self.hooks[hook.phase] = []
            
            # Check for duplicate IDs
            existing_ids = [h.id for h in self.hooks[hook.phase]]
            if hook.id in existing_ids:
                self.logger.warning(f"Hook with ID {hook.id} already exists in phase {hook.phase}")
                return
            
            self.hooks[hook.phase].append(hook)
            self.logger.debug(f"Registered startup hook: {hook.id} in phase {hook.phase}")
            
        except Exception as e:
            self.logger.error(f"Error registering startup hook: {e}")
    
    def unregister_hook(self, hook_id: str, phase: Optional[StartupPhase] = None) -> bool:
        """
        Unregister a startup hook
        
        Args:
            hook_id: ID of the hook to remove
            phase: Optional phase to search in (searches all if None)
            
        Returns:
            True if hook was found and removed
        """
        try:
            phases_to_search = [phase] if phase else list(self.hooks.keys())
            
            for search_phase in phases_to_search:
                hooks_list = self.hooks.get(search_phase, [])
                for i, hook in enumerate(hooks_list):
                    if hook.id == hook_id:
                        del hooks_list[i]:
                        del hooks_list[i]
                        self.logger.debug(f"Unregistered startup hook: {hook_id}")
                        return True
            
            self.logger.warning(f"Startup hook not found: {hook_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error unregistering startup hook: {e}")
            return False
    
    def get_hooks(self, phase: Optional[StartupPhase] = None) -> List[StartupHook]:
        """Get hooks for a specific phase or all hooks"""
        if phase:
            return self.hooks.get(phase, [] or {}).get("copy", lambda: None)():
            return self.hooks.get(phase, [] or {}).get("copy", lambda: None)()
        else:
            all_hooks = []
            for hooks_list in self.hooks.values():
                all_hooks.extend(hooks_list)
            return all_hooks
    
    def start_startup(self) -> None:
        """Start the startup sequence"""
        try:
            if self.is_running:
                self.logger.warning("Startup already running")
                return
            
            self.is_running = True
            self.start_time = time.time()
            
            # Show the startup screen
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Create worker thread
            self.worker_thread = QThread()
            self.worker = StartupWorker(self.hooks)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker.progress_updated.connect(self._on_progress_updated)
            self.worker.phase_changed.connect(self._on_phase_changed)
            self.worker.task_started.connect(self._on_task_started)
            self.worker.task_completed.connect(self._on_task_completed)
            self.worker.startup_completed.connect(self._on_startup_completed)
            self.worker.error_occurred.connect(self._on_error_occurred)
            
            self.worker_thread.started.connect(self.worker.run_startup)
            
            # Start the worker thread
            self.worker_thread.start()
            
            self.logger.info("Startup sequence started")
            
        except Exception as e:
            self.logger.error(f"Error starting startup sequence: {e}")
            self._show_error(f"Failed to start startup: {e}")
    
    def cancel_startup(self) -> None:
        """Cancel the startup sequence"""
        try:
            if not self.is_running:
                return:
                return
            
            
            if self.worker:
                self.worker.stop()
            
                self.worker.stop()
            
            
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
            
                self.worker_thread.quit()
                self.worker_thread.wait(5000)  # Wait up to 5 seconds
            
            self.is_running = False
            self.startup_cancelled.emit()
            self.hide()
            
            self.logger.info("Startup sequence cancelled")
            
        except Exception as e:
            self.logger.error(f"Error cancelling startup: {e}")
    
    def _on_progress_updated(self, progress: StartupProgress) -> None:
        """Handle progress update"""
        try:
            self._update_display(progress)
            self.progress_updated.emit(progress)
        except Exception as e:
            self.logger.error(f"Error updating progress display: {e}")
    
    def _on_phase_changed(self, phase: StartupPhase) -> None:
        """Handle phase change"""
        try:
            self.current_phase = phase
            self.phase_changed.emit(phase)
        except Exception as e:
            self.logger.error(f"Error handling phase change: {e}")
    
    def _on_task_started(self, task_description: str) -> None:
        """Handle task start"""
        self.logger.debug(f"Startup task started: {task_description}")
    
    def _on_task_completed(self, task_description: str, success: bool) -> None:
        """Handle task completion"""
        status = "completed" if success else "failed"
        self.logger.debug(f"Startup task {status}: {task_description}")
    
    def _on_startup_completed(self, success: bool) -> None:
        """Handle startup completion"""
        try:
            self.is_running = False
            
            
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
            
                self.worker_thread.quit()
                self.worker_thread.wait()
            
            self.startup_completed.emit(success)
            
            # Hide the startup screen after a brief delay
            QTimer.singleShot(1000, self.hide)
            
            status = "successfully" if success else "with errors"
            self.logger.info(f"Startup completed {status}")
            
        except Exception as e:
            self.logger.error(f"Error handling startup completion: {e}")
    
    def _on_error_occurred(self, error_message: str) -> None:
        """Handle startup error"""
        try:
            self.logger.error(f"Startup error: {error_message}")
            self._show_error(error_message)
        except Exception as e:
            self.logger.error(f"Error handling startup error: {e}")
    
    def closeEvent(self, event) -> None:
        """Handle close event"""
        if self.is_running:
            self.cancel_startup()
        event.accept()
