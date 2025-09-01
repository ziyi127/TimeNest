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
        self.window.geometry("400x500")
        
        # 初始化设置
        self.settings = {
            "background_color": "white",
            "text_color": "black",
            "transparency": 100,
            "position_x": 100,
            "position_y": 100,
            "show_next_class": True,
            "show_countdown": True
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
        self.bg_color_btn.pack(side=tk.RIGHT)
        
        # 文字颜色设置
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(text_frame, text="文字颜色:").pack(side=tk.LEFT)
        self.text_color_btn = tk.Button(text_frame, text="选择颜色", command=self.choose_text_color)
        self.text_color_btn.pack(side=tk.RIGHT)
        
        # 透明度设置
        transparency_frame = tk.Frame(self.window)
        transparency_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(transparency_frame, text="透明度:").pack(side=tk.LEFT)
        self.transparency_scale = tk.Scale(transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_transparency_change)
        self.transparency_scale.set(self.settings["transparency"])
        self.transparency_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        

        
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
                
                self.transparency_scale.set(self.settings["transparency"])
                self.show_next_class_var.set(self.settings["show_next_class"])
                self.show_countdown_var.set(self.settings["show_countdown"])
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
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置时出错: {e}")
    
    def apply_settings(self):
        """应用设置"""
        # 保存设置
        self.save_settings()
        
        # 应用背景颜色和透明度
        self.drag_window.background_color = self.settings["background_color"]
        self.drag_window.transparency = self.settings["transparency"]
        self.drag_window._apply_background_and_transparency()
        
        # 应用文字颜色
        self.drag_window.time_label.configure(fg=self.settings["text_color"])
        self.drag_window.date_label.configure(fg=self.settings["text_color"])
        self.drag_window.class_info_label.configure(fg=self.settings["text_color"])
        self.drag_window.next_class_label.configure(fg=self.settings["text_color"])
        
        # 应用显示控制
        print(f"应用显示设置: show_next_class={self.settings['show_next_class']}, show_countdown={self.settings['show_countdown']}")
        self.drag_window.show_next_class = self.settings["show_next_class"]
        self.drag_window.show_countdown = self.settings["show_countdown"]
        self.drag_window.update_display_settings()
        

    
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