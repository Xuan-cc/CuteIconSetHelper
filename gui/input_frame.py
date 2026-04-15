"""
输入界面 - 支持拖拽图片
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import typing as tp
from PIL import Image
import tkinter.dnd as dnd


class InputFrame(ttk.Frame):
    """图片输入界面"""
    
    def __init__(self, parent: ttk.Frame, app):
        super().__init__(parent)
        self.app = app
        self.image_paths: tp.List[str] = []
        self.images: tp.List[tp.Dict] = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 提示信息
        hint_frame = ttk.Frame(self)
        hint_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(
            hint_frame, 
            text="请导入需要处理的图片",
            font=("Microsoft YaHei", 12)
        ).pack(pady=5)
        
        ttk.Label(
            hint_frame,
            text="支持拖拽图片到下方区域，或点击按钮选择",
            font=("Microsoft YaHei", 9),
            foreground="gray"
        ).pack(pady=5)
        
        # 拖拽区域
        self.drop_frame = tk.Frame(
            self, 
            relief=tk.RIDGE, 
            borderwidth=2,
            bg="#f0f0f0",
            highlightbackground="#cccccc",
            highlightthickness=1
        )
        self.drop_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 拖拽提示
        self.drop_label = tk.Label(
            self.drop_frame,
            text="将图片拖拽到此处\n或点击选择文件",
            font=("Microsoft YaHei", 14),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.drop_label.pack(expand=True)
        
        # 绑定拖拽事件
        self.drop_frame.bind("<Enter>", self._on_drag_enter)
        self.drop_frame.bind("<Leave>", self._on_drag_leave)
        self.drop_frame.bind("<Button-1>", self._on_click_select)
        self.drop_label.bind("<Button-1>", self._on_click_select)
        
        # Windows 拖拽支持
        self.drop_frame.bind("<B1-Motion>", self._on_drag_motion)
        self._setup_windows_drop()
        
        # 图片列表区域
        list_frame = ttk.LabelFrame(self, text="已导入的图片")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 滚动条和列表
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Microsoft YaHei", 10),
            selectmode=tk.SINGLE
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.listbox.yview)
        
        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            btn_frame,
            text="选择图片",
            command=self._select_files
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="清空列表",
            command=self._clear_list
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="下一步",
            command=self._go_next
        ).pack(side=tk.RIGHT, padx=10)
    
    def _setup_windows_drop(self):
        """设置Windows拖拽支持"""
        try:
            import windnd
            windnd.hook_dropfiles(
                self.drop_frame,
                func=self._on_windows_drop
            )
        except ImportError:
            # 如果没有windnd，尝试使用TkinterDnD2
            try:
                from TkinterDnD2 import TkinterDnD, DND_FILES
                self.drop_frame.drop_target_register(DND_FILES)
                self.drop_frame.dnd_bind('<<Drop>>', self._on_tkdnd_drop)
            except ImportError:
                pass  # 拖拽功能不可用
    
    def _on_drag_enter(self, event):
        """拖拽进入"""
        self.drop_frame.configure(bg="#e0e8ff")
        self.drop_label.configure(bg="#e0e8ff")
    
    def _on_drag_leave(self, event):
        """拖拽离开"""
        self.drop_frame.configure(bg="#f0f0f0")
        self.drop_label.configure(bg="#f0f0f0")
    
    def _on_drag_motion(self, event):
        """拖拽移动"""
        pass
    
    def _on_windows_drop(self, file_list):
        """Windows拖拽文件"""
        for file_path in file_list:
            file_path = file_path.decode('gbk') if isinstance(file_path, bytes) else file_path
            self._add_image(file_path)
    
    def _on_tkdnd_drop(self, event):
        """TkinterDnD拖拽"""
        files = event.data
        if files:
            # 解析拖拽的文件路径
            import re
            paths = re.findall(r'\{([^}]+)\}|(\S+)', files)
            for match in paths:
                path = match[0] or match[1]
                if path:
                    self._add_image(path)
    
    def _on_click_select(self, event):
        """点击选择文件"""
        self._select_files()
    
    def _select_files(self):
        """选择图片文件"""
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        for file_path in files:
            self._add_image(file_path)
    
    def _add_image(self, file_path: str):
        """添加图片到列表"""
        file_path = str(file_path)
        
        # 检查是否已经存在
        if file_path in self.image_paths:
            return
        
        # 检查文件类型
        ext = Path(file_path).suffix.lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']:
            return
        
        try:
            # 加载图片并检查尺寸
            img = Image.open(file_path)
            width, height = img.size
            
            # 存储图片信息
            image_info = {
                "path": file_path,
                "image": img,
                "width": width,
                "height": height,
                "is_square": width == height,
                "cropped": width == height
            }
            
            self.images.append(image_info)
            self.image_paths.append(file_path)
            
            # 更新列表显示
            display_text = f"{Path(file_path).name} ({width}x{height})"
            if width != height:
                display_text += " [需要裁剪]"
            self.listbox.insert(tk.END, display_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片:\n{file_path}\n\n{str(e)}")
    
    def _clear_list(self):
        """清空列表"""
        self.image_paths.clear()
        self.images.clear()
        self.listbox.delete(0, tk.END)
    
    def _go_next(self):
        """进入下一步"""
        if not self.images:
            messagebox.showwarning("提示", "请先导入至少一张图片")
            return
        
        # 进入裁剪界面
        self.app.show_crop_frame(self.images)
