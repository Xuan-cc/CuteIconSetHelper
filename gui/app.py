"""
GUI模块 - 主应用框架
"""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import typing as tp

from gui.input_frame import InputFrame
from gui.crop_frame import CropFrame
from gui.generate_frame import GenerateFrame


class ImageComposerApp:
    """图片组合工具主应用"""
    
    def __init__(self, root: tk.Tk, dnd_available: bool = True):
        self.root = root
        self.root.title("图片组合工具")
        self.root.geometry("1000x800")  # 增加窗口大小
        self.root.minsize(900, 700)  # 增加最小尺寸
        self.dnd_available = dnd_available
        
        # 存储当前处理的图片数据
        self.image_data: tp.List[tp.Dict] = []  # [{"path": str, "image": PIL.Image, "cropped": bool}]
        self.cropped_images: tp.List[tp.Dict] = []  # 裁剪后的图片
        
        # 创建主框架
        self._create_main_frame()
        
        # 创建步骤指示器
        self._create_step_indicator()
        
        # 初始化各个界面
        self._init_frames()
        
        # 显示输入界面
        self.show_input_frame()
    
    def _create_main_frame(self):
        """创建主框架"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        self.title_label = ttk.Label(
            self.main_frame, 
            text="图片组合工具", 
            font=("Microsoft YaHei", 16, "bold")
        )
        self.title_label.pack(pady=5)
        
        # 项目地址
        self.url_label = tk.Label(
            self.main_frame,
            text="https://github.com/Xuan-cc/CuteIconSetHelper",
            font=("Microsoft YaHei", 9),
            fg="blue",
            cursor="hand2"
        )
        self.url_label.pack(pady=2)
        self.url_label.bind("<Button-1>", self._open_url)
        
    def _open_url(self, event):
        """打开项目地址"""
        import webbrowser
        webbrowser.open("https://github.com/Xuan-cc/CuteIconSetHelper")
    
    def _create_step_indicator(self):
        """创建步骤指示器"""
        self.step_frame = ttk.Frame(self.main_frame)
        self.step_frame.pack(fill=tk.X, pady=5)
        
        self.step_labels = []
        steps = ["1. 导入图片", "2. 裁剪图片", "3. 生成输出"]
        for i, step in enumerate(steps):
            lbl = ttk.Label(self.step_frame, text=step, font=("Microsoft YaHei", 10))
            lbl.pack(side=tk.LEFT, padx=20)
            self.step_labels.append(lbl)
        
        # 内容区域
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def _init_frames(self):
        """初始化所有界面"""
        self.input_frame = InputFrame(self.content_frame, self, dnd_available=self.dnd_available)
        self.crop_frame = CropFrame(self.content_frame, self)
        self.generate_frame = GenerateFrame(self.content_frame, self)
        
        # 全部隐藏
        for frame in [self.input_frame, self.crop_frame, self.generate_frame]:
            frame.pack_forget()
    
    def _update_step_indicator(self, current_step: int):
        """更新步骤指示器"""
        for i, lbl in enumerate(self.step_labels):
            if i == current_step - 1:
                lbl.configure(foreground="blue", font=("Microsoft YaHei", 10, "bold"))
            else:
                lbl.configure(foreground="gray", font=("Microsoft YaHei", 10))
    
    def show_input_frame(self):
        """显示输入界面"""
        self._hide_all_frames()
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        self._update_step_indicator(1)
    
    def show_crop_frame(self, images: tp.List[tp.Dict]):
        """显示裁剪界面"""
        self.image_data = images
        self._hide_all_frames()
        self.crop_frame.set_images(images)
        self.crop_frame.pack(fill=tk.BOTH, expand=True)
        self._update_step_indicator(2)
    
    def show_generate_frame(self, images: tp.List[tp.Dict]):
        """显示生成界面"""
        self.cropped_images = images
        self._hide_all_frames()
        self.generate_frame.set_images(images)
        self.generate_frame.pack(fill=tk.BOTH, expand=True)
        self._update_step_indicator(3)
    
    def _hide_all_frames(self):
        """隐藏所有界面"""
        for frame in [self.input_frame, self.crop_frame, self.generate_frame]:
            frame.pack_forget()
