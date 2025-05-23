# 🚀 GitHub同步指南 - 超简单版

## 📋 前提条件
- ✅ GitHub仓库已创建
- ✅ 项目文件已准备好

## 🎯 一键同步方案

### 方案一：使用一键脚本（最简单）

在Cursor终端中运行：
```bash
./sync_to_github.sh https://github.com/你的用户名/你的仓库名.git
```

**示例：**
```bash
./sync_to_github.sh https://github.com/allen/reddit-data-collection.git
```

### 方案二：手动三步走
```bash
# 1. 初始化并添加文件
git init
git add .
git commit -m "Initial commit"

# 2. 连接GitHub仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 3. 推送到GitHub
git branch -M main
git push -u origin main
```

### 方案三：GitHub Desktop（图形界面）
1. 打开GitHub Desktop
2. 选择 "Add an Existing Repository from your Hard Drive"
3. 选择项目文件夹：`/Users/allen/Desktop/网站/reddit数据采集`
4. 点击 "Publish repository"

## 🔄 后续更新
同步完成后，每次更新只需要：
```bash
git add .
git commit -m "更新描述"
git push
```

## 🌐 访问地址
- **GitHub仓库**: https://github.com/你的用户名/你的仓库名
- **本地网站**: http://127.0.0.1:5000

## ⚠️ 注意事项
- 数据库文件(*.db)会被自动忽略，不会上传到GitHub
- Reddit API凭据会被保护，不会泄露
- 首次推送可能需要GitHub登录验证 