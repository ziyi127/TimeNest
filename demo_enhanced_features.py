#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TimeNest 增强功能演示脚本
展示所有新实现的功能特性
"""

import sys
import logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QHBoxLayout
from PyQt6.QtCore import QTimer

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class EnhancedFeaturesDemo(QMainWindow):
    """增强功能演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TimeNest 增强功能演示")
        self.setGeometry(100, 100, 800, 600)
        
        self.setup_ui()
        self.init_components()
    
    def setup_ui(self):
        """设置界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.remind_button = QPushButton("演示 Remind API v2")
        self.remind_button.clicked.connect(self.demo_remind_api)
        button_layout.addWidget(self.remind_button)
        
        self.export_button = QPushButton("演示 Excel导出增强")
        self.export_button.clicked.connect(self.demo_excel_export)
        button_layout.addWidget(self.export_button)
        
        self.plugin_button = QPushButton("演示 插件交互")
        self.plugin_button.clicked.connect(self.demo_plugin_interaction)
        button_layout.addWidget(self.plugin_button)
        
        self.floating_button = QPushButton("演示 浮窗模块")
        self.floating_button.clicked.connect(self.demo_floating_modules)
        button_layout.addWidget(self.floating_button)
        
        layout.addLayout(button_layout)
        
        # 输出区域
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # 清除按钮
        clear_button = QPushButton("清除输出")
        clear_button.clicked.connect(self.output_text.clear)
        layout.addWidget(clear_button)
    
    def init_components(self):
        """初始化组件"""
        self.log("TimeNest 增强功能演示系统启动")
        self.log("=" * 50)
    
    def log(self, message: str):
        """记录日志到输出区域"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.append(f"[{timestamp}] {message}")
    
    def demo_remind_api(self):
        """演示 Remind API v2"""
        self.log("\n🔔 演示 Remind API v2 功能")
        
        try:
            from core.remind_api_v2 import (
                RemindAPIv2, ChainedReminder, ReminderAction, 
                ReminderCondition, ReminderChannel, ReminderPriority
            )
            
            # 创建模拟应用管理器
            class MockAppManager:
                def __init__(self):
                    self.notification_manager = None
                    self.floating_manager = None
            
            app_manager = MockAppManager()
            remind_api = RemindAPIv2(app_manager)
            
            # 创建课程提醒链
            self.log("创建课程提醒链...")
            
            # 条件：5秒后触发
            condition = ReminderCondition(
                type="time",
                value=(datetime.now() + timedelta(seconds=5)).isoformat(),
                operator="<="
            )
            
            # 动作：弹窗提醒
            action = ReminderAction(
                channel=ReminderChannel.POPUP,
                title="课程提醒",
                message="高等数学课程即将开始！请准备好课本和笔记。"
            )
            
            # 创建链式提醒
            reminder = ChainedReminder(
                id="course_reminder_demo",
                name="课程开始提醒",
                description="提醒学生课程即将开始",
                conditions=[condition],
                actions=[action],
                priority=ReminderPriority.HIGH
            )
            
            # 添加提醒
            success = remind_api.add_reminder(reminder)
            self.log(f"✓ 添加提醒: {'成功' if success else '失败'}")
            
            # 显示提醒信息
            reminders = remind_api.get_reminders()
            self.log(f"✓ 当前提醒数量: {len(reminders)}")
            
            for r in reminders:
                self.log(f"  - {r.name}: {r.status.value}")
            
            self.log("⏰ 提醒将在5秒后触发...")
            
            # 清理
            QTimer.singleShot(10000, lambda: remind_api.cleanup())
            
        except Exception as e:
            self.log(f"✗ Remind API v2 演示失败: {e}")
    
    def demo_excel_export(self):
        """演示 Excel导出增强"""
        self.log("\n📊 演示 Excel导出增强功能")
        
        try:
            from core.excel_export_enhanced import (
                ExcelExportEnhanced, ExportOptions, ExportTemplate, ExportFormat
            )
            
            exporter = ExcelExportEnhanced()
            
            # 创建示例课程数据
            schedule_data = {
                'courses': [
                    {
                        'id': 'math_001',
                        'name': '高等数学A',
                        'teacher': '张教授',
                        'classroom': '理学楼A101',
                        'day': 0,  # 周一
                        'start_time': '08:00',
                        'end_time': '09:40',
                        'credits': 4,
                        'course_type': '必修课',
                        'start_week': 1,
                        'end_week': 16
                    },
                    {
                        'id': 'eng_001',
                        'name': '大学英语',
                        'teacher': '李老师',
                        'classroom': '文科楼B203',
                        'day': 1,  # 周二
                        'start_time': '10:00',
                        'end_time': '11:40',
                        'credits': 2,
                        'course_type': '必修课',
                        'start_week': 1,
                        'end_week': 16
                    },
                    {
                        'id': 'phy_001',
                        'name': '大学物理',
                        'teacher': '王教授',
                        'classroom': '理学楼C305',
                        'day': 2,  # 周三
                        'start_time': '14:00',
                        'end_time': '15:40',
                        'credits': 3,
                        'course_type': '必修课',
                        'start_week': 1,
                        'end_week': 16
                    }
                ]
            }
            
            self.log("创建示例课程数据...")
            self.log(f"✓ 课程数量: {len(schedule_data['courses'])}")
            
            # 演示不同模板和格式
            export_demos = [
                (ExportTemplate.BASIC, ExportFormat.CSV, "basic_schedule.csv"),
                (ExportTemplate.DETAILED, ExportFormat.HTML, "detailed_schedule.html"),
                (ExportTemplate.STATISTICS, ExportFormat.CSV, "statistics_report.csv")
            ]
            
            for template, format_type, filename in export_demos:
                self.log(f"导出 {template.value} 模板到 {format_type.value.upper()}...")
                
                options = ExportOptions(
                    template=template,
                    format=format_type,
                    include_statistics=True,
                    include_teacher_info=True,
                    include_classroom_info=True,
                    custom_title="TimeNest 演示课程表",
                    font_size=12
                )
                
                success = exporter.export_schedule(schedule_data, filename, options)
                self.log(f"  {'✓' if success else '✗'} {filename}: {'成功' if success else '失败'}")
            
            # 显示可用模板
            templates = exporter.get_available_templates()
            self.log(f"✓ 可用导出模板: {len(templates)} 个")
            for template_id, template_info in templates.items():
                self.log(f"  - {template_info['name']}: {template_info['description']}")
            
        except Exception as e:
            self.log(f"✗ Excel导出增强演示失败: {e}")
    
    def demo_plugin_interaction(self):
        """演示 插件交互"""
        self.log("\n🔌 演示 插件交互增强功能")
        
        try:
            from core.plugin_interaction_enhanced import (
                PluginInteractionManager, PluginInterface
            )
            
            manager = PluginInteractionManager()
            
            # 创建示例插件接口
            self.log("创建示例插件接口...")
            
            def calculate_gpa(grades: list) -> float:
                """计算GPA"""
                if not grades:
                    return 0.0
                return sum(grades) / len(grades)
            
            def format_schedule(courses: list) -> str:
                """格式化课程表"""
                if not courses:
                    return "无课程安排"
                
                result = "课程安排:\n"
                for course in courses:
                    result += f"- {course.get('name', '未知课程')}\n"
                return result
            
            # 创建学术工具接口
            academic_interface = PluginInterface(
                name="academic_tools",
                version="1.0.0",
                description="学术工具插件接口"
            )
            academic_interface.add_method("calculate_gpa", calculate_gpa)
            academic_interface.add_method("format_schedule", format_schedule)
            academic_interface.add_event("gpa_calculated")
            academic_interface.add_event("schedule_formatted")
            
            # 注册接口
            success = manager.register_plugin_interface("academic_plugin", academic_interface)
            self.log(f"✓ 注册学术工具接口: {'成功' if success else '失败'}")
            
            # 演示方法调用
            self.log("演示接口方法调用...")
            
            # 计算GPA
            test_grades = [85, 92, 78, 88, 95]
            gpa = manager.call_plugin_method("academic_tools", "calculate_gpa", test_grades)
            self.log(f"✓ 计算GPA: {gpa:.2f}")
            
            # 格式化课程表
            test_courses = [
                {"name": "高等数学"},
                {"name": "大学英语"},
                {"name": "大学物理"}
            ]
            formatted = manager.call_plugin_method("academic_tools", "format_schedule", test_courses)
            self.log(f"✓ 格式化课程表:\n{formatted}")
            
            # 演示事件系统
            self.log("演示事件系统...")
            
            def on_calculation_event(data):
                self.log(f"  📢 收到计算事件: {data}")
            
            manager.subscribe_event("calculation_performed", on_calculation_event)
            manager.publish_event("calculation_performed", {
                "type": "gpa",
                "result": gpa,
                "timestamp": datetime.now().isoformat()
            })
            
            # 显示统计信息
            interfaces = manager.get_available_interfaces()
            stats = manager.get_call_statistics()
            
            self.log(f"✓ 可用接口: {len(interfaces)} 个")
            self.log(f"✓ 方法调用统计: {stats}")
            
            # 清理
            manager.cleanup()
            
        except Exception as e:
            self.log(f"✗ 插件交互演示失败: {e}")
    
    def demo_floating_modules(self):
        """演示 浮窗模块"""
        self.log("\n🎈 演示 增强浮窗模块功能")
        
        try:
            from ui.floating_widget.enhanced_modules import (
                EnhancedFloatingModules, ScrollingTextWidget, WeatherWidget
            )
            
            modules = EnhancedFloatingModules()
            
            self.log("创建增强浮窗模块...")
            
            # 创建滚动文本
            scrolling_text = modules.create_scrolling_text(
                "欢迎使用 TimeNest 智能课程管理系统！这是一个滚动文本演示。"
            )
            self.log("✓ 滚动文本模块创建成功")
            
            # 创建天气组件
            weather_widget = modules.create_weather_widget()
            weather_widget.set_city("北京")
            self.log("✓ 天气组件创建成功")
            
            # 创建轮播组件
            carousel = modules.create_carousel()
            self.log("✓ 轮播组件创建成功")
            
            # 创建进度条
            progress_bar = modules.create_progress_bar()
            progress_bar.set_progress(75)
            self.log("✓ 动画进度条创建成功 (进度: 75%)")
            
            # 创建通知横幅
            notification_banner = modules.create_notification_banner()
            notification_banner.show_message("这是一个演示通知消息", 3000)
            self.log("✓ 通知横幅创建成功")
            
            # 显示模块信息
            module_count = len(modules.modules)
            self.log(f"✓ 总共创建了 {module_count} 个增强模块")
            
            for name, module in modules.modules.items():
                self.log(f"  - {name}: {type(module).__name__}")
            
            # 演示模块功能
            self.log("演示模块功能...")
            
            # 更新滚动文本
            scrolling_text.set_text("文本内容已更新！TimeNest 功能强大且易用。")
            self.log("✓ 滚动文本内容已更新")
            
            # 设置进度条动画
            QTimer.singleShot(1000, lambda: progress_bar.set_progress(100))
            self.log("✓ 进度条将在1秒后更新到100%")
            
            # 延迟清理
            QTimer.singleShot(5000, modules.cleanup)
            self.log("✓ 模块将在5秒后自动清理")
            
        except Exception as e:
            self.log(f"✗ 浮窗模块演示失败: {e}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建演示窗口
    demo = EnhancedFeaturesDemo()
    demo.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
