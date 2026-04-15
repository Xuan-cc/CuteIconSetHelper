# 图片组合工具

一个支持拖拽、裁剪、多种排布方式的图片处理工具。

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

## 项目结构

```
image_composer/
├── main.py              # 入口文件
├── gui/                 # GUI模块
│   ├── app.py          # 主应用框架
│   ├── input_frame.py  # 输入界面
│   ├── crop_frame.py   # 裁剪界面
│   └── generate_frame.py # 生成界面
├── core/               # 核心模块
│   ├── image_processor.py  # 图像处理
│   └── layout_engine.py    # 排布算法
├── environment.yml     # Conda环境配置
└── README.md          # 说明文档
```
