#!/bin/bash

echo "正在打包游戏..."
echo ""

# 检查是否安装了PyInstaller
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装PyInstaller..."
    pip3 install pyinstaller
fi

# 清理之前的构建文件
rm -rf build dist *.spec

# 打包游戏（使用英文文件名避免编码问题）
echo "开始打包..."
pyinstaller --onefile --windowed --name "MinefieldBattle" \
    --hidden-import=pygame \
    --collect-all pygame \
    main.py

if [ $? -eq 0 ]; then
    # 尝试重命名为中文名称
    if [ -f "dist/MinefieldBattle" ]; then
        mv "dist/MinefieldBattle" "dist/魔法军团地雷战场" 2>/dev/null
        if [ $? -eq 0 ]; then
            EXE_NAME="魔法军团地雷战场"
        else
            EXE_NAME="MinefieldBattle"
        fi
    else
        EXE_NAME="MinefieldBattle"
    fi
    
    echo ""
    echo "打包完成！"
    echo "可执行文件位于: dist/$EXE_NAME"
    echo ""
else
    echo ""
    echo "打包失败！请检查错误信息。"
    exit 1
fi

