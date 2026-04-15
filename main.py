"""
图片组合工具 - 主入口
"""
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from gui.app import ImageComposerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageComposerApp(root)
    root.mainloop()
