# 魔法军团 - Python版

这是用 Python + Pygame 重写的魔法军团游戏。

## 项目说明

本项目是原网页版游戏的 Python 重写版本，使用 Pygame 作为游戏引擎。

> 💡 **开发记录**：相关问题记录在 `开发记录.md` 文件中，方便查阅。

## 安装说明

### 1. 安装 Python

- 访问 https://www.python.org/downloads/
- 下载并安装 Python 3.9 或更高版本（建议 3.11 或 3.12）
- 安装时勾选 "Add Python to PATH"

### 2. 安装依赖

在项目目录下运行：

```bash
pip install -r requirements.txt
```

或者直接安装 Pygame：

```bash
pip install pygame
```

### 3. 运行游戏

```bash
python game.py
```

## 项目结构

```
25111804/
├── game.py              # 游戏主文件（待实现）
├── requirements.txt     # Python依赖包列表
├── README.md           # 本文件
└── .gitignore          # Git忽略文件
```

## 开发计划

- [ ] 游戏核心逻辑
- [ ] 绘制系统
- [ ] UI系统（难度选择、重置按钮、勇士列表）
- [ ] 事件处理（鼠标点击、拖拽）
- [ ] 动画系统
- [ ] 游戏状态管理

## 功能说明

### 游戏特性
- 三种地图大小：9×9、16×16、16×30
- 迷雾探索系统
- 危险地块、安全地块、终点
- 勇士系统（可拖拽放置）
- 标记系统
- 自动提示和暴露机制
- 生命值系统

### 操作说明
- **左键点击**：打开迷雾方块
- **右键点击**：标记/取消标记
- **拖拽勇士**：从列表拖拽勇士到棋盘

## 技术栈

- **Python 3.9+**
- **Pygame 2.5.0+**

## 打包说明

### 使用 PyInstaller 打包

```bash
# 安装打包工具
pip install pyinstaller

# 打包成单文件
pyinstaller --onefile --windowed game.py

# 打包成文件夹
pyinstaller --windowed game.py
```

打包后的文件在 `dist` 目录中。

## 注意事项

- 本项目是网页版的重写版本，功能保持一致
- 原网页版文件保留在 `G:\CursorProject\25111603` 目录下
- 本项目独立开发，不影响原网页版

