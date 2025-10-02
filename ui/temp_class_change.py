import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# 此文件是临时调课窗口文件和类
class TempClassChangeWindow:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.window = None
        self.classtable_meta = None
        self.single_change_var = tk.BooleanVar(value=True)
        
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
            self.main_window._convert_classtable_meta_to_timetable(meta_file_path, timetable_file_path)
            
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存classtableMeta.json时出错: {e}")
            return False
    
    def open_window(self):
        """打开临时调课界面"""
        # 如果窗口已存在，将其带到前台
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        # 创建新窗口
        self.window = tk.Toplevel(self.parent)
        self.window.title("临时调课")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.iconbitmap("TKtimetable.ico")
        self.window.wm_iconbitmap("TKtimetable.ico")
        
        # 设置窗口属性以确保在任务栏显示
        try:
            # 移除transient属性，允许窗口在任务栏显示
            self.window.transient()
            # 设置窗口类名，有助于任务栏识别
            self.window.wm_attributes("-topmost", False)
        except Exception as e:
            print(f"设置窗口属性时出错: {e}")
        
        # 居中显示窗口
        if hasattr(self.main_window, '_center_window'):
            self.main_window._center_window(self.window)
        
        # 创建界面元素
        self.create_widgets()
        
        # 填充数据
        self.populate_data()
    
    def create_widgets(self):
        """创建界面元素"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 被调课的课程选择
        ttk.Label(main_frame, text="被调课的课程:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 星期选择
        ttk.Label(main_frame, text="星期:").grid(row=1, column=0, sticky=tk.W, padx=(10, 0))
        self.day_var = tk.StringVar()
        self.day_combo = ttk.Combobox(main_frame, textvariable=self.day_var, state="readonly", width=10)
        self.day_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 节次选择
        ttk.Label(main_frame, text="第几节:").grid(row=1, column=2, sticky=tk.W, padx=(10, 0))
        self.period_var = tk.StringVar()
        self.period_combo = ttk.Combobox(main_frame, textvariable=self.period_var, state="readonly", width=10)
        self.period_combo.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 更改后的课程选择
        ttk.Label(main_frame, text="更改后的课程:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # 课程选择
        ttk.Label(main_frame, text="课程:").grid(row=3, column=0, sticky=tk.W, padx=(10, 0))
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(main_frame, textvariable=self.class_var, state="readonly", width=15)
        self.class_combo.grid(row=3, column=1, columnspan=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 单次课程修改复选框
        self.single_change_check = ttk.Checkbutton(main_frame, text="仅修改单次课程", variable=self.single_change_var)
        self.single_change_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(10, 5))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存", command=self.save_changes)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 绑定选择事件
        self.day_combo.bind('<<ComboboxSelected>>', self.on_day_selected)
    
    def populate_data(self):
        """填充数据"""
        if not self.classtable_meta:
            return
        
        # 填充星期选择
        days = ["周一", "周二", "周三", "周四", "周五"]
        self.day_combo['values'] = days
        
        # 填充课程选择
        all_classes = self.classtable_meta.get("allclass", [])
        self.class_combo['values'] = all_classes
        
        # 默认选择第一个星期
        if days:
            self.day_var.set(days[0])
            self.update_period_combo(days[0])
    
    def on_day_selected(self, event=None):
        """当选择星期时更新节次选择"""
        selected_day = self.day_var.get()
        self.update_period_combo(selected_day)
    
    def update_period_combo(self, day_cn):
        """更新节次选择框"""
        # 星期中文到英文的映射
        day_map = {
            "周一": "monday",
            "周二": "tuesday",
            "周三": "wednesday",
            "周四": "thursday",
            "周五": "friday"
        }
        
        day_en = day_map.get(day_cn, "monday")
        
        # 获取该天的课程数量
        if self.classtable_meta and "classtable" in self.classtable_meta:
            periods = self.classtable_meta["classtable"].get(day_en, [])
            # 确保至少显示8节课
            max_periods = max(8, len(periods))
            period_values = [f"第{i+1}节" for i in range(max_periods)]
            self.period_combo['values'] = period_values
            
            # 默认选择第一节
            if period_values:
                self.period_var.set(period_values[0])
    
    def save_changes(self):
        """保存更改"""
        # 获取选择的值
        selected_day_cn = self.day_var.get()
        selected_period = self.period_var.get()
        selected_class = self.class_var.get()
        
        # 检查是否选择了所有必要的值
        if not selected_day_cn or not selected_period or not selected_class:
            messagebox.showwarning("警告", "请完整选择被调课的课程和更改后的课程")
            return
        
        # 星期中文到英文的映射
        day_map = {
            "周一": "monday",
            "周二": "tuesday",
            "周三": "wednesday",
            "周四": "thursday",
            "周五": "friday"
        }
        
        day_en = day_map.get(selected_day_cn)
        
        # 获取节次索引
        try:
            period_index = int(selected_period.replace("第", "").replace("节", "")) - 1
        except ValueError:
            messagebox.showerror("错误", "节次选择无效")
            return
        
        # 检查节次索引是否有效
        if day_en not in self.classtable_meta.get("classtable", {}) or \
           period_index >= len(self.classtable_meta["classtable"][day_en]):
            messagebox.showerror("错误", "选择的节次超出范围")
            return
        
        # 保存更改
        if self.single_change_var.get():
            # 仅修改单次课程
            self.save_single_change(day_en, period_index, selected_class)
        else:
            # 修改永久课程
            self.save_permanent_change(day_en, period_index, selected_class)
        
        # 显示成功消息
        messagebox.showinfo("成功", "课程调整已保存")
        
        # 关闭窗口
        self._cleanup_resources()
        self.window.destroy()
    
    def _cleanup_resources(self):
        """清理资源"""
        try:
            # 解除所有事件绑定
            try:
                self.day_combo.unbind('<<ComboboxSelected>>')
            except:
                pass
            
            # 解除所有按钮的事件绑定
            try:
                for child in self.window.winfo_children():
                    try:
                        if isinstance(child, tk.Button) or isinstance(child, ttk.Button):
                            child.unbind("<Button-1>")
                    except:
                        pass
                    
                    # 解除其他可能的事件绑定
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
            print(f"清理临时调课界面资源时出错: {e}")
    
    def save_single_change(self, day_en, period_index, new_class):
        """保存单次课程更改"""
        # 对于单次课程更改，我们可以在classtableMeta.json中添加一个特殊字段来记录
        # 这里简化处理，直接修改classtable，但在实际应用中可能需要更复杂的逻辑
        if "single_changes" not in self.classtable_meta:
            self.classtable_meta["single_changes"] = {}
        
        # 记录单次更改
        change_key = f"{day_en}_{period_index}"
        self.classtable_meta["single_changes"][change_key] = {
            "original_class": self.classtable_meta["classtable"][day_en][period_index],
            "new_class": new_class
        }
        
        # 保存文件
        self.save_classtable_meta()
    
    def save_permanent_change(self, day_en, period_index, new_class):
        """保存永久课程更改"""
        # 直接修改classtable
        self.classtable_meta["classtable"][day_en][period_index] = new_class
        
        # 如果新课程不在allclass中，添加到allclass
        if new_class not in self.classtable_meta.get("allclass", []):
            self.classtable_meta["allclass"].append(new_class)
        
        # 保存文件
        self.save_classtable_meta()