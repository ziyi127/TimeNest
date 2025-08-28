import tkinter as tk
from tkinter import ttk
import json
import os
import datetime

class DragWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("课程表悬浮窗")
        self.geometry("180x70")
        
        # 检查操作系统类型，Linux环境下不使用无边框窗口以避免兼容性问题
        import platform
        if platform.system() != "Linux":
            self.overrideredirect(True)  # 无边框窗口
            self.wm_attributes("-topmost", True)  # 窗口置顶
        else:
            # Linux环境下使用普通窗口并设置为工具窗口以减少装饰
            self.wm_attributes("-type", "splash")  # GNOME环境下减少窗口装饰
            self.resizable(False, False)  # 禁止调整大小
        
        # 初始化可拖动状态，默认为不可拖动
        self.is_draggable = False
        
        # 初始化after任务ID列表
        self.after_ids = []
        
        # 初始化更新任务ID
        self.update_job = None
        
        # 加载UI设置
        self.load_ui_settings()
        
        # 使用after方法确保窗口完全初始化后再加载窗口位置
        self.after(100, self.load_window_position)
        
        # 配置背景颜色
        self.configure(bg=self.background_color)
        
        # 创建主框架
        self.main_frame = tk.Frame(self, bg=self.background_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 创建时间框架
        self.time_frame = tk.Frame(self.main_frame, bg=self.background_color)
        self.time_frame.pack(anchor='w')
        
        # 创建时间标签
        self.time_label = tk.Label(self.time_frame, font=("Arial", 14), bg=self.background_color, fg=self.text_color)
        self.time_label.pack(side='left')
        
        # 设置初始鼠标穿透状态
        # 使用after方法确保窗口完全初始化后再设置
        self.after(100, self._initialize_transparency)
        
    def _initialize_transparency(self):
        """初始化透明度设置"""
        # 创建日期和星期标签
        self.date_label = tk.Label(self.time_frame, font=("Arial", 12), bg=self.background_color, fg=self.text_color)
        self.date_label.pack(side='left', padx=(3, 0))
        
        # 创建课程信息标签
        self.class_info_label = tk.Label(self.main_frame, font=("Arial", 12), bg=self.background_color, fg=self.text_color)
        if self.show_next_class:
            self.class_info_label.pack(anchor='w')
        
        # 创建下一节课信息标签
        self.next_class_label = tk.Label(self.main_frame, font=("Arial", 12), bg=self.background_color, fg=self.text_color)
        if self.show_countdown:
            self.next_class_label.pack(anchor='w')
        
        # 加载课程表
        self.timetable = self.load_timetable()
        
        # 绑定鼠标事件
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.on_motion)
        
        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 开始更新时间
        self.update_time()
    
    def _adjust_font_size(self, label, text):
        """根据文本长度调整标签的字体大小"""
        # 获取标签的宽度
        label_width = label.winfo_width()
        
        # 如果标签宽度为0（可能还未完全初始化），使用窗口宽度作为参考
        if label_width <= 0:
            label_width = self.winfo_width() - 20  # 减去一些边距
        
        # 获取当前字体
        current_font = label.cget("font")
        
        # 解析字体信息
        if isinstance(current_font, str):
            # 如果是字体名称字符串，需要解析
            font_parts = current_font.split()
            if len(font_parts) >= 2:
                font_family = font_parts[0]
                try:
                    font_size = int(font_parts[1])
                except ValueError:
                    font_size = 12  # 默认字体大小
            else:
                font_family = "Arial"
                font_size = 12
        else:
            # 如果是字体元组
            font_family = current_font[0] if len(current_font) > 0 else "Arial"
            font_size = current_font[1] if len(current_font) > 1 else 12
        
        # 创建一个临时的字体对象来测量文本宽度
        import tkinter.font as tkFont
        font_obj = tkFont.Font(family=font_family, size=font_size)
        text_width = font_obj.measure(text)
        
        # 如果文本宽度大于标签宽度，减小字体大小
        if text_width > label_width and font_size > 8:  # 最小字体大小为8
            # 计算新的字体大小
            new_font_size = max(8, int(font_size * (label_width / text_width * 0.9)))  # 保留一些边距
            label.config(font=(font_family, new_font_size))
        elif text_width < label_width * 0.8 and font_size < 14:  # 如果文本宽度小于标签宽度的80%，增大字体大小，但不超过14
            # 计算新的字体大小
            new_font_size = min(14, int(font_size * (label_width / text_width * 0.9)))
            label.config(font=(font_family, new_font_size))
    
    def _apply_background_and_transparency(self):
        """应用背景色和透明度设置"""
        # 重新设置背景色
        self.configure(bg=self.background_color)
        self.main_frame.configure(bg=self.background_color)
        self.time_label.configure(bg=self.background_color)
        self.date_label.configure(bg=self.background_color)
        self.class_info_label.configure(bg=self.background_color)
        self.next_class_label.configure(bg=self.background_color)
        
        # 应用透明度
        alpha = self.transparency / 100.0
        try:
            self.wm_attributes("-alpha", alpha)
        except Exception as e:
            print(f"应用透明度时出错: {e}")
        
        # 重新调整课程信息标签的字体大小
        if hasattr(self, 'class_info_label') and self.class_info_label.cget("text"):
            self._adjust_font_size(self.class_info_label, self.class_info_label.cget("text"))
        if hasattr(self, 'next_class_label') and self.next_class_label.cget("text"):
            self._adjust_font_size(self.next_class_label, self.next_class_label.cget("text"))
    
    def update_display_settings(self):
        """更新显示设置"""
        # 控制课程信息标签的显示
        if self.show_next_class:
            self.class_info_label.pack(anchor='w')
        else:
            self.class_info_label.pack_forget()
        
        # 控制下一节课信息标签的显示
        if self.show_countdown:
            self.next_class_label.pack(anchor='w')
        else:
            self.next_class_label.pack_forget()
    
    def load_ui_settings(self):
        """加载UI设置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 默认设置
            self.background_color = "white"
            self.text_color = "black"
            self.transparency = 100
            self.show_next_class = True
            self.show_countdown = True
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 应用设置
                self.background_color = settings.get("background_color", "white")
                self.text_color = settings.get("text_color", "black")
                self.transparency = settings.get("transparency", 100)
                self.show_next_class = settings.get("show_next_class", True)
                self.show_countdown = settings.get("show_countdown", True)
            
            # 应用透明度
            alpha = self.transparency / 100.0
            try:
                self.wm_attributes("-alpha", alpha)
            except Exception as e:
                print(f"应用透明度时出错: {e}")
        except Exception as e:
            print(f"加载UI设置时出错: {e}")
            # 使用默认设置
            self.background_color = "white"
            self.text_color = "black"
            self.transparency = 100
            self.show_next_class = True
            self.show_countdown = True
    
    def set_draggable(self, draggable):
        """设置窗口是否可拖动"""
        self.is_draggable = draggable
        print(f"设置可拖动状态: {draggable}")
        
        # 强制更新窗口
        self.update()
    
    def start_move(self, event):
        """开始移动窗口"""
        if self.is_draggable:
            self.x = event.x
            self.y = event.y
    
    def stop_move(self, event):
        """停止移动窗口"""
        if self.is_draggable:
            # 保存窗口位置
            self.save_window_position()
    
    def on_motion(self, event):
        """移动窗口"""
        if self.is_draggable:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.set_display_postion(x, y)
    
    def set_display_postion(self, x, y):
        """设置窗口显示位置"""
        self.geometry(f"+{x}+{y}")
    
    def update_time(self):
        """更新时间显示"""
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%m-%d")
            
            # 获取星期
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday = weekdays[now.weekday()]
            
            # 更新时间标签
            self.time_label.config(text=current_time)
            self.date_label.config(text=f"{current_date} {weekday}")
            
            # 更新课程信息
            self.update_info(now)
        except Exception as e:
            # 窗口可能已被销毁，停止更新
            print(f"更新时间时出错: {e}")
            return
        
        # 每秒更新一次
        try:
            after_id = self.after(1000, self.update_time)
            self.after_ids.append(after_id)
            # 保存更新任务ID
            self.update_job = after_id
        except Exception as e:
            # 窗口可能已被销毁，停止更新
            print(f"安排下次更新时出错: {e}")
    
    def load_timetable(self):
        """从项目目录加载课程表JSON文件"""
        try:
            # 获取项目目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 直接查找timetable.json文件
            timetable_file = "timetable.json"
            timetable_file_path = os.path.join(project_path, timetable_file)
            
            if not os.path.exists(timetable_file_path):
                print("未找到课程表文件")
                return {}
            
            # 加载课程表
            with open(timetable_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理可能的嵌套结构
            if "timetable" in data:
                timetable = data["timetable"]
            else:
                timetable = data
            
            # 转换星期名称为英文
            converted_timetable = {}
            weekdays_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            for i, day_cn in enumerate(weekdays_cn):
                if day_cn in timetable:
                    converted_timetable[weekdays_en[i]] = timetable[day_cn]
                elif weekdays_en[i] in timetable:
                    converted_timetable[weekdays_en[i]] = timetable[weekdays_en[i]]
                else:
                    converted_timetable[weekdays_en[i]] = []
            
            # 输出课程信息
            print("课表加载完成:")
            for i, day_cn in enumerate(weekdays_cn):
                if converted_timetable[weekdays_en[i]]:
                    print(f"{day_cn}: {converted_timetable[weekdays_en[i]]}")
                else:
                    print(f"{day_cn}: 无课程")
            
            return converted_timetable
        except Exception as e:
            print(f"加载课程表时出错: {e}")
            import traceback
            traceback.print_exc()  # 打印详细的错误信息
            return {}
    
    def update_info(self, now):
        """更新课程信息显示"""
        # 获取当前星期
        weekdays_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekdays_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        current_weekday_en = weekdays_en[now.weekday()]
        current_weekday_cn = weekdays_cn[now.weekday()]
        
        # print(f"当前时间: {now}")  # 调试信息
        # print(f"当前星期: {current_weekday_cn} ({current_weekday_en})")  # 调试信息
        
        # 获取当前时间和下一节课信息
        current_class = None
        next_class = None
        
        # 使用英文键访问课表
        if current_weekday_en in self.timetable:
            classes = self.timetable[current_weekday_en]
            # print(f"当天课程: {classes}")  # 调试信息
            
            # 遍历课程查找当前和下一节课
            for i, class_info in enumerate(classes):
                start_time = datetime.datetime.strptime(class_info["start_time"], "%H:%M").time()
                end_time = datetime.datetime.strptime(class_info["end_time"], "%H:%M").time()
                
                # print(f"检查课程: {class_info['subject']} ({start_time}-{end_time})")  # 调试信息
                # print(f"当前时间是否在课程时间段内: {start_time <= now.time() <= end_time}")  # 调试信息
                
                # 检查当前时间是否在课程时间段内
                if start_time <= now.time() <= end_time:
                    current_class = class_info
                
                # 查找下一节课
                if start_time > now.time() and (next_class is None or start_time < datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()):
                    next_class = class_info
        
        # 更新当前课程信息
        if current_class:
            text = f"现在是:{current_class['subject']}({current_class['start_time']}-{current_class['end_time']})"
            self.class_info_label.config(text=text)
            self._adjust_font_size(self.class_info_label, text)
            # print(f"当前课程: {current_class['subject']} ({current_class['start_time']}-{current_class['end_time']})")  # 调试信息
        else:
            # 特殊处理周末和课间休息
            if current_weekday_en in ['saturday', 'sunday'] and not self.timetable.get(current_weekday_en):
                text = "今天休息，无课程安排"
                self.class_info_label.config(text=text)
                self._adjust_font_size(self.class_info_label, text)
            elif next_class:
                # 计算距离下一节课的时间
                next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
                next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
                
                # 如果下一节课是明天的，需要调整日期
                if next_class_datetime < now:
                    next_class_datetime += datetime.timedelta(days=1)
                text = "课间休息中"
                self.class_info_label.config(text=text)
                self._adjust_font_size(self.class_info_label, text)
            elif self.timetable.get(current_weekday_en):
                # 当天有课程但不在课间休息时间（第一节课前或放学后）
                if classes:  # 确保当天有课程安排
                    text = "今天没有课程进行中"
                    self.class_info_label.config(text=text)
                    self._adjust_font_size(self.class_info_label, text)
                else:
                    text = "今天没有课程安排"
                    self.class_info_label.config(text=text)
                    self._adjust_font_size(self.class_info_label, text)
            else:
                # 当天无课程安排
                text = "今天没有课程安排"
                self.class_info_label.config(text=text)
                self._adjust_font_size(self.class_info_label, text)
            # print("今天没有课程")  # 调试信息
        
        # 更新下一节课信息
        if next_class and current_class:  # 只有在有当前课程时才显示下一节课信息
            # 计算距离下一节课的时间
            next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
            next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
            
            # 如果下一节课是明天的，需要调整日期
            if next_class_datetime < now:
                next_class_datetime += datetime.timedelta(days=1)
            
            time_diff = next_class_datetime - now
            
            text = f"下节课: {next_class['subject']}({next_class['start_time']})"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
            # print(f"下一节课: {next_class['subject']} ({next_class['start_time']})")  # 调试信息
        elif next_class and not current_class:
            # 在非课间时间显示下一节课信息（第一节课前）
            # 计算距离下一节课的时间
            next_class_time = datetime.datetime.strptime(next_class["start_time"], "%H:%M").time()
            next_class_datetime = datetime.datetime.combine(now.date(), next_class_time)
            
            # 如果下一节课是明天的，需要调整日期
            if next_class_datetime < now:
                next_class_datetime += datetime.timedelta(days=1)
            
            time_diff = next_class_datetime - now
            minutes_diff = int(time_diff.total_seconds() / 60)
            
            text = f"下一节课: {next_class['subject']} ({next_class['start_time']}) 还有{minutes_diff}分钟"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
        elif self.timetable.get(current_weekday_en):
            # 当天有课程但没有下一节课（已放学）
            text = "今天课程已结束"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
        else:
            # 即使当天没有更多课程也保持程序正常运行
            text = "今天没有更多课程"
            self.next_class_label.config(text=text)
            self._adjust_font_size(self.next_class_label, text)
            # print("今天没有更多课程")  # 调试信息
    
    def load_window_position(self):
        """加载窗口位置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 设置窗口位置
                self.set_display_postion(settings["position_x"], settings["position_y"])
        except Exception as e:
            print(f"加载窗口位置时出错: {e}")
    
    def save_window_position(self):
        """保存窗口位置"""
        try:
            # 获取程序主目录
            project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_file = os.path.join(project_path, "timetable_ui_settings.json")
            
            # 检查窗口是否仍然存在
            if self.winfo_exists():
                # 获取当前窗口位置
                x = self.winfo_x()
                y = self.winfo_y()
                
                # 读取现有设置
                if os.path.exists(settings_file):
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                else:
                    settings = {}
                
                # 更新位置信息
                settings["position_x"] = x
                settings["position_y"] = y
                
                # 保存设置到文件
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                print(f"窗口位置已保存: x={x}, y={y}")
        except Exception as e:
            print(f"保存窗口位置时出错: {e}")
    
    def on_closing(self):
        """窗口关闭事件"""
        try:
            # 取消所有待执行的after任务
            if hasattr(self, 'after_ids'):
                for after_id in self.after_ids:
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass  # 忽略可能的异常
                self.after_ids.clear()
            
            # 停止所有可能的更新循环
            if hasattr(self, 'update_job') and self.update_job:
                try:
                    self.after_cancel(self.update_job)
                except:
                    pass  # 忽略可能的异常
            
            # 停止更新循环标志
            if hasattr(self, 'update_loop_running'):
                self.update_loop_running = False
            
            # 保存窗口位置
            # 在解除事件绑定和销毁窗口之前保存位置
            try:
                # 检查窗口是否仍然存在
                if self.winfo_exists():
                    self.save_window_position()
            except:
                pass  # 忽略可能的异常
            
            # 解除所有事件绑定
            try:
                # 在窗口销毁前解除所有事件绑定，不检查窗口是否存在
                for widget in self.winfo_children():
                    try:
                        widget.unbind("<Button-1>")
                    except:
                        pass
                    try:
                        widget.unbind("<B1-Motion>")
                    except:
                        pass
                    try:
                        widget.unbind("<ButtonRelease-1>")
                    except:
                        pass
            except:
                # 忽略解除绑定时的任何异常
                pass
        except Exception as e:
            print(f"关闭窗口时出错: {e}")
        finally:
            # 销毁窗口
            try:
                # 直接销毁窗口，不再检查是否存在
                self.destroy()
            except Exception as e:
                # 忽略销毁时的异常
                pass
