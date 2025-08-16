"""
后端服务入口文件
"""

import sys
import os

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from backend.api.courses import courses_bp
from backend.api.schedules import schedules_bp
from backend.api.temp_changes import temp_changes_bp
from backend.api.settings import settings_bp
from backend.api.today_schedule import today_schedule_bp
from backend.api.weather import weather_bp

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 注册蓝图
    app.register_blueprint(courses_bp, url_prefix='/api')
    app.register_blueprint(schedules_bp, url_prefix='/api')
    app.register_blueprint(temp_changes_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')
    app.register_blueprint(today_schedule_bp, url_prefix='/api')
    app.register_blueprint(weather_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)