import tkinter as tk
from tkinter import ttk
import json
import os
import datetime
import platform
import logging
from pathlib import Path
import traceback

class DragWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 平台检测
        self.platform = platform.system().lower()
        
        # 获取跨平台文档路径
        self.doc_path = self._get_documents_path()
        self.doc_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化日志
        self.logger = logging.getLogger(__name__)
        
        # 设置窗口属性
        self.title("课程表")
        self.geometry("250x120")  # 调整窗口大小
        self.configure(bg='#2c3e50')
        
        # 设置窗口置顶和无边框
        self.wm_attributes("-topmost", True)
        self.overrideredirect(True)
        
        # 设置窗口透明度
        self.wm_attributes("-alpha", 0.85)
        
        # 设置窗口样式（仅Windows）
        if self.platform == "windows":
            self.wm_attributes("-toolwindow", True)
        
        # 初始化可拖动状态
        self.is_draggable = False
        self.pointer_passthrough = False  # 指针穿透状态
        
        # 初始化after任务ID列表
        self.after_ids = []
        
        # 初始化更新任务ID
        self.update_job = None
        
        # 定义主题配色方案（确保在加载前定义）
        self.themes = {
            "dark": {
                "bg_color": "#1a1a1a",
                "text_color": "#ffffff",
                "text_color_secondary": "#b3b3b3",
                "accent_color": "#00d4ff",
                "border_color": "#333333"
            },
            "light": {
                "bg_color": "#ffffff",
                "text_color": "#1a1a1a",
                "text_color_secondary": "#666666",
                "accent_color": "#0066cc",
                "border_color": "#e0e0e0"
            },
            "glass": {
                "bg_color": "#f8f9fa",
                "text_color": "#2c3e50",
                "text_color_secondary": "#7f8c8d",
                "accent_color": "#3498db",
                "border_color": "#bdc3c7"
            }
        }
        
        # 确保属性存在默认值
        self.current_theme = "dark"
        self.background_color = self.themes["dark"]["bg_color"]
        self.text_color = self.themes["dark"]["text_color"]
        self.text_color_secondary = self.themes["dark"]["text_color_secondary"]
        self.accent_color = self.themes["dark"]["accent_color"]
        self.border_color = self.themes["dark"]["border_color"]
        self.transparency = 0.85
        
        # 加载UI设置
        self.load_ui_settings()
        
        # 加载窗口位置
        self.load_window_position()
        
        # 配置背景颜色
        self.configure(bg=self.background_color)
        
        # 创建主框架 - 使用更现代的布局
        self.main_frame = tk.Frame(self, bg=self.background_color, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # 创建时间框架 - 使用网格布局
        self.time_frame = tk.Frame(self.main_frame, bg=self.background_color, highlightthickness=0)
        self.time_frame.pack(anchor='w', pady=(0, 8))
        
        # 创建时间标签 - 使用更现代的字体
        self.time_label = tk.Label(
            self.time_frame, 
            font=("Segoe UI", 28, "bold"), 
            bg=self.background_color, 
            fg=self.text_color,
            highlightthickness=0
        )
        self.time_label.pack(side='left', anchor='w')
        
        # 创建日期和星期标签 - 使用更优雅的字体
        self.date_label = tk.Label(
            self.time_frame, 
            font=("Segoe UI", 11), 
            bg=self.background_color, 
            fg=self.text_color_secondary,
            highlightthickness=0
        )
        self.date_label.pack(side='left', padx=(12, 0), anchor='s')
        
        # 创建分隔线 - 增加视觉层次
        self.separator = tk.Frame(
            self.main_frame, 
            height=1, 
            bg=self.border_color,
            highlightthickness=0
        )
        self.separator.pack(fill=tk.X, pady=(0, 10))
        
        # 创建课程信息容器
        self.info_container = tk.Frame(self.main_frame, bg=self.background_color, highlightthickness=0)
        self.info_container.pack(fill=tk.X, expand=True)
        
        # 创建课程信息标签 - 使用更清晰的字体层次
        self.class_info_label = tk.Label(
            self.info_container, 
            font=("Segoe UI", 11), 
            bg=self.background_color, 
            fg=self.text_color,
            wraplength=220,
            justify='left',
            highlightthickness=0
        )
        self.class_info_label.pack(anchor='w', pady=(0, 6))
        
        # 创建下一节课信息标签 - 使用强调色
        self.next_class_label = tk.Label(
            self.info_container, 
            font=("Segoe UI", 10), 
            bg=self.background_color, 
            fg=self.accent_color,
            wraplength=220,
            justify='left',
            highlightthickness=0
        )
        self.next_class_label.pack(anchor='w')
        
        # 设置初始鼠标穿透状态
        self.after(100, self._initialize_transparency)
        
    def _setup_platform_specific_window(self):
        """设置平台特定的窗口属性"""
        try:
            if self.platform == "windows":
                # Windows特定设置 - 使用更平滑的窗口边缘
                self.wm_attributes("-transparentcolor", "")
                # 移除窗口装饰
                self.overrideredirect(True)
            elif self.platform == "darwin":
                # macOS特定设置
                self.wm_attributes("-transparent", True)
                self.configure(highlightthickness=0)
            elif self.platform == "linux":
                # Linux特定设置
                self.configure(highlightthickness=0)
        except Exception as e:
            self.logger.warning(f"平台特定窗口设置失败: {e}")

    def _initialize_transparency(self):
        """初始化透明度设置（跨平台兼容）"""
        # 应用圆角效果（平台特定）
        self._apply_rounded_corners()
        
        if not self.is_draggable:
            # 不允许编辑时，鼠标事件穿透到后方界面
            try:
                # 使用更优雅的透明度值
                alpha_value = 0.85
                
                # 平台特定的透明度设置
                if self.platform == "darwin":
                    alpha_value = 0.9
                elif self.platform == "linux":
                    alpha_value = 0.8
                
                self.wm_attributes("-alpha", alpha_value)
                self.logger.info(f"设置窗口透明度为{alpha_value}")
                
            except Exception as e:
                self.logger.error(f"设置透明度时出错: {e}")
                # 尝试使用默认值
                try:
                    self.wm_attributes("-alpha", 0.9)
                    self.logger.info("使用默认透明度0.9")
                except Exception as e2:
                    self.logger.error(f"设置默认透明度失败: {e2}")
                    
            # 确保所有组件背景色一致
            self._update_all_colors()
            self.logger.info(f"UI主题已应用: {self.background_color}")
        else:
            self.logger.info("窗口已启用，鼠标事件被拦截")

    def _apply_rounded_corners(self):
        """应用圆角效果（Windows平台特定）"""
        if self.platform == "windows":
            try:
                # Windows 11风格的圆角窗口
                import ctypes
                from ctypes import wintypes
                
                # 设置窗口样式
                GWL_STYLE = -16
                WS_POPUP = 0x80000000
                WS_BORDER = 0x00800000
                WS_SYSMENU = 0x00080000
                
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                style = style & ~WS_BORDER & ~WS_SYSMENU
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
                
                self.logger.info("已应用Windows圆角窗口效果")
            except Exception as e:
                self.logger.debug(f"圆角效果设置失败: {e}")
        
        # 加载课程表
        self.timetable = self.load_timetable()
        
        # 绑定鼠标事件
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.on_motion)
        
        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建右键菜单
        self._create_context_menu()
        
        # 应用UI设置到组件
        self._update_all_colors()
        
        # 记录窗口初始化信息
        self.logger.info("窗口初始化完成")
        self.logger.info(f"  位置: ({self.winfo_x()}, {self.winfo_y()})")
        self.logger.info(f"  大小: {self.winfo_width()}x{self.winfo_height()}")
        self.logger.info(f"  透明度: {self.wm_attributes('-alpha')}")
        self.logger.info(f"  平台: {self.platform}")
        self.logger.info(f"  文档路径: {self.doc_path}")
        
        # 开始更新时间
        self.update_time()
    
    def _create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)
        
        # 指针穿透开关
        self.context_menu.add_command(label="启用指针穿透", command=self._toggle_pointer_passthrough)
        self.context_menu.add_separator()
        
        # UI设置
        self.context_menu.add_command(label="UI设置", command=self._open_ui_settings)
        self.context_menu.add_separator()
        
        self.context_menu.add_command(label="退出", command=self.on_closing)
        
        # 绑定右键菜单
        self.bind("<Button-3>", self._show_context_menu)
        self.bind("<Button-2>", self._show_context_menu)  # macOS右键
        
        self.logger.info("右键菜单已创建")
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        try:
            # 更新指针穿透菜单项文本
            if self.pointer_passthrough:
                self.context_menu.entryconfig(0, label="禁用指针穿透")
            else:
                self.context_menu.entryconfig(0, label="启用指针穿透")
            
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _toggle_pointer_passthrough(self):
        """切换指针穿透状态"""
        try:
            self.pointer_passthrough = not self.pointer_passthrough
            
            if self.platform == "windows":
                import ctypes
                from ctypes import wintypes
                
                # Windows API常量
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                
                # 获取窗口句柄
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                
                # 获取当前扩展样式
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                
                if self.pointer_passthrough:
                    # 添加透明样式
                    new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                    self.logger.info("启用指针穿透")
                else:
                    # 移除透明样式
                    new_style = current_style & ~WS_EX_TRANSPARENT
                    self.logger.info("禁用指针穿透")
                
                # 设置新样式
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                
            else:
                # 其他平台暂时不支持指针穿透
                messagebox.showinfo("提示", "当前平台暂不支持指针穿透功能")
                self.pointer_passthrough = False
                
        except Exception as e:
            self.logger.error(f"切换指针穿透时出错: {e}")
            messagebox.showerror("错误", f"切换指针穿透失败: {str(e)}")
    
    def _open_ui_settings(self):
        """打开UI设置窗口"""
        try:
            from .ui_settings import UISettings
            settings_window = UISettings(self)
            settings_window.grab_set()  # 模态窗口
        except Exception as e:
            self.logger.error(f"打开UI设置时出错: {e}")
            messagebox.showerror("错误", f"打开UI设置失败: {str(e)}")
    

    
    def _apply_background_and_transparency(self):
        """应用背景色和透明度设置"""
        try:
            # 重新设置背景色
            self.configure(bg=self.background_color)
            self.main_frame.configure(bg=self.background_color)
            self.time_label.configure(bg=self.background_color)
            self.date_label.configure(bg=self.background_color)
            self.class_info_label.configure(bg=self.background_color)
            self.next_class_label.configure(bg=self.background_color)
            
            # 应用透明度
            alpha = self.transparency / 100.0
            alpha = max(0.1, min(1.0, alpha))  # 限制透明度范围
            
            try:
                self.wm_attributes("-alpha", alpha)
                self.logger.info(f"应用透明度: {alpha}")
            except Exception as e:
                self.logger.error(f"应用透明度时出错: {e}")
                # 尝试使用默认透明度
                self.wm_attributes("-alpha", 0.85)
                
        except Exception as e:
            self.logger.error(f"应用背景色和透明度时出错: {e}")
            self.logger.error(traceback.format_exc())
    
    def load_ui_settings(self):
        """加载UI设置（跨平台兼容）"""
        try:
            # 获取用户文档目录
            doc_path = self._get_documents_path()
            settings_file = doc_path / "ui_settings.json"
            
            # 默认值
            default_theme = "dark"
            default_opacity = 0.85 if self.platform == "windows" else 0.9
            
            # 设置默认值
            self.current_theme = default_theme
            self.background_color = self.themes[default_theme]["bg_color"]
            self.text_color = self.themes[default_theme]["text_color"]
            self.text_color_secondary = self.themes[default_theme]["text_color_secondary"]
            self.accent_color = self.themes[default_theme]["accent_color"]
            self.border_color = self.themes[default_theme]["border_color"]
            self.transparency = default_opacity
            
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        
                    # 应用设置
                    theme = settings.get("theme", default_theme)
                    if theme in self.themes:
                        self.current_theme = theme
                        theme_data = self.themes[theme]
                        self.background_color = theme_data["bg_color"]
                        self.text_color = theme_data["text_color"]
                        self.text_color_secondary = theme_data["text_color_secondary"]
                        self.accent_color = theme_data["accent_color"]
                        self.border_color = theme_data["border_color"]
                    
                    opacity = settings.get("opacity", default_opacity)
                    self.transparency = max(0.1, min(1.0, opacity))
                    
                except (json.JSONDecodeError, ValueError) as e:
                    self.logger.warning(f"UI设置文件格式错误，使用默认设置: {e}")
            
            self.logger.info(f"UI设置已加载: 主题={self.current_theme}, 透明度={int(self.transparency*100)}%")
            
        except Exception as e:
            self.logger.error(f"加载UI设置时出错: {e}")
            # 使用默认深色主题
            self.current_theme = "dark"
            self.background_color = "#1a1a1a"
            self.text_color = "#ffffff"
            self.text_color_secondary = "#b3b3b3"
            self.accent_color = "#00d4ff"
            self.border_color = "#333333"
            self.transparency = 0.85

    def _update_all_colors(self):
        """更新所有组件的颜色主题"""
        try:
            # 检查组件是否存在
            if not hasattr(self, 'main_frame'):
                return
                
            # 更新主窗口和框架
            self.configure(bg=self.background_color)
            self.main_frame.configure(bg=self.background_color)
            self.time_frame.configure(bg=self.background_color)
            self.info_container.configure(bg=self.background_color)
            
            # 更新标签
            self.time_label.configure(bg=self.background_color, fg=self.text_color)
            self.date_label.configure(bg=self.background_color, fg=self.text_color_secondary)
            self.class_info_label.configure(bg=self.background_color, fg=self.text_color)
            self.next_class_label.configure(bg=self.background_color, fg=self.accent_color)
            
            # 更新分隔线
            self.separator.configure(bg=self.border_color)
            
            self.logger.info(f"颜色主题已更新: {self.current_theme}")
        except Exception as e:
            self.logger.error(f"更新颜色主题时出错: {e}")
    
    def set_draggable(self, draggable):
        """设置窗口是否可拖动（跨平台兼容）"""
        self.is_draggable = draggable
        self.logger.info(f"设置可拖动状态: {draggable}")
        
        # 设置鼠标穿透
        if draggable:
            # 允许编辑时，窗口拦截鼠标事件
            try:
                self.wm_attributes("-alpha", 1.0)
                self.logger.info("设置窗口完全不透明")
            except Exception as e:
                self.logger.error(f"设置窗口完全不透明时出错: {e}")
                
            # 确保背景色正确显示
            self.configure(bg=self.background_color)
            self.main_frame.configure(bg=self.background_color)
            self.logger.info("窗口已启用，鼠标事件被拦截")
        else:
            # 不允许编辑时，鼠标事件穿透到后方界面
            try:
                # 使用合理的透明度值，确保窗口可见但可穿透
                alpha_value = 0.7
                
                # 平台特定的透明度调整
                if self.platform == "darwin":
                    alpha_value = 0.8
                elif self.platform == "linux":
                    alpha_value = 0.75
                
                self.wm_attributes("-alpha", alpha_value)
                self.logger.info(f"设置窗口透明度为{alpha_value}")
                
            except Exception as e:
                self.logger.error(f"设置透明度时出错: {e}")
                # 使用安全的默认值
                try:
                    self.wm_attributes("-alpha", 0.9)
                    self.logger.info("使用安全透明度0.9")
                except Exception as e2:
                    self.logger.error(f"设置安全透明度失败: {e2}")
                    
            # 确保背景色正确显示
            self.configure(bg=self.background_color)
            self.main_frame.configure(bg=self.background_color)
            self.logger.info(f"窗口背景色已设置为: {self.background_color}")
            
            # 记录窗口信息
            self.logger.info(f"窗口位置: {self.winfo_x()}, {self.winfo_y()}")
            self.logger.info(f"窗口大小: {self.winfo_width()}x{self.winfo_height()}")
            
        # 强制更新窗口
        self.update()
    
    def set_display_postion(self, x, y):
        """设置窗口位置（带边界检查）"""
        try:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # 确保窗口在屏幕范围内
            x = max(0, min(x, screen_width - 250))
            y = max(0, min(y, screen_height - 120))
            
            self.geometry(f"+{x}+{y}")
            self.logger.debug(f"窗口位置设置为: ({x}, {y})")
            
        except Exception as e:
            self.logger.error(f"设置窗口位置时出错: {e}")
            self.geometry(f"+{x}+{y}")  # 仍然尝试设置位置

    def start_move(self, event):
        """开始移动窗口"""
        if self.is_draggable:
            self.x = event.x
            self.y = event.y
            self.logger.debug("开始拖动窗口")

    def stop_move(self, event):
        """停止移动窗口"""
        if self.is_draggable:
            # 保存窗口位置
            self.save_window_position()
            self.logger.debug("停止拖动窗口")

    def on_motion(self, event):
        """移动窗口"""
        if self.is_draggable:
            try:
                deltax = event.x - self.x
                deltay = event.y - self.y
                x = self.winfo_x() + deltax
                y = self.winfo_y() + deltay
                
                # 边界检查
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                
                x = max(0, min(x, screen_width - 250))
                y = max(0, min(y, screen_height - 120))
                
                self.geometry(f"+{x}+{y}")
                
            except Exception as e:
                self.logger.error(f"移动窗口时出错: {e}")
        """设置窗口显示位置"""
        self.geometry(f"+{x}+{y}")
    
    def update_time(self):
        """更新时间显示"""
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%m-%d")
            
            # 获取星期
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday = weekdays[now.weekday()]
            
            # 更新时间标签
            self.time_label.config(text=current_time)
            self.date_label.config(text=f"{current_date} {weekday}")
            
            # 更新课程信息
            self.update_info(now)
        except Exception as e:
            # 窗口可能已被销毁，停止更新
            self.logger.error(f"更新时间时出错: {e}")
            self.logger.error(traceback.format_exc())
            return
        
        # 每秒更新一次
        try:
            after_id = self.after(1000, self.update_time)
            self.after_ids.append(after_id)
            # 保存更新任务ID
            self.update_job = after_id
            self.logger.debug("已安排下次时间更新")
        except Exception as e:
            # 窗口可能已被销毁，停止更新
            self.logger.error(f"安排下次更新时出错: {e}")
            self.logger.error(traceback.format_exc())
    
    def load_timetable(self):
        """从用户文档目录加载课程表JSON文件（跨平台兼容）"""
        try:
            # 获取用户文档目录
            doc_path = self._get_documents_path()
            timetable_file = doc_path / "timetable.json"
            
            # 如果用户目录没有，尝试从项目目录复制
            if not timetable_file.exists():
                project_path = Path(__file__).parent.parent
                project_timetable = project_path / "timetable.json"
                
                if project_timetable.exists():
                    # 复制默认课程表到用户目录
                    import shutil
                    shutil.copy2(project_timetable, timetable_file)
                    self.logger.info(f"复制默认课程表到: {timetable_file}")
                else:
                    # 创建默认课程表
                    self._create_default_timetable(timetable_file)
            
            # 加载课程表
            with open(timetable_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理可能的嵌套结构
            timetable = data.get("timetable", data)
            
            # 转换星期名称为英文
            converted_timetable = {}
            weekdays_mapping = {
                "周一": "monday", "周二": "tuesday", "周三": "wednesday",
                "周四": "thursday", "周五": "friday", "周六": "saturday", "周日": "sunday"
            }
            
            for day_cn, day_en in weekdays_mapping.items():
                if day_cn in timetable:
                    converted_timetable[day_en] = timetable[day_cn]
                elif day_en in timetable:
                    converted_timetable[day_en] = timetable[day_en]
                else:
                    converted_timetable[day_en] = []
            
            self.logger.info("课程表加载成功")
            return converted_timetable
            
        except Exception as e:
            self.logger.error(f"加载课程表时出错: {e}")
            self.logger.error(traceback.format_exc())
            # 返回空课程表
            return {day: [] for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}
    
    def _create_default_timetable(self, filepath):
        """创建默认课程表"""
        default_timetable = {
            "timetable": {
                "周一": [
                    {"subject": "数学", "start_time": "08:00", "end_time": "09:40"},
                    {"subject": "英语", "start_time": "10:00", "end_time": "11:40"}
                ],
                "周二": [
                    {"subject": "语文", "start_time": "08:00", "end_time": "09:40"},
                    {"subject": "物理", "start_time": "14:00", "end_time": "15:40"}
                ],
                "周三": [
                    {"subject": "化学", "start_time": "10:00", "end_time": "11:40"}
                ],
                "周四": [
                    {"subject": "生物", "start_time": "08:00", "end_time": "09:40"}
                ],
                "周五": [
                    {"subject": "政治", "start_time": "10:00", "end_time": "11:40"}
                ],
                "周六": [],
                "周日": []
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_timetable, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"创建默认课程表: {filepath}")
    
    def update_info(self, now):
        """更新课程信息显示"""
        # 获取当前星期
        weekdays_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        current_weekday_en = weekdays_en[now.weekday()]
        current_weekday_cn = weekdays_cn[now.weekday()]
        
        # print(f"当前时间: {now}")  # 调试信息
        # print(f"当前星期: {current_weekday_cn} ({current_weekday_en})")  # 调试信息
        
        # 获取当前时间和下一节课信息
        current_class = None
        next_class = None
        
        # 使用英文键访问课表
        if current_weekday_en in self.timetable:
            classes = self.timetable[current_weekday_en]
            # print(f"当天课程: {classes}")  # 调试信息
            
            # 遍历课程查找当前和下一节课
            for i, class_info in enumerate(classes):
                start_time = datetime.datetime.strptime(class_info["start_time"], "%H:%M").time()
                end_time = datetime.datetime.strptime(class_info["end_time"], "%H:%M").time()
                
                # print(f"检查课程: {class_info['subject']} ({start_time}-{end_time})")  # 调试信息
                # print(f"当前时间是否在课程时间段内: {start_time <= now.time() <= end_time}")  # 调试信息
                
                # 检查当前时间是否在课程时间段内
                if start_time <= now.time() <= end_time:
                    current_class = class_info
                
                # 查找下一节课
                if start_time > now.time() and (next_class is None or start_time < datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()):
                    next_class = class_info
        
        # 更新当前课程信息
        if current_class:
            self.class_info_label.config(text=f"正在上课: {current_class['subject']} ({current_class['start_time']}-{current_class['end_time']})")
            self.logger.debug(f"当前课程: {current_class['subject']} ({current_class['start_time']}-{current_class['end_time']})")
        else:
            # 即使当天没有课程也保持程序正常运行
            self.class_info_label.config(text="今天没有课程")
            self.logger.debug("今天没有课程")
        
        # 更新下一节课信息
        if next_class:
            try:
                # 计算距离下一节课的时间
                next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
                next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
                
                # 如果下一节课是明天的，需要调整日期
                if next_class_datetime < now:
                    next_class_datetime += datetime.timedelta(days=1)
                
                time_diff = next_class_datetime - now
                minutes_diff = max(0, int(time_diff.total_seconds() / 60))
                
                if minutes_diff > 0:
                    self.next_class_label.config(text=f"下一节课: {next_class['subject']} ({next_class['start_time']}) 还有{minutes_diff}分钟")
                    self.logger.debug(f"下一节课: {next_class['subject']} 还有{minutes_diff}分钟")
                else:
                    self.next_class_label.config(text=f"下一节课: {next_class['subject']} ({next_class['start_time']}) 即将开始")
                    
            except Exception as e:
                self.logger.error(f"计算下一节课时间时出错: {e}")
                self.next_class_label.config(text=f"下一节课: {next_class['subject']} ({next_class['start_time']})")
        else:
            self.next_class_label.config(text="今天没有更多课程")
            self.logger.debug("今天没有更多课程")
    
    def _get_documents_path(self):
        """获取跨平台文档路径"""
        try:
            if self.platform == "windows":
                return Path.home() / "Documents" / "TimeNest-TkTT"
            elif self.platform == "darwin":  # macOS
                return Path.home() / "Documents" / "TimeNest-TkTT"
            else:  # Linux and others
                return Path.home() / "Documents" / "TimeNest-TkTT"
        except Exception as e:
            self.logger.error(f"获取文档路径失败: {e}")
            return Path.home() / "TimeNest-TkTT"
    
    def load_window_position(self):
        """加载窗口位置（跨平台兼容）"""
        try:
            position_file = self.doc_path / "window_position.json"
            
            # 默认位置 - 根据屏幕尺寸智能定位
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            # 默认右上角位置
            default_x = screen_width - 270  # 窗口宽度250 + 边距20
            default_y = 50
            
            if position_file.exists():
                try:
                    with open(position_file, 'r', encoding='utf-8') as f:
                        position = json.load(f)
                        default_x = position.get("x", default_x)
                        default_y = position.get("y", default_y)
                        
                        # 验证位置是否在屏幕范围内
                        if not (0 <= default_x <= screen_width - 100 and 
                               0 <= default_y <= screen_height - 100):
                            default_x = screen_width - 270
                            default_y = 50
                            
                except (json.JSONDecodeError, ValueError):
                    self.logger.warning("窗口位置文件格式错误，使用默认位置")
            
            # 设置窗口位置
            self.set_display_postion(default_x, default_y)
            self.logger.info(f"窗口位置设置为: ({default_x}, {default_y})")
            
        except Exception as e:
            self.logger.error(f"加载窗口位置时出错: {e}")
            self.set_display_postion(100, 100)

    def load_ui_settings(self):
        """加载UI设置（跨平台兼容）"""
        try:
            settings_file = self.doc_path / "ui_settings.json"
            
            # 默认值
            default_theme = "dark"
            default_opacity = 0.85 if self.platform == "windows" else 0.9
            
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        self.current_theme = settings.get("theme", default_theme)
                        self.transparency = settings.get("opacity", default_opacity)
                        
                        # 验证值范围
                        if self.transparency < 0.1:
                            self.transparency = 0.1
                        elif self.transparency > 1.0:
                            self.transparency = 1.0
                            
                except (json.JSONDecodeError, ValueError):
                    self.logger.warning("UI设置文件格式错误，使用默认设置")
                    self.current_theme = default_theme
                    self.transparency = default_opacity
            else:
                # 使用默认值
                self.current_theme = default_theme
                self.transparency = default_opacity
            
            # 应用主题和透明度
            self._update_all_colors()
            self.attributes('-alpha', self.transparency)
            
            self.logger.info(f"UI设置已加载: 主题={self.current_theme}, 透明度={self.transparency}%")
            
        except Exception as e:
            self.logger.error(f"加载UI设置时出错: {e}")
            self.current_theme = "dark"
            self.transparency = 0.85 if self.platform == "windows" else 0.9
    
    def save_window_position(self):
        """保存窗口位置（跨平台兼容）"""
        try:
            position_file = self.doc_path / "window_position.json"
            
            # 获取当前位置
            x, y = self.winfo_x(), self.winfo_y()
            
            # 验证位置合理性
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            if 0 <= x <= screen_width and 0 <= y <= screen_height:
                position = {"x": x, "y": y}
                
                with open(position_file, 'w', encoding='utf-8') as f:
                    json.dump(position, f, ensure_ascii=False, indent=2)
                    
                self.logger.info(f"窗口位置已保存: ({x}, {y})")
            else:
                self.logger.warning(f"窗口位置超出屏幕范围，不保存: ({x}, {y})")
                
        except Exception as e:
            self.logger.error(f"保存窗口位置时出错: {e}")

    def save_ui_settings(self):
        """保存UI设置（跨平台兼容）"""
        try:
            settings_file = self.doc_path / "ui_settings.json"
            
            settings = {
                "theme": self.current_theme,
                "opacity": self.transparency
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"UI设置已保存: 主题={self.current_theme}, 透明度={self.transparency}%")
            
        except Exception as e:
            self.logger.error(f"保存UI设置时出错: {e}")
    
    def on_closing(self):
        """关闭窗口时保存位置"""
        try:
            # 取消所有待执行的after任务
            if hasattr(self, 'after_ids'):
                for after_id in self.after_ids:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass  # 忽略可能的异常
                self.after_ids.clear()
            
            # 停止所有可能的更新循环
            if hasattr(self, 'update_job') and self.update_job:
                try:
                    self.after_cancel(self.update_job)
                except:
                    pass  # 忽略可能的异常
            
            # 停止更新循环标志
            if hasattr(self, 'update_loop_running'):
                self.update_loop_running = False
            
            # 解除所有事件绑定
            try:
                for widget in self.winfo_children():
                    try:
                        widget.unbind("<Button-1>")
                    except:
                        pass
                    try:
                        widget.unbind("<B1-Motion>")
                    except:
                        pass
                    try:
                        widget.unbind("<ButtonRelease-1>")
                    except:
                        pass
            except Exception as e:
                print(f"解除事件绑定时出错: {e}")
            
            # 保存窗口位置和UI设置
            self.save_window_position()
            self.save_ui_settings()
            self.logger.info("正在关闭应用程序...")
        except Exception as e:
            self.logger.error(f"关闭窗口时出错: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.info("应用程序已关闭")
            # 销毁窗口
            try:
                self.destroy()
            except Exception as e:
                self.logger.error(f"销毁窗口时出错: {e}")
