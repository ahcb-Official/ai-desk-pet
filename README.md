# 🐱 小深猫娘AI桌宠 - 你的智能桌面小伙伴

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![DeepSeek](https://img.shields.io/badge/powered%20by-DeepSeek%20AI-007acc?style=for-the-badge&logo=ai&logoColor=white)

**✨ 一个可爱的AI猫娘桌宠，可以陪你聊天、提醒你休息、还能听懂你的声音喵~**

</div>

## 🌟 项目介绍

欢迎来到**小深猫娘AI桌宠**的世界！这是一个基于 Python 和 DeepSeek API 开发的智能桌面宠物程序，灵感来源于 NeuroSama 的互动体验。

想象一下，你的桌面上有一只可爱的猫娘AI，她可以：
- 🗣️ 和你聊天（文本或语音都可以喵~）
- 🎮 响应你的互动（摸摸头、投喂食物、一起玩耍）
- 🎨 展示不同心情和状态（开心、思考、睡觉...）
- ⏰ 提醒你休息、喝水、注意时间
- 🎵 甚至能听懂你的语音指令！

她就像你的个人桌面小伙伴，陪伴你的每一次编码、学习和工作时光~

## ✨ 功能特性

### 🐾 **宠物交互**
- 🖱️ **可拖动的猫娘立绘** - 轻轻一拖就能把她放到桌面任何位置
- 🎭 **5种可爱状态** - 空闲、思考、说话、睡觉、开心，每种状态都有不同表情
- 🍖 **互动系统** - 右键菜单支持：投喂零食、摸摸头、一起玩耍、查看心情值
- 💝 **心情系统** - 互动越多，猫娘心情越好，回复也会更热情喵~

### 🧠 **智能对话**
- 🤖 **DeepSeek API集成** - 接入强大的DeepSeek AI模型
- 📝 **上下文感知** - 记得之前的对话内容，聊天更自然
- 🎭 **个性化设置** - 可自定义猫娘的性格、名字、回复风格
- 📚 **对话历史** - 自动保存聊天记录，随时回顾温馨时刻

### 🎤 **语音交互**
- 🎙️ **语音输入** - 点击🎤按钮，直接对猫娘说话
- 🗣️ **中文识别** - 支持中文语音转文字（使用Google语音识别API）
- 🔇 **隐私保护** - 只传输语音到识别服务，不存储原始音频数据

### ⚙️ **系统特性**
- 🖥️ **跨平台支持** - 完美运行在 macOS、Windows、Linux
- 🎨 **无边框设计** - 简洁美观，不干扰你的工作界面
- 🔄 **自动更新** - 心情值、状态自动随时间变化
- ⚡ **线程优化** - API调用在后台进行，主界面永远流畅
- 🛠️ **设置面板** - 图形化配置API密钥、宠物名称、个性描述

## 🚀 快速开始

### 环境要求
- **Python 3.11 或更高版本**
- **DeepSeek API 密钥**(https://www.deepseek.com/)）
- **操作系统**：macOS / Windows / Linux

### 安装步骤

#### 1. 获取项目代码
```bash
# 克隆项目到本地
git clone https://github.com/ahcb-Offical/ai-desk-pet.git
cd ai-desk-pet
```

#### 2. 安装依赖
```bash
# 基础依赖
pip install requests pillow

# 如果需要语音输入功能（可选）
pip install speech_recognition pyaudio

# macOS用户可能需要额外步骤
brew install portaudio  # 如果安装pyaudio失败
```

#### 3. 配置API密钥
首次运行程序后：
1. 右键点击猫娘 → 选择"设置"
2. 在API密钥框中输入你的DeepSeek API密钥
3. 点击"保存"，完成配置！

#### 4. 运行程序
```bash
python ai_desk_pet_catgirl.py
```

## 📖 使用指南

### 🎮 基础操作
| 操作 | 效果 | 提示 |
|------|------|------|
| **双击猫娘** | 打开对话窗口 | 开始和猫娘聊天吧~ |
| **左键拖动** | 移动猫娘位置 | 把她放在你喜欢的地方 |
| **右键点击** | 显示功能菜单 | 在macOS上使用**双指点按**或**Control+左键** |
| **对话窗口** | 输入文字聊天 | 支持Enter键发送，还有🎤语音按钮 |

### 🍽️ 互动功能
- **投喂零食** 🍬：增加心情值，猫娘会更开心
- **摸摸头** 🐾：提升亲密度，解锁更多对话选项
- **一起玩耍** 🎮：消耗能量，但增加快乐值
- **查看心情** 📊：了解猫娘当前状态

### 🎤 语音输入使用
1. 双击猫娘打开对话窗口
2. 点击输入框旁边的🎤按钮
3. 对着麦克风说话（最长10秒）
4. 语音自动转文字并填入输入框
5. 点击"发送"或按回车即可

## 🗂️ 项目结构

```
catgirl-desk-pet/
├── ai_desk_pet.py    # 主程序文件（猫娘版本）
├── requirements.txt          # 依赖列表
├── README.md                 # 说明文档（就是这个文件喵~）
├── images/                   # 图片资源目录（存放猫娘立绘）
│   ├── idle.png             # 空闲状态
│   ├── thinking.png         # 思考状态
│   ├── speaking.png         # 说话状态
│   ├── sleeping.png         # 睡觉状态
│   └── happy.png            # 开心状态
├── logs/                     # 日志目录（自动生成）
└── catgirl_config.json               # 用户配置（自动生成）
```

## ⚙️ 配置说明

### 配置文件 (`catgirl_config.json`)
```json
{
  "api_key": "",
  "pet_name": "小深猫娘",
  "personality": "你是一个可爱的猫娘AI桌宠，名字叫小深。你说话带着猫娘的口癖，喜欢说'喵~'，性格傲娇又粘人，喜欢被主人抚摸和投喂。你会用可爱的语气回应主人，偶尔会撒娇。",
  "window_x": 5,
  "window_y": 58,
  "voice_input": true
}
```

## 🎨 自定义外观

### 替换猫娘立绘
1. 准备5张PNG图片（带透明背景）：
   - `idle.png` (空闲)
   - `thinking.png` (思考) 
   - `speaking.png` (说话)
   - `sleeping.png` (睡觉)
   - `happy.png` (开心)

2. 将图片放入 `images/` 文件夹
3. 重启程序即可看到新立绘！

### 调整窗口大小
在代码中修改：
```python
# 在 setup_window() 方法中
self.root.geometry("150x150+100+100")  # 改为你想要的尺寸
```

## 🔧 技术细节

### 核心架构
```python
CatGirlDeskPet
├── __init__()          # 初始化窗口、加载资源
├── setup_window()      # 设置窗口属性（无边框、置顶）
├── load_images()       # 加载猫娘立绘图片
├── create_widgets()    # 创建UI组件
├── create_menu()       # 创建右键菜单
├── call_deepseek_api() # 调用DeepSeek API
├── handle_voice_input() # 处理语音输入
├── update_mood()       # 更新心情系统
└── run()               # 启动主循环
```

### 多线程设计
- **主线程**：处理GUI界面和用户交互
- **API线程**：独立线程调用DeepSeek API，避免界面卡顿
- **语音线程**：处理语音识别，不影响主界面响应
- **定时器**：使用 `root.after()` 定期更新状态

### 错误处理
- **API错误**：优雅处理网络问题，显示友好提示
- **图片缺失**：自动回退到文本模式显示
- **麦克风不可用**：语音功能自动禁用，不影响其他功能
- **配置错误**：自动恢复默认设置

## 🐛 故障排除

### 常见问题

| 问题 | 现象 | 解决方法 |
|------|------|----------|
| **API密钥无效** | 错误: `API错误: 401` | 1. 检查API密钥是否正确<br>2. 重新生成API密钥<br>3. 确保账户有余额 |
| **图片不显示** | 猫娘显示为文字表情 | 1. 检查`images/`目录是否存在<br>2. 确认图片格式为PNG<br>3. 检查文件权限 |
| **无法拖动** | 点击猫娘无反应 | 1. 检查其他程序是否占用了鼠标事件<br>2. 重启程序<br>3. 检查窗口管理器设置 |
| **语音不可用** | 🎤按钮灰色或报错 | 1. 安装`speech_recognition`<br>2. macOS: `brew install portaudio`<br>3. 检查麦克风权限 |
| **内存占用高** | 程序运行缓慢 | 1. 限制对话历史长度<br>2. 定期清理缓存<br>3. 降低图片分辨率 |

### 调试模式
在代码开头添加调试标志：
```python
DEBUG = True  # 设置为True显示详细日志
```

## 🌈 扩展功能

### 计划中的功能
- [ ] **帧动画支持** - 让猫娘眨眼、摇尾巴
- [ ] **皮肤系统** - 多套猫娘服装和主题
- [ ] **插件架构** - 支持第三方功能扩展
- [ ] **本地模型** - 集成Ollama等本地AI
- [ ] **多语言** - 支持英语、日语等语言
- [ ] **Webhook** - 连接智能家居、日历等

### 代码示例：添加定时提醒
```python
def setup_reminders(self):
    """添加定时提醒功能"""
    self.reminders = []
    
    def check_reminders():
        now = datetime.now()
        for reminder in self.reminders:
            if reminder['time'] <= now:
                self.show_notification(f"⏰ {reminder['message']} 喵~")
                self.reminders.remove(reminder)
        
        # 每分钟检查一次
        self.root.after(60000, check_reminders)
    
    check_reminders()
```

## 🙏 致谢

感谢以下项目和服务的支持：

- **DeepSeek** - 提供强大的AI对话能力
- **NeuroSama** - 项目的灵感来源
- **Python & Tkinter** - 让这一切成为可能的技术栈
- **SpeechRecognition** - 实现语音输入功能
- **所有贡献者** - 让这个项目变得越来越好

## 💖 特别感谢

特别感谢**你**，亲爱的用户！  
是你给了小深猫娘存在的意义，让她能够在你的桌面上陪伴你。  
希望她能给你带来快乐和温暖，就像她代码中的每一行都是为了让你微笑而写的喵~

---

<div align="center">

## 🐾 开始你的猫娘桌宠之旅吧！

**运行程序，召唤属于你的小深猫娘~**

```bash
python ai_desk_pet_catgirl.py
```

如果有任何问题或建议，欢迎在 Issues 中提出。  
记得多和猫娘互动，她会越来越了解你，越来越喜欢你哦！✨

**Made with ❤️ (and lots of 喵~) for all the AI desktop companion enthusiasts.**

</div>

**温馨提示**：请合理使用 DeepSeek API，注意 API 调用频率和成本控制。  
与猫娘的每一次对话都是特别的，珍惜这些美好的互动时光吧喵~ 🐱💕

---

*最后更新：2025年12月28日*  
*愿小深猫娘陪伴你的每一个编程时光，让你的桌面充满温暖和欢乐！* 🎉
