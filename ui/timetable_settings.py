import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime

class TimetableSettings:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("课程表设置")
        self.window.geometry("800x600")
        
        # 存储课表数据
        self.timetable_data = {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": []
        }
        
        # 存储时间块数据
        self.time_blocks = {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": []
        }
        
        # 存储课表块数据
        self.class_blocks = []
        
        # 当前选中的星期
        self.current_weekday = "monday"
        
        # 拖拽相关变量
        self.drag_data = {"x": 0, "y": 0, "item": None, "class_block": None}
        
        self.create_widgets()
        self.load_timetable()
    
    def create_widgets(self):
        # 创建顶部工具栏
        toolbar = tk.Frame(self.window)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Button(toolbar, text="保存", command=self.save_timetable).pack(side=tk.RIGHT, padx=5)
        tk.Button(toolbar, text="导入", command=self.import_timetable).pack(side=tk.RIGHT, padx=5)
        
        # 创建主内容区域
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建左侧时间轴
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 时间轴操作区
        time_op_frame = tk.Frame(left_frame)
        time_op_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(time_op_frame, text="复制", command=self.copy_time_blocks).pack(side=tk.LEFT)
        
        # 星期选择
        self.weekday_var = tk.StringVar(value="monday")
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        for i, (day, name) in enumerate(zip(weekdays, weekday_names)):
            tk.Radiobutton(time_op_frame, text=name, variable=self.weekday_var, value=day, 
                          command=self.switch_weekday).pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(left_frame, text="课表").pack()
        
        # 时间轴主体
        time_canvas_frame = tk.Frame(left_frame)
        time_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.time_canvas = tk.Canvas(time_canvas_frame, width=100, bg="lightgray")
        time_scrollbar = tk.Scrollbar(time_canvas_frame, orient="vertical", command=self.time_canvas.yview)
        self.time_canvas.configure(yscrollcommand=time_scrollbar.set)
        
        self.time_canvas.pack(side="left", fill="both", expand=True)
        time_scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        self.time_canvas.bind("<MouseWheel>", self.on_time_canvas_mousewheel)
        
        # 创建时间点
        self.create_time_points()
        
        # 创建中间课表区
        center_frame = tk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.schedule_canvas = tk.Canvas(center_frame, bg="white")
        schedule_scrollbar = tk.Scrollbar(center_frame, orient="vertical", command=self.schedule_canvas.yview)
        self.schedule_canvas.configure(yscrollcommand=schedule_scrollbar.set)
        
        self.schedule_canvas.pack(side="left", fill="both", expand=True)
        schedule_scrollbar.pack(side="right", fill="y")
        
        # 在课表区添加提示文字
        self.schedule_canvas.create_text(200, 150, text="将课表块拖动至此", fill="gray", tags="placeholder")
        
        # 绑定鼠标滚轮事件
        self.schedule_canvas.bind("<MouseWheel>", self.on_schedule_canvas_mousewheel)
        
        # 绑定拖拽事件
        self.schedule_canvas.bind("<Button-1>", self.on_schedule_click)
        self.schedule_canvas.bind("<B1-Motion>", self.on_schedule_drag)
        self.schedule_canvas.bind("<ButtonRelease-1>", self.on_schedule_drop)
        
        # 绑定鼠标进入和离开事件
        self.schedule_canvas.bind("<Enter>", self.on_schedule_enter)
        self.schedule_canvas.bind("<Leave>", self.on_schedule_leave)
        
        # 创建右侧侧边栏
        right_frame = tk.Frame(main_frame, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # 添加课程区域
        add_class_frame = tk.LabelFrame(right_frame, text="添加课程")
        add_class_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(add_class_frame, text="课程名:").pack(anchor=tk.W)
        self.subject_entry = tk.Entry(add_class_frame)
        self.subject_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(add_class_frame, text="教师:").pack(anchor=tk.W)
        self.teacher_entry = tk.Entry(add_class_frame)
        self.teacher_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(add_class_frame, text="教室:").pack(anchor=tk.W)
        self.classroom_entry = tk.Entry(add_class_frame)
        self.classroom_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Button(add_class_frame, text="添加", command=self.add_class_block).pack(pady=5)
        
        # 课表块列表
        tk.Label(right_frame, text="课表块").pack(anchor=tk.W)
        
        class_block_frame = tk.Frame(right_frame)
        class_block_frame.pack(fill=tk.BOTH, expand=True)
        
        self.class_block_listbox = tk.Listbox(class_block_frame)
        class_block_scrollbar = tk.Scrollbar(class_block_frame, orient="vertical", command=self.class_block_listbox.yview)
        self.class_block_listbox.configure(yscrollcommand=class_block_scrollbar.set)
        
        self.class_block_listbox.pack(side="left", fill="both", expand=True)
        class_block_scrollbar.pack(side="right", fill="y")
        
        # 绑定双击事件
        self.class_block_listbox.bind("<Double-Button-1>", self.on_block_double_click)
        
        # 绑定拖拽事件
        self.class_block_listbox.bind("<Button-1>", self.on_block_click)
        self.class_block_listbox.bind("<B1-Motion>", self.on_block_drag)
        self.class_block_listbox.bind("<ButtonRelease-1>", self.on_block_drop)
        
        # 创建底部星期栏
        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.weekday_buttons = []
        for i, name in enumerate(weekday_names):
            btn = tk.Button(bottom_frame, text=name, 
                           command=lambda day=weekdays[i]: self.switch_weekday_button(day))
            btn.pack(side=tk.LEFT, padx=2)
            self.weekday_buttons.append(btn)
        
        # 设置默认高亮
        self.weekday_buttons[0].config(relief=tk.SUNKEN)
    
    def create_time_points(self):
        """创建时间点"""
        self.time_canvas.delete("all")
        
        # 创建时间点
        for hour in range(24):
            y = hour * 60
            
            # 绘制时间线
            self.time_canvas.create_line(0, y, 100, y, fill="gray")
            
            # 显示时间
            self.time_canvas.create_text(50, y+10, text=f"{hour:02d}:00", anchor="n")
            
            # 创建时间块
            for block in self.time_blocks[self.current_weekday]:
                start_hour = int(block["start_time"].split(":")[0])
                start_minute = int(block["start_time"].split(":")[1])
                end_hour = int(block["end_time"].split(":")[0])
                end_minute = int(block["end_time"].split(":")[1])
                
                start_y = start_hour * 60 + start_minute
                end_y = end_hour * 60 + end_minute
                
                # 绘制时间块
                rect = self.time_canvas.create_rectangle(10, start_y, 90, end_y, fill="lightblue", tags=("time_block", block["id"]))
                
                # 绑定点击事件
                self.time_canvas.tag_bind(rect, "<Button-1>", lambda e, b=block: self.edit_time_block(b))
    
    def switch_weekday(self):
        """切换星期"""
        self.current_weekday = self.weekday_var.get()
        self.create_time_points()
        self.update_schedule_display()
    
    def switch_weekday_button(self, day):
        """通过底部按钮切换星期"""
        self.current_weekday = day
        self.weekday_var.set(day)
        
        # 更新按钮状态
        for i, btn in enumerate(self.weekday_buttons):
            if i == list(self.timetable_data.keys()).index(day):
                btn.config(relief=tk.SUNKEN)
            else:
                btn.config(relief=tk.RAISED)
        
        self.create_time_points()
        self.update_schedule_display()
    
    def add_time_block(self, start_time, end_time):
        """添加时间块"""
        block_id = str(len(self.time_blocks[self.current_weekday]) + 1)
        block = {
            "id": block_id,
            "start_time": start_time,
            "end_time": end_time
        }
        self.time_blocks[self.current_weekday].append(block)
        self.create_time_points()
    
    def edit_time_block(self, block):
        """编辑时间块"""
        # 这里可以添加编辑时间块的逻辑
        pass
    
    def copy_time_blocks(self):
        """复制时间块"""
        # 这里可以添加复制时间块的逻辑
        pass
    
    def add_class_block(self):
        """添加课表块"""
        subject = self.subject_entry.get()
        teacher = self.teacher_entry.get()
        classroom = self.classroom_entry.get()
        
        if subject:
            block = {
                "subject": subject,
                "teacher": teacher,
                "classroom": classroom
            }
            self.class_blocks.append(block)
            self.update_class_block_list()
            
            # 清空输入框
            self.subject_entry.delete(0, tk.END)
            self.teacher_entry.delete(0, tk.END)
            self.classroom_entry.delete(0, tk.END)
    
    def update_class_block_list(self):
        """更新课表块列表显示"""
        self.class_block_listbox.delete(0, tk.END)
        for block in self.class_blocks:
            display_text = f"{block['subject']}"
            if block['teacher']:
                display_text += f" - {block['teacher']}"
            if block['classroom']:
                display_text += f" - {block['classroom']}"
            self.class_block_listbox.insert(tk.END, display_text)
    
    def on_block_double_click(self, event):
        """双击课表块"""
        selection = self.class_block_listbox.curselection()
        if selection:
            index = selection[0]
            block = self.class_blocks[index]
            
            # 添加到当前星期的课表数据中
            self.timetable_data[self.current_weekday].append(block)
            self.update_schedule_display()
    
    def delete_class_block(self, index):
        """删除课表块"""
        if 0 <= index < len(self.class_blocks):
            del self.class_blocks[index]
            self.update_class_block_list()
            self.update_schedule_display()
    
    def update_schedule_display(self):
        """更新课表显示"""
        # 清空课表区
        self.schedule_canvas.delete("class_block")
        
        # 如果没有课程，显示提示文字
        if not self.timetable_data[self.current_weekday]:
            self.schedule_canvas.create_text(200, 150, text="将课表块拖动至此", fill="gray", tags="placeholder")
        else:
            # 隐藏提示文字
            self.schedule_canvas.delete("placeholder")
            
            # 显示课程
            for i, block in enumerate(self.timetable_data[self.current_weekday]):
                y = i * 60 + 10
                rect = self.schedule_canvas.create_rectangle(10, y, 390, y+50, fill="lightblue", tags="class_block")
                text = f"{block['subject']}"
                if block['teacher']:
                    text += f"\n{block['teacher']}"
                if block['classroom']:
                    text += f"\n{block['classroom']}"
                self.schedule_canvas.create_text(200, y+25, text=text, tags="class_block")
    
    def save_timetable(self):
        """保存课表"""
        try:
            # 获取用户文档目录
            doc_path = os.path.join(os.path.expanduser("~"), "Documents")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"timetable_{timestamp}.json"
            file_path = os.path.join(doc_path, filename)
            
            # 合并数据
            data = {
                "timetable": self.timetable_data,
                "time_blocks": self.time_blocks
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("保存成功", f"课表已保存到: {file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存课表时出错: {str(e)}")
    
    def import_timetable(self):
        """导入课表"""
        try:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择课表文件",
                filetypes=[("JSON files", "*.json")]
            )
            
            if file_path:
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新数据
                self.timetable_data = data.get("timetable", {})
                self.time_blocks = data.get("time_blocks", {})
                
                # 更新显示
                self.create_time_points()
                self.update_schedule_display()
                
                messagebox.showinfo("导入成功", "课表已成功导入")
        except Exception as e:
            messagebox.showerror("导入失败", f"导入课表时出错: {str(e)}")
    
    def load_timetable(self):
        """加载课表"""
        try:
            # 获取用户文档目录
            doc_path = os.path.join(os.path.expanduser("~"), "Documents")
            
            # 查找最新的课表文件
            timetable_files = [f for f in os.listdir(doc_path) if f.startswith("timetable_") and f.endswith(".json")]
            
            if timetable_files:
                # 获取最新的文件
                latest_file = max(timetable_files)
                file_path = os.path.join(doc_path, latest_file)
                
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新数据
                self.timetable_data = data.get("timetable", {})
                self.time_blocks = data.get("time_blocks", {})
                
                # 更新显示
                self.create_time_points()
                self.update_schedule_display()
        except Exception as e:
            print(f"加载课表时出错: {e}")
    
    def on_time_canvas_mousewheel(self, event):
        """时间轴画布鼠标滚轮事件"""
        self.time_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_schedule_canvas_mousewheel(self, event):
        """课表区画布鼠标滚轮事件"""
        self.schedule_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_schedule_click(self, event):
        """课表区点击事件"""
        # 记录点击位置
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_schedule_drag(self, event):
        """课表区拖拽事件"""
        # 如果正在拖拽课表块
        if self.drag_data["item"]:
            # 计算移动距离
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            
            # 移动课表块
            self.schedule_canvas.move(self.drag_data["item"], delta_x, delta_y)
            
            # 更新拖拽起始位置
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def on_schedule_drop(self, event):
        """课表区释放事件"""
        # 如果正在拖拽课表块
        if self.drag_data["item"]:
            # 删除拖拽的可视化元素
            self.schedule_canvas.delete(self.drag_data["item"])
            
            # 重置拖拽数据
            self.drag_data["item"] = None
            self.drag_data["class_block"] = None
            
            # 恢复课表区背景色
            self.schedule_canvas.config(bg="white")
    
    def on_schedule_enter(self, event):
        """鼠标进入课表区事件"""
        # 如果正在拖拽课表块，改变背景色
        if self.drag_data["class_block"]:
            self.schedule_canvas.config(bg="lightgray")
    
    def on_schedule_leave(self, event):
        """鼠标离开课表区事件"""
        # 恢复课表区背景色
        self.schedule_canvas.config(bg="white")
    
    def on_block_click(self, event):
        """点击课表块事件"""
        # 获取选中的课表块
        selection = self.class_block_listbox.curselection()
        if selection:
            index = selection[0]
            self.drag_data["class_block"] = self.class_blocks[index]
    
    def on_block_drag(self, event):
        """拖拽课表块事件"""
        # 如果有选中的课表块
        if self.drag_data["class_block"]:
            # 如果还没有创建拖拽的可视化元素
            if not self.drag_data["item"]:
                # 创建半透明的课表块
                self.drag_data["item"] = self.schedule_canvas.create_rectangle(
                    event.x-50, event.y-25, event.x+50, event.y+25,
                    fill="lightblue", stipple="gray50", tags="dragging"
                )
            else:
                # 更新拖拽的可视化元素位置
                self.schedule_canvas.coords(
                    self.drag_data["item"],
                    event.x-50, event.y-25, event.x+50, event.y+25
                )
    
    def on_block_drop(self, event):
        """释放课表块事件"""
        # 如果正在拖拽课表块
        if self.drag_data["class_block"]:
            # 检查是否在课表区内释放
            if self.schedule_canvas.find_withtag("current"):
                # 添加到当前星期的课表数据中
                self.timetable_data[self.current_weekday].append(self.drag_data["class_block"])
                self.update_schedule_display()
            
            # 重置拖拽数据
            self.drag_data["item"] = None
            self.drag_data["class_block"] = None