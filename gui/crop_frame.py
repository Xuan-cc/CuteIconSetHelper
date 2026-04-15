"""
裁剪界面 - 支持1:1比例裁剪（改进版：可拖动裁剪框）
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
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
        title_frame.pack(fill=tk.X, pady=5)
        
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
        self.progress_label.pack(pady=2)
        
        # 主内容区 - 使用水平分割
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧：图片显示画布
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(
            left_frame,
            bg="#2b2b2b",
            relief=tk.SUNKEN,
            borderwidth=2,
            height=400
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：控制面板 - 使用固定宽度并允许滚动
        right_container = ttk.Frame(content_frame, width=220)
        right_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        right_container.pack_propagate(False)
        
        # 创建Canvas和Scrollbar实现滚动
        right_canvas = tk.Canvas(right_container, width=200)
        scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=right_canvas.yview)
        control_frame = ttk.Frame(right_canvas)
        
        control_frame.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )
        
        right_canvas.create_window((0, 0), window=control_frame, anchor="nw", width=200)
        right_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 信息面板
        info_frame = ttk.LabelFrame(control_frame, text="图片信息")
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.info_size = ttk.Label(info_frame, text="尺寸: -")
        self.info_size.pack(anchor=tk.W, padx=5, pady=1)
        
        self.info_ratio = ttk.Label(info_frame, text="比例: -")
        self.info_ratio.pack(anchor=tk.W, padx=5, pady=1)
        
        # 状态提示
        self.status_label = ttk.Label(control_frame, text="就绪", foreground="gray", font=("Microsoft YaHei", 9))
        self.status_label.pack(pady=5)

        # 裁剪控制
        crop_control = ttk.LabelFrame(control_frame, text="裁剪控制")
        crop_control.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(
            crop_control,
            text="拖动裁剪框可移动\n框外拖动可重绘",
            wraplength=180,
            justify=tk.CENTER,
            font=("Microsoft YaHei", 9)
        ).pack(pady=2)

        # 裁剪形状选择 - 添加trace监听变化
        self.crop_shape_var = tk.StringVar(value="square")
        self.crop_shape_var.trace_add('write', self._on_shape_changed)
        shape_frame = ttk.Frame(crop_control)
        shape_frame.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(shape_frame, text="裁剪形状:").pack(side=tk.LEFT)
        ttk.Radiobutton(shape_frame, text="方形", variable=self.crop_shape_var,
                       value="square").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(shape_frame, text="圆形", variable=self.crop_shape_var,
                       value="circle").pack(side=tk.LEFT, padx=2)

        ttk.Button(
            crop_control,
            text="重置裁剪框",
            command=self._reset_crop
        ).pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(
            crop_control,
            text="自动居中裁剪",
            command=self._auto_crop
        ).pack(fill=tk.X, padx=5, pady=2)

        # 保存裁切按钮 - 移到裁剪控制栏
        ttk.Button(
            crop_control,
            text="✓ 保存裁切到素材库",
            command=self._save_crop_to_library
        ).pack(fill=tk.X, padx=5, pady=2)
        
        # 实时预览窗口
        preview_frame = ttk.LabelFrame(control_frame, text="裁剪预览")
        preview_frame.pack(fill=tk.X, pady=5, padx=5)

        self.preview_canvas = tk.Canvas(preview_frame, width=150, height=150, bg="#2b2b2b")
        self.preview_canvas.pack(pady=3)

        # 底部导航按钮 - 始终可见
        nav_frame = ttk.LabelFrame(control_frame, text="图片导航")
        nav_frame.pack(fill=tk.X, pady=5, padx=5)

        nav_btn_frame = ttk.Frame(nav_frame)
        nav_btn_frame.pack(fill=tk.X, padx=5, pady=3)

        self.prev_btn = ttk.Button(
            nav_btn_frame,
            text="← 上一张",
            command=self._go_to_prev_image
        )
        self.prev_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        self.next_btn = ttk.Button(
            nav_btn_frame,
            text="下一张 →",
            command=self._go_to_next_image
        )
        self.next_btn.pack(side=tk.RIGHT, padx=2, fill=tk.X, expand=True)

        # 流程导航按钮 - 固定放在底部
        nav_control_frame = ttk.LabelFrame(control_frame, text="流程导航")
        nav_control_frame.pack(fill=tk.X, pady=5, padx=5)

        nav_control_btn_frame = ttk.Frame(nav_control_frame)
        nav_control_btn_frame.pack(fill=tk.X, padx=5, pady=3)

        ttk.Button(
            nav_control_btn_frame,
            text="← 返回上一步",
            command=self._go_back
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        ttk.Button(
            nav_control_btn_frame,
            text="下一步 →",
            command=self._finish
        ).pack(side=tk.RIGHT, padx=5)
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
    
    def _on_shape_changed(self, *args):
        """裁剪形状改变时自动刷新"""
        self._draw_crop_rect()
        self._update_preview()
    
    def set_images(self, images: tp.List[tp.Dict]):
        """设置要处理的图片"""
        self.images = images
        # 重置素材库（新会话）
        self.cropped_images = []
        # 清除裁剪框状态缓存
        if hasattr(self, '_crop_states'):
            self._crop_states.clear()

        self.current_index = 0
        self._load_current_image()
    
    def _go_to_image(self, index: int):
        """切换到指定索引的图片"""
        if index < 0 or index >= len(self.images):
            return
        
        # 保存当前图片的裁剪框状态
        if self.current_index < len(self.images):
            self._save_crop_state()
        
        self.current_index = index
        self._load_current_image()
    
    def _go_to_prev_image(self):
        """切换到上一张图"""
        if self.current_index > 0:
            self._go_to_image(self.current_index - 1)
    
    def _go_to_next_image(self):
        """切换到下一张图"""
        if self.current_index < len(self.images) - 1:
            self._go_to_image(self.current_index + 1)
    
    def _save_crop_state(self):
        """保存当前裁剪框状态"""
        if not hasattr(self, '_crop_states'):
            self._crop_states = {}
        
        # 保存当前裁剪框的位置和形状
        self._crop_states[self.current_index] = {
            'crop_x1': self.crop_x1,
            'crop_y1': self.crop_y1,
            'crop_x2': self.crop_x2,
            'crop_y2': self.crop_y2,
            'crop_shape': self.crop_shape_var.get()
        }
    
    def _restore_crop_state(self):
        """恢复裁剪框状态"""
        if hasattr(self, '_crop_states') and self.current_index in self._crop_states:
            state = self._crop_states[self.current_index]
            self.crop_x1 = state['crop_x1']
            self.crop_y1 = state['crop_y1']
            self.crop_x2 = state['crop_x2']
            self.crop_y2 = state['crop_y2']
            self.crop_shape_var.set(state['crop_shape'])
            return True
        return False
    
    def _load_current_image(self):
        """加载当前图片"""
        if self.current_index >= len(self.images):
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
        
        # 在画布上显示图片
        self._display_image()
        
        # 更新导航按钮状态
        self._update_nav_buttons()
    
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
        
        # 尝试恢复裁剪框状态，如果没有则初始化
        if not self._restore_crop_state():
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
        
        # 自动刷新预览
        self._update_preview()
    
    def _draw_crop_rect(self):
        """绘制裁剪框"""
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
        # 根据裁剪形状绘制
        if self.crop_shape_var.get() == "circle":
            # 绘制圆形裁剪框
            self.crop_rect = self.canvas.create_oval(
                self.crop_x1, self.crop_y1,
                self.crop_x2, self.crop_y2,
                outline="red",
                width=2,
                dash=(5, 5)
            )
        else:
            # 绘制方形裁剪框
            self.crop_rect = self.canvas.create_rectangle(
                self.crop_x1, self.crop_y1,
                self.crop_x2, self.crop_y2,
                outline="red",
                width=2,
                dash=(5, 5)
            )
    
    def _update_preview(self):
        """更新裁剪预览"""
        if not self.original_image or not self.crop_rect:
            return
        
        try:
            # 计算裁剪区域（转换到原始图片坐标）
            x1 = int((min(self.crop_x1, self.crop_x2) - self.img_offset_x) / self.display_scale)
            y1 = int((min(self.crop_y1, self.crop_y2) - self.img_offset_y) / self.display_scale)
            x2 = int((max(self.crop_x1, self.crop_x2) - self.img_offset_x) / self.display_scale)
            y2 = int((max(self.crop_y1, self.crop_y2) - self.img_offset_y) / self.display_scale)
            
            # 确保正方形
            size = min(x2 - x1, y2 - y1)
            x2, y2 = x1 + size, y1 + size
            
            # 裁剪图片
            cropped = self.original_image.crop((x1, y1, x2, y2))
            
            # 如果是圆形裁剪，应用圆形遮罩
            if self.crop_shape_var.get() == "circle":
                cropped = self._apply_circle_mask(cropped)
            
            # 缩放到预览尺寸
            preview_size = 150
            cropped_preview = cropped.resize((preview_size, preview_size), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.preview_image = ImageTk.PhotoImage(cropped_preview)
            
            # 清空预览画布（填充背景色防止透明像素残留）
            self.preview_canvas.delete("all")
            self.preview_canvas.create_rectangle(
                0, 0, 150, 150,
                fill="#2b2b2b",
                outline=""
            )
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)
            
        except Exception as e:
            print(f"预览更新失败: {e}")
    
    def _apply_circle_mask(self, img: Image.Image) -> Image.Image:
        """应用圆形遮罩（方形外透明）"""
        # 转换为RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        width, height = img.size
        size = min(width, height)
        
        # 创建透明背景
        result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # 创建圆形遮罩
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        # 在中心绘制白色圆形
        left = (width - size) // 2
        top = (height - size) // 2
        draw.ellipse([left, top, left + size, top + size], fill=255)
        
        # 应用遮罩
        result.paste(img, (0, 0), mask)
        
        return result
    
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
        """鼠标释放 - 自动刷新预览"""
        self.is_dragging = False
        self.drag_mode = None
        # 自动刷新预览
        self._update_preview()
    
    def _reset_crop(self):
        """重置裁剪框"""
        self._init_crop_rect()
    
    def _auto_crop(self):
        """自动居中裁剪"""
        self._init_crop_rect()
    
    def _save_crop_to_library(self):
        """保存当前裁切到素材库（可多次裁切同一张图）"""
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

        # 如果是圆形裁剪，应用圆形遮罩
        if self.crop_shape_var.get() == "circle":
            cropped = self._apply_circle_mask(cropped)

        # 创建新的素材项
        img_data = self.images[self.current_index].copy()
        img_data["image"] = cropped
        img_data["width"] = size
        img_data["height"] = size
        img_data["is_square"] = True
        img_data["cropped"] = True
        img_data["crop_index"] = len(self.cropped_images)  # 记录裁切序号

        # 添加到素材库（不是替换，是追加）
        self.cropped_images.append(img_data)

        # 显示状态提示（非弹窗）
        self._show_status(f"✓ 已保存裁切 #{len(self.cropped_images)}")

    def _show_status(self, message: str, duration: int = 2000):
        """显示状态提示（自动消失）"""
        self.status_label.configure(text=message, foreground="green")
        self.after(duration, lambda: self.status_label.configure(text="就绪", foreground="gray"))
    
    def _update_nav_buttons(self):
        """更新导航按钮状态"""
        if hasattr(self, 'prev_btn'):
            self.prev_btn.configure(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        if hasattr(self, 'next_btn'):
            self.next_btn.configure(state=tk.NORMAL if self.current_index < len(self.images) - 1 else tk.DISABLED)
    
    def _go_back(self):
        """返回上一步（第一步）"""
        self.app.show_input_frame()
    
    def _finish(self):
        """完成裁剪，进入生成界面"""
        # 检查是否有已保存的裁切
        if len(self.cropped_images) == 0:
            # 没有裁切，询问是否使用所有原图
            if not messagebox.askyesno(
                "确认",
                "还没有保存任何裁切，\n"
                "是否将所有图片作为素材进入下一步？"
            ):
                return

            # 将所有原图添加到素材库
            for img_data in self.images:
                self.cropped_images.append(img_data.copy())

        self.app.show_generate_frame(self.cropped_images)
