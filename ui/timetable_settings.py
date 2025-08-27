import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import platform
import logging
from datetime import datetime
from pathlib import Path
import sys

class TimetableSettings:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("📅 智能课表编辑器")
        self.window.geometry("1000x700")
        self.window.minsize(800, 600)
        
        # 设置窗口图标
        try:
            if os.path.exists("TKtimetable.ico"):
                self.window.iconbitmap("TKtimetable.ico")
        except:
            pass
        
        # 跨平台支持
        self.platform = platform.system().lower()
        self.logger = logging.getLogger(__name__)
        
        # 获取用户文档目录（跨平台）
        self.doc_path = self._get_documents_path()
        self.doc_path.mkdir(parents=True, exist_ok=True)
        
        # 存储课表数据
        self.timetable_data = {
            "monday": [], "tuesday": [], "wednesday": [], "thursday": [], 
            "friday": [], "saturday": [], "sunday": []
        }
        
        # 存储时间块数据
        self.time_blocks = {
            "monday": [], "tuesday": [], "wednesday": [], "thursday": [],
            "friday": [], "saturday": [], "sunday": []
        }
        
        # 存储课表块数据
        self.class_blocks = []
        
        # 当前选中的星期
        self.current_weekday = "monday"
        
        # 拖拽相关变量
        self.drag_data = {"x": 0, "y": 0, "item": None, "class_block": None}
        
        # 新增功能变量
        self.zoom_level = 1.0
        self.undo_stack = []
        self.redo_stack = []
        self.conflict_detection = True
        self.smart_suggestions = True
        
        # 主题配置
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#333333",
                "accent": "#007bff",
                "secondary": "#6c757d",
                "success": "#28a745",
                "danger": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8"
            },
            "dark": {
                "bg": "#1a1a1a",
                "fg": "#e0e0e0",
                "accent": "#0d6efd",
                "secondary": "#6c757d",
                "success": "#198754",
                "danger": "#dc3545",
                "warning": "#fd7e14",
                "info": "#0dcaf0"
            }
        }
        
        # 当前主题
        self.current_theme = "light"
        
        # 智能时间推荐
        self.time_slots = [
            "08:00", "08:50", "09:40", "10:30", "11:20", "14:00", 
            "14:50", "15:40", "16:30", "19:00", "19:50", "20:40"
        ]
        
        self.create_widgets()
        self.load_timetable()
    
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

    def create_widgets(self):
        # 创建顶部工具栏
        toolbar = tk.Frame(self.window, bg="#f8f9fa")
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        
        # 左侧工具组
        left_tools = tk.Frame(toolbar, bg="#f8f9fa")
        left_tools.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 增强的保存按钮组
        save_frame = tk.Frame(left_tools, bg="#f8f9fa")
        save_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(save_frame, text="💾 保存", command=self.save_timetable, 
                 bg="#28a745", fg="white", relief=tk.FLAT, 
                 padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=2)
        
        tk.Button(save_frame, text="📁 导入", command=self.import_timetable,
                 bg="#007bff", fg="white", relief=tk.FLAT,
                 padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=2)
        
        tk.Button(save_frame, text="🔄 重置", command=self.reset_timetable,
                 bg="#6c757d", fg="white", relief=tk.FLAT,
                 padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=2)
        
        # 右侧视图控制组
        view_frame = tk.Frame(toolbar, bg="#f8f9fa")
        view_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 主题切换按钮
        self.theme_var = tk.StringVar(value="light")
        theme_frame = tk.Frame(view_frame, bg="#f8f9fa")
        theme_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(theme_frame, text="主题:", bg="#f8f9fa").pack(side=tk.LEFT, padx=(0, 5))
        
        themes = [("浅色", "light"), ("深色", "dark")]
        for text, value in themes:
            tk.Radiobutton(theme_frame, text=text, variable=self.theme_var, value=value,
                          command=self.switch_theme, bg="#f8f9fa").pack(side=tk.LEFT, padx=2)
        
        # 视图缩放
        zoom_frame = tk.Frame(view_frame, bg="#f8f9fa")
        zoom_frame.pack(side=tk.LEFT)
        
        tk.Button(zoom_frame, text="🔍+", command=self.zoom_in,
                 bg="#f8f9fa", relief=tk.FLAT, padx=5, pady=5).pack(side=tk.LEFT, padx=1)
        tk.Button(zoom_frame, text="🔍-", command=self.zoom_out,
                 bg="#f8f9fa", relief=tk.FLAT, padx=5, pady=5).pack(side=tk.LEFT, padx=1)
        
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
        """创建现代化时间点显示"""
        self.time_canvas.delete("all")
        
        # 设置画布背景
        theme = self.themes[self.current_theme]
        self.time_canvas.config(bg=theme["bg"])
        
        # 创建时间点 - 使用缩放
        hour_height = int(60 * self.zoom_level)
        
        for hour in range(6, 22):  # 只显示上课时间
            y = (hour - 6) * hour_height
            
            # 绘制时间线
            self.time_canvas.create_line(0, y, 100, y, fill=theme["secondary"], width=1)
            
            # 显示时间
            self.time_canvas.create_text(50, y+10, text=f"{hour:02d}:00", 
                                       anchor="n", fill=theme["fg"], 
                                       font=("Arial", 10, "bold"))
            
            # 半小时标记
            self.time_canvas.create_line(0, y + hour_height//2, 30, y + hour_height//2, 
                                       fill=theme["secondary"], width=1, stipple="gray50")
        
        # 创建时间块 - 智能时间推荐
        self.create_smart_time_blocks()
        
        # 配置滚动区域
        total_height = (22 - 6) * hour_height
        self.time_canvas.config(scrollregion=(0, 0, 100, total_height))
    
    def create_smart_time_blocks(self):
        """创建智能时间块"""
        theme = self.themes[self.current_theme]
        hour_height = int(60 * self.zoom_level)
        
        for block in self.time_blocks[self.current_weekday]:
            try:
                start_hour = int(block["start_time"].split(":")[0])
                start_minute = int(block["start_time"].split(":")[1])
                end_hour = int(block["end_time"].split(":")[0])
                end_minute = int(block["end_time"].split(":")[1])
                
                if 6 <= start_hour < 22:  # 只显示上课时间
                    start_y = (start_hour - 6) * hour_height + start_minute * hour_height // 60
                    end_y = (end_hour - 6) * hour_height + end_minute * hour_height // 60
                    
                    # 检查冲突
                    conflict = self.check_time_conflict(block)
                    color = theme["danger"] if conflict else theme["success"]
                    
                    # 绘制时间块
                    rect = self.time_canvas.create_rectangle(
                        5, start_y, 95, end_y, 
                        fill=color, outline=theme["accent"], width=2,
                        tags=("time_block", block["id"], "clickable")
                    )
                    
                    # 添加文字
                    if end_y - start_y > 20:  # 足够空间显示文字
                        self.time_canvas.create_text(
                            50, (start_y + end_y) // 2,
                            text=block.get("subject", "课程"),
                            fill="white", font=("Arial", 8),
                            tags=("time_block", block["id"])
                        )
                    
                    # 绑定事件
                    self.time_canvas.tag_bind(rect, "<Button-1>", 
                                            lambda e, b=block: self.edit_time_block(b))
                    self.time_canvas.tag_bind(rect, "<Enter>", 
                                            lambda e: self.on_block_hover(e, block))
                    self.time_canvas.tag_bind(rect, "<Leave>", 
                                            lambda e: self.on_block_leave(e, block))
                    
            except (ValueError, KeyError):
                continue
    
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
        """智能添加课表块"""
        subject = self.subject_entry.get().strip()
        teacher = self.teacher_entry.get().strip()
        classroom = self.classroom_entry.get().strip()
        
        if not subject:
            messagebox.showwarning("警告", "请输入课程名称！")
            return
        
        # 检查重复课程
        for block in self.class_blocks:
            if block["subject"] == subject and block["teacher"] == teacher:
                if not messagebox.askyesno("确认", f"已存在相同的课程 '{subject}'，是否继续添加？"):
                    return
        
        # 智能推荐时间
        suggested_time = self.suggest_time_slot(subject)
        
        block = {
            "subject": subject,
            "teacher": teacher,
            "classroom": classroom,
            "color": self.generate_course_color(subject),
            "suggested_time": suggested_time,
            "duration": 50,  # 默认50分钟
            "created_at": datetime.now().isoformat()
        }
        
        # 保存操作历史
        self.save_state("添加课程", block)
        
        self.class_blocks.append(block)
        self.update_class_block_list()
        
        # 清空输入框
        self.subject_entry.delete(0, tk.END)
        self.teacher_entry.delete(0, tk.END)
        self.classroom_entry.delete(0, tk.END)
        
        # 显示成功提示
        self.show_toast(f"成功添加课程: {subject}")
    
    def suggest_time_slot(self, subject):
        """智能推荐时间槽"""
        # 基于课程类型推荐时间
        subject_lower = subject.lower()
        
        if any(word in subject_lower for word in ["数学", "物理", "化学"]):
            return ["08:00", "09:40", "14:00", "15:40"]  # 上午和下午精力好的时间
        elif any(word in subject_lower for word in ["语文", "英语", "历史"]):
            return ["08:50", "10:30", "14:50", "16:30"]  # 记忆类课程
        elif any(word in subject_lower for word in ["体育", "音乐", "美术"]):
            return ["10:30", "15:40", "19:00", "19:50"]  # 下午或晚上活动类
        else:
            return self.time_slots
    
    def generate_course_color(self, subject):
        """为课程生成独特颜色"""
        import hashlib
        
        # 基于课程名称生成颜色
        hash_obj = hashlib.md5(subject.encode())
        color_hex = hash_obj.hexdigest()[:6]
        return f"#{color_hex}"
    
    def check_time_conflict(self, new_block):
        """检查时间冲突"""
        if not self.conflict_detection:
            return False
            
        try:
            new_start = self.time_to_minutes(new_block["start_time"])
            new_end = self.time_to_minutes(new_block["end_time"])
            
            for block in self.timetable_data[self.current_weekday]:
                if "start_time" in block and "end_time" in block:
                    existing_start = self.time_to_minutes(block["start_time"])
                    existing_end = self.time_to_minutes(block["end_time"])
                    
                    # 检查重叠
                    if (new_start < existing_end and new_end > existing_start):
                        return True
                        
        except (KeyError, ValueError):
            pass
            
        return False
    
    def time_to_minutes(self, time_str):
        """将时间字符串转换为分钟"""
        hour, minute = map(int, time_str.split(":"))
        return hour * 60 + minute
    
    def save_state(self, action, data):
        """保存操作历史用于撤销/重做"""
        self.undo_stack.append({
            "action": action,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录大小
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        
        # 清空重做栈
        self.redo_stack.clear()
    
    def show_toast(self, message, duration=2000):
        """显示临时提示"""
        toast = tk.Toplevel(self.window)
        toast.withdraw()
        toast.overrideredirect(True)
        toast.configure(bg="#333333")
        
        label = tk.Label(toast, text=message, bg="#333333", fg="white", 
                        padx=20, pady=10, font=("Arial", 10))
        label.pack()
        
        # 居中显示
        x = self.window.winfo_x() + self.window.winfo_width() // 2 - 100
        y = self.window.winfo_y() + self.window.winfo_height() - 100
        toast.geometry(f"200x40+{x}+{y}")
        
        toast.deiconify()
        toast.after(duration, toast.destroy)
    
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
        """现代化课表显示"""
        theme = self.themes[self.current_theme]
        self.schedule_canvas.config(bg=theme["bg"])
        self.schedule_canvas.delete("all")
        
        # 设置滚动区域
        total_height = max(500, len(self.timetable_data[self.current_weekday]) * 80 + 100)
        self.schedule_canvas.config(scrollregion=(0, 0, 400, total_height))
        
        # 绘制网格背景
        self.draw_schedule_grid()
        
        if not self.timetable_data[self.current_weekday]:
            # 现代化空状态提示
            self.show_empty_state()
        else:
            # 按时间排序
            sorted_courses = sorted(
                self.timetable_data[self.current_weekday],
                key=lambda x: self.time_to_minutes(x.get("start_time", "08:00"))
            )
            
            # 显示课程卡片
            for i, block in enumerate(sorted_courses):
                self.create_course_card(block, i)
    
    def draw_schedule_grid(self):
        """绘制课表网格"""
        theme = self.themes[self.current_theme]
        
        # 绘制时间线
        for hour in range(6, 22):
            y = (hour - 6) * 60
            self.schedule_canvas.create_line(
                0, y, 400, y, fill=theme["secondary"], 
                width=1, stipple="gray50"
            )
            
            # 时间标签
            self.schedule_canvas.create_text(
                20, y + 5, text=f"{hour:02d}:00",
                fill=theme["fg"], font=("Arial", 8), anchor="nw"
            )
    
    def show_empty_state(self):
        """显示现代化空状态"""
        theme = self.themes[self.current_theme]
        
        center_x, center_y = 200, 200
        
        # 空状态图标
        self.schedule_canvas.create_oval(
            center_x - 40, center_y - 40, center_x + 40, center_y + 40,
            outline=theme["accent"], width=2, stipple="gray50"
        )
        
        self.schedule_canvas.create_text(
            center_x, center_y, text="📅", font=("Arial", 24)
        )
        
        self.schedule_canvas.create_text(
            center_x, center_y + 60,
            text="暂无课程安排",
            fill=theme["fg"], font=("Arial", 12, "bold")
        )
        
        self.schedule_canvas.create_text(
            center_x, center_y + 80,
            text="拖拽课程卡片到此处添加",
            fill=theme["secondary"], font=("Arial", 10)
        )
    
    def create_course_card(self, block, index):
        """创建现代化课程卡片"""
        theme = self.themes[self.current_theme]
        
        # 计算位置
        y = index * 80 + 10
        card_height = 70
        
        # 获取课程颜色
        color = block.get("color", "#007bff")
        
        # 绘制卡片背景
        card = self.schedule_canvas.create_rounded_rectangle(
            50, y, 350, y + card_height, radius=10,
            fill=color, outline=color, width=0, tags="course_card"
        )
        
        # 课程名称
        self.schedule_canvas.create_text(
            60, y + 15, text=block.get("subject", "未知课程"),
            fill="white", font=("Arial", 12, "bold"), anchor="nw"
        )
        
        # 教师信息
        if block.get("teacher"):
            self.schedule_canvas.create_text(
                60, y + 35, text=f"👨‍🏫 {block['teacher']}",
                fill="white", font=("Arial", 10), anchor="nw"
            )
        
        # 教室信息
        if block.get("classroom"):
            self.schedule_canvas.create_text(
                60, y + 50, text=f"🏫 {block['classroom']}",
                fill="white", font=("Arial", 10), anchor="nw"
            )
        
        # 时间信息
        if block.get("start_time") and block.get("end_time"):
            self.schedule_canvas.create_text(
                300, y + 15, text=f"{block['start_time']}-{block['end_time']}",
                fill="white", font=("Arial", 9, "bold"), anchor="ne"
            )
        
        # 添加操作按钮
        edit_btn = self.schedule_canvas.create_oval(
            320, y + 40, 340, y + 60, fill="white", outline="white", tags="edit_btn"
        )
        self.schedule_canvas.create_text(
            330, y + 50, text="✏️", font=("Arial", 8), tags="edit_btn"
        )
        
        delete_btn = self.schedule_canvas.create_oval(
            300, y + 40, 320, y + 60, fill="white", outline="white", tags="delete_btn"
        )
        self.schedule_canvas.create_text(
            310, y + 50, text="🗑️", font=("Arial", 8), tags="delete_btn"
        )
        
        # 绑定事件
        self.schedule_canvas.tag_bind("course_card", "<Button-1>", 
                                    lambda e, b=block: self.edit_course(b))
        self.schedule_canvas.tag_bind("edit_btn", "<Button-1>", 
                                    lambda e, b=block: self.edit_course(b))
        self.schedule_canvas.tag_bind("delete_btn", "<Button-1>", 
                                    lambda e, b=block: self.delete_course(b))
    
    def edit_course(self, block):
        """编辑课程"""
        # 创建编辑对话框
        dialog = tk.Toplevel(self.window)
        dialog.title("编辑课程")
        dialog.geometry("300x250")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 编辑表单
        tk.Label(dialog, text="课程名称:").pack(pady=5)
        subject_entry = tk.Entry(dialog)
        subject_entry.insert(0, block.get("subject", ""))
        subject_entry.pack(pady=5)
        
        tk.Label(dialog, text="教师:").pack(pady=5)
        teacher_entry = tk.Entry(dialog)
        teacher_entry.insert(0, block.get("teacher", ""))
        teacher_entry.pack(pady=5)
        
        tk.Label(dialog, text="教室:").pack(pady=5)
        classroom_entry = tk.Entry(dialog)
        classroom_entry.insert(0, block.get("classroom", ""))
        classroom_entry.pack(pady=5)
        
        def save_changes():
            block["subject"] = subject_entry.get()
            block["teacher"] = teacher_entry.get()
            block["classroom"] = classroom_entry.get()
            
            self.save_state("编辑课程", block)
            self.update_schedule_display()
            dialog.destroy()
            self.show_toast("课程已更新")
        
        tk.Button(dialog, text="保存", command=save_changes).pack(pady=10)
    
    def delete_course(self, block):
        """删除课程"""
        if messagebox.askyesno("确认删除", f"确定要删除 '{block.get('subject', '课程')}' 吗？"):
            self.save_state("删除课程", block)
            
            # 从课表中移除
            for day in self.timetable_data:
                if block in self.timetable_data[day]:
                    self.timetable_data[day].remove(block)
            
            # 从课程列表中移除
            if block in self.class_blocks:
                self.class_blocks.remove(block)
            
            self.update_schedule_display()
            self.update_class_block_list()
            self.show_toast("课程已删除")
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        """创建圆角矩形"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1 + radius, y1
        ]
        return self.schedule_canvas.create_polygon(points, smooth=True, **kwargs)
    
    def switch_theme(self):
        """切换主题"""
        self.current_theme = self.theme_var.get()
        self.apply_theme()
        self.update_schedule_display()
        self.create_time_points()
    
    def apply_theme(self):
        """应用主题到所有组件"""
        theme = self.themes[self.current_theme]
        
        # 应用主题到主窗口
        self.window.configure(bg=theme["bg"])
        
        # 应用主题到所有子组件
        for widget in self.window.winfo_children():
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(bg=theme["bg"])
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Label, tk.Button, tk.Radiobutton)):
                        child.configure(bg=theme["bg"], fg=theme["fg"])
    
    def zoom_in(self):
        """放大"""
        self.zoom_level = min(self.zoom_level * 1.2, 2.0)
        self.create_time_points()
        self.update_schedule_display()
    
    def zoom_out(self):
        """缩小"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.5)
        self.create_time_points()
        self.update_schedule_display()
    
    def reset_timetable(self):
        """重置课表"""
        if messagebox.askyesno("确认重置", "确定要重置所有课程吗？此操作不可撤销！"):
            self.save_state("重置课表", {
                "timetable": self.timetable_data.copy(),
                "class_blocks": self.class_blocks.copy()
            })
            
            self.timetable_data = {day: [] for day in self.timetable_data}
            self.class_blocks.clear()
            self.time_blocks = {day: [] for day in self.time_blocks}
            
            self.update_schedule_display()
            self.update_class_block_list()
            self.create_time_points()
            self.show_toast("课表已重置")
    
    def on_block_hover(self, event, block):
        """鼠标悬停效果"""
        theme = self.themes[self.current_theme]
        self.time_canvas.config(cursor="hand2")
    
    def on_block_leave(self, event, block):
        """鼠标离开效果"""
        self.time_canvas.config(cursor="")
    
    def save_timetable(self):
        """增强保存功能"""
        try:
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timetable_{timestamp}.json"
            file_path = self.doc_path / filename
            
            # 增强的数据结构
            data = {
                "timetable": self.timetable_data,
                "time_blocks": self.time_blocks,
                "class_blocks": self.class_blocks,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "2.0",
                    "theme": self.current_theme,
                    "zoom_level": self.zoom_level
                }
            }
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 同时保存为最新版本
            latest_path = self.doc_path / "timetable_latest.json"
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"课表已保存到: {file_path}")
            self.show_toast("课表保存成功！")
            
        except Exception as e:
            self.logger.error(f"保存课表时出错: {e}")
            messagebox.showerror("保存失败", f"保存课表时出错: {str(e)}")
    
    def import_timetable(self):
        """增强导入功能"""
        try:
            initial_dir = str(self.doc_path)
            
            file_path = filedialog.askopenfilename(
                title="选择课表文件",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=initial_dir
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 保存当前状态用于撤销
                self.save_state("导入课表", {
                    "timetable": self.timetable_data.copy(),
                    "class_blocks": self.class_blocks.copy(),
                    "time_blocks": self.time_blocks.copy()
                })
                
                # 兼容性处理
                self.timetable_data = data.get("timetable", {})
                self.time_blocks = data.get("time_blocks", {})
                self.class_blocks = data.get("class_blocks", [])
                
                # 处理旧版本数据
                if "metadata" in data:
                    self.current_theme = data["metadata"].get("theme", "light")
                    self.zoom_level = data["metadata"].get("zoom_level", 1.0)
                    self.theme_var.set(self.current_theme)
                
                # 确保数据结构完整
                for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                    if day not in self.timetable_data:
                        self.timetable_data[day] = []
                    if day not in self.time_blocks:
                        self.time_blocks[day] = []
                
                # 更新显示
                self.apply_theme()
                self.create_time_points()
                self.update_schedule_display()
                self.update_class_block_list()
                
                self.show_toast(f"成功导入 {len(self.class_blocks)} 门课程")
                self.logger.info(f"课表导入成功: {file_path}")
                
        except Exception as e:
            self.logger.error(f"导入课表时出错: {e}")
            messagebox.showerror("导入失败", f"导入课表时出错: {str(e)}")
    
    def load_timetable(self):
        """增强加载功能"""
        try:
            # 优先加载最新版本
            latest_path = self.doc_path / "timetable_latest.json"
            
            if latest_path.exists():
                with open(latest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # 兼容旧版本文件
                timetable_files = [f for f in os.listdir(self.doc_path) 
                                 if f.startswith("timetable_") and f.endswith(".json")]
                if timetable_files:
                    latest_file = max(timetable_files)
                    file_path = self.doc_path / latest_file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    return
            
            # 加载数据
            self.timetable_data = data.get("timetable", {})
            self.time_blocks = data.get("time_blocks", {})
            self.class_blocks = data.get("class_blocks", [])
            
            # 加载元数据
            if "metadata" in data:
                self.current_theme = data["metadata"].get("theme", "light")
                self.zoom_level = data["metadata"].get("zoom_level", 1.0)
                self.theme_var.set(self.current_theme)
            
            # 确保数据结构完整
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                if day not in self.timetable_data:
                    self.timetable_data[day] = []
                if day not in self.time_blocks:
                    self.time_blocks[day] = []
            
            # 应用主题
            self.apply_theme()
            self.create_time_points()
            self.update_schedule_display()
            self.update_class_block_list()
            
        except Exception as e:
            self.logger.error(f"加载课表时出错: {e}")
            # 尝试加载旧格式
            self.load_legacy_timetable()
    
    def load_legacy_timetable(self):
        """加载旧版本课表格式"""
        try:
            legacy_files = [f for f in os.listdir(self.doc_path) 
                           if f.startswith("timetable_") and f.endswith(".json")]
            
            if legacy_files:
                latest_file = max(legacy_files)
                file_path = self.doc_path / latest_file
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 旧格式只包含timetable和time_blocks
                self.timetable_data = data.get("timetable", {})
                self.time_blocks = data.get("time_blocks", {})
                
                # 从timetable中提取课程信息
                courses = set()
                for day_courses in self.timetable_data.values():
                    for course in day_courses:
                        course_key = (course.get("subject"), course.get("teacher"), course.get("classroom"))
                        if course_key not in [(c.get("subject"), c.get("teacher"), c.get("classroom")) for c in self.class_blocks]:
                            new_block = {
                                "subject": course.get("subject", ""),
                                "teacher": course.get("teacher", ""),
                                "classroom": course.get("classroom", ""),
                                "color": self.generate_course_color(course.get("subject", ""))
                            }
                            self.class_blocks.append(new_block)
                
                self.create_time_points()
                self.update_schedule_display()
                self.update_class_block_list()
                
        except Exception as e:
            self.logger.error(f"加载旧版本课表时出错: {e}")
    
    def export_timetable_html(self):
        """导出为HTML格式"""
        try:
            from datetime import datetime
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>课程表</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .timetable { border-collapse: collapse; width: 100%; }
                    .timetable th, .timetable td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                    .timetable th { background-color: #f2f2f2; }
                    .course { margin: 2px; padding: 5px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <h1>课程表</h1>
                <table class="timetable">
                    <tr>
                        <th>时间</th>
                        <th>周一</th>
                        <th>周二</th>
                        <th>周三</th>
                        <th>周四</th>
                        <th>周五</th>
                        <th>周六</th>
                        <th>周日</th>
                    </tr>
            """
            
            # 添加课程数据
            # 这里可以添加更复杂的HTML生成逻辑
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            file_path = self.doc_path / f"timetable_{datetime.now().strftime('%Y%m%d')}.html"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.show_toast("HTML导出成功！")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出HTML时出错: {str(e)}")
    
    def load_timetable(self):
        """加载课表（跨平台兼容）"""
        try:
            # 查找最新的课表文件
            timetable_files = [f for f in os.listdir(self.doc_path) if f.startswith("timetable_") and f.endswith(".json")]
            
            if timetable_files:
                # 获取最新的文件
                latest_file = max(timetable_files)
                file_path = self.doc_path / latest_file
                
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
            self.logger.error(f"加载课表时出错: {e}")
    
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