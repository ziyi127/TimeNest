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
        self.latest_day_var = tk.StringVar(value="周一")
        self.latest_time_var = tk.StringVar(value="8:50")
        self.max_classes_per_day_var = tk.StringVar(value="8")
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
    
    def load_existing_data(self):
        """加载现有数据到UI"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meta_file_path = os.path.join(project_path, "classtableMeta.json")
            
            # 如果文件不存在，直接返回
            if not os.path.exists(meta_file_path):
                return
            
            # 读取现有数据
            with open(meta_file_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            # 加载设置项(在右键菜单打开的是这个？)
            if "settings" in meta_data:
                settings = meta_data["settings"]
                self.first_class_time_var.set(settings.get("first_class_time", "08:00"))
                self.latest_time_var.set(settings.get("latest_time", "8:50"))
                self.max_classes_per_day_var.set(str(settings.get("max_classes_per_day", 8)))
                self.small_break_var.set(str(settings.get("small_break_duration", 10)))
                self.large_break_var.set(str(settings.get("large_break_duration", 20)))
                self.lunch_break_var.set(str(settings.get("lunch_break_duration", 60)))
                self.lunch_break_period_var.set(str(settings.get("lunch_break_period", 4)))
                self.class_duration_var.set(str(settings.get("class_duration", 40)))
                self.latest_class_duration_var.set(str(settings.get("latest_class_duration", 40)))
            
            # 加载大课间设置
            if "large_break_periods" in meta_data:
                # 清除现有的大课间节次
                for frame, _ in self.large_break_periods:
                    frame.destroy()
                self.large_break_periods.clear()
                
                # 添加新的大课间节次
                for period in meta_data["large_break_periods"]:
                    self.add_large_break_period()
                    self.large_break_periods[-1][1].set(str(period))
            
            # 加载没有大课间的天
            if "no_large_break_days" in meta_data:
                # 清除现有的没有大课间的天
                for frame, _ in self.no_large_break_days:
                    frame.destroy()
                self.no_large_break_days.clear()
                
                # 添加新的没有大课间的天
                for day in meta_data["no_large_break_days"]:
                    self.add_no_large_break_day()
                    self.no_large_break_days[-1][1].set(day)
            
            # 加载课程列表
            if "allclass" in meta_data:
                # 清除现有的课程
                for frame, _ in self.classes:
                    frame.destroy()
                self.classes.clear()
                
                # 添加新的课程
                for class_name in meta_data["allclass"]:
                    self.add_class()
                    self.classes[-1][1].set(class_name)
        except Exception as e:
            print(f"加载现有数据时出错: {e}")
    
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
        self.window.geometry("580x570")
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
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 1. 最晚第一节课上课时间
        latest_time_label = ttk.Label(scrollable_frame, text="1. 最晚第一节课上课时间:")
        latest_time_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 最晚时间选择
        latest_frame = ttk.Frame(scrollable_frame)
        latest_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(latest_frame, text="周").pack(side=tk.LEFT)
        latest_day_combo = ttk.Combobox(latest_frame, textvariable=self.latest_day_var, state="readonly", width=10)
        latest_day_combo['values'] = ["一", "二", "三", "四", "五"]
        latest_day_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(latest_frame, text="最晚上课时间:").pack(side=tk.LEFT, padx=(10, 5))
        latest_time_entry = ttk.Entry(latest_frame, textvariable=self.latest_time_var, width=10)
        latest_time_entry.pack(side=tk.LEFT, padx=5)
        
        # 2. 一天最多有几节课
        max_classes_label = ttk.Label(scrollable_frame, text="2. 一天最多有几节课:")
        max_classes_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        max_classes_frame = ttk.Frame(scrollable_frame)
        max_classes_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        max_classes_entry = ttk.Entry(max_classes_frame, textvariable=self.max_classes_per_day_var, width=10)
        max_classes_entry.pack(side=tk.LEFT, padx=5)
        
        # 3. 日常第一节课上课时间
        first_class_label = ttk.Label(scrollable_frame, text="3. 日常第一节课上课时间:")
        first_class_label.grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        first_class_frame = ttk.Frame(scrollable_frame)
        first_class_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(first_class_frame, text="时间:").pack(side=tk.LEFT)
        first_class_entry = ttk.Entry(first_class_frame, textvariable=self.first_class_time_var, width=10)
        first_class_entry.pack(side=tk.LEFT, padx=5)
        
        # 4. 小课间时长
        small_break_label = ttk.Label(scrollable_frame, text="4. 小课间时长 (分钟):")
        small_break_label.grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        small_break_frame = ttk.Frame(scrollable_frame)
        small_break_frame.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        small_break_entry = ttk.Entry(small_break_frame, textvariable=self.small_break_var, width=10)
        small_break_entry.pack(side=tk.LEFT, padx=5)
        
        # 5. 最晚上课时间日子的上课时长
        latest_class_duration_label = ttk.Label(scrollable_frame, text="5. 最晚上课时间日子的上课时长 (分钟):")
        latest_class_duration_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        latest_class_duration_frame = ttk.Frame(scrollable_frame)
        latest_class_duration_frame.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        self.latest_class_duration_var = tk.StringVar(value="40")
        latest_class_duration_entry = ttk.Entry(latest_class_duration_frame, textvariable=self.latest_class_duration_var, width=10)
        latest_class_duration_entry.pack(side=tk.LEFT, padx=5)
        
        # 6. 大课间时长
        large_break_label = ttk.Label(scrollable_frame, text="6. 大课间时长 (分钟):")
        large_break_label.grid(row=8, column=0, sticky=tk.W, pady=(10, 5))
        large_break_frame = ttk.Frame(scrollable_frame)
        large_break_frame.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)
        large_break_entry = ttk.Entry(large_break_frame, textvariable=self.large_break_var, width=10)
        large_break_entry.pack(side=tk.LEFT, padx=5)
        
        # 6. 午休时长
        lunch_break_label = ttk.Label(scrollable_frame, text="6. 午休时长 (分钟):")
        lunch_break_label.grid(row=10, column=0, sticky=tk.W, pady=(10, 5))
        lunch_break_frame = ttk.Frame(scrollable_frame)
        lunch_break_frame.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5)
        lunch_break_entry = ttk.Entry(lunch_break_frame, textvariable=self.lunch_break_var, width=10)
        lunch_break_entry.pack(side=tk.LEFT, padx=5)
        
        # 7. 第几节课下课午休
        lunch_break_period_label = ttk.Label(scrollable_frame, text="7. 第几节课下课午休:")
        lunch_break_period_label.grid(row=12, column=0, sticky=tk.W, pady=(10, 5))
        lunch_break_period_frame = ttk.Frame(scrollable_frame)
        lunch_break_period_frame.grid(row=12, column=1, sticky=(tk.W, tk.E), pady=5)
        lunch_break_period_entry = ttk.Entry(lunch_break_period_frame, textvariable=self.lunch_break_period_var, width=10)
        lunch_break_period_entry.pack(side=tk.LEFT, padx=5)
        
        # 8. 上课时长
        class_duration_label = ttk.Label(scrollable_frame, text="8. 上课时长 (分钟):")
        class_duration_label.grid(row=14, column=0, sticky=tk.W, pady=(10, 5))
        class_duration_frame = ttk.Frame(scrollable_frame)
        class_duration_frame.grid(row=14, column=1, sticky=(tk.W, tk.E), pady=5)
        class_duration_entry = ttk.Entry(class_duration_frame, textvariable=self.class_duration_var, width=10)
        class_duration_entry.pack(side=tk.LEFT, padx=5)
        
        # 9. 第几节课下课有大课间
        large_break_period_label = ttk.Label(scrollable_frame, text="9. 第几节课下课有大课间:")
        large_break_period_label.grid(row=16, column=0, sticky=tk.W, pady=(10, 5))
        self.large_break_frame = ttk.Frame(scrollable_frame)
        self.large_break_frame.grid(row=16, column=1, sticky=(tk.W, tk.E), pady=5)
        self.add_large_break_period_button = ttk.Button(self.large_break_frame, text="+", command=self.add_large_break_period, width=2)
        self.add_large_break_period_button.pack(side=tk.LEFT, padx=2)
        self.add_large_break_period()
        
        # 10. 有哪些天没有大课间
        no_large_break_label = ttk.Label(scrollable_frame, text="10. 有哪些天没有大课间:")
        no_large_break_label.grid(row=18, column=0, sticky=tk.W, pady=(10, 5))
        self.no_large_break_frame = ttk.Frame(scrollable_frame)
        self.no_large_break_frame.grid(row=18, column=1, sticky=(tk.W, tk.E), pady=5)
        self.add_no_large_break_day_button = ttk.Button(self.no_large_break_frame, text="+", command=self.add_no_large_break_day, width=2)
        self.add_no_large_break_day_button.pack(side=tk.LEFT, padx=2)
        self.add_no_large_break_day()
        
        # 11. 学生有哪些课程要上
        classes_label = ttk.Label(scrollable_frame, text="11. 学生有哪些课程要上:")
        classes_label.grid(row=20, column=0, sticky=tk.W, pady=(10, 5))
        self.classes_frame = ttk.Frame(scrollable_frame)
        self.classes_frame.grid(row=20, column=1, sticky=(tk.W, tk.E), pady=5)
        self.add_class_button = ttk.Button(self.classes_frame, text="+", command=self.add_class, width=2)
        self.add_class_button.pack(side=tk.LEFT, padx=2)
        self.add_class()
        
        # 按钮框架
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=21, column=0, pady=20, sticky=tk.E)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存并继续", command=self.save_and_continue)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def add_large_break_period(self):
        """添加大课间节次"""
        frame = ttk.Frame(self.large_break_frame)
        frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(frame, text="-", command=lambda: self.remove_large_break_period(frame), width=2)
        remove_button.pack(side=tk.LEFT, padx=2)
        
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
        
        var = tk.StringVar(value="周一")
        combo = ttk.Combobox(frame, textvariable=var, state="readonly", width=10)
        combo['values'] = ["周一", "周二", "周三", "周四", "周五"]
        combo.pack(side=tk.LEFT, padx=5)
        
        remove_button = ttk.Button(frame, text="-", command=lambda: self.remove_no_large_break_day(frame), width=2)
        remove_button.pack(side=tk.LEFT, padx=2)
        
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
        
        remove_button = ttk.Button(frame, text="-", command=lambda: self.remove_class(frame), width=2)
        remove_button.pack(side=tk.LEFT, padx=2)
        
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
            "latest_day": self.latest_day_var.get(),
            "latest_time": self.latest_time_var.get(),
            "max_classes_per_day": self.max_classes_per_day_var.get(),
            "first_class_time": self.first_class_time_var.get(),
            "small_break": self.small_break_var.get(),
            "large_break": self.large_break_var.get(),
            "lunch_break": self.lunch_break_var.get(),
            "lunch_break_period": self.lunch_break_period_var.get(),
            "class_duration": self.class_duration_var.get(),
            "latest_class_duration": self.latest_class_duration_var.get(),
            "large_break_periods": [var.get() for _, var in self.large_break_periods],
            "no_large_break_days": [var.get() for _, var in self.no_large_break_days],
            "classes": [var.get() for _, var in self.classes]
        }
        #调试
        print("用户输入的日常第一节课时间：", data["first_class_time"])  #
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
            
            # 解除鼠标滚轮事件绑定
            try:
                canvas = self.window.nametowidget("!frame.!canvas")
                canvas.unbind_all("<MouseWheel>")
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
            
            if not self.is_valid_time(data["latest_time"]):
                messagebox.showerror("错误", "最晚上课时间格式不正确")
                return False
            
            # 验证数字字段
            int_fields = ["small_break", "large_break", "lunch_break", "lunch_break_period", "class_duration", "latest_class_duration", "max_classes_per_day"]
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
            
            # 保存设置项
            meta_data["settings"] = {
                "first_class_time": data["first_class_time"],
                "latest_time": data["latest_time"],
                "max_classes_per_day": int(data["max_classes_per_day"]),
                "small_break_duration": int(data["small_break"]),
                "large_break_duration": int(data["large_break"]),
                "lunch_break_duration": int(data["lunch_break"]),
                "lunch_break_period": int(data["lunch_break_period"]),
                "class_duration": int(data["class_duration"]),
                "latest_class_duration": int(data["latest_class_duration"])
            }
            
            # 保存大课间设置
            meta_data["large_break_periods"] = [int(p) for p in data["large_break_periods"] if p]
            meta_data["no_large_break_days"] = data["no_large_break_days"]
            
            # 保存到classtableMeta.json
            with open(meta_file_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存classtableMeta.json时出错: {e}")
            return False
    
    def generate_timetable(self, data):
        """根据用户输入生成时间表"""
        # 定义课程表数据
        timetable_data = {
            "Monday": ["历史", "历史", "英语", "英语", "数学", "数学", "班校会"],
            "Tuesday": ["体育", "体育", "语文", "语文", "电子技能与实训", "电子技能与实训", ""],
            "Wednesday": ["数学", "数学", "公共艺术", "英语", "语文", "语文", "心理健康"],
            "Thursday": ["哲学与人生", "哲学与人生", "体育", "移动通信网络设备", "单片机原理与应用", "单片机原理与应用", ""],
            "Friday": ["移动通信网络设备", "移动通信网络设备", "手机原理与维修", "手机原理与维修", "", "", ""]
        }

        # 时间规则
        rules = {
            "latest_first_class_time": data.get("latest_time", "08:40"),  # 周一最晚第一节课上课时间
            "normal_first_class_time": data.get("first_class_time", "08:00"),  # 日常第一节课上课时间
            "small_break_duration": int(data.get("small_break", 10)),  # 小课间时长（分钟）
            "large_break_duration": int(data.get("large_break", 20)),  # 大课间时长（分钟）
            "lunch_break_duration": int(data.get("lunch_break", 60)),  # 午休时长（分钟）
            "lunch_break_after_class": int(data.get("lunch_break_period", 4)),  # 第几节课下课午休
            "class_duration": int(data.get("class_duration", 45)),  # 上课时长（分钟）
            "latest_class_duration": int(data.get("latest_class_duration", 45)),  # 最晚上课时间日子的上课时长（分钟）
            "large_break_after_classes": [int(p) for p in data.get("large_break_periods", [2, 6]) if p],  # 第几节课下课有大课间
            "no_large_break_days": data.get("no_large_break_days", ["Monday"])  # 没有大课间的天
        }
        print("first_class_time_var的值：", self.first_class_time_var.get())
        print("data['first_class_time']的值：", data["first_class_time"])
        # 存储每天的课程时间
        daily_timetable = {}

        for day, subjects in timetable_data.items():
            daily_timetable[day.lower()] = []
            current_time = None
            # 确定当天第一节课的上课时间
            if day == "Monday":
                first_class_time = rules["latest_first_class_time"]
                print(f"第一节课上课时间{first_class_time}")
                # 检查周一是否在没有大课间的天数列表中
                is_large_break_day = "Monday" not in rules["no_large_break_days"]
            else:
                first_class_time = rules["normal_first_class_time"]
                is_large_break_day = day not in rules["no_large_break_days"]

            # 转换为分钟数，方便计算
            def time_to_minutes(time_str):
                hours, minutes = map(int, time_str.split(":"))
                return hours * 60 + minutes

            def minutes_to_time(minutes):
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours:02d}:{mins:02d}"

            first_class_minutes = time_to_minutes(first_class_time)

            for i, subject in enumerate(subjects, 1):
                # 确定当前课程的时长
                if day == "Monday":
                    current_class_duration = rules["latest_class_duration"]
                else:
                    current_class_duration = rules["class_duration"]
                
                # 计算上课时间
                class_start = first_class_minutes if i == 1 else current_time + rules["small_break_duration"]
                

                # 计算下课时间
                class_end = class_start + current_class_duration

                # 处理大课间
                if is_large_break_day and i in rules["large_break_after_classes"]:
                    break_end = class_end + rules["large_break_duration"]
                    daily_timetable[day.lower()].append({
                        "start_time": minutes_to_time(class_start),
                        "end_time": minutes_to_time(class_end)
                    })
                    current_time = break_end
                # 处理午休
                elif i == rules["lunch_break_after_class"]:
                    lunch_end = class_end + rules["lunch_break_duration"]
                    daily_timetable[day.lower()].append({
                        "start_time": minutes_to_time(class_start),
                        "end_time": minutes_to_time(class_end)
                    })
                    current_time = lunch_end
                # 普通课间
                else:
                    daily_timetable[day.lower()].append({
                        "start_time": minutes_to_time(class_start),
                        "end_time": minutes_to_time(class_end)
                    })
                    current_time = class_end

        return daily_timetable