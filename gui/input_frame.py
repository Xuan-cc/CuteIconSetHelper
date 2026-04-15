"""
输入界面 - 支持拖拽图片
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import typing as tp
from PIL import Image
import platform
import os


class InputFrame(ttk.Frame):
    """图片输入界面"""
    
    def __init__(self, parent: ttk.Frame, app, dnd_available: bool = True):
        super().__init__(parent)
        self.app = app
        self.dnd_available = dnd_available
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
        """设置拖拽支持 - 使用更安全的方式"""
        if not self.dnd_available:
            self.drag_hint_label.configure(
                text="请使用'选择图片'按钮导入文件",
                foreground="gray"
            )
            return
        
        system = platform.system()
        
        if system == "Windows":
            self._setup_windows_drag_drop()
        else:
            self.drag_hint_label.configure(
                text="请使用'选择图片'按钮导入文件",
                foreground="gray"
            )
    
    def _setup_windows_drag_drop(self):
        """设置Windows拖拽支持 - 使用tkinterDnD2作为首选"""
        try:
            # 首选：使用tkinterdnd2（更稳定）
            from tkinterdnd2 import DND_FILES, TkinterDnD
            
            # 注册为拖拽目标
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self._on_tkdnd_drop)
            
            self.drag_hint_label.configure(
                text="✓ 拖拽功能已启用 - 支持拖拽图片到上方区域",
                foreground="green"
            )
            return
        except ImportError:
            pass
        
        # 备选：使用windnd（修复线程安全问题）
        try:
            import windnd
            
            # 使用after()将回调调度到主线程，避免Tkinter线程安全问题
            def safe_drop_callback(file_list):
                # 将文件列表保存到实例变量，然后通过after调度到主线程处理
                self._pending_drop_files = file_list
                self.after(1, self._process_pending_drops)
            
            windnd.hook_dropfiles(self.drop_frame, func=safe_drop_callback)
            
            self.drag_hint_label.configure(
                text="✓ 拖拽功能已启用 - 支持拖拽图片到上方区域",
                foreground="green"
            )
        except ImportError:
            self.drag_hint_label.configure(
                text="提示：如需拖拽功能，请运行: pip install tkinterdnd2",
                foreground="orange"
            )
        except Exception as e:
            print(f"设置拖拽失败: {e}")
            self.drag_hint_label.configure(
                text="拖拽功能初始化失败，请使用按钮选择",
                foreground="orange"
            )
    
    def _on_tkdnd_drop(self, event):
        """处理tkinterdnd2拖拽 - 使用after()避免线程问题"""
        try:
            # 获取拖拽的文件路径
            data = event.data
            if not data:
                return
            
            # 解析文件路径
            files = self._parse_drop_data(data)
            
            # 使用after()调度到主线程处理
            for file_path in files:
                if os.path.isfile(file_path):
                    self.after(1, lambda path=file_path: self._add_image(path))
                    
        except Exception as e:
            print(f"处理拖拽失败: {e}")
            # 使用after()显示错误，避免在回调中直接调用messagebox
            self.after(1, lambda msg=str(e): messagebox.showerror("错误", f"处理拖拽文件时出错:\n{msg}"))
    
    def _parse_drop_data(self, data: str) -> tp.List[str]:
        """解析拖拽数据，提取文件路径"""
        files = []
        
        # 处理Windows路径格式
        # 格式可能是: {C:\path\to\file.png} C:\path\to\file2.png
        import re
        
        # 匹配花括号包围的路径和普通路径
        pattern = r'\{([^}]+)\}|([^\s]+)'
        matches = re.findall(pattern, data)
        
        for match in matches:
            path = match[0] or match[1]
            if path:
                # 去除引号
                path = path.strip('"').strip("'")
                # 转换为标准路径
                path = os.path.normpath(path)
                files.append(path)
        
        return files
    
    def _process_pending_drops(self):
        """处理windnd拖拽的文件（在主线程中执行）"""
        if not hasattr(self, '_pending_drop_files') or not self._pending_drop_files:
            return
        
        file_list = self._pending_drop_files
        self._pending_drop_files = []  # 清空待处理列表
        
        try:
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
                file_path = file_path.strip('{}').strip('"')
                # 标准化路径
                file_path = os.path.normpath(file_path)
                
                if os.path.isfile(file_path):
                    self._add_image(file_path)
        except Exception as e:
            print(f"处理拖拽文件错误: {e}")
            messagebox.showerror("错误", f"处理拖拽文件时出错:\n{str(e)}")
    
    def _on_click_select(self, event):
        """点击选择文件"""
        self._select_files()
    
    def _select_files(self):
        """选择图片文件"""
        try:
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
        except Exception as e:
            messagebox.showerror("错误", f"选择文件时出错:\n{str(e)}")
    
    def _add_image(self, file_path: str):
        """添加图片到列表"""
        try:
            file_path = str(file_path)
            
            # 检查是否已经存在
            if file_path in self.image_paths:
                return
            
            # 检查文件类型
            ext = Path(file_path).suffix.lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']:
                return
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return
            
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
            print(f"添加图片错误: {e}")
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
