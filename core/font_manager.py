#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体管理器

负责管理应用的全局字体设置
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal


class FontManager(QObject):
    """字体管理器"""
    
    # 信号
    font_changed = pyqtSignal(str, QFont)  # 字体名称, 字体对象
    
    def __init__(self, config_manager=None):
        super().__init__()
        self.logger = logging.getLogger(f'{__name__}.FontManager')
        self.config_manager = config_manager
        
        # 字体数据库 - 使用静态方法
        self.font_database = QFontDatabase
        
        # 字体目录
        self.fonts_dir = Path(__file__).parent.parent / 'resources' / 'fonts'
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # 已加载的字体
        self.loaded_fonts: Dict[str, str] = {}  # 字体名称 -> 字体文件路径
        
        # 默认字体配置
        self.default_fonts = {
            'app': 'MiSans-Light',      # 应用主字体
            'ui': 'MiSans-Light',       # UI界面字体
            'floating': 'MiSans-Light', # 浮窗字体
            'monospace': 'Consolas'     # 等宽字体
        }
        
        # 字体大小配置
        self.font_sizes = {
            'small': 9,
            'normal': 12,
            'large': 14,
            'xlarge': 16
        }
        
        # 初始化
        self._load_custom_fonts()
        self._setup_default_fonts()
        
        self.logger.info("字体管理器初始化完成")
    
    def _load_custom_fonts(self):
        """加载自定义字体"""
        try:
            # 扫描字体目录
            font_files = list(self.fonts_dir.glob('*.ttf')) + list(self.fonts_dir.glob('*.otf'))
            
            for font_file in font_files:
                self._load_font_file(font_file)
            
            self.logger.info(f"已加载 {len(self.loaded_fonts)} 个自定义字体")
            
        except Exception as e:
            self.logger.error(f"加载自定义字体失败: {e}")
    
    def _load_font_file(self, font_file: Path) -> bool:
        """加载单个字体文件"""
        try:
            font_id = self.font_database.addApplicationFont(str(font_file))

            if font_id != -1:
                # 获取字体族名称
                font_families = self.font_database.applicationFontFamilies(font_id)

                for family in font_families:
                    self.loaded_fonts[family] = str(font_file)
                    self.logger.debug(f"字体已加载: {family} ({font_file.name})")

                return True
            else:
                self.logger.warning(f"字体加载失败: {font_file}")
                return False

        except Exception as e:
            self.logger.error(f"加载字体文件失败 {font_file}: {e}")
            return False
    
    def _setup_default_fonts(self):
        """设置默认字体"""
        try:
            # 检查MiSans-Light是否可用
            if 'MiSans-Light' in self.loaded_fonts:
                self.logger.info("MiSans-Light 字体可用")
            else:
                self.logger.warning("MiSans-Light 字体不可用，使用系统默认字体")
                # 使用系统默认字体作为备选
                self.default_fonts = {
                    'app': 'Arial',
                    'ui': 'Arial', 
                    'floating': 'Arial',
                    'monospace': 'Consolas'
                }
            
            # 应用全局字体
            self._apply_global_font()
            
        except Exception as e:
            self.logger.error(f"设置默认字体失败: {e}")
    
    def _apply_global_font(self):
        """应用全局字体"""
        try:
            app = QApplication.instance()
            if not app:
                return
            
            # 创建主字体
            main_font = self.create_font('app', 'normal')
            
            # 设置应用全局字体
            app.setFont(main_font)
            
            self.logger.info(f"全局字体已设置: {main_font.family()} {main_font.pointSize()}pt")
            
            # 发送字体变更信号
            self.font_changed.emit('global', main_font)
            
        except Exception as e:
            self.logger.error(f"应用全局字体失败: {e}")
    
    def create_font(self, font_type: str = 'app', size_type: str = 'normal', 
                   bold: bool = False, italic: bool = False) -> QFont:
        """创建字体对象"""
        try:
            # 获取字体族名称
            font_family = self.default_fonts.get(font_type, 'Arial')
            
            # 获取字体大小
            font_size = self.font_sizes.get(size_type, 12)
            
            # 创建字体对象
            font = QFont(font_family, font_size)
            font.setBold(bold)
            font.setItalic(italic)
            
            # 如果是自定义字体，确保字体可用
            if font_family in self.loaded_fonts:
                # 验证字体是否正确加载
                if font.family() != font_family:
                    self.logger.warning(f"字体 {font_family} 可能未正确加载，实际使用: {font.family()}")
            
            return font
            
        except Exception as e:
            self.logger.error(f"创建字体失败: {e}")
            # 返回默认字体
            return QFont('Arial', 12)
    
    def get_available_fonts(self) -> List[str]:
        """获取可用字体列表"""
        try:
            # 系统字体
            system_fonts = self.font_database.families()

            # 自定义字体
            custom_fonts = list(self.loaded_fonts.keys())

            # 合并并去重
            all_fonts = list(set(system_fonts + custom_fonts))
            all_fonts.sort()

            return all_fonts

        except Exception as e:
            self.logger.error(f"获取可用字体列表失败: {e}")
            return ['Arial', 'Times New Roman', 'Courier New']
    
    def set_font_config(self, font_type: str, font_family: str, save: bool = True):
        """设置字体配置"""
        try:
            if font_type in self.default_fonts:
                old_font = self.default_fonts[font_type]
                self.default_fonts[font_type] = font_family
                
                self.logger.info(f"字体配置已更新: {font_type} {old_font} -> {font_family}")
                
                # 如果是主字体，重新应用全局字体
                if font_type == 'app':
                    self._apply_global_font()
                
                # 保存配置
                if save and self.config_manager:
                    self.config_manager.set_config(f'fonts.{font_type}', font_family)
                
                return True
            else:
                self.logger.warning(f"未知的字体类型: {font_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"设置字体配置失败: {e}")
            return False
    
    def load_font_config(self):
        """加载字体配置"""
        try:
            if not self.config_manager:
                return
            
            # 加载字体配置
            for font_type in self.default_fonts.keys():
                config_key = f'fonts.{font_type}'
                font_family = self.config_manager.get_config(config_key, self.default_fonts[font_type])
                self.default_fonts[font_type] = font_family
            
            # 重新应用全局字体
            self._apply_global_font()
            
            self.logger.info("字体配置已加载")
            
        except Exception as e:
            self.logger.error(f"加载字体配置失败: {e}")
    
    def get_font_info(self) -> Dict[str, str]:
        """获取字体信息"""
        try:
            info = {
                'fonts_dir': str(self.fonts_dir),
                'loaded_fonts_count': len(self.loaded_fonts),
                'current_fonts': self.default_fonts.copy(),
                'misans_available': 'MiSans-Light' in self.loaded_fonts
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"获取字体信息失败: {e}")
            return {}
    
    def install_font(self, font_file_path: str) -> bool:
        """安装字体文件"""
        try:
            source_path = Path(font_file_path)
            if not source_path.exists():
                self.logger.error(f"字体文件不存在: {font_file_path}")
                return False
            
            # 复制字体文件到字体目录
            target_path = self.fonts_dir / source_path.name
            
            if target_path.exists():
                self.logger.warning(f"字体文件已存在: {target_path}")
                return True
            
            import shutil
            shutil.copy2(source_path, target_path)

            # 加载字体
            success = self._load_font_file(target_path)

            if success:
                self.logger.info(f"字体安装成功: {source_path.name}")
                return True
            else:
                # 删除复制的文件
                target_path.unlink()
                return False
                
        except Exception as e:
            self.logger.error(f"安装字体失败: {e}")
            return False
