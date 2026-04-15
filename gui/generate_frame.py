"""
生成界面 - 配置输出选项并生成图片
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import typing as tp
from pathlib import Path
import itertools
import os

from core.image_processor import ImageProcessor
from core.layout_engine import LayoutEngine


class GenerateFrame(ttk.Frame):
    """图片生成界面"""
    
    def __init__(self, parent: ttk.Frame, app):
        super().__init__(parent)
        self.app = app
        self.images: tp.List[tp.Dict] = []
        self.output_dir = ""
        self.image_names: tp.List[str] = []  # 存储用户定义的图片名称
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        ttk.Label(
            self,
            text="生成配置",
            font=("Microsoft YaHei", 12, "bold")
        ).pack(pady=10)
        
        # 配置区域
        config_frame = ttk.LabelFrame(self, text="输出设置")
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 图片尺寸
        size_frame = ttk.Frame(config_frame)
        size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(size_frame, text="输出图片尺寸:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="256")
        self.size_var.trace_add('write', self._on_size_changed)  # 监听变化
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var, width=10)
        size_entry.pack(side=tk.LEFT, padx=5)
        self.size_label = ttk.Label(size_frame, text="x 256 (像素)")
        self.size_label.pack(side=tk.LEFT)
        
        # 排布方式 - 使用中文
        layout_frame = ttk.Frame(config_frame)
        layout_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(layout_frame, text="排布方式:").pack(side=tk.LEFT)
        
        # 中文显示映射
        self.layout_display = {
            "横排": "horizontal",
            "竖排": "vertical",
            "圆形排布": "circular"
        }
        self.layout_reverse = {v: k for k, v in self.layout_display.items()}
        
        self.layout_var = tk.StringVar(value="横排")
        layout_combo = ttk.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["横排", "竖排", "圆形排布"],
            state="readonly",
            width=15
        )
        layout_combo.pack(side=tk.LEFT, padx=5)
        
        # 输出目录
        dir_frame = ttk.Frame(config_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dir_frame, text="输出目录:").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            dir_frame,
            text="浏览",
            command=self._browse_dir
        ).pack(side=tk.LEFT, padx=5)
        
        # 已有素材预览（原名：图片预览）
        preview_frame = ttk.LabelFrame(self, text="已有素材预览（可编辑名称）")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 滚动区域
        self.canvas = tk.Canvas(
            preview_frame,
            bg="#f0f0f0"
        )
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 预览内容框架
        self.preview_inner = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.preview_inner, anchor=tk.NW)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)
        
        self.status_label = ttk.Label(self, text="准备就绪")
        self.status_label.pack(pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=20, padx=20)
        
        # 生成输出按钮（更明显）
        generate_btn = tk.Button(
            btn_frame,
            text="生成输出",
            command=self._generate_images,
            bg="#4CAF50",
            fg="white",
            font=("Microsoft YaHei", 10, "bold"),
            padx=20,
            pady=5
        )
        generate_btn.pack(side=tk.RIGHT, padx=5)
    
    def _on_size_changed(self, *args):
        """尺寸变化时同步更新标签"""
        try:
            size = int(self.size_var.get())
            self.size_label.configure(text=f"x {size} (像素)")
        except ValueError:
            pass
    
    def set_images(self, images: tp.List[tp.Dict]):
        """设置图片列表"""
        self.images = images
        # 初始化图片名称（默认使用序号）
        if not self.image_names or len(self.image_names) != len(images):
            self.image_names = [f"{i+1}" for i in range(len(images))]
        self._update_preview()
    
    def _update_preview(self):
        """更新图片预览（支持重命名）"""
        # 清空预览区域
        for widget in self.preview_inner.winfo_children():
            widget.destroy()
        
        if not self.images:
            return
        
        # 存储名称输入框的引用
        self.name_entries = []
        
        # 显示所有图片缩略图
        for i, img_data in enumerate(self.images):
            # 创建框架
            frame = ttk.Frame(self.preview_inner)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # 图片缩略图
            img = img_data["image"].copy()
            img.thumbnail((80, 80))
            
            photo = tk.PhotoImage(data=self._pil_to_tk_data(img))
            lbl = ttk.Label(frame, image=photo)
            lbl.image = photo  # 保持引用
            lbl.pack(side=tk.LEFT, padx=5)
            
            # 信息区域
            info_frame = ttk.Frame(frame)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            # 名称输入框
            name_frame = ttk.Frame(info_frame)
            name_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(name_frame, text="名称:").pack(side=tk.LEFT)
            name_var = tk.StringVar(value=self.image_names[i])
            name_entry = ttk.Entry(name_frame, textvariable=name_var, width=20)
            name_entry.pack(side=tk.LEFT, padx=5)
            
            # 保存引用以便后续获取
            self.name_entries.append(name_var)
            
            # 尺寸信息
            ttk.Label(
                info_frame,
                text=f"尺寸: {img_data['width']}x{img_data['height']}",
                font=("Microsoft YaHei", 8)
            ).pack(anchor=tk.W)
        
        # 更新滚动区域
        self.preview_inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _pil_to_tk_data(self, img: Image.Image) -> bytes:
        """将PIL图片转换为Tk可用数据"""
        import io
        img_rgb = img.convert("RGBA")
        buffer = io.BytesIO()
        img_rgb.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def _browse_dir(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.dir_var.set(dir_path)
            self.output_dir = dir_path
    
    def _generate_images(self):
        """生成图片"""
        # 验证
        if not self.images:
            messagebox.showwarning("提示", "没有可生成的图片")
            return
        
        output_dir = self.dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning("提示", "请选择输出目录")
            return
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录:\n{str(e)}")
                return
        
        # 获取参数
        try:
            tile_size = int(self.size_var.get())
            if tile_size < 32 or tile_size > 2048:
                messagebox.showwarning("提示", "图片尺寸应在32-2048之间")
                return
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的数字")
            return
        
        # 获取排布方式（转换为英文）
        layout_cn = self.layout_var.get()
        layout = self.layout_display.get(layout_cn, "horizontal")
        
        # 获取用户定义的图片名称
        image_names = [var.get() if var.get().strip() else f"{i+1}" 
                      for i, var in enumerate(self.name_entries)]
        
        # 开始生成
        self.status_label.configure(text="正在生成图片...")
        self.progress_var.set(0)
        self.update_idletasks()
        
        try:
            self._do_generate(tile_size, layout, output_dir, image_names)
            self.status_label.configure(text="生成完成！")
            self.progress_var.set(100)
            
            # 询问是否打开输出目录
            if messagebox.askyesno("完成", f"图片已生成到:\n{output_dir}\n\n是否打开输出目录？"):
                import subprocess
                # 使用实际输出目录
                actual_output_dir = os.path.normpath(output_dir)
                if os.path.exists(actual_output_dir):
                    subprocess.run(["explorer", actual_output_dir])
                else:
                    messagebox.showwarning("提示", f"目录不存在: {actual_output_dir}")
                
        except Exception as e:
            self.status_label.configure(text=f"生成失败: {str(e)}")
            messagebox.showerror("错误", f"生成图片时出错:\n{str(e)}")
    
    def _do_generate(self, tile_size: int, layout: str, output_dir: str, image_names: tp.List[str]):
        """执行生成 - 支持所有组合"""
        processor = ImageProcessor()
        layout_engine = LayoutEngine()
        
        n = len(self.images)
        
        # 计算总任务数：所有可能的组合
        # 1张图: C(n,1) = n
        # 2张图: C(n,2) 
        # 3张图: C(n,3)
        # ...
        # n张图: C(n,n) = 1
        total_tasks = sum(self._count_combinations(n, k) for k in range(1, n+1))
        completed = 0
        
        # 1. 生成单张图片 (k=1)
        for i, img_data in enumerate(self.images):
            img = processor.resize_image(img_data["image"], tile_size, tile_size)
            # 使用用户定义的名称
            output_path = os.path.join(output_dir, f"{image_names[i]}.png")
            img.save(output_path, "PNG")
            
            completed += 1
            self.progress_var.set(completed / total_tasks * 100)
            self.update_idletasks()
        
        # 2. 生成所有组合 (k=2 到 k=n)
        for k in range(2, n + 1):
            indices_list = list(range(n))
            for combo_indices in itertools.combinations(indices_list, k):
                # 获取组合中的图片
                combo_images = [
                    processor.resize_image(self.images[idx]["image"], tile_size, tile_size)
                    for idx in combo_indices
                ]
                
                # 生成组合名称（使用用户定义的名字）
                combo_name = "".join(image_names[idx] for idx in combo_indices)
                
                # 根据排布方式生成
                if layout == "horizontal":
                    result = layout_engine.horizontal_layout(combo_images)
                    suffix = "_h"
                elif layout == "vertical":
                    result = layout_engine.vertical_layout(combo_images)
                    suffix = "_v"
                else:  # circular
                    result = layout_engine.circular_layout(combo_images)
                    suffix = "_c"
                
                output_path = os.path.join(output_dir, f"{combo_name}{suffix}.png")
                result.save(output_path, "PNG")
                
                completed += 1
                self.progress_var.set(completed / total_tasks * 100)
                self.update_idletasks()
    
    def _count_combinations(self, n: int, k: int) -> int:
        """计算组合数 C(n,k)"""
        if n < k or k < 0:
            return 0
        import math
        return math.comb(n, k)
