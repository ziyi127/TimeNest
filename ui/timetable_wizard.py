import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class TimetableWizard:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.window = None
        
        # 初始化变量
        self.earliest_day_var = tk.StringVar(value="周一")
        self.earliest_time_var = tk.StringVar(value="最早")
        self.latest_day_var = tk.StringVar(value="周五")
        self.latest_time_var = tk.StringVar(value="最晚")
        self.first_class_time_var = tk.StringVar(value="08:00")
        self.small_break_var = tk.StringVar(value="10")
        self.large_break_var = tk.StringVar(value="20")
        self.lunch_break_var = tk.StringVar(value="60")
        self.lunch_break_period_var = tk.StringVar(value="4")
        self.class_duration_var = tk.StringVar(value="40")
        
        # 动态添加的变量列表
        self.large_break_periods = []
        self.no_large_break_days = []
        self.classes = []
    
    def open_window(self):
        """打开时间表设置向导"""
        # 如果窗口已存在，将其带到前台
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        # 创建新窗口
        self.window = tk.Toplevel(self.parent)
        self.window.title("时间表设置向导")
        self.window.geometry("600x700")
        self.window.resizable(True, True)
        
        # 设置窗口属性
        try:
            self.window.transient()
            self.window.wm_attributes("-topmost", False)
        except Exception as e:
            print(f"设置窗口属性时出错: {e}")
        
        # 创建界面元素
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面元素"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 创建滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 1. 最早或最晚第一节课上课时间
        ttk.Label(scrollable_frame, text="1. 最早或最晚第一节课上课时间:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 最早时间选择
        earliest_frame = ttk.Frame(scrollable_frame)
        earliest_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(earliest_frame, text="最早:").pack(side=tk.LEFT)
        earliest_day_combo = ttk.Combobox(earliest_frame, textvariable=self.earliest_day_var, state="readonly", width=10)
        earliest_day_combo['values'] = ["周一", "周二", "周三", "周四", "周五"]
        earliest_day_combo.pack(side=tk.LEFT, padx=5)
        earliest_time_combo = ttk.Combobox(earliest_frame, textvariable=self.earliest_time_var, state="readonly", width=10)
        earliest_time_combo['values'] = ["最早", "最晚"]
        earliest_time_combo.pack(side=tk.LEFT, padx=5)
        
        # 最晚时间选择
        latest_frame = ttk.Frame(scrollable_frame)
        latest_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(latest_frame, text="最晚:").pack(side=tk.LEFT)
        latest_day_combo = ttk.Combobox(latest_frame, textvariable=self.latest_day_var, state="readonly", width=10)
        latest_day_combo['values'] = ["周一", "周二", "周三", "周四", "周五"]
        latest_day_combo.pack(side=tk.LEFT, padx=5)
        latest_time_combo = ttk.Combobox(latest_frame, textvariable=self.latest_time_var, state="readonly", width=10)
        latest_time_combo['values'] = ["最早", "最晚"]
        latest_time_combo.pack(side=tk.LEFT, padx=5)
        
        # 2. 日常第一节课上课时间
        ttk.Label(scrollable_frame, text="2. 日常第一节课上课时间:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        first_class_frame = ttk.Frame(scrollable_frame)
        first_class_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(first_class_frame, text="时间:").pack(side=tk.LEFT)
        first_class_entry = ttk.Entry(first_class_frame, textvariable=self.first_class_time_var, width=10)
        first_class_entry.pack(side=tk.LEFT, padx=5)
        
        # 3. 小课间时长
        ttk.Label(scrollable_frame, text="3. 小课间时长 (分钟):")
        ttk.Label(scrollable_frame, text="3. 小课间时长 (分钟):").grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        small_break_frame = ttk.Frame(scrollable_frame)
        small_break_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)
        small_break_entry = ttk.Entry(small_break_frame, textvariable=self.small_break_var, width=10)
        small_break_entry.pack(side=tk.LEFT, padx=5)
        
        # 4. 大课间时长
        ttk.Label(scrollable_frame, text="4. 大课间时长 (分钟):")
        ttk.Label(scrollable_frame, text="4. 大课间时长 (分钟):").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        large_break_frame = ttk.Frame(scrollable_frame)
        large_break_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=5)
        large_break_entry = ttk.Entry(large_break_frame, textvariable=self.large_break_var, width=10)
        large_break_entry.pack(side=tk.LEFT, padx=5)
        
        # 5. 午休时长
        ttk.Label(scrollable_frame, text="5. 午休时长 (分钟):")
        ttk.Label(scrollable_frame, text="5. 午休时长 (分钟):").grid(row=9, column=0, sticky=tk.W, pady=(10, 5))
        lunch_break_frame = ttk.Frame(scrollable_frame)
        lunch_break_frame.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=5)
        lunch_break_entry = ttk.Entry(lunch_break_frame, textvariable=self.lunch_break_var, width=10)
        lunch_break_entry.pack(side=tk.LEFT, padx=5)
        
        # 6. 第几节课下课午休
        ttk.Label(scrollable_frame, text="6. 第几节课下课午休:")
        ttk.Label(scrollable_frame, text="6. 第几节课下课午休:").grid(row=11, column=0, sticky=tk.W, pady=(10, 5))
        lunch_break_period_frame = ttk.Frame(scrollable_frame)
        lunch_break_period_frame.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=5)
        lunch_break_period_entry = ttk.Entry(lunch_break_period_frame, textvariable=self.lunch_break_period_var, width=10)
        lunch_break_period_entry.pack(side=tk.LEFT, padx=5)
        
        # 7. 上课时长
        ttk.Label(scrollable_frame, text="7. 上课时长 (分钟):")
        ttk.Label(scrollable_frame, text="7. 上课时长 (分钟):").grid(row=13, column=0, sticky=tk.W, pady=(10, 5))
        class_duration_frame = ttk.Frame(scrollable_frame)
        class_duration_frame.grid(row=14, column=0, sticky=(tk.W, tk.E), pady=5)
        class_duration_entry = ttk.Entry(class_duration_frame, textvariable=self.class_duration_var, width=10)
        class_duration_entry.pack(side=tk.LEFT, padx=5)
        
        # 8. 第几节课下课有大课间
        ttk.Label(scrollable_frame, text="8. 第几节课下课有大课间:").grid(row=15, column=0, sticky=tk.W, pady=(10, 5))
        self.large_break_frame = ttk.Frame(scrollable_frame)
        self.large_break_frame.grid(row=16, column=0, sticky=(tk.W, tk.E), pady=5)
        self.add_large_break_period_button = ttk.Button(self.large_break_frame, text="+", command=self.add_large_break_period)
        self.add_large_break_period_button.pack(side=tk.LEFT, padx=5)
        self.add_large_break_period()
        
        # 9. 有哪些天没有大课间
        ttk.Label(scrollable_frame, text="9. 有哪些天没有大课间:").grid(row=17, column=0, sticky=tk.W, pady=(10, 5))
        self.no_large_break_frame = ttk.Frame(scrollable_frame)
        self.no_large_break_frame.grid(row=18, column=0, sticky=(tk.W, tk.E), pady=5)
        self.add_no_large_break_day_button = ttk.Button(self.no_large_break_frame, text="+", command=self.add_no_large_break_day)
        self.add_no_large_break_day_button.pack(side=tk.LEFT, padx=5)
        self.add_no_large_break_day()
        
        # 10. 学生有哪些课程要上
        ttk.Label(scrollable_frame, text="10. 学生有哪些课程要上:").grid(row=19, column=0, sticky=tk.W, pady=(10, 5))
        self.classes_frame = ttk.Frame(scrollable_frame)
        self.classes_frame.grid(row=20, column=0, sticky=(tk.W, tk.E), pady=5)
        self.add_class_button = ttk.Button(self.classes_frame, text="+", command=self.add_class)
        self.add_class_button.pack(side=tk.LEFT, padx=5)
        self.add_class()
        
        # 按钮框架
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=21, column=0, pady=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存并继续", command=self.save_and_continue)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def add_large_break_period(self):
        """添加大课间节次"""
        frame = ttk.Frame(self.large_break_frame)
        frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(frame, text="-", command=lambda: self.remove_large_break_period(frame))
        remove_button.pack(side=tk.LEFT, padx=5)
        
        self.large_break_periods.append((frame, var))
    
    def remove_large_break_period(self, frame):
        """移除大课间节次"""
        for i, (f, var) in enumerate(self.large_break_periods):
            if f == frame:
                self.large_break_periods.pop(i)
                break
        frame.destroy()
    
    def add_no_large_break_day(self):
        """添加没有大课间的天"""
        frame = ttk.Frame(self.no_large_break_frame)
        frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        var = tk.StringVar()
        combo = ttk.Combobox(frame, textvariable=var, state="readonly", width=10)
        combo['values'] = ["周一", "周二", "周三", "周四", "周五"]
        combo.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(frame, text="-", command=lambda: self.remove_no_large_break_day(frame))
        remove_button.pack(side=tk.LEFT, padx=5)
        
        self.no_large_break_days.append((frame, var))
    
    def remove_no_large_break_day(self, frame):
        """移除没有大课间的天"""
        for i, (f, var) in enumerate(self.no_large_break_days):
            if f == frame:
                self.no_large_break_days.pop(i)
                break
        frame.destroy()
    
    def add_class(self):
        """添加课程"""
        frame = ttk.Frame(self.classes_frame)
        frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var, width=20)
        entry.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(frame, text="-", command=lambda: self.remove_class(frame))
        remove_button.pack(side=tk.LEFT, padx=5)
        
        self.classes.append((frame, var))
    
    def remove_class(self, frame):
        """移除课程"""
        for i, (f, var) in enumerate(self.classes):
            if f == frame:
                self.classes.pop(i)
                break
        frame.destroy()
    
    def save_and_continue(self):
        """保存并继续到课程表设置向导"""
        # 收集数据
        data = {
            "earliest_day": self.earliest_day_var.get(),
            "earliest_time": self.earliest_time_var.get(),
            "latest_day": self.latest_day_var.get(),
            "latest_time": self.latest_time_var.get(),
            "first_class_time": self.first_class_time_var.get(),
            "small_break": self.small_break_var.get(),
            "large_break": self.large_break_var.get(),
            "lunch_break": self.lunch_break_var.get(),
            "lunch_break_period": self.lunch_break_period_var.get(),
            "class_duration": self.class_duration_var.get(),
            "large_break_periods": [var.get() for _, var in self.large_break_periods],
            "no_large_break_days": [var.get() for _, var in self.no_large_break_days],
            "classes": [var.get() for _, var in self.classes]
        }
        
        # 验证数据
        if not self.validate_data(data):
            return
        
        # 保存到classtableMeta.json
        if self.save_to_file(data):
            messagebox.showinfo("成功", "时间表设置已保存")
            # 关闭当前窗口
            self._cleanup_resources()
            self.window.destroy()
            # 打开课程表设置向导
            self.main_window.open_class_table_wizard()
    
    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 解除所有事件绑定
            try:
                # 解除开始时间输入框的事件绑定
                for _, var in self.large_break_periods:
                    try:
                        var.trace_remove("write", var.trace_info()[0][1])
                    except:
                        pass
            except:
                pass
            
            # 解除结束时间输入框的事件绑定
            try:
                for _, var in self.no_large_break_days:
                    try:
                        var.trace_remove("write", var.trace_info()[0][1])
                    except:
                        pass
            except:
                pass
            
            # 解除复选框的事件绑定
            try:
                for _, var in self.classes:
                    try:
                        var.trace_remove("write", var.trace_info()[0][1])
                    except:
                        pass
            except:
                pass
            
            # 解除其他可能的事件绑定
            try:
                for child in self.window.winfo_children():
                    try:
                        child.unbind("<Configure>")
                    except:
                        pass
                    try:
                        child.unbind("<Destroy>")
                    except:
                        pass
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
            print(f"清理时间表向导界面资源时出错: {e}")
    
    def validate_data(self, data):
        """验证数据"""
        try:
            # 验证时间格式
            if not self.is_valid_time(data["first_class_time"]):
                messagebox.showerror("错误", "日常第一节课上课时间格式不正确")
                return False
            
            # 验证数字字段
            int_fields = ["small_break", "large_break", "lunch_break", "lunch_break_period", "class_duration"]
            for field in int_fields:
                int(data[field])
            
            # 验证大课间节次
            for period in data["large_break_periods"]:
                if period:  # 只验证非空值
                    int(period)
            
            # 验证课程
            if not data["classes"] or all(not c for c in data["classes"]):
                messagebox.showerror("错误", "请至少添加一个课程")
                return False
            
            return True
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的数字")
            return False
    
    def is_valid_time(self, time_str):
        """验证时间格式 HH:MM"""
        try:
            hours, minutes = time_str.split(":")
            hours = int(hours)
            minutes = int(minutes)
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except:
            return False
    
    def save_to_file(self, data):
        """保存数据到classtableMeta.json"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meta_file_path = os.path.join(project_path, "classtableMeta.json")
            
            # 如果文件存在，加载现有数据
            if os.path.exists(meta_file_path):
                with open(meta_file_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
            else:
                meta_data = {}
            
            # 更新timetable和allclass字段
            meta_data["timetable"] = self.generate_timetable(data)
            meta_data["allclass"] = data["classes"]
            
            # 保存到classtableMeta.json
            with open(meta_file_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存classtableMeta.json时出错: {e}")
            return False
    
    def generate_timetable(self, data):
        """根据用户输入生成时间表"""
        # 获取项目目录
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        meta_file_path = os.path.join(project_path, "classtableMeta.json")
        
        # 读取现有数据
        if os.path.exists(meta_file_path):
            with open(meta_file_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
        else:
            meta_data = {}
        
        # 获取用户设置
        first_class_time = data.get("first_class_time", "08:00")
        class_duration = int(data.get("class_duration", 40))
        small_break = int(data.get("small_break", 10))
        large_break = int(data.get("large_break", 20))
        lunch_break = int(data.get("lunch_break", 60))
        lunch_break_period = int(data.get("lunch_break_period", 4))
        large_break_periods = [int(p) for p in data.get("large_break_periods", []) if p]
        no_large_break_days = data.get("no_large_break_days", [])
        
        # 星期映射
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        
        # 生成时间表
        timetable = {}
        
        # 解析第一节课时间
        try:
            start_hour, start_minute = map(int, first_class_time.split(":"))
            current_time = start_hour * 60 + start_minute
        except:
            current_time = 8 * 60  # 默认8:00
        
        # 为每天生成时间表
        for day in weekdays:
            day_schedule = []
            
            # 生成8节课
            for period in range(1, 9):
                # 计算开始时间
                start_time = f"{current_time // 60:02d}:{current_time % 60:02d}"
                
                # 计算结束时间
                end_time_minutes = current_time + class_duration
                end_time = f"{end_time_minutes // 60:02d}:{end_time_minutes % 60:02d}"
                
                # 添加课程时间段
                day_schedule.append({
                    "start_time": start_time,
                    "end_time": end_time
                })
                
                # 更新当前时间
                current_time = end_time_minutes
                
                # 添加课间休息
                if period == lunch_break_period:
                    # 午休
                    current_time += lunch_break
                elif period in large_break_periods and day not in no_large_break_days:
                    # 大课间
                    current_time += large_break
                else:
                    # 小课间
                    current_time += small_break
            
            timetable[day] = day_schedule
            
            # 重置时间为第二天的第一节课时间
            try:
                start_hour, start_minute = map(int, first_class_time.split(":"))
                current_time = start_hour * 60 + start_minute
            except:
                current_time = 8 * 60  # 默认8:00
        
        return timetable