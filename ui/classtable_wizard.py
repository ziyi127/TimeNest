import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ClassTableWizard:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.window = None
        self.classtable_meta = None
        self.buttons = []
        self.entries = []
        self.current_focus_row = 0
        self.current_focus_col = 0
        
        # 加载classtableMeta.json
        self.load_classtable_meta()
    
    def load_classtable_meta(self):
        """加载classtableMeta.json文件"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meta_file_path = os.path.join(project_path, "classtableMeta.json")
            
            if os.path.exists(meta_file_path):
                with open(meta_file_path, 'r', encoding='utf-8') as f:
                    self.classtable_meta = json.load(f)
            else:
                messagebox.showerror("错误", "未找到classtableMeta.json文件")
                return False
        except Exception as e:
            messagebox.showerror("错误", f"加载classtableMeta.json时出错: {e}")
            return False
        
        return True
    
    def save_classtable_meta(self):
        """保存classtableMeta.json文件"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            meta_file_path = os.path.join(project_path, "classtableMeta.json")
            
            with open(meta_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.classtable_meta, f, ensure_ascii=False, indent=2)
            
            # 同时更新timetable.json
            timetable_file_path = os.path.join(project_path, "timetable.json")
            if hasattr(self.main_window, '_convert_classtable_meta_to_timetable'):
                self.main_window._convert_classtable_meta_to_timetable(meta_file_path, timetable_file_path)
            
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存classtableMeta.json时出错: {e}")
            return False
    
    def open_window(self):
        """打开课程表设置向导"""
        # 如果窗口已存在，将其带到前台
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        # 创建新窗口
        self.window = tk.Toplevel(self.parent)
        self.window.title("课程表设置向导")
        self.window.geometry("800x600")
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
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=3)  # 课程表区域
        main_frame.columnconfigure(1, weight=1)  # 课程按钮区域
        main_frame.rowconfigure(0, weight=1)
        
        # 左侧课程表区域 (3/4)
        timetable_frame = ttk.Frame(main_frame)
        timetable_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        timetable_frame.columnconfigure(0, weight=1)
        timetable_frame.rowconfigure(0, weight=1)
        
        # 创建课程表
        self.create_timetable(timetable_frame)
        
        # 右侧课程按钮区域 (1/4)
        classes_frame = ttk.Frame(main_frame)
        classes_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        classes_frame.columnconfigure(0, weight=1)
        classes_frame.rowconfigure(1, weight=1)
        
        # 标题
        ttk.Label(classes_frame, text="课程选择").grid(row=0, column=0, pady=(0, 10))
        
        # 创建课程按钮
        self.create_class_buttons(classes_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存并重启", command=self.save_and_restart)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def create_timetable(self, parent):
        """创建课程表"""
        # 创建画布和滚动条
        canvas = tk.Canvas(parent)
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 获取午休节次
        lunch_break_period = 4  # 默认值
        if self.classtable_meta and "lunch_break_period" in self.classtable_meta:
            try:
                lunch_break_period = int(self.classtable_meta["lunch_break_period"])
            except:
                pass
        
        # 创建课程表标题
        days = ["周一", "周二", "周三", "周四", "周五"]
        for i, day in enumerate(days):
            label = ttk.Label(scrollable_frame, text=day, font=("Arial", 10, "bold"))
            label.grid(row=0, column=i+1, padx=5, pady=5)
        
        # 创建节次标题和输入框
        max_periods = 8  # 默认节数
        if self.classtable_meta and "timetable" in self.classtable_meta:
            # 计算最大节数
            timetable = self.classtable_meta["timetable"]
            for day_data in timetable.values():
                if len(day_data) > max_periods:
                    max_periods = len(day_data)
        
        # 创建节次行
        for period in range(max_periods):
            # 节次标题
            period_label = ttk.Label(scrollable_frame, text=f"第{period+1}节")
            period_label.grid(row=period+1, column=0, padx=5, pady=5)
            
            # 创建输入框
            row_entries = []
            for day in range(5):  # 周一到周五
                entry = ttk.Entry(scrollable_frame, width=12)
                entry.grid(row=period+1, column=day+1, padx=5, pady=5)
                
                # 绑定点击事件
                entry.bind("<Button-1>", lambda e, r=period, c=day: self.on_entry_click(r, c))
                
                # 如果是午休节次，在右侧添加分隔线
                if period+1 == lunch_break_period:
                    entry.configure(style="Lunch.TEntry")
                
                row_entries.append(entry)
            
            self.entries.append(row_entries)
        
        # 配置午休样式
        style = ttk.Style()
        style.configure("Lunch.TEntry", relief="solid", borderwidth=2)
    
    def on_entry_click(self, row, col):
        """当点击输入框时设置焦点"""
        self.current_focus_row = row
        self.current_focus_col = col
    
    def create_class_buttons(self, parent):
        """创建课程按钮"""
        # 创建滚动区域
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # 获取所有课程
        all_classes = []
        if self.classtable_meta and "allclass" in self.classtable_meta:
            all_classes = self.classtable_meta["allclass"]
        
        # 创建课程按钮
        for i, class_name in enumerate(all_classes):
            button = ttk.Button(scrollable_frame, text=class_name, 
                              command=lambda name=class_name: self.on_class_button_click(name))
            button.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            scrollable_frame.columnconfigure(0, weight=1)
            self.buttons.append(button)
    
    def on_class_button_click(self, class_name):
        """当点击课程按钮时"""
        # 如果有选中的输入框，填入课程
        if 0 <= self.current_focus_row < len(self.entries) and \
           0 <= self.current_focus_col < len(self.entries[self.current_focus_row]):
            entry = self.entries[self.current_focus_row][self.current_focus_col]
            entry.delete(0, tk.END)
            entry.insert(0, class_name)
            
            # 移动焦点到下一个输入框
            self.move_focus()
        else:
            # 否则从左到右填入课程
            self.fill_class_from_left(class_name)
    
    def move_focus(self):
        """移动焦点到下一个输入框"""
        # 移动到下一列
        self.current_focus_col += 1
        
        # 如果超出列数，移动到下一行
        if self.current_focus_col >= 5:  # 周一到周五
            self.current_focus_col = 0
            self.current_focus_row += 1
            
            # 如果超出行数，回到第一行
            if self.current_focus_row >= len(self.entries):
                self.current_focus_row = 0
    
    def fill_class_from_left(self, class_name):
        """从左到右填入课程"""
        # 遍历所有输入框
        for row in range(len(self.entries)):
            for col in range(len(self.entries[row])):
                entry = self.entries[row][col]
                if not entry.get():  # 如果输入框为空
                    entry.delete(0, tk.END)
                    entry.insert(0, class_name)
                    # 更新焦点位置
                    self.current_focus_row = row
                    self.current_focus_col = col
                    return
    
    def save_and_restart(self):
        """保存并重启程序"""
        # 收集课程表数据
        classtable = {}
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        
        # 初始化classtable
        for day in weekdays:
            classtable[day] = []
        
        # 填充课程数据
        for row, row_entries in enumerate(self.entries):
            for col, entry in enumerate(row_entries):
                class_name = entry.get()
                if class_name:
                    classtable[weekdays[col]].append(class_name)
                else:
                    classtable[weekdays[col]].append("")
        
        # 保存到classtableMeta.json
        if self.classtable_meta is not None:
            self.classtable_meta["classtable"] = classtable
            
            if self.save_classtable_meta():
                messagebox.showinfo("成功", "课程表已保存")
                
                # 删除timetable.json（如果有）
                try:
                    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    timetable_file_path = os.path.join(project_path, "timetable.json")
                    if os.path.exists(timetable_file_path):
                        os.remove(timetable_file_path)
                except Exception as e:
                    print(f"删除timetable.json时出错: {e}")
                
                # 关闭窗口
                self._cleanup_resources()
                self.window.destroy()
                
                # 重启程序
                self.restart_program()
    
    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 解除所有事件绑定
            try:
                # 解除输入框的点击事件绑定
                for row_entries in self.entries:
                    for entry in row_entries:
                        try:
                            entry.unbind("<Button-1>")
                        except:
                            pass
            except:
                pass
            
            # 解除所有按钮的事件绑定
            try:
                for button in self.buttons:
                    try:
                        button.unbind("<Button-1>")
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
            print(f"清理课程表向导界面资源时出错: {e}")
    
    def restart_program(self):
        """重启程序"""
        # 这里需要实现程序重启逻辑
        # 为简化起见，我们只关闭当前窗口
        # 实际应用中可能需要使用subprocess或其他方法重启程序
        try:
            # 尝试重启程序
            import sys
            import subprocess
            
            # 获取当前程序路径
            program = sys.executable
            script = sys.argv[0]
            
            # 启动新实例
            subprocess.Popen([program, script])
            
            # 关闭当前实例
            self.main_window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"重启程序时出错: {e}")