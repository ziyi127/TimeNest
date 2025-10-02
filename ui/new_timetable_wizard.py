import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class NewTimetableWizard:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.window = None
        
        # 课程数据
        self.timetable_data = {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": []
        }
        
        # 星期映射
        self.day_names = {
            "monday": "星期一",
            "tuesday": "星期二",
            "wednesday": "星期三",
            "thursday": "星期四",
            "friday": "星期五",
            "saturday": "星期六",
            "sunday": "星期日"
        }
        
        # 当前选中的星期
        self.current_day = "monday"
        
        # 课程框架列表
        self.class_frames = []
    
    def load_existing_data(self):
        """加载现有数据到UI"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_file_path = os.path.join(project_path, "timetable.json")
            
            # 如果文件不存在，直接返回
            if not os.path.exists(data_file_path):
                return
            
            # 读取现有数据
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载时间表数据
            if "timetable" in data:
                self.timetable_data = data["timetable"]
        except Exception as e:
            print(f"加载现有数据时出错: {e}")
            messagebox.showerror("错误", f"加载现有数据时出错: {e}")
    
    def save_data(self):
        """保存数据到文件"""
        try:
            # 确保当前编辑的日期数据也被保存
            self.save_current_day_data()
            
            # 验证所有时间格式
            if not self.validate_all_times():
                messagebox.showerror("错误", "存在无效的时间格式，请检查所有开始时间和结束时间")
                return
            
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_file_path = os.path.join(project_path, "timetable.json")
            
            # 保存数据为timetable.json格式
            data = {
                "timetable": self.timetable_data
            }
            
            # 确保使用UTF-8编码保存
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 同时保存classtableMeta.json以保持兼容性
            meta_file_path = os.path.join(project_path, "classtableMeta.json")
            meta_data = {
                "timetable": {},
                "classtable": {},
                "allclass": []
            }
            
            # 提取时间信息和课程信息
            weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            all_classes = set()
            
            for day in weekdays:
                if day in self.timetable_data:
                    # 提取时间信息
                    meta_data["timetable"][day] = [
                        {"start_time": slot.get("start_time", ""), "end_time": slot.get("end_time", "")}
                        for slot in self.timetable_data[day]
                    ]
                    
                    # 提取课程信息
                    meta_data["classtable"][day] = [slot.get("subject", "") for slot in self.timetable_data[day]]
                    
                    # 收集所有课程
                    all_classes.update(meta_data["classtable"][day])
            
            # 设置allclass
            meta_data["allclass"] = list(all_classes)
            
            # 确保使用UTF-8编码保存
            with open(meta_file_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            # 显示成功消息
            messagebox.showinfo("成功", "时间表已保存成功！")
            
            # 更新主窗口的时间表
            if self.main_window and hasattr(self.main_window, 'load_timetable'):
                self.main_window.load_timetable()
        except Exception as e:
            print(f"保存数据时出错: {e}")
            messagebox.showerror("错误", f"保存数据时出错: {e}")
    
    def validate_all_times(self):
        """验证所有时间格式是否正确"""
        # 验证当前编辑的日期数据
        self.save_current_day_data()
        
        # 验证所有日期的时间格式
        for day, classes in self.timetable_data.items():
            for class_info in classes:
                start_time = class_info.get("start_time", "")
                end_time = class_info.get("end_time", "")
                
                # 验证开始时间格式
                if not self.is_valid_time_format(start_time):
                    return False
                
                # 验证结束时间格式
                if not self.is_valid_time_format(end_time):
                    return False
        
        return True
    
    def is_valid_time_format(self, time_str):
        """验证时间格式是否为HH:MM"""
        if not time_str or not isinstance(time_str, str):
            return False
        
        # 检查是否包含冒号
        if ":" not in time_str:
            return False
        
        # 分割小时和分钟
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        
        hours, minutes = parts
        
        # 验证是否为数字
        try:
            h = int(hours)
            m = int(minutes)
        except ValueError:
            return False
        
        # 验证范围
        return 0 <= h <= 23 and 0 <= m <= 59
    
    def open_window(self):
        """打开时间表设置向导"""
        # 如果窗口已存在，将其带到前台
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        # 创建新窗口
        self.window = tk.Toplevel(self.parent)
        self.window.title("时间表设置向导 - 自定义上下课时间")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # 居中显示窗口
        if hasattr(self.main_window, '_center_window'):
            self.main_window._center_window(self.window)
        
        # 设置窗口属性
        try:
            self.window.transient()
            self.window.wm_attributes("-topmost", False)
        except Exception as e:
            print(f"设置窗口属性时出错: {e}")
        
        # 创建界面元素
        self.create_widgets()
        
        # 加载现有数据
        self.load_existing_data()
        
        # 显示默认星期的数据
        self.display_day_classes()
    
    def create_widgets(self):
        """创建界面元素"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="时间表设置 - 自定义每节课上下课时间", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 星期选择框架
        day_frame = ttk.LabelFrame(main_frame, text="选择星期", padding="10")
        day_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 星期按钮
        day_buttons_frame = ttk.Frame(day_frame)
        day_buttons_frame.pack()
        
        days = [
            ("星期一", "monday"),
            ("星期二", "tuesday"),
            ("星期三", "wednesday"),
            ("星期四", "thursday"),
            ("星期五", "friday"),
            ("星期六", "saturday"),
            ("星期日", "sunday")
        ]
        
        # 保存星期按钮的引用，以便后续更新样式
        self.day_buttons = {}
        
        for i, (display_name, day_key) in enumerate(days):
            # 使用默认参数值修复闭包问题，确保每个按钮绑定正确的day_key
            btn = tk.Button(
                day_buttons_frame, 
                text=display_name, 
                command=lambda d=day_key: self.switch_day(d),
                width=8,
                relief=tk.RAISED,
                bd=1,
                highlightthickness=0
            )
            btn.grid(row=0, column=i, padx=2, pady=5)
            self.day_buttons[day_key] = btn
        
        # 初始化选中状态
        self.update_day_button_styles()
        
        # 课程列表框架
        self.classes_frame = ttk.LabelFrame(main_frame, text="课程列表", padding="10")
        self.classes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 课程列表标题
        headers_frame = ttk.Frame(self.classes_frame)
        headers_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(headers_frame, text="序号", width=5).grid(row=0, column=0, padx=5)
        ttk.Label(headers_frame, text="开始时间", width=10).grid(row=0, column=1, padx=5)
        ttk.Label(headers_frame, text="结束时间", width=10).grid(row=0, column=2, padx=5)
        ttk.Label(headers_frame, text="课程名称", width=15).grid(row=0, column=3, padx=5)
        ttk.Label(headers_frame, text="教师", width=10).grid(row=0, column=4, padx=5)
        ttk.Label(headers_frame, text="教室", width=10).grid(row=0, column=5, padx=5)
        ttk.Label(headers_frame, text="操作", width=10).grid(row=0, column=6, padx=5)
        
        # 课程滚动区域
        self.classes_canvas = tk.Canvas(self.classes_frame)
        scrollbar = ttk.Scrollbar(self.classes_frame, orient="vertical", command=self.classes_canvas.yview)
        self.scrollable_classes_frame = ttk.Frame(self.classes_canvas)
        
        self.scrollable_classes_frame.bind(
            "<Configure>",
            lambda e: self.classes_canvas.configure(scrollregion=self.classes_canvas.bbox("all"))
        )
        
        self.classes_canvas.create_window((0, 0), window=self.scrollable_classes_frame, anchor="nw")
        self.classes_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            self.classes_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.classes_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.scrollable_classes_frame.bind("<MouseWheel>", _on_mousewheel)
        
        self.classes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加课程按钮
        add_button_frame = ttk.Frame(main_frame)
        add_button_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(add_button_frame, text="添加课程", command=self.add_class).pack(side=tk.LEFT)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存时间表", command=self.save_data)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)

    def switch_day(self, day):
        """切换星期"""
        # 保存当前星期的数据
        self.save_current_day_data()
        
        # 切换到新星期
        self.current_day = day
        self.update_day_button_styles()
        self.display_day_classes()
    
    def update_day_button_styles(self):
        """更新星期按钮的样式，选中的按钮显示为按下状态"""
        for day_key, btn in self.day_buttons.items():
            if day_key == self.current_day:
                # 选中的按钮显示为按下状态
                btn.config(relief=tk.SUNKEN, bd=2)
            else:
                # 未选中的按钮恢复默认样式
                btn.config(relief=tk.RAISED, bd=1)
    
    def display_day_classes(self):
        """显示当前星期的课程"""
        # 清除现有的课程框架
        for frame in self.class_frames:
            frame.destroy()
        self.class_frames.clear()
        
        # 添加当前星期的课程
        classes = self.timetable_data.get(self.current_day, [])
        for i, class_info in enumerate(classes):
            self.create_class_frame(i+1, class_info)
    
    def create_class_frame(self, index, class_info=None):
        """创建课程框架"""
        if class_info is None:
            class_info = {
                "start_time": "08:00",
                "end_time": "08:45",
                "subject": "",
                "teacher": "教师",
                "classroom": "教室"
            }
        
        frame = ttk.Frame(self.scrollable_classes_frame)
        frame.pack(fill=tk.X, pady=2)
        
        # 序号
        ttk.Label(frame, text=str(index), width=5).grid(row=0, column=0, padx=5)
        
        # 开始时间
        start_time_var = tk.StringVar(value=class_info["start_time"])
        start_time_entry = ttk.Entry(frame, textvariable=start_time_var, width=10)
        start_time_entry.grid(row=0, column=1, padx=5)
        # 添加验证回调，保护时间格式
        start_time_var.trace_add("write", lambda *args: self.validate_time_format(start_time_var, "08:00"))
        
        # 结束时间
        end_time_var = tk.StringVar(value=class_info["end_time"])
        end_time_entry = ttk.Entry(frame, textvariable=end_time_var, width=10)
        end_time_entry.grid(row=0, column=2, padx=5)
        # 添加验证回调，保护时间格式
        end_time_var.trace_add("write", lambda *args: self.validate_time_format(end_time_var, "08:45"))
        
        # 课程名称
        subject_var = tk.StringVar(value=class_info["subject"])
        subject_entry = ttk.Entry(frame, textvariable=subject_var, width=15)
        subject_entry.grid(row=0, column=3, padx=5)
        
        # 教师
        teacher_var = tk.StringVar(value=class_info["teacher"])
        teacher_entry = ttk.Entry(frame, textvariable=teacher_var, width=10)
        teacher_entry.grid(row=0, column=4, padx=5)
        
        # 教室
        classroom_var = tk.StringVar(value=class_info["classroom"])
        classroom_entry = ttk.Entry(frame, textvariable=classroom_var, width=10)
        classroom_entry.grid(row=0, column=5, padx=5)
        
        # 删除按钮
        delete_button = ttk.Button(frame, text="删除", command=lambda f=frame: self.delete_class(f))
        delete_button.grid(row=0, column=6, padx=5)
        
        # 保存变量引用
        frame.data = {
            "start_time_var": start_time_var,
            "end_time_var": end_time_var,
            "subject_var": subject_var,
            "teacher_var": teacher_var,
            "classroom_var": classroom_var
        }
        
        self.class_frames.append(frame)
    
    def validate_time_format(self, time_var, default_value):
        """验证并保护时间格式为HH:MM"""
        current_value = time_var.get()
        
        # 如果输入为空，恢复默认值
        if not current_value:
            time_var.set(default_value)
            return
        
        # 如果不包含冒号，尝试修复
        if ":" not in current_value:
            # 如果是4位数字，格式化为HH:MM
            if current_value.isdigit() and len(current_value) == 4:
                hours = current_value[:2]
                minutes = current_value[2:]
                # 验证有效性
                try:
                    h = int(hours)
                    m = int(minutes)
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        time_var.set(f"{hours}:{minutes}")
                        return
                except ValueError:
                    pass
            # 其他情况恢复默认值
            time_var.set(default_value)
            return
        
        # 如果包含冒号，验证格式
        parts = current_value.split(":")
        if len(parts) != 2:
            time_var.set(default_value)
            return
            
        hours, minutes = parts
        
        # 验证小时和分钟
        try:
            h = int(hours)
            m = int(minutes)
            if not (0 <= h <= 23 and 0 <= m <= 59):
                time_var.set(default_value)
                return
        except ValueError:
            time_var.set(default_value)
            return
            
        # 确保格式正确（HH:MM）
        formatted_time = f"{h:02d}:{m:02d}"
        if current_value != formatted_time:
            time_var.set(formatted_time)
    
    def add_class(self):
        """添加新课程"""
        self.create_class_frame(len(self.class_frames) + 1)
    
    def delete_class(self, frame):
        """删除课程"""
        # 从界面中移除
        frame.destroy()
        self.class_frames.remove(frame)
        
        # 重新编号
        for i, f in enumerate(self.class_frames):
            # 更新序号标签
            for widget in f.winfo_children():
                if isinstance(widget, ttk.Label) and widget.grid_info()["column"] == 0:
                    widget.config(text=str(i+1))
    
    def save_current_day_data(self):
        """保存当前星期的数据"""
        # 收集当前星期的数据
        classes = []
        for frame in self.class_frames:
            class_data = {
                "start_time": frame.data["start_time_var"].get(),
                "end_time": frame.data["end_time_var"].get(),
                "subject": frame.data["subject_var"].get(),
                "teacher": frame.data["teacher_var"].get(),
                "classroom": frame.data["classroom_var"].get()
            }
            classes.append(class_data)
        
        # 保存到数据结构
        self.timetable_data[self.current_day] = classes
    
    def save_and_close(self):
        """保存并关闭"""
        # 保存当前星期的数据
        self.save_current_day_data()
        
        # 保存到文件
        self.save_data()
        
        # 关闭窗口
        self.window.destroy()