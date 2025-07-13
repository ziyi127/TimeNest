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
Plugin Metadata Widget
Displays comprehensive plugin information including store data
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QProgressBar, QFrame, QScrollArea, QGridLayout, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPalette

from core.plugin_system import PluginMetadata, PluginStatus
from core.plugin_system.dependency_validator import ValidationResult, CompatibilityLevel
from .plugin_store_client import PluginStoreClient, PluginStoreMetadata


class StarRatingWidget(QWidget):
    """Widget to display star ratings"""
    
    def __init__(self, rating: float = 0.0, max_stars: int = 5):
        super().__init__()
        self.rating = rating
        self.max_stars = max_stars
        self.setFixedHeight(20)
        self.setMinimumWidth(max_stars * 20)
    
    def paintEvent(self, event):
        """Paint star rating"""
        from PyQt6.QtGui import QPainter, QColor, QPolygon
        from PyQt6.QtCore import QPoint
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        star_size = 16
        spacing = 2
        
        for i in range(self.max_stars):
            x = i * (star_size + spacing)
            
            # Determine star color
            if i < int(self.rating):
                color = QColor(255, 215, 0)  # Gold
            elif i < self.rating:
                color = QColor(255, 215, 0, 128)  # Half gold
            else:
                color = QColor(200, 200, 200)  # Gray
            
            painter.setBrush(color)
            painter.setPen(QColor(0, 0, 0, 50))
            
            # Draw star shape
            star = QPolygon([
                QPoint(x + star_size//2, 2),
                QPoint(x + star_size//2 + 3, star_size//2 - 1),
                QPoint(x + star_size - 2, star_size//2 - 1),
                QPoint(x + star_size//2 + 5, star_size//2 + 3),
                QPoint(x + star_size//2 + 8, star_size - 2),
                QPoint(x + star_size//2, star_size//2 + 6),
                QPoint(x + star_size//2 - 8, star_size - 2),
                QPoint(x + star_size//2 - 5, star_size//2 + 3),
                QPoint(x + 2, star_size//2 - 1),
                QPoint(x + star_size//2 - 3, star_size//2 - 1)
            ])
            
            painter.drawPolygon(star)


class CompatibilityStatusWidget(QWidget):
    """Widget to display compatibility status"""
    
    def __init__(self, compatibility_level: CompatibilityLevel):
        super().__init__()
        self.compatibility_level = compatibility_level
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status indicator
        indicator = QLabel("●")
        indicator.setFixedSize(16, 16)
        
        # Status text
        status_text = QLabel()
        
        
        if self.compatibility_level == CompatibilityLevel.COMPATIBLE:
            indicator.setStyleSheet("color: #4CAF50; font-size: 14px;")
            status_text.setText("Compatible")
            status_text.setStyleSheet("color: #4CAF50;")
        elif self.compatibility_level == CompatibilityLevel.PARTIALLY_COMPATIBLE:
            indicator.setStyleSheet("color: #FF9800; font-size: 14px;")
            status_text.setText("Partially Compatible")
            status_text.setStyleSheet("color: #FF9800;")
        elif self.compatibility_level == CompatibilityLevel.INCOMPATIBLE:
            indicator.setStyleSheet("color: #F44336; font-size: 14px;")
            status_text.setText("Incompatible")
            status_text.setStyleSheet("color: #F44336;")
        else:
            indicator.setStyleSheet("color: #9E9E9E; font-size: 14px;")
            status_text.setText("Unknown")
            status_text.setStyleSheet("color: #9E9E9E;")
        
        layout.addWidget(indicator)
        layout.addWidget(status_text)
        layout.addStretch()


class PluginMetadataWidget(QWidget):
    """
    Plugin Metadata Widget
    
    Displays comprehensive plugin information including local metadata,
    store data, ratings, reviews, and compatibility status.
    """
    
    # Signals
    install_requested = pyqtSignal(str)    # plugin_id
    uninstall_requested = pyqtSignal(str)  # plugin_id
    activate_requested = pyqtSignal(str)   # plugin_id
    deactivate_requested = pyqtSignal(str) # plugin_id
    
    def __init__(self, store_client: Optional[PluginStoreClient] = None):
        super().__init__()
        self.store_client = store_client
        self.current_plugin_id: Optional[str] = None
        self.logger = logging.getLogger(f'{__name__}.PluginMetadataWidget')
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Top section: Basic info and actions
        top_widget = self._create_top_section()
        splitter.addWidget(top_widget)
        
        # Bottom section: Detailed info
        bottom_widget = self._create_bottom_section()
        splitter.addWidget(bottom_widget)
        
        # Set splitter proportions
        splitter.setSizes([200, 400])
    
    def _create_top_section(self) -> QWidget:
        """Create the top section with basic info and actions"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Left side: Plugin info
        info_layout = QVBoxLayout()
        
        # Plugin name and version
        self.name_label = QLabel("No plugin selected")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.name_label.setFont(font)
        info_layout.addWidget(self.name_label)
        
        self.version_label = QLabel("")
        info_layout.addWidget(self.version_label)
        
        # Author and description
        self.author_label = QLabel("")
        info_layout.addWidget(self.author_label)
        
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumHeight(60)
        info_layout.addWidget(self.description_label)
        
        # Store info (downloads, rating)
        store_layout = QHBoxLayout()
        
        self.downloads_label = QLabel("")
        store_layout.addWidget(self.downloads_label)
        
        self.rating_widget = StarRatingWidget()
        store_layout.addWidget(self.rating_widget)
        
        self.rating_text = QLabel("")
        store_layout.addWidget(self.rating_text)
        
        store_layout.addStretch()
        info_layout.addLayout(store_layout)
        
        # Compatibility status
        self.compatibility_widget = CompatibilityStatusWidget(CompatibilityLevel.UNKNOWN)
        info_layout.addWidget(self.compatibility_widget)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Right side: Actions
        actions_layout = QVBoxLayout()
        
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self._on_install_clicked)
        actions_layout.addWidget(self.install_button)
        
        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.clicked.connect(self._on_uninstall_clicked)
        actions_layout.addWidget(self.uninstall_button)
        
        self.activate_button = QPushButton("Activate")
        self.activate_button.clicked.connect(self._on_activate_clicked)
        actions_layout.addWidget(self.activate_button)
        
        self.deactivate_button = QPushButton("Deactivate")
        self.deactivate_button.clicked.connect(self._on_deactivate_clicked)
        actions_layout.addWidget(self.deactivate_button)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_bottom_section(self) -> QWidget:
        """Create the bottom section with detailed info"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create tab-like sections
        # Dependencies section
        deps_group = QGroupBox("Dependencies")
        deps_layout = QVBoxLayout(deps_group)
        
        self.dependencies_text = QTextEdit()
        self.dependencies_text.setMaximumHeight(100)
        self.dependencies_text.setReadOnly(True)
        deps_layout.addWidget(self.dependencies_text)
        
        layout.addWidget(deps_group)
        
        # Validation results section
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout(validation_group)
        
        self.validation_text = QTextEdit()
        self.validation_text.setMaximumHeight(100)
        self.validation_text.setReadOnly(True)
        validation_layout.addWidget(self.validation_text)
        
        layout.addWidget(validation_group)
        
        # Store information section
        store_group = QGroupBox("Store Information")
        store_layout = QVBoxLayout(store_group)
        
        self.store_info_text = QTextEdit()
        self.store_info_text.setMaximumHeight(100)
        self.store_info_text.setReadOnly(True)
        store_layout.addWidget(self.store_info_text)
        
        layout.addWidget(store_group)
        
        return widget
    
    def _connect_signals(self):
        """Connect store client signals"""
        if self.store_client:
            self.store_client.metadata_fetched.connect(self._on_store_metadata_received)
            self.store_client.reviews_fetched.connect(self._on_store_reviews_received)
            self.store_client.fetch_error.connect(self._on_store_error)
    
    def display_plugin(self, plugin_id: str, metadata: PluginMetadata, 
                      status: PluginStatus, validation_result: Optional[ValidationResult] = None):
        """
        Display plugin information
        
        Args:
            plugin_id: Plugin ID
            metadata: Plugin metadata
            status: Plugin status
            validation_result: Optional validation result
        """
        try:
            self.current_plugin_id = plugin_id
            
            # Update basic info
            self.name_label.setText(metadata.name)
            self.version_label.setText(f"Version: {metadata.version}")
            self.author_label.setText(f"Author: {metadata.author}")
            self.description_label.setText(metadata.description)
            
            # Update dependencies
            if metadata.dependencies:
                deps_text = "\n".join([f"• {dep}" for dep in metadata.dependencies])
            else:
                deps_text = "No dependencies"
            self.dependencies_text.setPlainText(deps_text)
            
            # Update validation results
            if validation_result and hasattr(validation_result, "self._display_validation_result"):
    self._display_validation_result(validation_result)
                self._display_validation_result(validation_result)
                
                # Update compatibility widget
                self.compatibility_widget.deleteLater()
                self.compatibility_widget = CompatibilityStatusWidget(validation_result.compatibility_level)
                # Add to layout (you'd need to track the layout reference)
            
            # Update action buttons based on status
            self._update_action_buttons(status)
            
            # Fetch store data if available
            if self.store_client:
                self.store_client.fetch_plugin_metadata(plugin_id)
                self.store_client.fetch_plugin_reviews(plugin_id)
            
        except Exception as e:
            self.logger.error(f"Error displaying plugin {plugin_id}: {e}")
    
    def clear_display(self):
        """Clear the display"""
        self.current_plugin_id = None
        self.name_label.setText("No plugin selected")
        self.version_label.setText("")
        self.author_label.setText("")
        self.description_label.setText("")
        self.downloads_label.setText("")
        self.rating_text.setText("")
        self.dependencies_text.clear()
        self.validation_text.clear()
        self.store_info_text.clear()
        
        # Reset rating widget
        self.rating_widget.rating = 0.0
        self.rating_widget.update()
        
        # Disable all buttons
        self.install_button.setEnabled(False)
        self.uninstall_button.setEnabled(False)
        self.activate_button.setEnabled(False)
        self.deactivate_button.setEnabled(False)

    def _display_validation_result(self, result: ValidationResult):
        """Display validation result details"""
        text_parts = []


        if result.is_valid:
            text_parts.append("✓ Validation passed")

            text_parts.append("✓ Validation passed")
        else:
            text_parts.append("✗ Validation failed")


        if result.errors:
            text_parts.append("\nErrors:")

            text_parts.append("\nErrors:")
            for error in result.errors:
                text_parts.append(f"  • {error}")


        if result.warnings:
            text_parts.append("\nWarnings:")

            text_parts.append("\nWarnings:")
            for warning in result.warnings:
                text_parts.append(f"  • {warning}")


        if result.missing_dependencies:
            text_parts.append("\nMissing dependencies:")

            text_parts.append("\nMissing dependencies:")
            for dep in result.missing_dependencies:
                text_parts.append(f"  • {dep.name} ({dep.version_constraint})")


        if result.version_conflicts:
            text_parts.append("\nVersion conflicts:")

            text_parts.append("\nVersion conflicts:")
            for dep, available_version in result.version_conflicts:
                text_parts.append(f"  • {dep.name}: requires {dep.version_constraint}, found {available_version}")

        self.validation_text.setPlainText("\n".join(text_parts))

    def _update_action_buttons(self, status: PluginStatus):
        """Update action button states based on plugin status"""
        # Reset all buttons
        self.install_button.setEnabled(False)
        self.uninstall_button.setEnabled(False)
        self.activate_button.setEnabled(False)
        self.deactivate_button.setEnabled(False)


        if status == PluginStatus.UNKNOWN:
            # Plugin not installed:

            # Plugin not installed
            self.install_button.setEnabled(True)
        elif status == PluginStatus.LOADED:
            # Plugin installed but not active
            self.uninstall_button.setEnabled(True)
            self.activate_button.setEnabled(True)
        elif status == PluginStatus.ENABLED:
            # Plugin active
            self.uninstall_button.setEnabled(True)
            self.deactivate_button.setEnabled(True)
        elif status == PluginStatus.DISABLED:
            # Plugin disabled
            self.uninstall_button.setEnabled(True)
            self.activate_button.setEnabled(True)
        elif status == PluginStatus.ERROR:
            # Plugin has errors
            self.uninstall_button.setEnabled(True)

    def _on_store_metadata_received(self, plugin_id: str, metadata: PluginStoreMetadata):
        """Handle store metadata received"""
        if plugin_id != self.current_plugin_id:
            return:
            return

        try:
            # Update downloads
            if metadata.download_count > 0:
                self.downloads_label.setText(f"Downloads: {metadata.download_count:,}")

            # Update rating
            if metadata.star_rating > 0:
                self.rating_widget.rating = metadata.star_rating
                self.rating_widget.update()
                self.rating_text.setText(f"{metadata.star_rating:.1f} ({metadata.review_count} reviews)")

            # Update store info
            store_info_parts = []


            if metadata.last_updated:
                store_info_parts.append(f"Last updated: {metadata.last_updated}")

                store_info_parts.append(f"Last updated: {metadata.last_updated}")


            if metadata.file_size > 0:
                size_mb = metadata.file_size / (1024 * 1024)

                size_mb = metadata.file_size / (1024 * 1024)
                store_info_parts.append(f"Size: {size_mb:.1f} MB")


            if metadata.license:
                store_info_parts.append(f"License: {metadata.license}")

                store_info_parts.append(f"License: {metadata.license}")


            if metadata.tags:
                store_info_parts.append(f"Tags: {', '.join(metadata.tags)}"):

                store_info_parts.append(f"Tags: {', '.join(metadata.tags)}")


            if metadata.changelog:
                store_info_parts.append(f"\nChangelog:\n{metadata.changelog}")

                store_info_parts.append(f"\nChangelog:\n{metadata.changelog}")

            self.store_info_text.setPlainText("\n".join(store_info_parts))

        except Exception as e:
            self.logger.error(f"Error processing store metadata: {e}")

    def _on_store_reviews_received(self, plugin_id: str, reviews):
        """Handle store reviews received"""
        if plugin_id != self.current_plugin_id:
            return:
            return

        try:
            if reviews:
                # Add reviews to store info:
                # Add reviews to store info
                current_text = self.store_info_text.toPlainText()

                reviews_text = "\n\nRecent Reviews:\n"
                for review in reviews[:3]:  # Show top 3 reviews:
                    stars = "★" * review.rating + "☆" * (5 - review.rating)
                    reviews_text += f"\n{stars} by {review.reviewer} ({review.date})\n"
                    reviews_text += f"{review.comment}\n"

                self.store_info_text.setPlainText(current_text + reviews_text)

        except Exception as e:
            self.logger.error(f"Error processing store reviews: {e}")

    def _on_store_error(self, plugin_id: str, error_message: str):
        """Handle store fetch error"""
        if plugin_id != self.current_plugin_id:
            return:
            return

        self.logger.warning(f"Store fetch error for {plugin_id}: {error_message}")

        # Show offline message in store info
        self.store_info_text.setPlainText("Store information unavailable (offline)")

    def _on_install_clicked(self):
        """Handle install button click"""
        if self.current_plugin_id:
            self.install_requested.emit(self.current_plugin_id)

    def _on_uninstall_clicked(self):
        """Handle uninstall button click"""
        if self.current_plugin_id:
            self.uninstall_requested.emit(self.current_plugin_id)

    def _on_activate_clicked(self):
        """Handle activate button click"""
        if self.current_plugin_id:
            self.activate_requested.emit(self.current_plugin_id)

    def _on_deactivate_clicked(self):
        """Handle deactivate button click"""
        if self.current_plugin_id:
            self.deactivate_requested.emit(self.current_plugin_id)
