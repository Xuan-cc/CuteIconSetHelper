# 图片组合工具

一个支持拖拽、裁剪、多种排布方式的图片处理工具。

**项目地址**: https://github.com/Xuan-cc/CuteIconSetHelper

**开发方式**: 本项目由 [vibecoding](https://en.wikipedia.org/wiki/Vibe_coding) 完成

## 功能特性

1. **图片导入**：支持拖拽和选择文件导入
2. **自动裁剪**：非1:1图片自动进入裁剪界面
3. **多种排布**：
   - 横排：水平拼接
   - 竖排：垂直拼接
   - 圆形：环形排列，自适应缩放
4. **组合输出**：支持单张、双张组合、全部组合

## 安装

```bash
conda env create -f environment.yml
conda activate image_composer
```

## 运行

```bash
python main.py
```

## 打包

```bash
pyinstaller --onefile --windowed main.py
```

## 使用说明

### 工作流程

1. **导入图片**
   - 拖拽图片到窗口中，或点击"选择图片"按钮
   - 支持 PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP 格式

2. **裁剪图片（仅非1:1图片）**
   - 自动识别需要裁剪的图片
   - 在画布上拖动鼠标绘制裁剪区域（保持1:1比例）
   - 点击"应用裁剪"继续
   - 已经是1:1的图片会自动跳过

3. **配置输出**
   - **尺寸**：默认256x256像素，可自定义
   - **排布方式**：
     - 横排：水平拼接
     - 竖排：垂直拼接  
     - 圆形：环形排列，自动缩放避免重叠
   - **输出目录**：点击浏览或手动输入路径

4. **生成图片**
   - 点击"生成图片"按钮
   - 自动生成以下组合：
     - 单张：1.png, 2.png, 3.png...
     - 双张组合：12.png, 13.png, 23.png...
     - 全部组合：all.png

### 输出示例（3张256x256原图）

**横排输出：**
- 单张：256x256 (3张)
- 双张：256x512 (3张)
- 全部：256x768 (1张)

**竖排输出：**
- 单张：256x256 (3张)
- 双张：512x256 (3张)
- 全部：768x256 (1张)

**圆形排布：**
- 单张：256x256 (3张)
- 双张：256x256 (环形排列，180度间隔)
- 全部：256x256 (环形排列，120度间隔)

## 项目结构

```
image_composer/
├── main.py              # 入口文件
├── gui/                 # GUI模块
│   ├── app.py          # 主应用框架
│   ├── input_frame.py  # 输入界面（支持拖拽）
│   ├── crop_frame.py   # 裁剪界面
│   └── generate_frame.py # 生成界面
├── core/               # 核心模块
│   ├── image_processor.py  # 图像处理（PIL封装）
│   └── layout_engine.py    # 排布算法
├── environment.yml     # Conda环境配置
├── main.spec          # PyInstaller打包配置
└── README.md          # 说明文档
```

## 技术栈

- **GUI**: tkinter (Python内置)
- **图像处理**: Pillow (PIL)
- **拖拽支持**: windnd (Windows)
- **打包**: PyInstaller
