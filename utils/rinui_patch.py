"""
RinUI配置文件修复补丁
在导入RinUI之前修复配置文件问题
"""

import os
import sys
import json
import tempfile
import logging
from pathlib import Path

def patch_rinui_config():
    """修复RinUI配置文件问题"""
    try:
        # 创建临时配置文件
        temp_dir = tempfile.gettempdir()
        temp_config_dir = Path(temp_dir) / "RinUI" / "config"
        temp_config_dir.mkdir(parents=True, exist_ok=True)
        
        temp_config_file = temp_config_dir / "rin_ui.json"
        
        # 默认配置
        default_config = {
            "theme": {
                "current_theme": "Auto"
            },
            "win10_feat": {
                "backdrop_light": 2801795071,
                "backdrop_dark": 2785017856
            },
            "theme_color": "#605ed2",
            "backdrop_effect": "none"
        }
        
        # 写入配置文件
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        # 设置环境变量，让RinUI使用临时配置
        os.environ['RINUI_CONFIG_PATH'] = str(temp_config_dir)
        
        logging.info(f"创建临时RinUI配置: {temp_config_file}")
        return True
        
    except Exception as e:
        logging.error(f"创建临时RinUI配置失败: {e}")
        return False

def monkey_patch_json_load():
    """猴子补丁：修复json.load的空文件问题"""
    import json
    original_load = json.load
    original_loads = json.loads
    
    def safe_load(fp, **kwargs):
        try:
            content = fp.read()
            if not content.strip():
                # 如果文件为空，返回默认配置
                return {
                    "theme": {"current_theme": "Auto"},
                    "win10_feat": {"backdrop_light": 2801795071, "backdrop_dark": 2785017856},
                    "theme_color": "#605ed2",
                    "backdrop_effect": "none"
                }
            fp.seek(0)  # 重置文件指针
            return original_load(fp, **kwargs)
        except json.JSONDecodeError:
            # JSON解析错误时返回默认配置
            return {
                "theme": {"current_theme": "Auto"},
                "win10_feat": {"backdrop_light": 2801795071, "backdrop_dark": 2785017856},
                "theme_color": "#605ed2",
                "backdrop_effect": "none"
            }
    
    def safe_loads(s, **kwargs):
        try:
            if not s.strip():
                return {
                    "theme": {"current_theme": "Auto"},
                    "win10_feat": {"backdrop_light": 2801795071, "backdrop_dark": 2785017856},
                    "theme_color": "#605ed2",
                    "backdrop_effect": "none"
                }
            return original_loads(s, **kwargs)
        except json.JSONDecodeError:
            return {
                "theme": {"current_theme": "Auto"},
                "win10_feat": {"backdrop_light": 2801795071, "backdrop_dark": 2785017856},
                "theme_color": "#605ed2",
                "backdrop_effect": "none"
            }
    
    json.load = safe_load
    json.loads = safe_loads
    logging.info("应用JSON加载补丁")

def apply_rinui_patches():
    """应用所有RinUI补丁"""
    try:
        # 应用JSON补丁
        monkey_patch_json_load()
        
        # 创建临时配置
        patch_rinui_config()
        
        # 设置其他环境变量
        os.environ.setdefault('QT_QPA_PLATFORM_PLUGIN_PATH', '')
        os.environ.setdefault('QT_PLUGIN_PATH', '')
        
        return True
    except Exception as e:
        logging.error(f"应用RinUI补丁失败: {e}")
        return False
