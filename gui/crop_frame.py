"""
裁剪界面 - 支持1:1比例裁剪（改进版：可拖动裁剪框）
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import typing as tp
import math


class CropFrame(ttk.Frame):
    """图片裁剪界面"""
    
    def __init__(self, parent: ttk.Frame, app):
        super().__init__(parent)
        self.app = app
        self.images: tp.List[tp.Dict] = []
        self.current_index = 0
        self.cropped_images: tp.List[tp.Dict] = []
        
        # 画布相关
        self.canvas: tk.Canvas = None
        self.photo_image: ImageTk.PhotoImage = None
        self.original_image: Image.Image = None
        self.display_scale = 1.0
        
        # 裁剪框
        self.crop_rect = None
        self.crop_x1 = 0  # 裁剪框左上角
        self.crop_y1 = 0
        self.crop_x2 = 0  # 裁剪框右下角
        self.crop_y2 = 0
        self.is_dragging = False
        self.drag_mode = None  # 'move' 或 'create'
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=10)
        
        self.title_label = ttk.Label(
            title_frame,
            text="裁剪图片",
            font=("Microsoft YaHei", 12, "bold")
        )
        self.title_label.pack()
        
        self.progress_label = ttk.Label(
            title_frame,
            text="",
            font=("Microsoft YaHei", 10)
        )
        self.progress_label.pack(pady=5)
        
        # 主内容区
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 图片显示画布
        self.canvas = tk.Canvas(
            content_frame,
            bg="#2b2b2b",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 控制面板
        control_frame = ttk.Frame(content_frame, width=200)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        control_frame.pack_propagate(False)
        
        # 信息面板
        info_frame = ttk.LabelFrame(control_frame, text="图片信息")
        info_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.info_size = ttk.Label(info_frame, text="尺寸: -")
        self.info_size.pack(anchor=tk.W, padx=5, pady=2)
        
        self.info_ratio = ttk.Label(info_frame, text="比例: -")
        self.info_ratio.pack(anchor=tk.W, padx=5, pady=2)
        
        # 裁剪控制
        crop_control = ttk.LabelFrame(control_frame, text="裁剪控制")
        crop_control.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Label(
            crop_control,
            text="拖动裁剪框可移动位置\n在框外拖动可重新绘制",
            wraplength=180,
            justify=tk.CENTER
        ).pack(pady=10)
        
        ttk.Button(
            crop_control,
            text="重置裁剪框",
            command=self._reset_crop
        ).pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            crop_control,
            text="自动居中裁剪",
            command=self._auto_crop
        ).pack(fill=tk.X, padx=5, pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="跳过此图",
            command=self._skip_current
        ).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(
            btn_frame,
            text="应用裁剪",
            command=self._apply_crop
        ).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(
            btn_frame,
            text="下一步",
            command=self._finish
        ).pack(fill=tk.X, padx=5, pady=5)
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
    
    def set_images(self, images: tp.List[tp.Dict]):
        """设置要处理的图片"""
        self.images = images
        # 保留已裁剪的图片（如果重新进入）
        if not self.cropped_images:
            self.cropped_images = []
        self.current_index = len(self.cropped_images)  # 从上次位置继续
        
        # 找到下一个需要裁剪的图片
        self._find_next_non_square()
        self._load_current_image()
    
    def _find_next_non_square(self):
        """找到下一个非1:1的图片"""
        while self.current_index < len(self.images):
            img = self.images[self.current_index]
            if not img.get("is_square", False):
                return
            # 已经是1:1的，直接加入裁剪完成列表
            if self.current_index >= len(self.cropped_images):
                self.cropped_images.append(img)
            self.current_index += 1
    
    def _load_current_image(self):
        """加载当前图片"""
        if self.current_index >= len(self.images):
            self._finish()
            return
        
        img_data = self.images[self.current_index]
        self.original_image = img_data["image"].copy()
        
        # 更新信息
        width, height = self.original_image.size
        self.info_size.configure(text=f"尺寸: {width} x {height}")
        ratio = width / height
        self.info_ratio.configure(text=f"比例: {ratio:.2f}:1")
        
        self.progress_label.configure(
            text=f"处理第 {self.current_index + 1} / {len(self.images)} 张图片"
        )
        
        # 在画布上显示图片（包括初始化裁剪框）
        self._display_image()
    
    def _display_image(self):
        """在画布上显示图片"""
        if not self.original_image:
            return
        
        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # 画布还未渲染，稍后重试
            self.after(100, self._display_image)
            return
        
        # 计算缩放比例
        img_width, img_height = self.original_image.size
        scale_w = canvas_width / img_width
        scale_h = canvas_height / img_height
        self.display_scale = min(scale_w, scale_h, 1.0) * 0.9  # 留边距
        
        # 缩放图片
        new_width = int(img_width * self.display_scale)
        new_height = int(img_height * self.display_scale)
        
        display_img = self.original_image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )
        
        self.photo_image = ImageTk.PhotoImage(display_img)
        
        # 清空画布并显示图片
        self.canvas.delete("all")
        
        # 居中显示
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
        self.canvas.image = self.photo_image  # 保持引用
        
        # 保存图片位置
        self.img_offset_x = x
        self.img_offset_y = y
        self.img_display_width = new_width
        self.img_display_height = new_height
        
        # 图片显示完成后，初始化裁剪框
        self._init_crop_rect()
    
    def _init_crop_rect(self):
        """初始化裁剪框"""
        # 默认裁剪框：取图片中心，边长为min(宽,高)
        width, height = self.original_image.size
        size = min(width, height)
        
        # 计算显示尺寸
        display_size = int(size * self.display_scale)
        display_x = self.img_offset_x + (self.img_display_width - display_size) // 2
        display_y = self.img_offset_y + (self.img_display_height - display_size) // 2
        
        # 设置裁剪框坐标
        self.crop_x1 = display_x
        self.crop_y1 = display_y
        self.crop_x2 = display_x + display_size
        self.crop_y2 = display_y + display_size
        
        # 创建裁剪框
        self._draw_crop_rect()
    
    def _draw_crop_rect(self):
        """绘制裁剪框"""
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_x1, self.crop_y1,
            self.crop_x2, self.crop_y2,
            outline="red",
            width=2,
            dash=(5, 5)
        )
    
    def _is_point_in_crop_rect(self, x, y):
        """检查点是否在裁剪框内"""
        return (self.crop_x1 <= x <= self.crop_x2 and 
                self.crop_y1 <= y <= self.crop_y2)
    
    def _on_mouse_down(self, event):
        """鼠标按下"""
        # 检查是否点击在裁剪框内
        if self._is_point_in_crop_rect(event.x, event.y):
            self.drag_mode = 'move'
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        elif (self.img_offset_x <= event.x <= self.img_offset_x + self.img_display_width and
              self.img_offset_y <= event.y <= self.img_offset_y + self.img_display_height):
            # 在图片范围内但不在裁剪框内，重新绘制
            self.drag_mode = 'create'
            self.crop_x1 = event.x
            self.crop_y1 = event.y
        
        self.is_dragging = True
    
    def _on_mouse_drag(self, event):
        """鼠标拖动"""
        if not self.is_dragging:
            return
        
        # 限制在图片范围内
        x = max(self.img_offset_x, min(event.x, self.img_offset_x + self.img_display_width))
        y = max(self.img_offset_y, min(event.y, self.img_offset_y + self.img_display_height))
        
        if self.drag_mode == 'move':
            # 移动裁剪框
            dx = x - self.drag_start_x
            dy = y - self.drag_start_y
            
            # 计算新位置
            new_x1 = self.crop_x1 + dx
            new_y1 = self.crop_y1 + dy
            new_x2 = self.crop_x2 + dx
            new_y2 = self.crop_y2 + dy
            
            # 确保不超出图片范围
            crop_width = self.crop_x2 - self.crop_x1
            crop_height = self.crop_y2 - self.crop_y1
            
            if new_x1 < self.img_offset_x:
                new_x1 = self.img_offset_x
                new_x2 = new_x1 + crop_width
            if new_y1 < self.img_offset_y:
                new_y1 = self.img_offset_y
                new_y2 = new_y1 + crop_height
            if new_x2 > self.img_offset_x + self.img_display_width:
                new_x2 = self.img_offset_x + self.img_display_width
                new_x1 = new_x2 - crop_width
            if new_y2 > self.img_offset_y + self.img_display_height:
                new_y2 = self.img_offset_y + self.img_display_height
                new_y1 = new_y2 - crop_height
            
            self.crop_x1 = new_x1
            self.crop_y1 = new_y1
            self.crop_x2 = new_x2
            self.crop_y2 = new_y2
            
            self.drag_start_x = x
            self.drag_start_y = y
            
            self._draw_crop_rect()
            
        elif self.drag_mode == 'create':
            # 重新绘制裁剪框（保持正方形）
            width = abs(x - self.crop_x1)
            height = abs(y - self.crop_y1)
            size = min(width, height)
            
            if x >= self.crop_x1:
                self.crop_x2 = self.crop_x1 + size
            else:
                self.crop_x2 = self.crop_x1
                self.crop_x1 = self.crop_x1 - size
            
            if y >= self.crop_y1:
                self.crop_y2 = self.crop_y1 + size
            else:
                self.crop_y2 = self.crop_y1
                self.crop_y1 = self.crop_y1 - size
            
            # 限制在图片范围内
            self._constrain_crop_rect()
            self._draw_crop_rect()
    
    def _constrain_crop_rect(self):
        """确保裁剪框在图片范围内"""
        crop_width = self.crop_x2 - self.crop_x1
        crop_height = self.crop_y2 - self.crop_y1
        
        if self.crop_x1 < self.img_offset_x:
            self.crop_x1 = self.img_offset_x
            self.crop_x2 = self.crop_x1 + crop_width
        if self.crop_y1 < self.img_offset_y:
            self.crop_y1 = self.img_offset_y
            self.crop_y2 = self.crop_y1 + crop_height
        if self.crop_x2 > self.img_offset_x + self.img_display_width:
            self.crop_x2 = self.img_offset_x + self.img_display_width
            self.crop_x1 = self.crop_x2 - crop_width
        if self.crop_y2 > self.img_offset_y + self.img_display_height:
            self.crop_y2 = self.img_offset_y + self.img_display_height
            self.crop_y1 = self.crop_y2 - crop_height
    
    def _on_mouse_up(self, event):
        """鼠标释放"""
        self.is_dragging = False
        self.drag_mode = None
    
    def _reset_crop(self):
        """重置裁剪框"""
        self._init_crop_rect()
    
    def _auto_crop(self):
        """自动居中裁剪"""
        self._init_crop_rect()
    
    def _skip_current(self):
        """跳过当前图片"""
        # 使用原图
        img_data = self.images[self.current_index]
        if self.current_index >= len(self.cropped_images):
            self.cropped_images.append(img_data)
        else:
            self.cropped_images[self.current_index] = img_data
        
        self.current_index += 1
        self._find_next_non_square()
        self._load_current_image()
    
    def _apply_crop(self):
        """应用裁剪"""
        if not self.crop_rect:
            return
        
        # 计算裁剪区域（转换到原始图片坐标）
        x1 = (min(self.crop_x1, self.crop_x2) - self.img_offset_x) / self.display_scale
        y1 = (min(self.crop_y1, self.crop_y2) - self.img_offset_y) / self.display_scale
        x2 = (max(self.crop_x1, self.crop_x2) - self.img_offset_x) / self.display_scale
        y2 = (max(self.crop_y1, self.crop_y2) - self.img_offset_y) / self.display_scale
        
        # 转换为整数坐标
        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)
        
        # 确保正方形
        size = min(x2 - x1, y2 - y1)
        x2, y2 = x1 + size, y1 + size
        
        # 裁剪图片
        cropped = self.original_image.crop((x1, y1, x2, y2))
        
        # 更新图片数据
        img_data = self.images[self.current_index].copy()
        img_data["image"] = cropped
        img_data["width"] = size
        img_data["height"] = size
        img_data["is_square"] = True
        img_data["cropped"] = True
        
        if self.current_index >= len(self.cropped_images):
            self.cropped_images.append(img_data)
        else:
            self.cropped_images[self.current_index] = img_data
        
        self.current_index += 1
        self._find_next_non_square()
        self._load_current_image()
    
    def _finish(self):
        """完成裁剪，进入生成界面"""
        if not self.cropped_images:
            messagebox.showwarning("提示", "没有可处理的图片")
            return
        
        self.app.show_generate_frame(self.cropped_images)
