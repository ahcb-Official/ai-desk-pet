# ai_desk_pet_catgirl.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont
import time
import sys
import os
from datetime import datetime
import platform
import random
import queue

class CatGirlDeskPet:
    def __init__(self, api_key=None):
        # 配置文件路径
        self.config_file = "catgirl_config.json"
        
        # 语音识别队列
        self.speech_queue = queue.Queue()
        
        # 加载配置文件
        self.config = self.load_config()
        
        # 使用配置文件中的设置，如果没有则使用默认值
        self.api_key = api_key or self.config.get("api_key") or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 检查操作系统
        self.is_macos = platform.system() == "Darwin"
        
        # 初始化主窗口
        self.root = tk.Tk()
        self.setup_window()
        
        # 宠物状态
        self.pet_state = "idle"  # idle, thinking, speaking, sleeping, happy
        self.conversation_history = []
        self.pet_name = self.config.get("pet_name", "小深猫娘")
        
        # 猫娘个性设定
        self.personality = self.config.get("personality", "你是一个可爱的猫娘AI桌宠，名字叫小深。你说话带着猫娘的口癖，喜欢说'喵~'，性格傲娇又粘人，喜欢被主人抚摸和投喂。你会用可爱的语气回应主人，偶尔会撒娇。")
        
        # 心情系统
        self.mood = "happy"  # happy, normal, bored, angry
        self.mood_value = 80  # 0-100
        self.last_interaction = datetime.now()
        self.start_time = datetime.now()
        
        # 语音输入状态
        self.is_listening = False
        
        # 图片相关变量（防止被垃圾回收）
        self.pet_images = {}
        self.photo_images = {}
        
        # 加载资源
        self.load_images()
        self.create_widgets()
        
        # 状态循环
        self.update_pet_state()
        
        # 启动语音队列处理
        self.process_speech_queue()
        
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "api_key": "",
            "pet_name": "小深猫娘",
            "personality": "你是一个可爱的猫娘AI桌宠，名字叫小深。你说话带着猫娘的口癖，喜欢说'喵~'，性格傲娇又粘人，喜欢被主人抚摸和投喂。你会用可爱的语气回应主人，偶尔会撒娇。",
            "window_x": 100,
            "window_y": 100,
            "voice_input": True  # 默认开启语音输入
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print("✅ 配置文件加载成功")
                    return {**default_config, **config}  # 用配置文件覆盖默认值
            else:
                print("⚠️ 配置文件不存在，使用默认配置")
                return default_config
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            # 保存窗口位置
            if hasattr(self.root, 'winfo_x') and hasattr(self.root, 'winfo_y'):
                self.config["window_x"] = self.root.winfo_x()
                self.config["window_y"] = self.root.winfo_y()
            
            # 保存其他配置
            self.config["api_key"] = self.api_key
            self.config["pet_name"] = self.pet_name
            self.config["personality"] = self.personality
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("✅ 配置文件保存成功")
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
    
    def setup_window(self):
        """设置宠物窗口属性"""
        self.root.title("AI Desk Pet - 小深猫娘")
        
        # 增大窗口以适应猫娘立绘
        window_width = 180
        window_height = 250
        
        # 从配置文件获取窗口位置
        window_x = self.config.get("window_x", 100)
        window_y = self.config.get("window_y", 100)
        
        # 确保窗口在屏幕内
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if window_x < 0 or window_x > screen_width - window_width:
            window_x = screen_width - window_width - 50
        if window_y < 0 or window_y > screen_height - window_height:
            window_y = 100
        
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶
        
        # macOS 特定的窗口设置
        if self.is_macos:
            self.root.config(bg='#f5f5f5')  # 使用浅灰色背景
            self.root.wm_attributes('-transparent', False)
            self.root.wm_attributes('-alpha', 0.95)  # 轻微透明
        else:
            self.root.attributes('-transparentcolor', 'white')
            self.root.config(bg='white')
        
        # 窗口拖动功能
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.on_move)
        
        # 右键菜单 - 适配不同操作系统
        if self.is_macos:
            self.root.bind("<Button-2>", self.show_context_menu)
            self.root.bind("<Control-Button-1>", self.show_context_menu)
        else:
            self.root.bind("<Button-3>", self.show_context_menu)
        
        # 确保窗口显示在最前面
        self.root.lift()
        self.root.focus_force()
        
        # 窗口关闭时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """窗口关闭时保存配置"""
        self.save_config()
        self.root.quit()
    
    def load_images(self):
        """加载猫娘图片"""
        # 定义图片文件和对应的状态
        image_files = {
            "idle": "idle.png",
            "thinking": "thinking.png", 
            "speaking": "speaking.png",
            "sleeping": "sleeping.png",
            "happy": "happy.png"
        }
        
        # 图片尺寸（适配猫娘立绘）
        image_size = (160, 160)  # 增大尺寸显示更多细节
        
        # 确保images目录存在
        if not os.path.exists("images"):
            os.makedirs("images")
            print("⚠️ 已创建images目录，但未找到猫娘图片")
            print("请将猫娘图片放入images/文件夹:")
            print("  - idle.png (空闲状态)")
            print("  - thinking.png (思考状态)")
            print("  - speaking.png (说话状态)")
            print("  - sleeping.png (睡觉状态)")
            print("  - happy.png (开心状态)")
            print("\n如果缺少图片，程序将自动生成简易版本")
        
        for state, filename in image_files.items():
            image_path = os.path.join("images", filename)
            
            # 如果图片存在，加载并缩放
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    
                    # 确保图片有透明度
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # 调整大小
                    img = img.resize(image_size, Image.Resampling.LANCZOS)
                    
                    # 转换为PhotoImage格式
                    photo_img = ImageTk.PhotoImage(img)
                    
                    # 存储到字典中
                    self.pet_images[state] = photo_img
                    self.photo_images[state] = photo_img  # 保持引用
                    
                    print(f"✅ 成功加载图片: {filename}")
                    
                except Exception as e:
                    print(f"❌ 加载图片 {filename} 失败: {e}")
                    self.create_catgirl_image(state, image_size)
            else:
                # 图片不存在，创建默认猫娘图片
                print(f"⚠️ 未找到图片: {filename}，正在生成简易猫娘...")
                self.create_catgirl_image(state, image_size)
                
        # 确保所有状态都有图片
        for state in ["idle", "thinking", "speaking", "sleeping", "happy"]:
            if state not in self.pet_images:
                self.create_catgirl_image(state, image_size)
    
    def create_catgirl_image(self, state, size=(160, 160)):
        """创建简易猫娘图片"""
        # 状态对应的配置
        state_config = {
            "idle": {
                "bg_color": (173, 216, 230, 220),  # 浅蓝色
                "face": "smile",
                "ears": "relaxed",
                "extra": None
            },
            "thinking": {
                "bg_color": (221, 160, 221, 220),  # 浅紫色
                "face": "thinking", 
                "ears": "perked",
                "extra": "question"
            },
            "speaking": {
                "bg_color": (144, 238, 144, 220),  # 浅绿色
                "face": "talking",
                "ears": "forward",
                "extra": "bubble"
            },
            "sleeping": {
                "bg_color": (211, 211, 211, 220),  # 浅灰色
                "face": "sleeping",
                "ears": "dropped",
                "extra": "zzz"
            },
            "happy": {
                "bg_color": (255, 255, 102, 220),  # 浅黄色
                "face": "happy",
                "ears": "excited",
                "extra": "hearts"
            }
        }
        
        config = state_config.get(state, state_config["idle"])
        
        try:
            # 创建新图片
            img = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # 绘制背景圆形
            circle_size = min(size) - 20
            x1 = (size[0] - circle_size) // 2
            y1 = (size[1] - circle_size) // 2
            x2 = x1 + circle_size
            y2 = y1 + circle_size
            
            # 绘制渐变背景
            for i in range(circle_size):
                alpha = int(200 - i * 0.5)
                if alpha < 50:
                    alpha = 50
                color = (*config["bg_color"][:3], alpha)
                draw.ellipse([x1+i//4, y1+i//4, x2-i//4, y2-i//4], 
                            outline=color, width=1)
            
            # 绘制猫耳朵
            ear_color = (255, 182, 193, 255)  # 粉红色
            ear_width = 20
            ear_height = 30
            
            # 左耳
            draw.polygon([
                (size[0]//2 - 30, y1 + 10),
                (size[0]//2 - 10, y1 - ear_height + 10),
                (size[0]//2 + 10, y1 + 10)
            ], fill=ear_color)
            
            # 右耳  
            draw.polygon([
                (size[0]//2 + 30, y1 + 10),
                (size[0]//2 + 10, y1 - ear_height + 10),
                (size[0]//2 - 10, y1 + 10)
            ], fill=ear_color)
            
            # 绘制脸部
            face_center_x = size[0] // 2
            face_center_y = size[1] // 2
            
            # 绘制眼睛
            eye_size = 15
            eye_y = face_center_y - 10
            
            if config["face"] in ["smile", "talking", "happy"]:
                # 开心的眼睛
                draw.ellipse([
                    face_center_x - 25, eye_y,
                    face_center_x - 25 + eye_size, eye_y + eye_size
                ], fill=(100, 149, 237, 255))  # 蓝色眼睛
                
                draw.ellipse([
                    face_center_x + 10, eye_y,
                    face_center_x + 10 + eye_size, eye_y + eye_size
                ], fill=(100, 149, 237, 255))
                
                # 瞳孔
                draw.ellipse([
                    face_center_x - 20, eye_y + 3,
                    face_center_x - 20 + 5, eye_y + 3 + 5
                ], fill=(0, 0, 0, 255))
                
                draw.ellipse([
                    face_center_x + 15, eye_y + 3,
                    face_center_x + 15 + 5, eye_y + 3 + 5
                ], fill=(0, 0, 0, 255))
                
            elif config["face"] == "thinking":
                # 思考的眼睛（半闭）
                draw.ellipse([
                    face_center_x - 25, eye_y + 5,
                    face_center_x - 25 + eye_size, eye_y + 5 + eye_size//2
                ], fill=(100, 149, 237, 255))
                
                draw.ellipse([
                    face_center_x + 10, eye_y + 5,
                    face_center_x + 10 + eye_size, eye_y + 5 + eye_size//2
                ], fill=(100, 149, 237, 255))
                
            elif config["face"] == "sleeping":
                # 睡觉的眼睛（线状）
                draw.line([
                    face_center_x - 25, eye_y + eye_size//2,
                    face_center_x - 10, eye_y + eye_size//2
                ], fill=(0, 0, 0, 255), width=3)
                
                draw.line([
                    face_center_x + 10, eye_y + eye_size//2,
                    face_center_x + 25, eye_y + eye_size//2
                ], fill=(0, 0, 0, 255), width=3)
            
            # 绘制嘴巴
            mouth_y = face_center_y + 20
            
            if config["face"] == "smile":
                draw.arc([
                    face_center_x - 20, mouth_y,
                    face_center_x + 20, mouth_y + 15
                ], 0, 180, fill=(0, 0, 0, 255), width=3)
                
            elif config["face"] == "talking":
                draw.ellipse([
                    face_center_x - 15, mouth_y,
                    face_center_x + 15, mouth_y + 10
                ], fill=(255, 255, 255, 255))
                
                draw.arc([
                    face_center_x - 15, mouth_y,
                    face_center_x + 15, mouth_y + 10
                ], 0, 180, fill=(0, 0, 0, 255), width=3)
                
            elif config["face"] == "happy":
                draw.arc([
                    face_center_x - 25, mouth_y - 5,
                    face_center_x + 25, mouth_y + 20
                ], 0, 180, fill=(0, 0, 0, 255), width=4)
                
            elif config["face"] == "thinking":
                draw.line([
                    face_center_x - 15, mouth_y + 5,
                    face_center_x + 15, mouth_y + 5
                ], fill=(0, 0, 0, 255), width=3)
                
            elif config["face"] == "sleeping":
                draw.line([
                    face_center_x - 10, mouth_y + 5,
                    face_center_x + 10, mouth_y + 5
                ], fill=(0, 0, 0, 255), width=2)
            
            # 绘制胡须
            whisker_color = (0, 0, 0, 180)
            whisker_length = 25
            
            # 左胡须
            draw.line([
                face_center_x - 20, face_center_y + 5,
                face_center_x - 20 - whisker_length, face_center_y - 5
            ], fill=whisker_color, width=2)
            
            draw.line([
                face_center_x - 20, face_center_y + 5,
                face_center_x - 20 - whisker_length, face_center_y + 15
            ], fill=whisker_color, width=2)
            
            # 右胡须
            draw.line([
                face_center_x + 20, face_center_y + 5,
                face_center_x + 20 + whisker_length, face_center_y - 5
            ], fill=whisker_color, width=2)
            
            draw.line([
                face_center_x + 20, face_center_y + 5,
                face_center_x + 20 + whisker_length, face_center_y + 15
            ], fill=whisker_color, width=2)
            
            # 绘制额外元素
            if config["extra"] == "question":
                # 问号
                draw.ellipse([
                    size[0] - 40, 20,
                    size[0] - 10, 50
                ], fill=(255, 255, 255, 220))
                
                try:
                    font = ImageFont.truetype("Arial", 20)
                    draw.text((size[0] - 25, 35), "?", fill=(0, 0, 0, 255), font=font, anchor="mm")
                except:
                    draw.text((size[0] - 25, 35), "?", fill=(0, 0, 0, 255), anchor="mm")
                    
            elif config["extra"] == "bubble":
                # 对话气泡
                draw.ellipse([
                    size[0] - 45, 25,
                    size[0] - 5, 65
                ], fill=(255, 255, 255, 220))
                
                # 气泡内的点
                for i in range(3):
                    draw.ellipse([
                        size[0] - 40 + i*12, 40,
                        size[0] - 30 + i*12, 50
                    ], fill=(100, 149, 237, 255))
                    
            elif config["extra"] == "zzz":
                # Zzz
                try:
                    font = ImageFont.truetype("Arial", 24)
                    draw.text((face_center_x, 30), "Z z z", fill=(0, 0, 0, 180), font=font, anchor="mm")
                except:
                    draw.text((face_center_x, 30), "Z z z", fill=(0, 0, 0, 180), anchor="mm")
                    
            elif config["extra"] == "hearts":
                # 爱心
                heart_color = (255, 105, 180, 255)
                heart_positions = [(30, 30), (size[0]-40, 40), (50, size[1]-50)]
                
                for hx, hy in heart_positions:
                    draw.ellipse([hx, hy, hx+8, hy+8], fill=heart_color)
                    draw.ellipse([hx+6, hy, hx+14, hy+8], fill=heart_color)
                    draw.polygon([
                        (hx, hy+4),
                        (hx+14, hy+4),
                        (hx+7, hy+12)
                    ], fill=heart_color)
            
            # 保存图片到文件
            image_path = os.path.join("images", f"{state}.png")
            img.save(image_path, "PNG")
            print(f"📁 已创建猫娘图片: {image_path}")
            
            # 转换为PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            
            # 存储
            self.pet_images[state] = photo_img
            self.photo_images[state] = photo_img
            
        except Exception as e:
            print(f"❌ 创建猫娘图片失败: {e}")
            # 最后备选：使用纯文本
            self.pet_images[state] = "🐱"
    
    def create_widgets(self):
        """创建界面组件"""
        # 背景色
        bg_color = '#f5f5f5' if self.is_macos else '#f5f5f5'
        
        # 主框架
        main_frame = tk.Frame(self.root, bg=bg_color, bd=0)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # 宠物图片标签
        self.pet_label = tk.Label(
            main_frame,
            bg=bg_color,
            bd=0
        )
        self.pet_label.pack(expand=True)
        
        # 设置初始图片
        self.update_pet_image()
        
        # 绑定事件
        self.pet_label.bind("<Double-Button-1>", self.open_chat_window)
        self.pet_label.bind("<Button-1>", self.start_move)
        
        # 为宠物标签绑定右键事件
        if self.is_macos:
            self.pet_label.bind("<Button-2>", self.show_context_menu)
            self.pet_label.bind("<Control-Button-1>", self.show_context_menu)
        else:
            self.pet_label.bind("<Button-3>", self.show_context_menu)
        
        # 对话窗口（初始隐藏）
        self.chat_window = None
        
        # 底部信息栏
        bottom_frame = tk.Frame(main_frame, bg=bg_color, height=40)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 宠物名称标签
        self.name_label = tk.Label(
            bottom_frame,
            text=self.pet_name,
            bg=bg_color,
            fg='#333333',
            font=("Arial", 11, "bold")
        )
        self.name_label.pack(side=tk.LEFT, padx=10)
        
        # 心情标签
        self.mood_label = tk.Label(
            bottom_frame,
            text="😊",
            bg=bg_color,
            fg='#FF6B6B',
            font=("Arial", 14)
        )
        self.mood_label.pack(side=tk.RIGHT, padx=10)
        
        # 更新心情显示
        self.update_mood()
        
        # 绑定右键事件到底部框架
        if self.is_macos:
            bottom_frame.bind("<Button-2>", self.show_context_menu)
            bottom_frame.bind("<Control-Button-1>", self.show_context_menu)
            self.name_label.bind("<Button-2>", self.show_context_menu)
            self.name_label.bind("<Control-Button-1>", self.show_context_menu)
        else:
            bottom_frame.bind("<Button-3>", self.show_context_menu)
            self.name_label.bind("<Button-3>", self.show_context_menu)
        
        # 确保窗口可见
        self.root.deiconify()
        self.root.update()
        
    def update_pet_image(self):
        """更新宠物显示的图片"""
        if hasattr(self, 'pet_images') and self.pet_state in self.pet_images:
            # 如果是PhotoImage对象
            if isinstance(self.pet_images[self.pet_state], ImageTk.PhotoImage):
                bg_color = '#f5f5f5' if self.is_macos else '#f5f5f5'
                self.pet_label.config(
                    image=self.pet_images[self.pet_state],
                    bg=bg_color
                )
            else:
                # 如果是文本（备用情况）
                bg_color = '#f5f5f5' if self.is_macos else '#f5f5f5'
                self.pet_label.config(
                    text=self.pet_images[self.pet_state],
                    font=("Arial", 72),
                    bg=bg_color
                )
        
    def start_move(self, event):
        """开始拖动窗口"""
        self.x = event.x
        self.y = event.y
        
    def stop_move(self, event):
        """停止拖动"""
        self.x = None
        self.y = None
        
    def on_move(self, event):
        """处理拖动"""
        if hasattr(self, 'x') and self.x is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 创建菜单
        menu = tk.Menu(self.root, tearoff=0, font=("Arial", 10))
        
        # 猫娘特色菜单项
        menu.add_command(label="对话喵~", command=self.open_chat_window)
        menu.add_separator()
        menu.add_command(label="投喂小鱼干", command=self.feed_fish)
        menu.add_command(label="摸摸头", command=self.pet_head)
        menu.add_command(label="玩耍", command=self.play_with_cat)
        menu.add_separator()
        menu.add_command(label="查看心情", command=self.show_mood)
        menu.add_command(label="换装", command=self.change_outfit)
        menu.add_separator()
        menu.add_command(label="设置", command=self.open_settings)
        menu.add_separator()
        menu.add_command(label="睡觉", command=self.go_to_sleep)
        menu.add_command(label="退出", command=self.on_closing)
        
        # 显示菜单
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            # 确保菜单被释放
            menu.grab_release()
    
    def feed_fish(self):
        """投喂小鱼干"""
        self.set_pet_state("happy")
        self.mood_value = min(100, self.mood_value + 20)
        self.update_mood()
        
        response = random.choice([
            "谢谢主人的小鱼干！好好吃喵~",
            "喵呜~最喜欢吃小鱼干了！",
            "主人对人家真好，要给主人蹭蹭~",
            "好吃！还要吃更多小鱼干喵！"
        ])
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        self.root.after(3000, lambda: self.set_pet_state("idle"))
        
    def pet_head(self):
        """摸摸头"""
        self.set_pet_state("happy")
        self.mood_value = min(100, self.mood_value + 15)
        self.update_mood()
        
        response = random.choice([
            "喵~好舒服，主人多摸摸~",
            "呼噜呼噜~最喜欢被主人摸了！",
            "主人的手好温暖喵~",
            "被摸摸好幸福，要一直陪着主人~"
        ])
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        self.root.after(2500, lambda: self.set_pet_state("idle"))
        
    def play_with_cat(self):
        """与猫娘玩耍"""
        self.set_pet_state("happy")
        self.mood_value = min(100, self.mood_value + 10)
        self.update_mood()
        
        response = random.choice([
            "喵！来抓这个毛线球！",
            "和主人一起玩最开心了！",
            "追尾巴游戏开始喵~",
            "主人要一直陪人家玩哦！"
        ])
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        self.root.after(3000, lambda: self.set_pet_state("idle"))
        
    def show_mood(self):
        """显示心情"""
        mood_text = ""
        if self.mood_value >= 80:
            mood_text = "超开心喵！"
            emoji = "😻"
        elif self.mood_value >= 60:
            mood_text = "心情不错~"
            emoji = "😸"
        elif self.mood_value >= 40:
            mood_text = "有点无聊喵..."
            emoji = "😼"
        elif self.mood_value >= 20:
            mood_text = "不开心了！"
            emoji = "😾"
        else:
            mood_text = "生气啦！"
            emoji = "🙀"
            
        messagebox.showinfo("小深的心情", 
                          f"{emoji} 心情值: {self.mood_value}/100\n{mood_text}")
        
    def change_outfit(self):
        """换装（预留功能）"""
        messagebox.showinfo("换装", "换装功能开发中喵~")
        
    def go_to_sleep(self):
        """睡觉"""
        self.set_pet_state("sleeping")
        self.conversation_history.append({
            "role": "assistant",
            "content": "喵...人家困了，先睡一会儿...Zzz",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
    def open_chat_window(self, event=None):
        """打开对话窗口"""
        if self.chat_window and tk.Toplevel.winfo_exists(self.chat_window):
            self.chat_window.lift()
            self.chat_window.focus_force()
            return
            
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.title(f"与{self.pet_name}对话")
        self.chat_window.geometry("500x550+200+200")
        self.chat_window.attributes('-topmost', True)
        
        # 设置窗口图标
        try:
            if "idle" in self.photo_images:
                self.chat_window.iconphoto(False, self.photo_images["idle"])
        except:
            pass
        
        # 对话历史显示
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_window,
            height=20,
            width=60,
            wrap=tk.WORD,
            state='disabled',
            bg='#f8f9fa',
            fg='#212529',
            font=("Microsoft YaHei", 10),
            padx=10,
            pady=10
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 输入框区域
        input_frame = ttk.Frame(self.chat_window)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.user_input = ttk.Entry(input_frame, width=45, font=("Microsoft YaHei", 11))
        self.user_input.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        # 语音输入按钮
        voice_btn = ttk.Button(input_frame, text="🎤", command=self.start_voice_input, width=3)
        voice_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 发送按钮
        send_btn = ttk.Button(input_frame, text="发送", command=self.send_message, width=8)
        send_btn.pack(side=tk.RIGHT)
        
        # 显示历史对话
        self.update_chat_display()
        
        # 聚焦到输入框
        self.user_input.focus_set()
        
    def start_voice_input(self):
        """开始语音输入"""
        if self.is_listening:
            return
            
        # 检查语音识别库是否安装
        try:
            import speech_recognition as sr
        except ImportError:
            messagebox.showwarning("语音输入", "语音输入功能需要安装 speech_recognition 库\n请运行: pip install speech_recognition")
            return
            
        # 检查麦克风是否可用
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                # 测试麦克风
                pass
        except Exception as e:
            messagebox.showerror("麦克风错误", f"无法访问麦克风:\n{str(e)}")
            return
        
        # 在新线程中开始语音识别
        self.is_listening = True
        threading.Thread(target=self.recognize_speech, daemon=True).start()
        
        # 在输入框显示提示
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, "正在聆听...请说话")
        self.user_input.config(foreground="gray")
        
    def recognize_speech(self):
        """识别语音"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                # 调整环境噪声
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # 开始录音
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # 识别语音（使用百度API免费版，支持中文）
                try:
                    # 使用Google语音识别（需要网络）
                    text = recognizer.recognize_google(audio, language="zh-CN")
                    
                    # 将结果放入队列
                    self.speech_queue.put(("success", text))
                    
                except sr.UnknownValueError:
                    self.speech_queue.put(("error", "无法识别语音，请再试一次喵~"))
                except sr.RequestError as e:
                    self.speech_queue.put(("error", f"语音服务错误: {str(e)}"))
                except Exception as e:
                    self.speech_queue.put(("error", f"识别失败: {str(e)}"))
                    
        except Exception as e:
            self.speech_queue.put(("error", f"语音输入错误: {str(e)}"))
        finally:
            self.is_listening = False
    
    def process_speech_queue(self):
        """处理语音识别队列"""
        try:
            while not self.speech_queue.empty():
                result_type, data = self.speech_queue.get_nowait()
                
                if result_type == "success":
                    # 更新输入框
                    self.root.after(0, lambda t=data: self.update_voice_input(t))
                else:
                    # 显示错误信息
                    self.root.after(0, lambda m=data: messagebox.showinfo("语音输入", m))
                    
        except queue.Empty:
            pass
        finally:
            # 每100毫秒检查一次队列
            self.root.after(100, self.process_speech_queue)
    
    def update_voice_input(self, text):
        """更新语音输入到输入框"""
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, text)
        self.user_input.config(foreground="black")
        
        # 可选：自动发送
        # self.send_message()
        
    def update_chat_display(self):
        """更新对话显示"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        
        if not self.conversation_history:
            # 如果没有对话历史，显示欢迎语
            welcome_msg = f"喵~我是{self.pet_name}，你的猫娘AI桌宠！\n双击我可以开始对话，右键我有很多互动选项喵~\n\n提示：点击🎤按钮可以使用语音输入哦！"
            self.chat_display.insert(tk.END, f"{self.pet_name}:\n", "ai_tag")
            self.chat_display.insert(tk.END, f"  {welcome_msg}\n\n", "ai_msg")
        else:
            # 显示最近15条对话
            for msg in self.conversation_history[-15:]:
                role = "你" if msg["role"] == "user" else self.pet_name
                
                # 添加时间戳
                time_str = f" [{msg['time']}]" if 'time' in msg else ""
                
                # 设置不同角色的颜色
                if msg["role"] == "user":
                    self.chat_display.insert(tk.END, f"{role}{time_str}:\n", "user_tag")
                    self.chat_display.insert(tk.END, f"  {msg['content']}\n\n", "user_msg")
                else:
                    self.chat_display.insert(tk.END, f"{role}{time_str}:\n", "ai_tag")
                    self.chat_display.insert(tk.END, f"  {msg['content']}\n\n", "ai_msg")
        
        # 配置标签样式
        self.chat_display.tag_config("user_tag", foreground="#2C3E50", font=("Microsoft YaHei", 10, "bold"))
        self.chat_display.tag_config("user_msg", foreground="#2C3E50")
        self.chat_display.tag_config("ai_tag", foreground="#E91E63", font=("Microsoft YaHei", 10, "bold"))
        self.chat_display.tag_config("ai_msg", foreground="#E91E63")
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
    def send_message(self):
        """发送消息给AI"""
        user_text = self.user_input.get().strip()
        if not user_text or user_text == "正在聆听...请说话":
            return
            
        # 更新最后互动时间
        self.last_interaction = datetime.now()
        self.mood_value = min(100, self.mood_value + 5)
        self.update_mood()
            
        # 添加到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_text,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        # 清空输入框
        self.user_input.delete(0, tk.END)
        
        # 更新显示
        self.update_chat_display()
        
        # 改变宠物状态为思考
        self.set_pet_state("thinking")
        
        # 在新线程中调用API
        threading.Thread(target=self.call_deepseek_api, args=(user_text,), daemon=True).start()
        
    def call_deepseek_api(self, user_message):
        """调用DeepSeek API"""
        if not self.api_key:
            self.show_error("请先设置DeepSeek API密钥喵~")
            self.set_pet_state("idle")
            return
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建对话历史（格式转换）
        messages = []
        
        # 添加系统提示词，定义猫娘性格
        messages.append({
            "role": "system",
            "content": self.personality
        })
        
        # 添加最近对话历史
        for msg in self.conversation_history[-8:]:  # 最近8轮对话
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.8,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                # 添加到历史
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                
                # 在GUI线程中更新
                self.root.after(0, self.update_chat_display)
                self.root.after(0, lambda: self.set_pet_state("speaking"))
                
                # 3秒后恢复空闲状态
                self.root.after(3000, lambda: self.set_pet_state("idle"))
                
            else:
                error_msg = f"API错误: {response.status_code}"
                if response.status_code == 401:
                    error_msg = "API密钥无效，请检查设置喵~"
                elif response.status_code == 429:
                    error_msg = "请求过于频繁，请稍后再试喵~"
                    
                self.show_error(error_msg)
                self.set_pet_state("idle")
                
        except requests.exceptions.Timeout:
            self.show_error("请求超时，请检查网络连接喵~")
            self.set_pet_state("idle")
        except requests.exceptions.ConnectionError:
            self.show_error("网络连接错误，请检查网络喵~")
            self.set_pet_state("idle")
        except Exception as e:
            self.show_error(f"未知错误: {str(e)}")
            self.set_pet_state("idle")
            
    def set_pet_state(self, state):
        """设置宠物状态并更新图片"""
        self.pet_state = state
        self.update_pet_image()
        
    def update_mood(self):
        """更新心情显示"""
        # 根据心情值更新表情
        if self.mood_value >= 80:
            emoji = "😻"
            color = "#4CAF50"  # 绿色
        elif self.mood_value >= 60:
            emoji = "😸"
            color = "#8BC34A"  # 浅绿
        elif self.mood_value >= 40:
            emoji = "😼"
            color = "#FFC107"  # 黄色
        elif self.mood_value >= 20:
            emoji = "😾"
            color = "#FF9800"  # 橙色
        else:
            emoji = "🙀"
            color = "#F44336"  # 红色
            
        self.mood_label.config(text=emoji, fg=color)
        
    def update_pet_state(self):
        """定期更新宠物状态（模拟行为）"""
        # 更新心情（随时间下降）
        now = datetime.now()
        
        # 确保 last_interaction 属性存在
        if hasattr(self, 'last_interaction'):
            time_diff = (now - self.last_interaction).seconds
        else:
            # 如果不存在，初始化为现在
            self.last_interaction = now
            time_diff = 0
        
        if time_diff > 300:  # 5分钟无互动
            self.mood_value = max(0, self.mood_value - 5)
            self.update_mood()
            self.last_interaction = now
        
        # 如果空闲超过60秒，可能进入睡觉状态
        if self.pet_state == "idle":
            last_activity = [msg for msg in self.conversation_history 
                           if msg["role"] == "user"]
            if last_activity:
                try:
                    last_time = datetime.strptime(last_activity[-1]["time"], "%H:%M:%S")
                    now = datetime.now()
                    idle_seconds = (now - last_time.replace(year=now.year, 
                                                           month=now.month, 
                                                           day=now.day)).seconds
                    if idle_seconds > 60:
                        self.set_pet_state("sleeping")
                except:
                    pass
            else:
                # 如果从来没有对话过，且空闲超过30秒，进入睡觉状态
                if hasattr(self, 'start_time'):
                    idle_seconds = (datetime.now() - self.start_time).seconds
                    if idle_seconds > 30:
                        self.set_pet_state("sleeping")
                else:
                    self.start_time = datetime.now()
        
        # 每30秒随机改变状态（如果处于空闲或睡觉状态）
        if self.pet_state in ["idle", "sleeping"]:
            if random.random() < 0.1:  # 10%概率
                self.set_pet_state("happy")
                self.root.after(2000, lambda: self.set_pet_state("idle"))
        
        # 每10秒检查一次状态
        self.root.after(10000, self.update_pet_state)
        
    def show_error(self, message):
        """显示错误信息"""
        self.root.after(0, lambda: messagebox.showerror("错误喵~", message))
        
    def open_settings(self):
        """打开设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置 - 小深猫娘")
        settings_window.geometry("450x400")
        settings_window.resizable(False, False)
        
        # 标签页
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API设置标签页
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="API设置")
        
        ttk.Label(api_frame, text="DeepSeek API密钥:", font=("Microsoft YaHei", 11)).pack(pady=(20, 5), anchor=tk.W)
        
        api_key_var = tk.StringVar(value=self.api_key)
        api_entry = ttk.Entry(api_frame, textvariable=api_key_var, width=50, show="*")
        api_entry.pack(pady=5, padx=20, fill=tk.X)
        
        ttk.Label(api_frame, text="获取API密钥: https://platform.deepseek.com/", 
                 font=("Microsoft YaHei", 9), foreground="blue", cursor="hand2").pack(pady=5)
        
        # 宠物设置标签页
        pet_frame = ttk.Frame(notebook)
        notebook.add(pet_frame, text="猫娘设置")
        
        ttk.Label(pet_frame, text="猫娘名称:", font=("Microsoft YaHei", 11)).pack(pady=(20, 5), anchor=tk.W)
        
        name_var = tk.StringVar(value=self.pet_name)
        name_entry = ttk.Entry(pet_frame, textvariable=name_var, width=30)
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        
        # 个性设置
        ttk.Label(pet_frame, text="个性描述:", font=("Microsoft YaHei", 11)).pack(pady=(15, 5), anchor=tk.W)
        
        personality_text = scrolledtext.ScrolledText(pet_frame, height=6, width=50, font=("Microsoft YaHei", 9))
        personality_text.pack(padx=20, pady=5, fill=tk.X)
        personality_text.insert("1.0", self.personality)
        
        # 说明标签
        ttk.Label(pet_frame, text="提示: 将猫娘图片放入images文件夹可自定义外观", 
                 font=("Microsoft YaHei", 9), foreground="gray").pack(pady=20)
        
        def save_settings():
            self.api_key = api_key_var.get()
            self.pet_name = name_var.get()
            self.personality = personality_text.get("1.0", tk.END).strip()
            self.name_label.config(text=self.pet_name)
            
            # 保存配置到文件
            self.save_config()
            
            settings_window.destroy()
            messagebox.showinfo("提示", "设置已保存喵~")
            
        # 保存按钮
        btn_frame = ttk.Frame(settings_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="保存", command=save_settings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=settings_window.destroy, width=15).pack(side=tk.RIGHT, padx=5)
        
    def run(self):
        """运行主循环"""
        print("=" * 60)
        print("🐱 小深猫娘AI桌宠启动成功！")
        print(f"📱 操作系统: {platform.system()}")
        print("🎮 操作提示：")
        print("  - 双击猫娘打开对话窗口")
        print("  - 拖动猫娘可移动位置")
        print("  - 右键点击猫娘显示功能菜单")
        if self.is_macos:
            print("     * 在macOS上：使用双指点按或Control+左键")
        else:
            print("     * 使用鼠标右键")
        print("  - 菜单功能：投喂、摸摸头、玩耍、查看心情等")
        print("  - 对话窗口中点击🎤按钮可以使用语音输入")
        print("  - 首次使用请在设置中配置API密钥")
        print("=" * 60)
        
        # 确保窗口显示
        self.root.deiconify()
        self.root.update()
        
        # 启动主循环
        self.root.mainloop()

# 启动函数
def main():
    # 检查依赖
    try:
        import requests
    except ImportError:
        print("正在安装所需依赖...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pillow"])
            print("依赖安装完成，请重新运行程序。")
        except Exception as e:
            print(f"安装依赖失败: {e}")
            print("请手动安装依赖: pip install requests pillow")
        return
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("正在安装Pillow库...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("Pillow安装完成，请重新运行程序。")
        except:
            print("安装Pillow失败，将使用文本模式运行。")
    
    # 检查语音识别库
    try:
        import speech_recognition
        print("✅ 语音输入功能可用")
    except ImportError:
        print("⚠️ 语音输入功能需要安装 speech_recognition 库")
        print("   安装命令: pip install speech_recognition")
        print("   或安装完整依赖: pip install speech_recognition pyaudio")
    
    # 创建并运行猫娘宠物
    try:
        pet = CatGirlDeskPet()
        pet.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")

if __name__ == "__main__":
    main()