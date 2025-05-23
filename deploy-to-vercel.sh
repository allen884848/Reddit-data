#!/bin/bash

# Reddit数据采集系统 - Vercel自动部署脚本
# ==========================================

echo "🚀 Reddit数据采集系统 - Vercel部署脚本"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要工具
echo -e "${BLUE}📋 检查部署环境...${NC}"

# 检查Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git未安装，请先安装Git${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git已安装${NC}"

# 检查Node.js（用于Vercel CLI）
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️ Node.js未安装，将跳过Vercel CLI安装${NC}"
    SKIP_CLI=true
else
    echo -e "${GREEN}✅ Node.js已安装${NC}"
    SKIP_CLI=false
fi

# 检查项目文件
echo -e "${BLUE}📁 检查项目文件...${NC}"

required_files=("app.py" "config.py" "reddit_scraper.py" "database.py" "vercel.json" "requirements-vercel.txt")

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file 缺失${NC}"
        exit 1
    fi
done

# 检查API目录
if [[ -d "api" ]] && [[ -f "api/index.py" ]]; then
    echo -e "${GREEN}✅ api/index.py${NC}"
else
    echo -e "${RED}❌ api/index.py 缺失${NC}"
    exit 1
fi

# 初始化Git仓库（如果需要）
echo -e "${BLUE}🔧 准备Git仓库...${NC}"

if [[ ! -d ".git" ]]; then
    echo -e "${YELLOW}📦 初始化Git仓库...${NC}"
    git init
    git add .
    git commit -m "Initial commit: Reddit Data Collector for Vercel deployment"
    echo -e "${GREEN}✅ Git仓库初始化完成${NC}"
else
    echo -e "${GREEN}✅ Git仓库已存在${NC}"
    
    # 检查是否有未提交的更改
    if [[ -n $(git status --porcelain) ]]; then
        echo -e "${YELLOW}📝 发现未提交的更改，正在提交...${NC}"
        git add .
        git commit -m "Update: Prepare for Vercel deployment - $(date)"
        echo -e "${GREEN}✅ 更改已提交${NC}"
    fi
fi

# 安装Vercel CLI（如果需要）
if [[ "$SKIP_CLI" == false ]]; then
    echo -e "${BLUE}🛠️ 检查Vercel CLI...${NC}"
    
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}📦 安装Vercel CLI...${NC}"
        npm install -g vercel
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Vercel CLI安装成功${NC}"
        else
            echo -e "${RED}❌ Vercel CLI安装失败${NC}"
            echo -e "${YELLOW}💡 您可以手动访问 https://vercel.com 进行部署${NC}"
            SKIP_CLI=true
        fi
    else
        echo -e "${GREEN}✅ Vercel CLI已安装${NC}"
    fi
fi

# 显示环境变量配置提醒
echo -e "${BLUE}🔐 环境变量配置提醒${NC}"
echo -e "${YELLOW}请确保在Vercel项目中配置以下环境变量：${NC}"
echo ""
echo "REDDIT_CLIENT_ID=eyB_HEwp6ttuc0UInIv_og"
echo "REDDIT_CLIENT_SECRET=tHIoRB0ucx0Q95XdxSg2-WyD5F01_w"
echo "REDDIT_USERNAME=Aware-Blueberry-3586"
echo "REDDIT_PASSWORD=Liu@8848"
echo "SECRET_KEY=your-production-secret-key"
echo "FLASK_ENV=production"
echo "VERCEL=1"
echo ""

# 部署选项
echo -e "${BLUE}🚀 部署选项${NC}"
echo "1. 使用Vercel CLI部署（推荐）"
echo "2. 手动部署指导"
echo "3. 退出"

read -p "请选择部署方式 (1-3): " choice

case $choice in
    1)
        if [[ "$SKIP_CLI" == true ]]; then
            echo -e "${RED}❌ Vercel CLI不可用${NC}"
            choice=2
        else
            echo -e "${GREEN}🚀 使用Vercel CLI部署...${NC}"
            
            # 检查是否已登录
            if ! vercel whoami &> /dev/null; then
                echo -e "${YELLOW}🔑 请登录Vercel账户...${NC}"
                vercel login
            fi
            
            # 部署到Vercel
            echo -e "${BLUE}📤 开始部署...${NC}"
            vercel --prod
            
            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}🎉 部署成功！${NC}"
                echo -e "${BLUE}📋 后续步骤：${NC}"
                echo "1. 在Vercel控制台配置环境变量"
                echo "2. 测试应用功能"
                echo "3. 配置自定义域名（可选）"
            else
                echo -e "${RED}❌ 部署失败，请检查错误信息${NC}"
            fi
        fi
        ;;
    2)
        echo -e "${BLUE}📖 手动部署指导${NC}"
        echo ""
        echo -e "${YELLOW}步骤1: 创建GitHub仓库${NC}"
        echo "1. 访问 https://github.com/new"
        echo "2. 创建名为 'reddit-data-collector' 的仓库"
        echo "3. 设置为私有仓库"
        echo ""
        
        echo -e "${YELLOW}步骤2: 推送代码到GitHub${NC}"
        echo "运行以下命令："
        echo "git remote add origin https://github.com/YOUR_USERNAME/reddit-data-collector.git"
        echo "git branch -M main"
        echo "git push -u origin main"
        echo ""
        
        echo -e "${YELLOW}步骤3: 在Vercel中导入项目${NC}"
        echo "1. 访问 https://vercel.com"
        echo "2. 点击 'New Project'"
        echo "3. 导入您的GitHub仓库"
        echo "4. 配置环境变量"
        echo "5. 部署项目"
        echo ""
        
        echo -e "${GREEN}📚 详细指导请查看: VERCEL_DEPLOYMENT_GUIDE.md${NC}"
        ;;
    3)
        echo -e "${BLUE}👋 退出部署脚本${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 部署脚本执行完成！${NC}"
echo -e "${BLUE}📚 更多信息请查看 VERCEL_DEPLOYMENT_GUIDE.md${NC}" 