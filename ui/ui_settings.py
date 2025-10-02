import tkinter as tk
from tkinter import ttk, colorchooser
import json
import os

class UISettings:
    def __init__(self, parent, drag_window):
        self.parent = parent
        self.drag_window = drag_window
        self.window = tk.Toplevel(parent)
        self.window.title("UI设置")
        self.window.geometry("400x600")
        
        # 居中显示窗口
        if hasattr(self.drag_window, '_center_window'):
            self.drag_window._center_window(self.window)
        
        # 初始化设置
        self.settings = {
            "background_color": "white",
            "text_color": "black",
            "transparency": 100,
            "position_x": 100,
            "position_y": 100,
            "show_next_class": True,
            "show_countdown": True,
            "time_font_size": 14,
            "date_font_size": 12,
            "class_info_font_size": 12,
            "next_class_font_size": 12,
            "window_width": 280,
            "window_height": 65
        }
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        # 创建设置项
        
        # 背景颜色设置
        bg_frame = tk.Frame(self.window)
        bg_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(bg_frame, text="背景颜色:").pack(side=tk.LEFT)
        self.bg_color_btn = tk.Button(bg_frame, text="选择颜色", command=self.choose_bg_color)
        self.bg_color_btn.pack(side=tk.RIGHT, padx=5)
        
        # 背景颜色推荐按钮
        self.bg_recommended_frame = tk.Frame(bg_frame)
        self.bg_recommended_frame.pack(side=tk.RIGHT)
        
        # 推荐颜色：蓝色（理性与秩序）
        self.blue_btn = tk.Button(self.bg_recommended_frame, width=2, bg="#2962FF", command=lambda: self.set_recommended_color("background", "#2962FF"))
        self.blue_btn.pack(side=tk.LEFT, padx=1)
        
        # 推荐颜色：绿色（学习与成长）
        self.green_btn = tk.Button(self.bg_recommended_frame, width=2, bg="#00C853", command=lambda: self.set_recommended_color("background", "#00C853"))
        self.green_btn.pack(side=tk.LEFT, padx=1)
        
        # 推荐颜色：橙色（活力）
        self.orange_btn = tk.Button(self.bg_recommended_frame, width=2, bg="#FF6D00", command=lambda: self.set_recommended_color("background", "#FF6D00"))
        self.orange_btn.pack(side=tk.LEFT, padx=1)
        
        # 文字颜色设置
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(text_frame, text="文字颜色:").pack(side=tk.LEFT)
        self.text_color_btn = tk.Button(text_frame, text="选择颜色", command=self.choose_text_color)
        self.text_color_btn.pack(side=tk.RIGHT, padx=5)
        
        # 文字颜色推荐按钮
        self.text_recommended_frame = tk.Frame(text_frame)
        self.text_recommended_frame.pack(side=tk.RIGHT)
        
        # 推荐颜色：蓝色（理性与秩序）
        self.blue_text_btn = tk.Button(self.text_recommended_frame, width=2, bg="#2962FF", command=lambda: self.set_recommended_color("text", "#2962FF"))
        self.blue_text_btn.pack(side=tk.LEFT, padx=1)
        
        # 推荐颜色：绿色（学习与成长）
        self.green_text_btn = tk.Button(self.text_recommended_frame, width=2, bg="#00C853", command=lambda: self.set_recommended_color("text", "#00C853"))
        self.green_text_btn.pack(side=tk.LEFT, padx=1)
        
        # 推荐颜色：橙色（活力）
        self.orange_text_btn = tk.Button(self.text_recommended_frame, width=2, bg="#FF6D00", command=lambda: self.set_recommended_color("text", "#FF6D00"))
        self.orange_text_btn.pack(side=tk.LEFT, padx=1)
        
        # 透明度设置
        transparency_frame = tk.Frame(self.window)
        transparency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(transparency_frame, text="透明度:").pack(side=tk.LEFT)
        self.transparency_scale = tk.Scale(transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_transparency_change)
        self.transparency_scale.set(self.settings["transparency"])
        self.transparency_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 字体大小设置
        font_size_frame = tk.LabelFrame(self.window, text="字体大小")
        font_size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 时间字体大小
        time_font_frame = tk.Frame(font_size_frame)
        time_font_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(time_font_frame, text="时间:").pack(side=tk.LEFT)
        self.time_font_scale = tk.Scale(time_font_frame, from_=8, to=24, orient=tk.HORIZONTAL)
        self.time_font_scale.set(self.settings["time_font_size"])
        self.time_font_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 日期字体大小
        date_font_frame = tk.Frame(font_size_frame)
        date_font_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(date_font_frame, text="日期:").pack(side=tk.LEFT)
        self.date_font_scale = tk.Scale(date_font_frame, from_=8, to=24, orient=tk.HORIZONTAL)
        self.date_font_scale.set(self.settings["date_font_size"])
        self.date_font_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 课程信息字体大小
        class_info_font_frame = tk.Frame(font_size_frame)
        class_info_font_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(class_info_font_frame, text="课程信息:").pack(side=tk.LEFT)
        self.class_info_font_scale = tk.Scale(class_info_font_frame, from_=8, to=24, orient=tk.HORIZONTAL)
        self.class_info_font_scale.set(self.settings["class_info_font_size"])
        self.class_info_font_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 下一节课字体大小
        next_class_font_frame = tk.Frame(font_size_frame)
        next_class_font_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(next_class_font_frame, text="下一节课:").pack(side=tk.LEFT)
        self.next_class_font_scale = tk.Scale(next_class_font_frame, from_=8, to=24, orient=tk.HORIZONTAL)
        self.next_class_font_scale.set(self.settings["next_class_font_size"])
        self.next_class_font_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 窗口大小设置
        window_size_frame = tk.LabelFrame(self.window, text="窗口大小")
        window_size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 添加一个说明标签
        tk.Label(window_size_frame, text="通过拖动条调整窗口大小，文字会同时变大").pack(fill=tk.X, padx=5, pady=2)
        
        # 使用单个拖动条调整窗口大小
        size_frame = tk.Frame(window_size_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(size_frame, text="窗口大小:").pack(side=tk.LEFT)
        self.size_scale = tk.Scale(size_frame, from_=1, to=3, orient=tk.HORIZONTAL, resolution=0.1)
        self.size_scale.set(1.0)  # 默认比例为1.0
        self.size_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 显示控制
        display_frame = tk.Frame(self.window)
        display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.show_next_class_var = tk.BooleanVar(value=self.settings["show_next_class"])
        tk.Checkbutton(display_frame, text="显示正在上的课程名称和休息提示", variable=self.show_next_class_var).pack(anchor=tk.W)
        
        self.show_countdown_var = tk.BooleanVar(value=self.settings["show_countdown"])
        tk.Checkbutton(display_frame, text="显示下节课的时间和名称", variable=self.show_countdown_var).pack(anchor=tk.W)
        
        # 按钮区域
        button_frame = tk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="应用", command=self.apply_settings).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="确定", command=self.save_and_close).pack(side=tk.RIGHT, padx=5)
    
    def load_settings(self):
        """加载设置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                
                # 确保所有设置项都存在
                if "time_font_size" not in self.settings:
                    self.settings["time_font_size"] = 14
                if "date_font_size" not in self.settings:
                    self.settings["date_font_size"] = 12
                if "class_info_font_size" not in self.settings:
                    self.settings["class_info_font_size"] = 12
                if "next_class_font_size" not in self.settings:
                    self.settings["next_class_font_size"] = 12
                if "window_width" not in self.settings:
                    self.settings["window_width"] = 180
                if "window_height" not in self.settings:
                    self.settings["window_height"] = 70
                
                self.transparency_scale.set(self.settings["transparency"])
                self.show_next_class_var.set(self.settings["show_next_class"])
                self.show_countdown_var.set(self.settings["show_countdown"])
                self.time_font_scale.set(self.settings["time_font_size"])
                self.date_font_scale.set(self.settings["date_font_size"])
                self.class_info_font_scale.set(self.settings["class_info_font_size"])
                self.next_class_font_scale.set(self.settings["next_class_font_size"])
                # 移除对宽度和高度滑块的设置
                # 添加对新的size_scale滑块的设置
                # 根据窗口宽度计算比例因子
                scale_factor = self.settings["window_width"] / 180.0
                self.size_scale.set(scale_factor)
        except Exception as e:
            print(f"加载设置时出错: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 更新设置值
            self.settings["transparency"] = self.transparency_scale.get()
            self.settings["show_next_class"] = self.show_next_class_var.get()
            self.settings["show_countdown"] = self.show_countdown_var.get()
            self.settings["time_font_size"] = self.time_font_scale.get()
            self.settings["date_font_size"] = self.date_font_scale.get()
            self.settings["class_info_font_size"] = self.class_info_font_scale.get()
            self.settings["next_class_font_size"] = self.next_class_font_scale.get()
            
            # 根据size_scale的值计算窗口的宽度和高度
            scale_factor = self.size_scale.get()
            self.settings["window_width"] = int(180 * scale_factor)
            self.settings["window_height"] = int(70 * scale_factor)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置时出错: {e}")
    
    def apply_settings(self):
        """应用设置到主窗口"""
        if self.drag_window:
            # 更新设置值
            self.settings["transparency"] = self.transparency_scale.get()
            self.settings["show_next_class"] = self.show_next_class_var.get()
            self.settings["show_countdown"] = self.show_countdown_var.get()
            
            # 根据size_scale的值计算窗口的宽度和高度
            scale_factor = self.size_scale.get()
            self.settings["window_width"] = int(180 * scale_factor)
            self.settings["window_height"] = int(70 * scale_factor)
            
            # 获取用户设置的字体大小（不立即应用比例因子调整）
            user_time_font_size = self.time_font_scale.get()
            user_date_font_size = self.date_font_scale.get()
            user_class_info_font_size = self.class_info_font_scale.get()
            user_next_class_font_size = self.next_class_font_scale.get()
            
            # 保存用户设置的字体大小到设置中（不应用比例因子调整）
            self.settings["time_font_size"] = user_time_font_size
            self.settings["date_font_size"] = user_date_font_size
            self.settings["class_info_font_size"] = user_class_info_font_size
            self.settings["next_class_font_size"] = user_next_class_font_size
            
            # 更新主窗口的设置
            self.drag_window.background_color = self.settings["background_color"]
            self.drag_window.text_color = self.settings["text_color"]
            self.drag_window.transparency = self.settings["transparency"]
            self.drag_window.show_next_class = self.settings["show_next_class"]
            self.drag_window.show_countdown = self.settings["show_countdown"]
            self.drag_window.time_font_size = self.settings["time_font_size"]
            self.drag_window.date_font_size = self.settings["date_font_size"]
            self.drag_window.class_info_font_size = self.settings["class_info_font_size"]
            self.drag_window.next_class_font_size = self.settings["next_class_font_size"]
            self.drag_window.window_width = self.settings["window_width"]
            self.drag_window.window_height = self.settings["window_height"]
            
            # 应用背景色和透明度
            self.drag_window._apply_background_and_transparency()
            
            # 应用字体设置
            self.drag_window._apply_fonts()
            
            # 设置窗口大小
            self.drag_window.geometry(f"{self.settings['window_width']}x{self.settings['window_height']}")
            
            # 更新显示设置
            self.drag_window.update_display_settings()
            
            print("设置已应用到主窗口")
        # 保存设置
        self.save_settings()
    
    def save_and_close(self):
        """保存设置并关闭窗口"""
        self.apply_settings()
        self._cleanup_resources()
        self.window.destroy()
    
    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 解除所有事件绑定
            try:
                self.bg_color_btn.unbind("<Button-1>")
            except:
                pass
            try:
                self.text_color_btn.unbind("<Button-1>")
            except:
                pass
            
            # 解除透明度滑块的事件绑定
            try:
                self.transparency_scale.unbind("<Configure>")
            except:
                pass
            
            # 解除字体大小滑块的事件绑定
            try:
                self.time_font_scale.unbind("<Configure>")
            except:
                pass
            try:
                self.date_font_scale.unbind("<Configure>")
            except:
                pass
            try:
                self.class_info_font_scale.unbind("<Configure>")
            except:
                pass
            try:
                self.next_class_font_scale.unbind("<Configure>")
            except:
                pass
            
            # 解除窗口大小滑块的事件绑定
            try:
                self.size_scale.unbind("<Configure>")
            except:
                pass
            
            # 解除复选框的事件绑定
            try:
                self.show_next_class_var.trace_remove('write', self.show_next_class_var.trace_info()[0][1])
            except:
                pass
            try:
                self.show_countdown_var.trace_remove('write', self.show_countdown_var.trace_info()[0][1])
            except:
                pass
            
            # 销毁所有子控件
            try:
                for child in self.window.winfo_children():
                    try:
                        child.destroy()
                    except:
                        pass
            except:
                pass
        except Exception as e:
            print(f"清理UI设置界面资源时出错: {e}")
    
    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色")[1]
        if color:
            self.settings["background_color"] = color
    
    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色")[1]
        if color:
            self.settings["text_color"] = color
    
    def on_transparency_change(self, value):
        """透明度改变事件"""
        # 实时预览透明度变化
        alpha = int(value) / 100.0
        try:
            self.drag_window.wm_attributes("-alpha", alpha)
        except Exception as e:
            print(f"设置透明度时出错: {e}")
    
    def set_recommended_color(self, color_type, color_value):
        """设置推荐颜色
        
        Args:
            color_type: 颜色类型，"background" 或 "text"
            color_value: 颜色值，如 "#2962FF"
        """
        if color_type == "background":
            self.settings["background_color"] = color_value
        elif color_type == "text":
            self.settings["text_color"] = color_value
        
        # 应用设置到主窗口
        self.apply_settings()
        
        print(f"已设置{color_type}颜色为: {color_value}")