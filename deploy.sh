#!/bin/bash

# demo_v2 快速部署脚本

echo "🚀 开始部署 demo_v2..."
echo ""

# 进入demo_v2目录
cd "$(dirname "$0")/demo_v2"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告：存在未提交的更改"
    echo "建议先提交更改再部署"
    echo ""
    read -p "是否继续部署？(y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 部署已取消"
        exit 1
    fi
fi

# 构建项目
echo "📦 构建项目..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

echo "✅ 构建成功"
echo ""

# 部署到GitHub Pages
echo "📤 部署到 GitHub Pages..."
npm run deploy

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "访问地址："
    echo "🌐 https://journeyhans.github.io/MinefieldBattle/demo_v2/"
    echo ""
    echo "如果看到旧版本，请强制刷新浏览器 (Ctrl+Shift+R 或 Cmd+Shift+R)"
else
    echo ""
    echo "❌ 部署失败"
    exit 1
fi
