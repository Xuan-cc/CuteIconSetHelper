"""
图片组合工具 - 主入口
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 尝试导入tkinterdnd2，如果失败则使用标准tkinter
try:
    from tkinterdnd2 import TkinterDnD
    root = TkinterDnD.Tk()  # 使用DnD支持的root窗口
    dnd_available = True
except ImportError:
    import tkinter as tk
    root = tk.Tk()  # 使用标准root窗口
    dnd_available = False

from gui.app import ImageComposerApp

if __name__ == "__main__":
    app = ImageComposerApp(root, dnd_available=dnd_available)
    root.mainloop()
