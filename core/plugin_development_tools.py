#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 插件开发工具
提供插件创建、测试、打包等开发功能
"""

import logging
import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

from core.base_manager import BaseManager


class PluginDevelopmentTools(BaseManager):
    """
    插件开发工具
    
    提供插件开发的完整工具链：
    - 插件模板生成
    - 插件测试
    - 插件打包
    - 插件验证
    """
    
    # 信号
    template_generated = pyqtSignal(str, str)  # template_type, output_path
    plugin_tested = pyqtSignal(str, bool, str)  # plugin_path, success, message
    plugin_packaged = pyqtSignal(str, str)  # plugin_path, package_path
    validation_completed = pyqtSignal(str, bool, list)  # plugin_path, is_valid, issues
    
    def __init__(self, config_manager=None):
        super().__init__(config_manager, "PluginDevelopmentTools")
        
        # 模板定义
        self.plugin_templates = {
            'basic': {
                'name': '基础插件模板',
                'description': '包含基本插件结构的模板',
                'files': ['main.py', 'plugin.json', 'README.md']
            },
            'ui_component': {
                'name': 'UI组件插件模板',
                'description': '用于创建UI组件的插件模板',
                'files': ['main.py', 'plugin.json', 'ui.py', 'resources.qrc', 'README.md']
            },
            'notification': {
                'name': '通知插件模板',
                'description': '用于扩展通知功能的插件模板',
                'files': ['main.py', 'plugin.json', 'notification_handler.py', 'README.md']
            },
            'theme': {
                'name': '主题插件模板',
                'description': '用于创建主题的插件模板',
                'files': ['main.py', 'plugin.json', 'theme.json', 'styles.qss', 'README.md']
            }
        }
        
        self.logger.info("插件开发工具初始化完成")
    
    def initialize(self) -> bool:
        """初始化开发工具"""
        try:
            self.logger.info("插件开发工具初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"插件开发工具初始化失败: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            self.logger.info("插件开发工具清理完成")
        except Exception as e:
            self.logger.error(f"插件开发工具清理失败: {e}")
    
    def get_available_templates(self) -> Dict[str, Dict[str, str]]:
        """获取可用的插件模板"""
        return self.plugin_templates
    
    def create_plugin_from_template(self, template_type: str, plugin_info: Dict[str, str], 
                                  output_dir: str) -> bool:
        """
        从模板创建插件
        
        Args:
            template_type: 模板类型
            plugin_info: 插件信息 (id, name, author, description, version)
            output_dir: 输出目录
            
        Returns:
            bool: 创建是否成功
        """
        try:
            if template_type not in self.plugin_templates:
                self.logger.error(f"未知的模板类型: {template_type}")
                return False
            
            template = self.plugin_templates[template_type]
            plugin_dir = Path(output_dir) / plugin_info['id']
            
            # 创建插件目录
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成插件文件
            for file_name in template['files']:
                file_path = plugin_dir / file_name
                content = self._generate_file_content(file_name, template_type, plugin_info)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 创建资源目录
            (plugin_dir / 'resources').mkdir(exist_ok=True)
            
            self.template_generated.emit(template_type, str(plugin_dir))
            self.logger.info(f"插件模板创建成功: {plugin_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建插件模板失败: {e}")
            return False
    
    def test_plugin(self, plugin_path: str) -> bool:
        """
        测试插件
        
        Args:
            plugin_path: 插件路径
            
        Returns:
            bool: 测试是否成功
        """
        try:
            plugin_dir = Path(plugin_path)
            
            # 检查插件结构
            issues = []
            
            # 检查必需文件
            required_files = ['main.py', 'plugin.json']
            for file_name in required_files:
                if not (plugin_dir / file_name).exists():
                    issues.append(f"缺少必需文件: {file_name}")
            
            # 验证plugin.json
            plugin_json_path = plugin_dir / 'plugin.json'
            if plugin_json_path.exists():
                try:
                    with open(plugin_json_path, 'r', encoding='utf-8') as f:
                        plugin_config = json.load(f)
                    
                    required_fields = ['id', 'name', 'version', 'main_class']
                    for field in required_fields:
                        if field not in plugin_config:
                            issues.append(f"plugin.json缺少必需字段: {field}")
                            
                except json.JSONDecodeError as e:
                    issues.append(f"plugin.json格式错误: {e}")
            
            # 检查Python语法
            main_py_path = plugin_dir / 'main.py'
            if main_py_path.exists():
                try:
                    with open(main_py_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    compile(code, str(main_py_path), 'exec')
                    
                except SyntaxError as e:
                    issues.append(f"main.py语法错误: {e}")
            
            # 尝试导入插件
            try:
                import sys
                import importlib.util
                
                spec = importlib.util.spec_from_file_location("test_plugin", main_py_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 检查是否有插件类
                    if hasattr(module, plugin_config.get('main_class', 'Plugin')):
                        self.logger.info("插件类导入成功")
                    else:
                        issues.append(f"未找到插件主类: {plugin_config.get('main_class', 'Plugin')}")
                        
            except Exception as e:
                issues.append(f"插件导入失败: {e}")
            
            success = len(issues) == 0
            message = "插件测试通过" if success else f"发现 {len(issues)} 个问题"
            
            self.plugin_tested.emit(plugin_path, success, message)
            
            if issues:
                self.logger.warning(f"插件测试发现问题: {issues}")
            else:
                self.logger.info("插件测试通过")
            
            return success
            
        except Exception as e:
            self.logger.error(f"插件测试失败: {e}")
            self.plugin_tested.emit(plugin_path, False, f"测试失败: {e}")
            return False
    
    def package_plugin(self, plugin_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        打包插件
        
        Args:
            plugin_path: 插件路径
            output_path: 输出路径（可选）
            
        Returns:
            str: 打包文件路径，失败返回None
        """
        try:
            plugin_dir = Path(plugin_path)
            
            if not plugin_dir.exists():
                self.logger.error(f"插件目录不存在: {plugin_path}")
                return None
            
            # 读取插件信息
            plugin_json_path = plugin_dir / 'plugin.json'
            if not plugin_json_path.exists():
                self.logger.error("缺少plugin.json文件")
                return None
            
            with open(plugin_json_path, 'r', encoding='utf-8') as f:
                plugin_config = json.load(f)
            
            plugin_id = plugin_config.get('id', 'unknown')
            plugin_version = plugin_config.get('version', '1.0.0')
            
            # 确定输出路径
            if output_path is None:
                output_path = plugin_dir.parent / f"{plugin_id}-{plugin_version}.tnp"
            else:
                output_path = Path(output_path)
            
            # 创建ZIP包
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in plugin_dir.rglob('*'):
                    if file_path.is_file():
                        # 排除临时文件和缓存
                        if any(exclude in str(file_path) for exclude in ['.pyc', '__pycache__', '.git']):
                            continue
                        
                        arcname = file_path.relative_to(plugin_dir)
                        zipf.write(file_path, arcname)
            
            self.plugin_packaged.emit(plugin_path, str(output_path))
            self.logger.info(f"插件打包成功: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"插件打包失败: {e}")
            return None
    
    def validate_plugin_package(self, package_path: str) -> bool:
        """
        验证插件包
        
        Args:
            package_path: 插件包路径
            
        Returns:
            bool: 验证是否通过
        """
        try:
            issues = []
            
            # 检查文件是否存在
            if not Path(package_path).exists():
                issues.append("插件包文件不存在")
                self.validation_completed.emit(package_path, False, issues)
                return False
            
            # 解压到临时目录进行验证
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(package_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # 验证解压后的插件
                temp_plugin_dir = Path(temp_dir)
                
                # 检查必需文件
                required_files = ['main.py', 'plugin.json']
                for file_name in required_files:
                    if not any(temp_plugin_dir.rglob(file_name)):
                        issues.append(f"缺少必需文件: {file_name}")
                
                # 验证plugin.json
                plugin_json_files = list(temp_plugin_dir.rglob('plugin.json'))
                if plugin_json_files:
                    try:
                        with open(plugin_json_files[0], 'r', encoding='utf-8') as f:
                            plugin_config = json.load(f)
                        
                        required_fields = ['id', 'name', 'version', 'main_class']
                        for field in required_fields:
                            if field not in plugin_config:
                                issues.append(f"plugin.json缺少必需字段: {field}")
                                
                    except json.JSONDecodeError as e:
                        issues.append(f"plugin.json格式错误: {e}")
            
            is_valid = len(issues) == 0
            self.validation_completed.emit(package_path, is_valid, issues)
            
            if is_valid:
                self.logger.info("插件包验证通过")
            else:
                self.logger.warning(f"插件包验证失败: {issues}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"插件包验证失败: {e}")
            self.validation_completed.emit(package_path, False, [f"验证失败: {e}"])
            return False
    
    def _generate_file_content(self, file_name: str, template_type: str, 
                             plugin_info: Dict[str, str]) -> str:
        """生成文件内容"""
        try:
            if file_name == 'plugin.json':
                return self._generate_plugin_json(plugin_info)
            elif file_name == 'main.py':
                return self._generate_main_py(template_type, plugin_info)
            elif file_name == 'README.md':
                return self._generate_readme(plugin_info)
            elif file_name == 'ui.py':
                return self._generate_ui_py(plugin_info)
            elif file_name == 'notification_handler.py':
                return self._generate_notification_handler(plugin_info)
            elif file_name == 'theme.json':
                return self._generate_theme_json(plugin_info)
            elif file_name == 'styles.qss':
                return self._generate_styles_qss(plugin_info)
            elif file_name == 'resources.qrc':
                return self._generate_resources_qrc(plugin_info)
            else:
                return f"# {file_name}\n# 由TimeNest插件开发工具生成\n"
                
        except Exception as e:
            self.logger.error(f"生成文件内容失败 {file_name}: {e}")
            return f"# 生成失败: {e}\n"
    
    def _generate_plugin_json(self, plugin_info: Dict[str, str]) -> str:
        """生成plugin.json"""
        config = {
            "id": plugin_info.get('id', 'my_plugin'),
            "name": plugin_info.get('name', 'My Plugin'),
            "version": plugin_info.get('version', '1.0.0'),
            "description": plugin_info.get('description', 'A TimeNest plugin'),
            "author": plugin_info.get('author', 'Plugin Developer'),
            "main_class": "Plugin",
            "api_version": "1.0.0",
            "min_app_version": "1.0.0",
            "dependencies": [],
            "permissions": [],
            "tags": ["utility"],
            "homepage": "",
            "repository": "",
            "license": "MIT"
        }
        
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def _generate_main_py(self, template_type: str, plugin_info: Dict[str, str]) -> str:
        """生成main.py"""
        plugin_name = plugin_info.get('name', 'My Plugin')
        plugin_id = plugin_info.get('id', 'my_plugin')
        author = plugin_info.get('author', 'Plugin Developer')
        
        if template_type == 'basic':
            return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{plugin_name}
作者: {author}
"""

import logging
from core.plugin_system import IPlugin, PluginMetadata, PluginStatus


class Plugin(IPlugin):
    """
    {plugin_name}插件
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{{__name__}}.{plugin_id}')
        self.status = PluginStatus.LOADED
        
    def get_metadata(self) -> PluginMetadata:
        """获取插件元数据"""
        # 这里会从plugin.json自动加载
        return self.metadata
    
    def initialize(self, plugin_manager) -> bool:
        """初始化插件"""
        try:
            self.logger.info("{plugin_name}插件初始化")
            # 在这里添加初始化代码
            return True
        except Exception as e:
            self.logger.error(f"插件初始化失败: {{e}}")
            return False
    
    def activate(self) -> bool:
        """激活插件"""
        try:
            self.logger.info("{plugin_name}插件激活")
            # 在这里添加激活代码
            return True
        except Exception as e:
            self.logger.error(f"插件激活失败: {{e}}")
            return False
    
    def deactivate(self) -> bool:
        """停用插件"""
        try:
            self.logger.info("{plugin_name}插件停用")
            # 在这里添加停用代码
            return True
        except Exception as e:
            self.logger.error(f"插件停用失败: {{e}}")
            return False
    
    def cleanup(self) -> None:
        """清理插件资源"""
        try:
            self.logger.info("{plugin_name}插件清理")
            # 在这里添加清理代码
        except Exception as e:
            self.logger.error(f"插件清理失败: {{e}}")
    
    def get_status(self) -> PluginStatus:
        """获取插件状态"""
        return self.status
'''
        else:
            # 其他模板类型的基础结构
            return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{plugin_name}
作者: {author}
"""

import logging
from core.plugin_system import IPlugin, PluginMetadata, PluginStatus


class Plugin(IPlugin):
    """
    {plugin_name}插件
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f'{{__name__}}.{plugin_id}')
        self.status = PluginStatus.LOADED
        
    # TODO: 实现插件接口方法
    # 请参考IPlugin接口文档
'''
    
    def _generate_readme(self, plugin_info: Dict[str, str]) -> str:
        """生成README.md"""
        plugin_name = plugin_info.get('name', 'My Plugin')
        description = plugin_info.get('description', 'A TimeNest plugin')
        author = plugin_info.get('author', 'Plugin Developer')
        version = plugin_info.get('version', '1.0.0')
        
        return f'''# {plugin_name}

{description}

## 信息

- **版本**: {version}
- **作者**: {author}
- **兼容性**: TimeNest 1.0.0+

## 功能

- 功能1
- 功能2
- 功能3

## 安装

1. 下载插件包
2. 在TimeNest中打开插件管理器
3. 点击"安装本地插件"
4. 选择插件包文件

## 使用

插件安装后会自动激活，您可以在设置中配置插件选项。

## 开发

本插件使用TimeNest插件开发工具生成。

## 许可证

MIT License
'''
    
    def _generate_ui_py(self, plugin_info: Dict[str, str]) -> str:
        """生成ui.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件模块
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class PluginWidget(QWidget):
    """插件UI组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        label = QLabel("插件UI组件")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # 在这里添加更多UI组件
'''
    
    def _generate_notification_handler(self, plugin_info: Dict[str, str]) -> str:
        """生成notification_handler.py"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知处理模块
"""

import logging
from typing import Dict, Any


class NotificationHandler:
    """通知处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'{__name__}.NotificationHandler')
    
    def handle_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        处理通知
        
        Args:
            notification_data: 通知数据
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # 在这里实现通知处理逻辑
            self.logger.info(f"处理通知: {notification_data}")
            return True
        except Exception as e:
            self.logger.error(f"通知处理失败: {e}")
            return False
'''
    
    def _generate_theme_json(self, plugin_info: Dict[str, str]) -> str:
        """生成theme.json"""
        theme_config = {
            "name": plugin_info.get('name', 'My Theme'),
            "version": plugin_info.get('version', '1.0.0'),
            "author": plugin_info.get('author', 'Theme Developer'),
            "description": "自定义主题",
            "colors": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "background": "#ffffff",
                "text": "#2c3e50",
                "accent": "#e74c3c"
            },
            "fonts": {
                "default": "Microsoft YaHei",
                "size": 12
            }
        }
        
        return json.dumps(theme_config, indent=2, ensure_ascii=False)
    
    def _generate_styles_qss(self, plugin_info: Dict[str, str]) -> str:
        """生成styles.qss"""
        return '''/* 主题样式文件 */

/* 主要颜色 */
QWidget {
    background-color: #ffffff;
    color: #2c3e50;
    font-family: "Microsoft YaHei";
    font-size: 12px;
}

/* 按钮样式 */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

/* 在这里添加更多样式 */
'''
    
    def _generate_resources_qrc(self, plugin_info: Dict[str, str]) -> str:
        """生成resources.qrc"""
        return '''<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource>
        <!-- 在这里添加资源文件 -->
        <!-- <file>icons/icon.png</file> -->
    </qresource>
</RCC>
'''
