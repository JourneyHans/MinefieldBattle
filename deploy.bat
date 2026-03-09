@echo off
REM demo_v2 快速部署脚本 (Windows)

echo ========================================
echo  demo_v2 快速部署脚本
echo ========================================
echo.

cd /d "%~dp0demo_v2"

echo [1/3] 构建项目...
call npm run build
if errorlevel 1 (
    echo.
    echo ❌ 构建失败
    pause
    exit /b 1
)

echo ✅ 构建成功
echo.

echo [2/3] 部署到 GitHub Pages...
call npm run deploy
if errorlevel 1 (
    echo.
    echo ❌ 部署失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo  🎉 部署成功！
echo ========================================
echo.
echo 访问地址：
echo 🌐 https://journeyhans.github.io/MinefieldBattle/demo_v2/
echo.
echo 如果看到旧版本，请强制刷新浏览器 (Ctrl+Shift+R)
echo.
pause
