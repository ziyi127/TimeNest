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
        # 保存并关闭按钮
        save_and_close_button = ttk.Button(button_frame, text="保存并关闭", command=self.save_and_close)
        save_and_close_button.pack(side=tk.RIGHT, padx=5) 
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存", command=self.save_data)
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
        # 添加光标控制和删除键处理
        start_time_entry.bind("<KeyRelease>", lambda e: self.handle_time_key_release(e, start_time_entry, start_time_var))
        start_time_entry.bind("<KeyPress>", lambda e: self.handle_time_key_press(e, start_time_entry, start_time_var))
        
        # 结束时间
        end_time_var = tk.StringVar(value=class_info["end_time"])
        end_time_entry = ttk.Entry(frame, textvariable=end_time_var, width=10)
        end_time_entry.grid(row=0, column=2, padx=5)
        # 添加验证回调，保护时间格式
        end_time_var.trace_add("write", lambda *args: self.validate_time_format(end_time_var, "08:45"))
        # 添加光标控制和删除键处理
        end_time_entry.bind("<KeyRelease>", lambda e: self.handle_time_key_release(e, end_time_entry, end_time_var))
        end_time_entry.bind("<KeyPress>", lambda e: self.handle_time_key_press(e, end_time_entry, end_time_var))
        
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
    
    def handle_time_key_press(self, event, entry, time_var):
        """处理时间输入框按键按下事件"""
        # 获取当前光标位置
        cursor_pos = entry.index(tk.INSERT)
        current_value = time_var.get()
        
        # 处理删除键 - 防止删除冒号
        if event.keysym == "BackSpace":
            # 如果光标正好在冒号位置，阻止删除冒号并移动光标
            if cursor_pos == 3 and len(current_value) > 2 and current_value[2] == ":":
                entry.icursor(2)  # 将光标移动到冒号前
                return "break"  # 阻止默认的删除行为
        
        # 限制小时部分输入长度
        if ":" in current_value:
            parts = current_value.split(":", 1)  # 只分割一次
            # 如果光标在小时部分（冒号前）且小时部分已经有两位，阻止继续输入
            if len(parts) == 2 and len(parts[0]) >= 2 and cursor_pos <= 2 and event.char.isdigit():
                return "break"
        else:
            # 如果还没有冒号且小时部分已经有两位，阻止继续输入
            if len(current_value) >= 2 and cursor_pos <= 2 and event.char.isdigit():
                return "break"
        
        # 限制分钟部分输入长度
        if ":" in current_value:
            parts = current_value.split(":", 1)  # 只分割一次
            if len(parts) == 2 and len(parts[1]) >= 2 and cursor_pos > 3:
                # 如果分钟部分已经有两位且光标在分钟部分，阻止继续输入
                if event.char.isdigit():  # 只阻止数字输入
                    return "break"
        
        # 允许所有其他输入，不过滤字符
        return None  # 不阻止任何输入
    
    def handle_time_key_release(self, event, entry, time_var):
        """处理时间输入框按键释放事件"""
        # 获取当前光标位置和输入内容
        cursor_pos = entry.index(tk.INSERT)
        current_value = time_var.get()
        
        # 自动转换数字为时间格式的功能
        # 如果输入的是纯数字且在1000以内，则转换为时间格式
        if current_value.isdigit() and len(current_value) <= 4 and len(current_value) >= 1:
            num_value = int(current_value)
            if num_value < 1000:  # 确保是1000以内的数字
                # 根据数字长度转换为时间格式
                new_value = None
                if len(current_value) == 1:
                    # 例如: 3 -> 00:03
                    new_value = "00:0" + current_value
                elif len(current_value) == 2:
                    # 例如: 43 -> 00:43
                    new_value = "00:" + current_value
                elif len(current_value) == 3:
                    # 例如: 643 -> 06:43
                    hours = "0" + current_value[0]
                    minutes = current_value[1:]
                    # 验证时间有效性
                    try:
                        hour_val = int(hours)
                        min_val = int(minutes)
                        if hour_val <= 23 and min_val <= 59:
                            new_value = hours + ":" + minutes
                    except ValueError:
                        pass
                elif len(current_value) == 4:
                    # 例如: 0643 -> 06:43 或者 1800 -> 18:00
                    hours = current_value[:2]
                    minutes = current_value[2:]
                    # 验证时间有效性
                    try:
                        hour_val = int(hours)
                        min_val = int(minutes)
                        if hour_val <= 23 and min_val <= 59:
                            new_value = hours + ":" + minutes
                        else:
                            # 尝试其他可能的组合
                            # 例如: 2501 -> 02:50 (把25当作2和50)
                            # 或者 2559 -> 02:55 (把25当作2和55)
                            # 这种情况比较复杂，我们简单处理
                            pass
                    except ValueError:
                        pass
                
                # 如果生成了有效的时间格式，则更新值
                if new_value and ":" in new_value and new_value != current_value:
                    time_var.set(new_value)
                    # 将光标移动到末尾
                    entry.icursor(len(new_value))
                    return
        
        # 检查并限制小时部分长度（冒号前的部分）
        if ":" in current_value:
            parts = current_value.split(":", 1)  # 只分割一次，避免多个冒号的问题
            if len(parts) == 2:
                # 限制小时部分为两位数
                if len(parts[0]) > 2:
                    # 如果小时部分超过两位，只保留最后两位
                    new_hours = parts[0][-2:]
                    new_value = new_hours + ":" + parts[1]
                    time_var.set(new_value)
                    # 调整光标位置
                    entry.icursor(min(len(new_value), cursor_pos))
                    return
                # 限制分钟部分为两位数
                elif len(parts[1]) > 2:
                    # 如果分钟部分超过两位，截取前两位
                    new_value = parts[0] + ":" + parts[1][:2]
                    time_var.set(new_value)
                    # 调整光标位置
                    entry.icursor(min(len(new_value), cursor_pos))
                    return
                # 验证小时和分钟的有效性
                try:
                    hour_val = int(parts[0])
                    min_val = int(parts[1])
                    if hour_val > 23 or min_val > 59:
                        # 时间无效，但不自动修改，让用户自己修正
                        pass
                except ValueError:
                    # 包含非数字字符，不处理
                    pass
        else:
            # 如果还没有冒号且小时部分超过两位，只保留最后两位
            if len(current_value) > 2:
                new_value = current_value[-2:]
                time_var.set(new_value)
                # 调整光标位置
                entry.icursor(min(len(new_value), cursor_pos))
                return
        
        # 自动插入冒号功能
        if len(current_value) == 2 and ":" not in current_value and current_value.isdigit():
            # 在两位数字后自动插入冒号
            new_value = current_value + ":"
            time_var.set(new_value)
            # 自动将光标移动到分钟位置
            entry.icursor(3)
        elif len(current_value) == 3 and current_value[2] != ":" and ":" not in current_value and current_value.isdigit():
            # 如果第三位不是冒号且还没有冒号，插入冒号
            new_value = current_value[:2] + ":" + current_value[2:]
            time_var.set(new_value)
            # 调整光标位置
            entry.icursor(cursor_pos + 1)
        elif len(current_value) > 3 and ":" in current_value:
            # 确保冒号在正确位置
            parts = current_value.split(":", 1)  # 只分割一次
            if len(parts) == 2 and len(parts[0]) > 2:
                # 小时部分超过两位，重新格式化
                hours = parts[0][-2:]
                minutes = parts[1][:2] if parts[1] else ""
                new_value = hours + ":" + minutes
                time_var.set(new_value)
                # 调整光标位置
                if cursor_pos > 3:
                    entry.icursor(min(len(new_value), cursor_pos))
    
    def validate_time_format(self, time_var, default_value):
        """验证时间格式为HH:MM，但不自动修改用户输入"""
        # 不对用户输入进行自动修改，只在需要时提供基本验证
        # 用户可以自由输入，只有在保存时才会验证格式是否正确
        pass
    
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