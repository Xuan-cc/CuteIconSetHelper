"""
生成界面 - 配置输出选项并生成图片（完整版）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import typing as tp
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
        self.image_names: tp.List[str] = []
        self.selected_images: tp.List[bool] = []  # 选中状态
        self.card_frames: tp.List[ttk.Frame] = []
        self.name_entries: tp.List[tk.StringVar] = []
        self.select_indicators: tp.List[tk.Label] = []  # 选中状态指示器
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        ttk.Label(
            self,
            text="生成配置",
            font=("Microsoft YaHei", 12, "bold")
        ).pack(pady=5)
        
        # 配置区域
        config_frame = ttk.LabelFrame(self, text="输出设置")
        config_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 图片尺寸
        size_frame = ttk.Frame(config_frame)
        size_frame.pack(fill=tk.X, padx=10, pady=3)
        
        ttk.Label(size_frame, text="输出图片尺寸:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="256")
        self.size_var.trace_add('write', self._on_size_changed)
        size_entry = ttk.Entry(size_frame, textvariable=self.size_var, width=10)
        size_entry.pack(side=tk.LEFT, padx=5)
        self.size_label = ttk.Label(size_frame, text="x 256 (像素)")
        self.size_label.pack(side=tk.LEFT)
        
        # 排布方式
        layout_frame = ttk.Frame(config_frame)
        layout_frame.pack(fill=tk.X, padx=10, pady=3)
        
        ttk.Label(layout_frame, text="排布方式:").pack(side=tk.LEFT)
        
        self.layout_display = {
            "横排": "horizontal",
            "竖排": "vertical",
            "圆形排布": "circular"
        }
        
        self.layout_var = tk.StringVar(value="横排")
        layout_combo = ttk.Combobox(
            layout_frame,
            textvariable=self.layout_var,
            values=["横排", "竖排", "圆形排布"],
            state="readonly",
            width=15
        )
        layout_combo.pack(side=tk.LEFT, padx=5)
        
        # 最大组合图数
        max_combo_frame = ttk.Frame(config_frame)
        max_combo_frame.pack(fill=tk.X, padx=10, pady=3)
        
        ttk.Label(max_combo_frame, text="最大组合图数:").pack(side=tk.LEFT)
        self.max_combo_var = tk.StringVar(value="0")
        max_combo_entry = ttk.Entry(max_combo_frame, textvariable=self.max_combo_var, width=10)
        max_combo_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(max_combo_frame, text="(0=无限制, 必须≤选中素材数)", 
                 font=("Microsoft YaHei", 8), foreground="gray").pack(side=tk.LEFT)
        
        # 全体都有选项
        all_together_frame = ttk.Frame(config_frame)
        all_together_frame.pack(fill=tk.X, padx=10, pady=3)
        
        self.all_together_var = tk.BooleanVar(value=True)
        all_together_check = ttk.Checkbutton(
            all_together_frame, 
            text="全体都有（额外输出所有选中素材组合到一起的结果）",
            variable=self.all_together_var
        )
        all_together_check.pack(anchor=tk.W)
        
        # 输出目录
        dir_frame = ttk.Frame(config_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=3)
        
        ttk.Label(dir_frame, text="输出目录:").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            dir_frame,
            text="浏览",
            command=self._browse_dir
        ).pack(side=tk.LEFT, padx=5)
        
        # 提示信息
        hint_frame = ttk.Frame(self)
        hint_frame.pack(fill=tk.X, padx=20, pady=2)
        
        self.selected_count_label = ttk.Label(
            hint_frame,
            text="已选中 0 个素材（点击卡片选中/取消）",
            font=("Microsoft YaHei", 9),
            foreground="blue"
        )
        self.selected_count_label.pack(side=tk.LEFT)
        
        ttk.Button(
            hint_frame,
            text="全选",
            command=self._select_all
        ).pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(
            hint_frame,
            text="取消全选",
            command=self._deselect_all
        ).pack(side=tk.RIGHT, padx=2)
        
        # 已有素材预览（卡片格式）- 使用固定高度而非expand
        preview_frame = ttk.LabelFrame(self, text="选择要使用的素材（点击卡片选中）")
        preview_frame.pack(fill=tk.X, padx=20, pady=5)
        preview_frame.pack_propagate(False)
        preview_frame.configure(height=240)  # 限制预览区域高度
        
        # 创建Canvas和滚动条
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cards_canvas = tk.Canvas(canvas_frame, bg="#f0f0f0")
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.cards_canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.cards_canvas.yview)
        self.cards_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 卡片容器
        self.cards_frame = ttk.Frame(self.cards_canvas)
        self.cards_canvas_window = self.cards_canvas.create_window((0, 0), window=self.cards_frame, anchor=tk.NW)
        
        self.cards_frame.bind("<Configure>", self._on_cards_frame_configure)
        self.cards_canvas.bind("<Configure>", self._on_canvas_configure)

        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10, padx=20)

        # 返回上一步按钮
        ttk.Button(
            btn_frame,
            text="返回上一步",
            command=self._go_back
        ).pack(side=tk.LEFT, padx=5)

        # 生成输出按钮
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

    def _go_back(self):
        """返回上一步（裁剪界面）"""
        self.app.go_back_to_crop()
    
    def _on_cards_frame_configure(self, event=None):
        """卡片框架大小改变时更新滚动区域"""
        self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        """画布大小改变时更新窗口大小"""
        self.cards_canvas.itemconfig(self.cards_canvas_window, width=event.width)
    
    def _on_size_changed(self, *args):
        """尺寸变化时同步更新标签"""
        try:
            size = int(self.size_var.get())
            self.size_label.configure(text=f"x {size} (像素)")
        except ValueError:
            pass
    
    def _select_all(self):
        """全选所有图片"""
        for i in range(len(self.selected_images)):
            self.selected_images[i] = True
        self._update_card_styles()
        self._update_selected_count()
    
    def _deselect_all(self):
        """取消全选"""
        for i in range(len(self.selected_images)):
            self.selected_images[i] = False
        self._update_card_styles()
        self._update_selected_count()
    
    def _toggle_card_selection(self, index):
        """切换卡片选中状态"""
        self.selected_images[index] = not self.selected_images[index]
        self._update_card_styles()
        self._update_selected_count()
    
    def _update_card_styles(self):
        """更新卡片样式"""
        for i, frame in enumerate(self.card_frames):
            if i < len(self.selected_images):
                # 查找内部框架
                inner = None
                for child in frame.winfo_children():
                    if isinstance(child, tk.Frame):
                        inner = child
                        break
                if inner:
                    if self.selected_images[i]:
                        frame.configure(style="Selected.TFrame")
                        inner.configure(bg="#e3f2fd")
                        for widget in inner.winfo_children():
                            if isinstance(widget, (tk.Label, tk.Frame)):
                                widget.configure(bg="#e3f2fd")
                    else:
                        frame.configure(style="Card.TFrame")
                        inner.configure(bg="white")
                        for widget in inner.winfo_children():
                            if isinstance(widget, (tk.Label, tk.Frame)):
                                widget.configure(bg="white")
                
                # 更新选中状态指示器
                if i < len(self.select_indicators):
                    select_text = "✓ 已选中" if self.selected_images[i] else "× 未选中"
                    select_fg = "green" if self.selected_images[i] else "gray"
                    self.select_indicators[i].configure(text=select_text, fg=select_fg)
    
    def _update_selected_count(self):
        """更新选中数量显示"""
        count = sum(self.selected_images)
        self.selected_count_label.configure(text=f"已选中 {count} 个素材（点击卡片选中/取消）")
    
    def set_images(self, images: tp.List[tp.Dict]):
        """设置图片列表"""
        self.images = images
        # 初始化图片名称（默认使用序号）
        if not self.image_names or len(self.image_names) != len(images):
            self.image_names = [f"{i+1}" for i in range(len(images))]
        # 初始化选择状态（默认全选）
        if not self.selected_images or len(self.selected_images) != len(images):
            self.selected_images = [True] * len(images)
        self._update_preview()
    
    def _update_preview(self):
        """更新图片预览（卡片格式）"""
        # 清空现有卡片
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        self.card_frames.clear()
        self.name_entries.clear()
        self.select_indicators.clear()
        
        if not self.images:
            return
        
        # 创建卡片样式
        style = ttk.Style()
        style.configure("Card.TFrame", background="white")
        style.configure("Selected.TFrame", background="#e3f2fd")
        
        # 每行显示5个卡片
        cards_per_row = 5
        
        for i, img_data in enumerate(self.images):
            # 计算行列
            row = i // cards_per_row
            col = i % cards_per_row
            
            # 创建卡片框架 - 减小尺寸以适应更小的预览区域
            bg_color = "#e3f2fd" if self.selected_images[i] else "white"
            card = ttk.Frame(
                self.cards_frame, 
                style="Selected.TFrame" if self.selected_images[i] else "Card.TFrame",
                width=140, 
                height=180
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            
            # 绑定点击事件
            card.bind("<Button-1>", lambda e, idx=i: self._toggle_card_selection(idx))
            
            # 内部框架
            inner_frame = tk.Frame(card, bg=bg_color, width=130, height=170)
            inner_frame.place(relx=0.5, rely=0.5, anchor="center")
            inner_frame.bind("<Button-1>", lambda e, idx=i: self._toggle_card_selection(idx))
            
            # 图片缩略图 - 减小尺寸
            img = img_data["image"].copy()
            img.thumbnail((80, 80))
            
            photo = tk.PhotoImage(data=self._pil_to_tk_data(img))
            lbl = tk.Label(inner_frame, image=photo, bg=bg_color)
            lbl.image = photo
            lbl.pack(pady=5)
            lbl.bind("<Button-1>", lambda e, idx=i: self._toggle_card_selection(idx))
            
            # 名称输入框
            name_frame = tk.Frame(inner_frame, bg=bg_color)
            name_frame.pack(fill=tk.X, padx=5, pady=2)
            
            tk.Label(name_frame, text="名称:", font=("Microsoft YaHei", 8), bg=bg_color).pack(side=tk.LEFT)
            name_var = tk.StringVar(value=self.image_names[i])
            name_entry = tk.Entry(name_frame, textvariable=name_var, width=12, font=("Microsoft YaHei", 8))
            name_entry.pack(side=tk.LEFT, padx=2)
            
            # 保存引用
            self.name_entries.append(name_var)
            
            # 尺寸信息
            info_lbl = tk.Label(
                inner_frame,
                text=f"{img_data['width']}x{img_data['height']}",
                font=("Microsoft YaHei", 8),
                fg="gray",
                bg=bg_color
            )
            info_lbl.pack(pady=2)
            info_lbl.bind("<Button-1>", lambda e, idx=i: self._toggle_card_selection(idx))
            
            # 选中状态指示器
            select_text = "✓ 已选中" if self.selected_images[i] else "× 未选中"
            select_fg = "green" if self.selected_images[i] else "gray"
            select_indicator = tk.Label(
                inner_frame,
                text=select_text,
                font=("Microsoft YaHei", 8, "bold"),
                fg=select_fg,
                bg=bg_color
            )
            select_indicator.pack(pady=2)
            select_indicator.bind("<Button-1>", lambda e, idx=i: self._toggle_card_selection(idx))
            
            self.card_frames.append(card)
            self.select_indicators.append(select_indicator)
        
        # 更新选中计数
        self._update_selected_count()
        
        # 更新滚动区域
        self.cards_frame.update_idletasks()
        self._on_cards_frame_configure()
    
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
        
        # 获取选中的图片
        selected_indices = [i for i, selected in enumerate(self.selected_images) if selected]
        
        if not selected_indices:
            messagebox.showwarning("提示", "请至少选择一张图片")
            return
        
        # 验证最大组合图数
        try:
            max_combo = int(self.max_combo_var.get())
            if max_combo < 0:
                messagebox.showwarning("提示", "最大组合图数不能为负数")
                return
            if max_combo > len(selected_indices):
                messagebox.showwarning("提示", f"最大组合图数({max_combo})不能大于选中素材数({len(selected_indices)})")
                return
        except ValueError:
            messagebox.showwarning("提示", "最大组合图数请输入有效数字")
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
        
        # 获取用户定义的图片名称（仅选中的）
        image_names = []
        for i in selected_indices:
            if i < len(self.name_entries):
                name = self.name_entries[i].get().strip()
                image_names.append(name if name else f"{i+1}")
            else:
                image_names.append(f"{i+1}")
        
        # 获取选中的图片数据
        selected_images = [self.images[i] for i in selected_indices]
        
        # 开始生成
        self.status_label.configure(text=f"正在生成图片（使用{len(selected_images)}张素材）...")
        self.progress_var.set(0)
        self.update_idletasks()
        
        try:
            self._do_generate(tile_size, layout, output_dir, image_names, selected_images, max_combo)
            self.status_label.configure(text="生成完成！")
            self.progress_var.set(100)
            
            # 询问是否打开输出目录
            if messagebox.askyesno("完成", f"图片已生成到:\n{output_dir}\n\n是否打开输出目录？"):
                import subprocess
                actual_output_dir = os.path.normpath(output_dir)
                if os.path.exists(actual_output_dir):
                    subprocess.run(["explorer", actual_output_dir])
                else:
                    messagebox.showwarning("提示", f"目录不存在: {actual_output_dir}")
                
        except Exception as e:
            self.status_label.configure(text=f"生成失败: {str(e)}")
            messagebox.showerror("错误", f"生成图片时出错:\n{str(e)}")
    
    def _do_generate(self, tile_size: int, layout: str, output_dir: str, 
                    image_names: tp.List[str], selected_images: tp.List[tp.Dict], max_combo: int):
        """执行生成 - 支持最大组合数限制"""
        processor = ImageProcessor()
        layout_engine = LayoutEngine()
        
        n = len(selected_images)
        
        # 确定实际的最大组合数
        actual_max_combo = max_combo if max_combo > 0 else n
        actual_max_combo = min(actual_max_combo, n)
        
        # 计算总任务数
        total_tasks = sum(self._count_combinations(n, k) for k in range(1, actual_max_combo + 1))
        
        # 如果勾选了"全体都有"，额外加1
        if self.all_together_var.get():
            total_tasks += 1
        
        completed = 0
        
        # 1. 生成单张图片 (k=1)
        for i, img_data in enumerate(selected_images):
            img = processor.resize_image(img_data["image"], tile_size, tile_size)
            output_path = os.path.join(output_dir, f"{image_names[i]}.png")
            img.save(output_path, "PNG")
            
            completed += 1
            self.progress_var.set(completed / total_tasks * 100)
            self.update_idletasks()
        
        # 2. 生成组合 (k=2 到 k=actual_max_combo)
        for k in range(2, actual_max_combo + 1):
            indices_list = list(range(n))
            for combo_indices in itertools.combinations(indices_list, k):
                # 获取组合中的图片
                combo_images = [
                    processor.resize_image(selected_images[idx]["image"], tile_size, tile_size)
                    for idx in combo_indices
                ]
                
                # 生成组合名称（用英文x连接）
                combo_name = "x".join(image_names[idx] for idx in combo_indices)
                
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
        
        # 3. 如果勾选了"全体都有"，生成所有选中素材的组合
        if self.all_together_var.get():
            all_images = [
                processor.resize_image(img_data["image"], tile_size, tile_size)
                for img_data in selected_images
            ]
            
            combo_name = "x".join(image_names)
            
            if layout == "horizontal":
                result = layout_engine.horizontal_layout(all_images)
                suffix = "_h"
            elif layout == "vertical":
                result = layout_engine.vertical_layout(all_images)
                suffix = "_v"
            else:  # circular
                result = layout_engine.circular_layout(all_images)
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
