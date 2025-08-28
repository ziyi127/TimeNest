import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import json
import os
import platform
import logging
from pathlib import Path

class UISettings:
    def __init__(self, parent, drag_window):
        self.parent = parent
        self.drag_window = drag_window
        self.window = tk.Toplevel(parent)
        self.window.title("UI设置")
        self.window.geometry("480x650")
        self.window.resizable(True, True)
        self.window.minsize(450, 600)
        
        # 初始化设置
        self.settings = {
            "theme": "dark",
            "transparency": 85,
            "position_x": 100,
            "position_y": 100,
            "show_next_class": True,
            "show_countdown": True,
            "background_color": "#2b2b2b",
            "text_color": "#ffffff"
        }
        
        # 窗口拖动相关变量
        self._drag_data = {"x": 0, "y": 0}
        
        self.create_widgets()
        self.load_settings()
        
        # 确保窗口在屏幕中央
        self._center_window()
    
    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建可滚动画布
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 主题设置
        theme_frame = tk.LabelFrame(scrollable_frame, text="主题设置", padx=10, pady=10)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        theme_options = [
            ("深色主题", "dark"),
            ("浅色主题", "light"), 
            ("玻璃主题", "glass")
        ]
        
        for text, value in theme_options:
            tk.Radiobutton(theme_frame, text=text, value=value, 
                          variable=self.theme_var, command=self.on_theme_change).pack(anchor=tk.W)
        
        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 外观设置
        appearance_frame = tk.LabelFrame(scrollable_frame, text="外观设置", padx=10, pady=10)
        appearance_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 透明度设置
        transparency_frame = tk.Frame(appearance_frame)
        transparency_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(transparency_frame, text="透明度:").pack(side=tk.LEFT)
        self.transparency_scale = tk.Scale(transparency_frame, from_=30, to=100, 
                                         orient=tk.HORIZONTAL, command=self.on_transparency_change)
        self.transparency_scale.set(self.settings["transparency"])
        self.transparency_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.transparency_label = tk.Label(appearance_frame, text=f"{self.settings['transparency']}%")
        self.transparency_label.pack()
        
        # 颜色设置（根据主题自动调整或自定义）
        self.color_frame = tk.LabelFrame(scrollable_frame, text="自定义颜色", padx=10, pady=10)
        self.color_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 背景颜色设置
        bg_frame = tk.Frame(self.color_frame)
        bg_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(bg_frame, text="背景颜色:").pack(side=tk.LEFT)
        self.bg_color_btn = tk.Button(bg_frame, text="选择颜色", command=self.choose_bg_color,
                                    bg=self.settings["background_color"], 
                                    fg=self.settings["text_color"])
        self.bg_color_btn.pack(side=tk.RIGHT)
        
        # 文字颜色设置
        text_frame = tk.Frame(self.color_frame)
        text_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(text_frame, text="文字颜色:").pack(side=tk.LEFT)
        self.text_color_btn = tk.Button(text_frame, text="选择颜色", command=self.choose_text_color,
                                      bg=self.settings["text_color"], 
                                      fg=self.settings["background_color"])
        self.text_color_btn.pack(side=tk.RIGHT)
        
        # 位置设置
        position_frame = tk.LabelFrame(scrollable_frame, text="位置设置", padx=10, pady=10)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(position_frame, text="位置:").pack(side=tk.LEFT)
        
        x_frame = tk.Frame(position_frame)
        x_frame.pack(side=tk.RIGHT)
        
        tk.Label(x_frame, text="X:").pack(side=tk.LEFT)
        self.x_entry = tk.Entry(x_frame, width=5)
        self.x_entry.insert(0, str(self.settings["position_x"]))
        self.x_entry.pack(side=tk.LEFT)
        
        tk.Label(x_frame, text="Y:").pack(side=tk.LEFT)
        self.y_entry = tk.Entry(x_frame, width=5)
        self.y_entry.insert(0, str(self.settings["position_y"]))
        self.y_entry.pack(side=tk.LEFT)
        
        # 位置预览框
        self.preview_frame = tk.Frame(position_frame, width=50, height=50, bg=self.settings["background_color"])
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)  # 保持框架大小
        
        # 添加拖拽功能到预览框
        self.preview_frame.bind("<Button-1>", self.start_drag)
        self.preview_frame.bind("<B1-Motion>", self.on_drag)
        
        # 显示设置区域
        display_frame = tk.LabelFrame(scrollable_frame, text="显示设置", padx=10, pady=10)
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.show_next_class_var = tk.BooleanVar(value=self.settings["show_next_class"])
        tk.Checkbutton(display_frame, text="显示下一节课名称", variable=self.show_next_class_var).pack(anchor=tk.W)
        
        self.show_countdown_var = tk.BooleanVar(value=self.settings["show_countdown"])
        tk.Checkbutton(display_frame, text="显示距离下节课的倒计时", variable=self.show_countdown_var).pack(anchor=tk.W)
        
        self.compact_mode_var = tk.BooleanVar(value=self.settings.get("compact_mode", False))
        tk.Checkbutton(display_frame, text="启用紧凑模式", variable=self.compact_mode_var).pack(anchor=tk.W)
        
        # 高级设置
        advanced_frame = tk.LabelFrame(scrollable_frame, text="高级设置", padx=10, pady=10)
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 指针穿透功能已默认启用，不再提供选项
        
        # 按钮区域
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
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
                
                # 更新主题选择
                self.theme_var.set(self.settings.get("theme", "dark"))
                
                # 更新输入框的值
                self.x_entry.delete(0, tk.END)
                self.x_entry.insert(0, str(self.settings["position_x"]))
                self.y_entry.delete(0, tk.END)
                self.y_entry.insert(0, str(self.settings["position_y"]))
                
                # 更新预览框的样式
                self.preview_frame.config(bg=self.settings["background_color"])
                self.transparency_scale.set(self.settings["transparency"])
                self.transparency_label.config(text=f"{self.settings['transparency']}%")
                self.show_next_class_var.set(self.settings["show_next_class"])
                self.show_countdown_var.set(self.settings["show_countdown"])
                self.compact_mode_var.set(self.settings.get("compact_mode", False))
                
                # 更新颜色按钮
                self.bg_color_btn.config(bg=self.settings["background_color"])
                self.text_color_btn.config(bg=self.settings["text_color"])
                
                # 根据主题启用/禁用自定义颜色
                self._update_color_frame_state()
                
        except Exception as e:
            print(f"加载设置时出错: {e}")
    
    def _update_color_frame_state(self):
        """根据主题更新颜色框架状态"""
        theme = self.theme_var.get()
        if theme in ["dark", "light", "glass"]:
            # 预设主题，禁用自定义颜色
            for child in self.color_frame.winfo_children():
                for widget in child.winfo_children():
                    if isinstance(widget, tk.Button):
                        widget.config(state=tk.DISABLED)
        else:
            # 自定义主题，启用颜色选择
            for child in self.color_frame.winfo_children():
                for widget in child.winfo_children():
                    if isinstance(widget, tk.Button):
                        widget.config(state=tk.NORMAL)
    
    def save_settings(self):
        """保存设置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 更新设置值
            self.settings["theme"] = self.theme_var.get()
            self.settings["position_x"] = int(self.x_entry.get())
            self.settings["position_y"] = int(self.y_entry.get())
            self.settings["transparency"] = self.transparency_scale.get()
            self.settings["show_next_class"] = self.show_next_class_var.get()
            self.settings["show_countdown"] = self.show_countdown_var.get()
            self.settings["compact_mode"] = self.compact_mode_var.get()
            self.settings["pointer_passthrough"] = True  # 强制启用指针穿透，不可更改
            self.settings["background_color"] = self.settings["background_color"]
            self.settings["text_color"] = self.settings["text_color"]
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
            # 应用设置到主窗口
            if hasattr(self.drag_window, 'apply_settings'):
                self.drag_window.apply_settings(self.settings)
                
        except Exception as e:
            print(f"保存设置时出错: {e}")
    
    def _center_window(self):
        """将窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _setup_window_dragging(self):
        """设置窗口拖动功能"""
        # 绑定鼠标事件到整个窗口
        self.window.bind("<Button-1>", self._start_drag)
        self.window.bind("<B1-Motion>", self._do_drag)
        
        # 添加右侧拖动区域
        drag_handle = tk.Frame(self.window, width=8, bg="#cccccc", cursor="fleur")
        drag_handle.pack(side=tk.RIGHT, fill=tk.Y)
        drag_handle.bind("<Button-1>", self._start_drag)
        drag_handle.bind("<B1-Motion>", self._do_drag)
    
    def _start_drag(self, event):
        """开始拖动窗口"""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def _do_drag(self, event):
        """执行窗口拖动"""
        x = self.window.winfo_x() + event.x - self._drag_data["x"]
        y = self.window.winfo_y() + event.y - self._drag_data["y"]
        self.window.geometry(f"+{x}+{y}")
    
    def _on_transparency_change(self, value):
        """透明度滑块变化时的回调"""
        self.transparency_label.config(text=f"透明度: {int(float(value))}%")
    
    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色", initialcolor=self.settings["background_color"])
        if color[1]:
            self.settings["background_color"] = color[1]
            self.bg_color_btn.config(text=color[1])
    
    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色", initialcolor=self.settings["text_color"])
        if color[1]:
            self.settings["text_color"] = color[1]
            self.text_color_btn.config(text=color[1])
    
    def apply_settings(self):
        """应用设置"""
        try:
            # 保存设置
            self.save_settings()
            
            # 应用主题
            theme = self.settings["theme"]
            
            # 根据主题设置颜色
            if theme == "dark":
                self.settings["background_color"] = "#2c3e50"
                self.settings["text_color"] = "#ffffff"
            elif theme == "light":
                self.settings["background_color"] = "#ffffff"
                self.settings["text_color"] = "#000000"
            elif theme == "glass":
                self.settings["background_color"] = "#f0f0f0"
                self.settings["text_color"] = "#333333"
            
            # 应用设置到主窗口
            if hasattr(self.parent, 'reload_settings'):
                # 更新主窗口的设置
                self.parent.background_color = self.settings["background_color"]
                self.parent.text_color = self.settings["text_color"]
                self.parent.transparency = self.settings["transparency"]
                self.parent.show_next_class = self.settings["show_next_class"]
                self.parent.show_countdown = self.settings["show_countdown"]
                self.parent.compact_mode = self.settings["compact_mode"]
                self.parent.pointer_passthrough = True  # 始终启用指针穿透
                
                # 重新加载所有设置
                self.parent.reload_settings()
                
            # 应用位置
            try:
                if hasattr(self.parent, 'set_display_postion'):
                    self.parent.set_display_postion(self.settings["position_x"], self.settings["position_y"])
            except Exception as e:
                print(f"应用位置时出错: {e}")
                
        except Exception as e:
            print(f"应用设置时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def save_and_close(self):
        """保存设置并关闭窗口"""
        self.apply_settings()
        self.window.destroy()
    
    def choose_bg_color(self):
        """选择背景颜色"""
        color = colorchooser.askcolor(title="选择背景颜色")[1]
        if color:
            self.settings["background_color"] = color
            self.preview_frame.config(bg=color)
    
    def choose_text_color(self):
        """选择文字颜色"""
        color = colorchooser.askcolor(title="选择文字颜色")[1]
        if color:
            self.settings["text_color"] = color
    
    def on_transparency_change(self, value):
        """透明度变化时的处理"""
        try:
            alpha = int(value) / 100.0
            self.transparency_label.config(text=f"{value}%")
            self.drag_window.wm_attributes("-alpha", alpha)
        except Exception as e:
            print(f"更新透明度时出错: {e}")
    
    def on_theme_change(self):
        """主题变化时的处理"""
        theme = self.theme_var.get()
        self.settings["theme"] = theme
        
        # 根据主题自动设置颜色
        if theme == "dark":
            self.settings["background_color"] = "#2b2b2b"
            self.settings["text_color"] = "#ffffff"
        elif theme == "light":
            self.settings["background_color"] = "#ffffff"
            self.settings["text_color"] = "#000000"
        elif theme == "glass":
            self.settings["background_color"] = "#f0f0f0"
            self.settings["text_color"] = "#333333"
        
        # 更新颜色按钮显示
        self.bg_color_btn.config(bg=self.settings["background_color"], 
                               fg=self.settings["text_color"])
        self.text_color_btn.config(bg=self.settings["text_color"], 
                                   fg=self.settings["background_color"])
        
        # 更新预览框
        self.preview_frame.config(bg=self.settings["background_color"])
        
        # 更新颜色框架状态
        self._update_color_frame_state()
        
        # 立即应用主题
        if hasattr(self.drag_window, '_switch_theme'):
            self.drag_window._switch_theme(theme)

    def start_drag(self, event):
        """开始拖拽预览框"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        """拖拽预览框"""
        # 计算新的位置
        delta_x = event.x - self.drag_start_x
        delta_y = event.y - self.drag_start_y
        
        # 获取当前预览框的位置
        x = self.preview_frame.winfo_x() + delta_x
        y = self.preview_frame.winfo_y() + delta_y
        
        # 移动预览框
        self.preview_frame.place(x=x, y=y)
        
        # 更新位置输入框
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))