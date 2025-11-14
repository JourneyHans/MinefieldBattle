@echo off
chcp 65001 >nul
echo 正在打包游戏...
echo.

REM 检查是否安装了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM 打包游戏（使用英文文件名避免编码问题）
echo 开始打包...
pyinstaller --onefile --windowed --name "MinefieldBattle" ^
    --hidden-import=pygame ^
    --collect-all pygame ^
    main.py

if errorlevel 1 (
    echo.
    echo 打包失败！请检查错误信息。
    pause
    exit /b 1
)

REM 重命名为中文名称（如果系统支持）
if exist "dist\MinefieldBattle.exe" (
    if exist "dist\魔法军团地雷战场.exe" del /q "dist\魔法军团地雷战场.exe"
    move "dist\MinefieldBattle.exe" "dist\魔法军团地雷战场.exe" >nul 2>&1
    if errorlevel 1 (
        echo 注意：无法重命名为中文文件名，使用英文文件名 MinefieldBattle.exe
        set EXE_NAME=MinefieldBattle.exe
    ) else (
        set EXE_NAME=魔法军团地雷战场.exe
    )
) else (
    set EXE_NAME=MinefieldBattle.exe
)

echo.
echo 打包完成！
echo 可执行文件位于: dist\%EXE_NAME%
echo.
pause

