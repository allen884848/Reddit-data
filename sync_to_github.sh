#!/bin/bash

# 🚀 Reddit数据采集项目 - 一键同步到GitHub脚本
# 使用方法：./sync_to_github.sh [你的GitHub仓库URL]

echo "🚀 开始同步Reddit数据采集项目到GitHub..."

# 检查是否提供了GitHub仓库URL
if [ -z "$1" ]; then
    echo "❌ 请提供GitHub仓库URL"
    echo "使用方法: ./sync_to_github.sh https://github.com/你的用户名/你的仓库名.git"
    exit 1
fi

GITHUB_URL="$1"

# 1. 初始化Git仓库
echo "📁 初始化Git仓库..."
git init

# 2. 创建.gitignore文件
echo "📝 创建.gitignore文件..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Temporary files
*.tmp
*.temp
temp/

# Reddit API credentials (security)
config_local.py
credentials.json

# Backup files
*.bak
*.backup
EOF

# 3. 添加所有文件
echo "📦 添加项目文件..."
git add .

# 4. 创建初始提交
echo "💾 创建初始提交..."
git commit -m "🎉 Initial commit: Reddit数据采集网站完整项目

✨ 功能特性:
- Reddit API集成与数据采集
- AI驱动的推广内容检测
- 完整的Web界面和RESTful API
- 数据导出和分析功能
- Vercel部署方案
- 完整的英文文档

🛠️ 技术栈:
- Python + Flask + SQLite
- PRAW (Reddit API)
- HTML5 + CSS3 + JavaScript
- 自研AI推广检测算法

📊 项目状态: 生产就绪 ✅"

# 5. 添加远程仓库
echo "🔗 连接到GitHub仓库..."
git remote add origin "$GITHUB_URL"

# 6. 推送到GitHub
echo "⬆️ 推送到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "🎉 同步完成！"
echo "📍 您的项目现在可以在以下地址访问："
echo "   $GITHUB_URL"
echo ""
echo "🌐 本地网站访问地址："
echo "   http://127.0.0.1:5000"
echo ""
echo "✅ 下次更新只需要运行："
echo "   git add ."
echo "   git commit -m '更新描述'"
echo "   git push" 