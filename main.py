#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TimeNest - 智能课程表桌面应用
完整重构自ClassIsland的C#实现
"""

# 导入必要的模块
import logging

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from core.application import TimeNestApplication


def setup_logging():
    """配置应用程序日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("TimeNest.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)


def get_app_data_path():
    """获取应用数据目录，按平台规范设置"""
    if sys.platform == "win32":
        # Windows: %APPDATA%\TimeNest\
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "TimeNest"
        # 如果APPDATA环境变量不存在，使用用户目录下的.config
        return Path.home() / ".config" / "TimeNest"
    if sys.platform == "darwin":
        # macOS: ~/Library/Application Support/TimeNest/
        return Path.home() / "Library" / "Application Support" / "TimeNest"
    # Linux和其他类Unix系统: ~/.config/TimeNest/
    config_home = os.environ.get("XDG_CONFIG_HOME", "")
    if config_home:
        return Path(config_home) / "TimeNest"
    return Path.home() / ".config" / "TimeNest"


def main():
    """应用程序主入口点"""
    logger = setup_logging()

    try:
        # 创建应用数据目录
        app_data_path = get_app_data_path()
        app_data_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"应用数据目录: {app_data_path}")

        # 创建并运行应用程序
        logger.info("启动TimeNest应用程序")
        app = TimeNestApplication(sys.argv)
        exit_code = app.run()
        app.shutdown()

        logger.info("TimeNest应用程序已退出")
        return exit_code

    except Exception as e:
        logger.error(f"启动TimeNest时发生错误: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
