"""
RinUI初始化和配置管理模块
确保RinUI正确初始化，处理配置文件问题
"""

import os
import sys
import json
import logging
from pathlib import Path

def ensure_rinui_config():
    """确保RinUI配置文件存在且格式正确"""
    try:
        # 获取应用程序目录
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径
            app_dir = Path(sys._MEIPASS)
        else:
            # 开发环境路径
            app_dir = Path(__file__).parent.parent
        
        # RinUI配置目录和文件路径
        rinui_config_dir = app_dir / "RinUI" / "config"
        rinui_config_file = rinui_config_dir / "rin_ui.json"
        
        # 确保配置目录存在
        rinui_config_dir.mkdir(parents=True, exist_ok=True)
        
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
        
        # 检查配置文件是否存在且有效
        config_valid = False
        if rinui_config_file.exists():
            try:
                with open(rinui_config_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        json.loads(content)  # 验证JSON格式
                        config_valid = True
                        logging.info("RinUI配置文件验证成功")
            except (json.JSONDecodeError, Exception) as e:
                logging.warning(f"RinUI配置文件格式错误: {e}")
        
        # 如果配置文件不存在或无效，创建默认配置
        if not config_valid:
            try:
                with open(rinui_config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                logging.info(f"创建RinUI默认配置文件: {rinui_config_file}")
            except Exception as e:
                logging.error(f"创建RinUI配置文件失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        logging.error(f"RinUI配置初始化失败: {e}")
        return False

def init_rinui_safely():
    """安全地初始化RinUI"""
    try:
        # 确保配置文件存在
        if not ensure_rinui_config():
            logging.warning("RinUI配置初始化失败，但继续尝试导入")

        # 设置环境变量，防止RinUI配置文件错误
        import tempfile
        temp_dir = tempfile.gettempdir()
        os.environ.setdefault('RINUI_CONFIG_DIR', temp_dir)

        # 尝试导入RinUI
        import RinUI
        from RinUI import RinUIWindow

        logging.info("RinUI导入成功")
        return True, RinUI, RinUIWindow

    except json.JSONDecodeError as e:
        logging.error(f"RinUI配置文件JSON错误: {e}")
        # 尝试重新创建配置文件
        try:
            ensure_rinui_config()
            import RinUI
            from RinUI import RinUIWindow
            return True, RinUI, RinUIWindow
        except:
            return False, None, None
    except ImportError as e:
        logging.error(f"RinUI导入失败: {e}")
        return False, None, None
    except Exception as e:
        logging.error(f"RinUI初始化异常: {e}")
        # 如果是配置相关错误，尝试使用临时配置
        if "config" in str(e).lower() or "json" in str(e).lower():
            try:
                # 创建临时配置
                temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                default_config = {
                    "theme": {"current_theme": "Auto"},
                    "win10_feat": {"backdrop_light": 2801795071, "backdrop_dark": 2785017856},
                    "theme_color": "#605ed2",
                    "backdrop_effect": "none"
                }
                json.dump(default_config, temp_config, indent=4)
                temp_config.close()

                # 设置环境变量指向临时配置
                os.environ['RINUI_CONFIG_FILE'] = temp_config.name

                import RinUI
                from RinUI import RinUIWindow
                return True, RinUI, RinUIWindow
            except:
                pass
        return False, None, None

def setup_rinui_environment():
    """设置RinUI运行环境"""
    try:
        # 设置环境变量
        os.environ.setdefault('QT_QPA_PLATFORM_PLUGIN_PATH', '')
        os.environ.setdefault('QT_PLUGIN_PATH', '')
        
        # 如果是Windows，设置DPI感知
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
        return True
    except Exception as e:
        logging.error(f"RinUI环境设置失败: {e}")
        return False

def get_rinui_fallback():
    """获取RinUI的备用实现"""
    class FallbackRinUIWindow:
        def __init__(self, *args, **kwargs):
            logging.warning("使用RinUI备用实现")
            self.app = None
        
        def show(self):
            pass
        
        def exec(self):
            return 0
    
    class FallbackRinUI:
        RinUIWindow = FallbackRinUIWindow
    
    return FallbackRinUI, FallbackRinUIWindow
