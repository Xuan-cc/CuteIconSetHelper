"""
输入界面 - 支持拖拽图片
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import typing as tp
from PIL import Image
import platform


class InputFrame(ttk.Frame):
    """图片输入界面"""
    
    def __init__(self, parent: ttk.Frame, app):
        super().__init__(parent)
        self.app = app
        self.image_paths: tp.List[str] = []
        self.images: tp.List[tp.Dict] = []
        
        self._create_widgets()
        self._setup_drag_drop()
    
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
        
        self.drag_hint_label = ttk.Label(
            hint_frame,
            text="支持拖拽图片到下方区域，或点击按钮选择",
            font=("Microsoft YaHei", 9),
            foreground="gray"
        )
        self.drag_hint_label.pack(pady=5)
        
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
        
        # 绑定点击事件
        self.drop_frame.bind("<Button-1>", self._on_click_select)
        self.drop_label.bind("<Button-1>", self._on_click_select)
        
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
    
    def _setup_drag_drop(self):
        """设置拖拽支持"""
        system = platform.system()
        
        if system == "Windows":
            self._setup_windows_drag_drop()
        elif system == "Darwin":  # macOS
            self._setup_macos_drag_drop()
        else:  # Linux
            self._setup_linux_drag_drop()
    
    def _setup_windows_drag_drop(self):
        """设置Windows拖拽支持"""
        try:
            # 尝试使用windnd库
            import windnd
            windnd.hook_dropfiles(self.drop_frame, func=self._on_files_dropped)
            self.drag_hint_label.configure(text="✓ 拖拽功能已启用 - 支持拖拽图片到上方区域")
        except ImportError:
            # 如果windnd不可用，提示用户
            self.drag_hint_label.configure(
                text="提示：如需拖拽功能，请运行: pip install windnd",
                foreground="orange"
            )
    
    def _setup_macos_drag_drop(self):
        """设置macOS拖拽支持"""
        self.drag_hint_label.configure(
            text="macOS: 请使用"选择图片"按钮导入",
            foreground="gray"
        )
    
    def _setup_linux_drag_drop(self):
        """设置Linux拖拽支持"""
        self.drag_hint_label.configure(
            text="Linux: 请使用"选择图片"按钮导入",
            foreground="gray"
        )
    
    def _on_files_dropped(self, file_list):
        """处理拖拽的文件"""
        for file_path in file_list:
            # 处理不同编码
            if isinstance(file_path, bytes):
                try:
                    file_path = file_path.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        file_path = file_path.decode('gbk')
                    except UnicodeDecodeError:
                        file_path = file_path.decode('latin-1')
            
            file_path = str(file_path)
            # 去除可能的花括号
            file_path = file_path.strip('{}')
            
            self._add_image(file_path)
    
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
            
            # 转换为RGBA模式以支持透明通道
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
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
