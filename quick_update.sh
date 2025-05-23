#!/bin/bash

# 🚀 Reddit数据采集项目 - 快速更新脚本
# 使用方法：./quick_update.sh [可选的提交信息]

echo "🔄 开始同步更新到GitHub..."

# 检查是否有未提交的更改
if [[ -z $(git status --porcelain) ]]; then
    echo "✅ 没有需要提交的更改"
    exit 0
fi

# 获取提交信息
if [ -z "$1" ]; then
    COMMIT_MSG="更新项目 - $(date '+%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

echo "📦 添加所有更改..."
git add .

echo "💾 提交更改..."
git commit -m "$COMMIT_MSG"

echo "⬆️ 推送到GitHub..."
git push

echo ""
echo "🎉 更新完成！"
echo "📍 查看更新：https://github.com/allen884848/Reddit-data"
echo ""
echo "🌐 本地网站访问地址："
echo "   http://127.0.0.1:5000" 