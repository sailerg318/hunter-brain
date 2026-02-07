#!/bin/bash
# Streamlit Cloud 快速部署脚本

echo "🚀 开始部署 NEXUS 人才智能平台..."

# 检查是否在 hunter-brain 目录
if [ ! -f "app.py" ]; then
    echo "❌ 错误：请在 hunter-brain 目录下运行此脚本"
    exit 1
fi

# 初始化 Git（如果还没有）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git branch -M main
fi

# 添加所有文件
echo "📝 添加文件..."
git add .

# 提交更改
echo "💾 提交更改..."
git commit -m "性能优化：懒加载+缓存+简化渲染"

# 提示用户添加远程仓库
echo ""
echo "✅ 本地提交完成！"
echo ""
echo "📌 下一步：推送到 GitHub"
echo "如果你还没有添加远程仓库，请运行："
echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo ""
echo "然后推送："
echo "  git push -u origin main"
echo ""
echo "🎯 推送后，Streamlit Cloud 会自动检测更新并重新部署"
