# CuteIconSetHelper - 图片组合工具

一个支持拖拽、裁剪、多种排布方式的图片处理工具，专为制作图标组合而生。

[![GitHub](https://img.shields.io/badge/GitHub-CuteIconSetHelper-blue)](https://github.com/Xuan-cc/CuteIconSetHelper)
[![VibeCoding](https://img.shields.io/badge/Built%20with-VibeCoding-orange)](https://en.wikipedia.org/wiki/Vibe_coding)
[![AI Assisted](https://img.shields.io/badge/AI%20Assisted-Claude%20%7C%20Sisyphus-purple)]()

> 🤖 **AI 生成提示**: 本项目完全使用 AI（Claude + Sisyphus Agent）通过 VibeCoding 方式开发
> 
> 💡 **VibeCoding 提示**: 如果你也想用 AI 开发类似项目，可以尝试描述你的需求给 AI，让它帮你实现功能

## ✨ 功能特性

### 1. 图片导入
- 📁 **文件选择**：支持多文件批量选择
- 🖱️ **拖拽导入**：直接拖拽图片到窗口（支持 tkinterdnd2）
- 📋 **路径粘贴**：支持粘贴图片路径
- 🖼️ **格式支持**：PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP

### 2. 智能裁剪
- 📐 **1:1 比例裁剪**：保持正方形比例
- 🔲 **方形/圆形切换**：支持方形和圆形裁剪
- ✋ **可拖动裁剪框**：框内拖动移动，框外拖动重绘
- 👁️ **实时预览**：150x150 预览窗口实时显示效果
- 🔄 **应用并再裁一张**：支持从同一张大图裁剪多个区域

### 3. 灵活配置
- 📏 **自定义尺寸**：默认 256x256，可自由调整
- 🎨 **三种排布方式**：
  - **横排**：水平拼接
  - **竖排**：垂直拼接
  - **圆形**：正多边形环形排列，底边水平
- 🔢 **最大组合图数**：限制组合数量（0 = 无限制）
- ✅ **全体都有**：额外输出所有选中素材的组合

### 4. 素材管理
- 🎴 **卡片式预览**：每行 5 个卡片，直观展示
- ☑️ **点击选中/取消**：点击卡片切换选择状态
- 📝 **自定义名称**：每个素材可设置独立名称
- 🔤 **名称连接**：组合文件名使用 "x" 连接（如：`小明x小红.png`）

### 5. 批量输出
- 🚀 **一键生成**：自动生成所有组合
- 📊 **进度显示**：实时显示生成进度
- 📂 **自动打开**：完成后可自动打开输出目录

## 📦 安装

### 方式一：使用 Conda（推荐）

```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate image_composer

# 安装拖拽支持（可选但推荐）
pip install tkinterdnd2
```

### 方式二：使用 pip

```bash
pip install pillow tkinterdnd2
```

## 🚀 使用

### 运行源码

```bash
python main.py
```

### 运行打包版本

直接双击 `dist/CuteIconSetHelper.exe`（Windows）

## 📖 工作流程

1. **导入图片**
   - 拖拽图片到窗口，或点击"选择图片"按钮
   - 支持批量导入多个图片

2. **裁剪图片**
   - 非 1:1 比例的图片需要裁剪
   - 拖动调整裁剪框位置
   - 选择方形或圆形裁剪
   - 点击"应用并再裁一张"可从同一张图裁剪多个区域

3. **配置输出**
   - **尺寸**：设置输出图片尺寸（默认 256x256）
   - **排布方式**：选择横排、竖排或圆形
   - **最大组合图数**：限制组合数量，避免生成过多文件
   - **全体都有**：勾选后额外生成所有素材的组合
   - **素材名称**：为每个素材设置名称，用于生成文件名

4. **生成图片**
   - 选择输出目录
   - 点击"生成输出"按钮
   - 等待生成完成

### 输出文件名示例

假设有 3 个素材，名称分别为：小明、小红、小蓝

- **单张**：`小明.png`、`小红.png`、`小蓝.png`
- **双张组合**：`小明x小红_h.png`、 `小明x小红_v.png`、 `小明x小红_c.png`
- **全体都有**：`小明x小红x小蓝_h.png`、 `小明x小红x小蓝_v.png`、 `小明x小红x小蓝_c.png`

（后缀 `_h`=横排，`_v`=竖排，`_c`=圆形）

## 📁 项目结构

```
CuteIconSetHelper/
├── main.py                    # 入口文件
├── gui/                       # GUI 模块
│   ├── app.py                # 主应用框架
│   ├── input_frame.py        # 输入界面（支持拖拽）
│   ├── crop_frame.py         # 裁剪界面
│   └── generate_frame.py     # 生成界面
├── core/                      # 核心模块
│   ├── image_processor.py    # 图像处理
│   └── layout_engine.py      # 排布算法
├── dist/                      # 打包输出目录
│   └── CuteIconSetHelper.exe # Windows 可执行文件
├── environment.yml            # Conda 环境配置
├── main.spec                  # PyInstaller 配置
├── README.md                  # 说明文档
└── .gitignore                 # Git 忽略文件
```

## 🛠️ 技术栈

- **GUI**: tkinter + tkinterdnd2
- **图像处理**: Pillow (PIL)
- **打包**: PyInstaller
- **开发方式**: [VibeCoding](https://en.wikipedia.org/wiki/Vibe_coding)

## 📦 打包

### 打包为可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包（单文件 + 无控制台窗口）
pyinstaller --onefile --windowed --name CuteIconSetHelper main.py

# 或直接使用 spec 文件
pyinstaller main.spec
```

打包后的文件位于 `dist/CuteIconSetHelper.exe`

## 📝 更新日志

### v1.1.0 (2026-04-15)
- ✨ **重构裁剪界面工作流程**
  - 删除 1:1 校验，所有图片都进入裁剪步骤
  - 改为保存裁切到素材库模式，支持同一张图多次裁切不同区域
  - 添加状态标签提示（无弹窗），1秒自动消失
  - 返回第一步时保留素材库和裁剪框状态（图片未变时）
  - 添加图片导航按钮（上一张/下一张）
  - 删除"跳过图片"和"应用并再裁一张"按钮
  - 下一步按钮单独放置在流程导航区域
- 🎨 **UI 优化**
  - 删除裁剪界面的图片信息显示面板
  - 调整布局使返回/下一步按钮始终可见
  - 修复生成界面进度条和状态标签丢失的问题
- 🐛 **Bug 修复**
  - 修复 PyInstaller 打包后拖拽功能失效的问题（添加 tkinterdnd2 hook）
  - 修复裁剪预览透明像素残留问题
  - 修复选中状态提示不实时更新的问题

### v1.0.0 (2026-04-15)
- ✨ 初始版本发布
- 🎴 卡片式素材管理界面
- 🔤 使用 "x" 连接素材名称
- 📐 修复裁剪预览透明像素残留问题
- 🖥️ 优化 UI 布局，确保初始窗口显示完整

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 链接

- **项目地址**: https://github.com/Xuan-cc/CuteIconSetHelper
- **问题反馈**: https://github.com/Xuan-cc/CuteIconSetHelper/issues

---

**Made with ❤️ by VibeCoding**
