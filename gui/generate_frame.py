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
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var, width=10)
        size_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="x 256 (像素)").pack(side=tk.LEFT)
        
        # 排布方式
        layout_frame = ttk.Frame(config_frame)
        layout_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(layout_frame, text="排布方式:").pack(side=tk.LEFT)
        self.layout_var = tk.StringVar(value="horizontal")
        layout_combo = ttk.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["horizontal", "vertical", "circular"],
            state="readonly",
            width=15
        )
        layout_combo.pack(side=tk.LEFT, padx=5)
        
        # 显示中文
        self.layout_display = {
            "horizontal": "横排",
            "vertical": "竖排",
            "circular": "圆形排布"
        }
        
        # 绑定选择事件
        layout_combo.bind("<<ComboboxSelected>>", self._on_layout_change)
        
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
        
        # 图片预览
        preview_frame = ttk.LabelFrame(self, text="图片预览")
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
        
        ttk.Button(
            btn_frame,
            text="返回上一步",
            command=self._go_back
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="生成图片",
            command=self._generate_images
        ).pack(side=tk.RIGHT, padx=5)
    
    def set_images(self, images: tp.List[tp.Dict]):
        """设置图片列表"""
        self.images = images
        self._update_preview()
    
    def _update_preview(self):
        """更新图片预览"""
        # 清空预览区域
        for widget in self.preview_inner.winfo_children():
            widget.destroy()
        
        if not self.images:
            return
        
        # 显示所有图片缩略图
        row = 0
        col = 0
        max_cols = 5
        
        for i, img_data in enumerate(self.images):
            # 创建缩略图
            img = img_data["image"].copy()
            img.thumbnail((100, 100))
            
            # 创建标签
            frame = ttk.Frame(self.preview_inner)
            frame.grid(row=row, column=col, padx=5, pady=5)
            
            photo = tk.PhotoImage(data=self._pil_to_tk_data(img))
            lbl = ttk.Label(frame, image=photo)
            lbl.image = photo  # 保持引用
            lbl.pack()
            
            ttk.Label(
                frame,
                text=f"#{i+1}\n{img_data['width']}x{img_data['height']}",
                font=("Microsoft YaHei", 8)
            ).pack()
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
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
    
    def _on_layout_change(self, event=None):
        """排布方式改变"""
        pass  # 可以在这里添加预览更新
    
    def _browse_dir(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.dir_var.set(dir_path)
            self.output_dir = dir_path
    
    def _go_back(self):
        """返回上一步"""
        self.app.show_input_frame()
    
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
        
        layout = self.layout_var.get()
        
        # 开始生成
        self.status_label.configure(text="正在生成图片...")
        self.progress_var.set(0)
        self.update_idletasks()
        
        try:
            self._do_generate(tile_size, layout, output_dir)
            self.status_label.configure(text="生成完成！")
            self.progress_var.set(100)
            
            # 询问是否打开输出目录
            if messagebox.askyesno("完成", f"图片已生成到:\n{output_dir}\n\n是否打开输出目录？"):
                import subprocess
                subprocess.run(["explorer", output_dir])
                
        except Exception as e:
            self.status_label.configure(text=f"生成失败: {str(e)}")
            messagebox.showerror("错误", f"生成图片时出错:\n{str(e)}")
    
    def _do_generate(self, tile_size: int, layout: str, output_dir: str):
        """执行生成"""
        processor = ImageProcessor()
        layout_engine = LayoutEngine()
        
        n = len(self.images)
        total_tasks = n + self._count_combinations(n, 2) + (1 if n >= 3 else 0)
        completed = 0
        
        # 1. 生成单张图片
        for i, img_data in enumerate(self.images):
            img = processor.resize_image(img_data["image"], tile_size, tile_size)
            output_path = os.path.join(output_dir, f"{i+1}.png")
            img.save(output_path, "PNG")
            
            completed += 1
            self.progress_var.set(completed / total_tasks * 100)
            self.update_idletasks()
        
        # 2. 生成两张组合
        if n >= 2:
            indices = list(range(n))
            for combo in itertools.combinations(indices, 2):
                idx1, idx2 = combo
                img1 = processor.resize_image(self.images[idx1]["image"], tile_size, tile_size)
                img2 = processor.resize_image(self.images[idx2]["image"], tile_size, tile_size)
                
                if layout == "horizontal":
                    result = layout_engine.horizontal_layout([img1, img2])
                    output_path = os.path.join(output_dir, f"{idx1+1}{idx2+1}_h.png")
                elif layout == "vertical":
                    result = layout_engine.vertical_layout([img1, img2])
                    output_path = os.path.join(output_dir, f"{idx1+1}{idx2+1}_v.png")
                else:  # circular
                    result = layout_engine.circular_layout([img1, img2])
                    output_path = os.path.join(output_dir, f"{idx1+1}{idx2+1}_c.png")
                
                result.save(output_path, "PNG")
                
                completed += 1
                self.progress_var.set(completed / total_tasks * 100)
                self.update_idletasks()
        
        # 3. 生成全部组合
        if n >= 3:
            all_images = [
                processor.resize_image(img_data["image"], tile_size, tile_size)
                for img_data in self.images
            ]
            
            if layout == "horizontal":
                result = layout_engine.horizontal_layout(all_images)
                output_path = os.path.join(output_dir, f"all_h.png")
            elif layout == "vertical":
                result = layout_engine.vertical_layout(all_images)
                output_path = os.path.join(output_dir, f"all_v.png")
            else:  # circular
                result = layout_engine.circular_layout(all_images)
                output_path = os.path.join(output_dir, f"all_c.png")
            
            result.save(output_path, "PNG")
            
            completed += 1
            self.progress_var.set(completed / total_tasks * 100)
            self.update_idletasks()
    
    def _count_combinations(self, n: int, k: int) -> int:
        """计算组合数 C(n,k)"""
        if n < k:
            return 0
        import math
        return math.comb(n, k)
