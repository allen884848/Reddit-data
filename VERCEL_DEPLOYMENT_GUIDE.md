# 🚀 Vercel部署指南 - Reddit数据采集系统

**将您的Reddit数据采集系统部署到Vercel云平台**

---

## 📋 部署前准备

### ✅ 确认系统状态
在部署前，请确认：
- ✅ 本地系统运行正常
- ✅ Reddit API配置正确
- ✅ 所有测试通过
- ✅ 数据收集功能正常

### 📁 项目文件检查
确保以下文件存在：
```
reddit数据采集/
├── app.py                    # 主应用文件
├── config.py                 # 配置文件
├── reddit_scraper.py         # Reddit采集模块
├── database.py               # 数据库模块
├── vercel.json              # Vercel配置
├── requirements-vercel.txt   # 精简依赖
├── env.example              # 环境变量示例
├── api/
│   └── index.py             # Vercel入口文件
└── static/                  # 静态文件
    ├── css/
    ├── js/
    └── images/
```

---

## 🌐 第一步：准备Vercel账户

### 1. 注册Vercel账户
- 访问：https://vercel.com
- 使用GitHub账户注册（推荐）
- 完成账户验证

### 2. 安装Vercel CLI（可选）
```bash
npm install -g vercel
```

---

## 📂 第二步：准备代码仓库

### 1. 初始化Git仓库
```bash
cd /Users/allen/Desktop/网站/reddit数据采集
git init
git add .
git commit -m "Initial commit: Reddit Data Collector"
```

### 2. 创建GitHub仓库
- 访问：https://github.com/new
- 仓库名称：`reddit-data-collector`
- 设置为私有仓库（推荐）
- 不要初始化README（我们已有文件）

### 3. 推送代码到GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/reddit-data-collector.git
git branch -M main
git push -u origin main
```

---

## ⚙️ 第三步：配置Vercel项目

### 1. 导入GitHub仓库
- 登录Vercel控制台
- 点击"New Project"
- 选择"Import Git Repository"
- 选择您的`reddit-data-collector`仓库
- 点击"Import"

### 2. 配置项目设置
在Vercel项目设置中：

**Framework Preset**: Other
**Root Directory**: ./
**Build Command**: 留空
**Output Directory**: 留空
**Install Command**: `pip install -r requirements-vercel.txt`

---

## 🔐 第四步：配置环境变量

在Vercel项目设置 → Environment Variables中添加：

### 必需的环境变量
```
REDDIT_CLIENT_ID = eyB_HEwp6ttuc0UInIv_og
REDDIT_CLIENT_SECRET = tHIoRB0ucx0Q95XdxSg2-WyD5F01_w
REDDIT_USERNAME = Aware-Blueberry-3586
REDDIT_PASSWORD = Liu@8848
SECRET_KEY = your-production-secret-key-here
FLASK_ENV = production
VERCEL = 1
```

### 可选的环境变量
```
LOG_LEVEL = INFO
PORT = 3000
```

### 🔒 安全提示
- 为生产环境生成新的SECRET_KEY
- 考虑为生产环境创建专用的Reddit应用
- 定期轮换API密钥

---

## 🚀 第五步：部署应用

### 1. 自动部署
- 配置完成后，Vercel会自动开始部署
- 部署过程大约需要2-5分钟
- 可以在Vercel控制台查看部署日志

### 2. 手动部署（使用CLI）
```bash
vercel --prod
```

### 3. 部署状态检查
部署完成后，您会获得：
- 🌐 生产URL：`https://your-project.vercel.app`
- 📊 部署状态：成功/失败
- 📝 部署日志：详细的构建信息

---

## 🔍 第六步：验证部署

### 1. 访问应用
打开您的Vercel URL，检查：
- ✅ 主页正常加载
- ✅ 静态资源（CSS/JS）正常
- ✅ API端点响应正常

### 2. 测试API端点
```bash
# 健康检查
curl https://your-project.vercel.app/api/health

# 测试搜索功能
curl -X POST "https://your-project.vercel.app/api/search" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["test"], "limit": 1}'
```

### 3. 功能验证
- 🔍 搜索功能
- 📊 数据收集
- 🤖 推广检测
- 📈 统计显示

---

## ⚠️ 重要注意事项

### 🚨 Vercel限制
1. **函数执行时间**: 最大30秒
2. **内存限制**: 1024MB
3. **文件系统**: 只读（除了/tmp目录）
4. **数据库**: 需要外部数据库服务

### 💾 数据库解决方案
由于Vercel是无服务器环境，建议：

#### 选项1：使用外部数据库
- **Supabase** (PostgreSQL)
- **PlanetScale** (MySQL)
- **MongoDB Atlas**
- **Firebase Firestore**

#### 选项2：使用Vercel KV存储
```bash
# 安装Vercel KV
npm install @vercel/kv
```

#### 选项3：临时存储（当前方案）
- 数据存储在`/tmp`目录
- 函数重启时数据丢失
- 适合演示和测试

---

## 🔧 故障排除

### 常见问题

#### 1. 部署失败
**错误**: `Build failed`
**解决**: 检查requirements-vercel.txt中的依赖版本

#### 2. 环境变量未生效
**错误**: `Configuration error`
**解决**: 确认所有环境变量已正确设置

#### 3. API超时
**错误**: `Function timeout`
**解决**: 减少搜索限制，优化查询

#### 4. 静态文件404
**错误**: `Static files not found`
**解决**: 确认static目录结构正确

### 调试方法
1. 查看Vercel部署日志
2. 使用Vercel CLI本地测试
3. 检查函数日志
4. 验证环境变量

---

## 📈 性能优化

### 1. 缓存策略
```javascript
// vercel.json中添加
{
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 2. 函数优化
- 减少冷启动时间
- 优化依赖加载
- 使用连接池

### 3. 监控设置
- 启用Vercel Analytics
- 配置错误监控
- 设置性能警报

---

## 🔄 持续部署

### 自动部署设置
1. **GitHub集成**: 推送到main分支自动部署
2. **预览部署**: PR创建预览环境
3. **回滚功能**: 一键回滚到之前版本

### 部署流程
```bash
# 开发流程
git add .
git commit -m "Feature: Add new functionality"
git push origin main
# Vercel自动部署
```

---

## 📊 监控和维护

### 1. Vercel Analytics
- 访问量统计
- 性能指标
- 错误率监控

### 2. 日志监控
- 函数执行日志
- 错误日志分析
- 性能瓶颈识别

### 3. 定期维护
- 依赖更新
- 安全补丁
- 性能优化

---

## 🎉 部署完成检查清单

### ✅ 部署前
- [ ] 本地测试通过
- [ ] 代码推送到GitHub
- [ ] 环境变量准备完毕
- [ ] Vercel项目创建

### ✅ 部署中
- [ ] 构建成功
- [ ] 环境变量配置
- [ ] 域名分配
- [ ] SSL证书生成

### ✅ 部署后
- [ ] 应用正常访问
- [ ] API功能正常
- [ ] 数据收集测试
- [ ] 性能监控设置

---

## 🆘 获取帮助

### 官方资源
- **Vercel文档**: https://vercel.com/docs
- **Vercel社区**: https://github.com/vercel/vercel/discussions
- **Flask部署指南**: https://vercel.com/guides/deploying-flask-with-vercel

### 项目支持
- 查看项目README.md
- 检查部署日志
- 参考故障排除部分

---

**🚀 恭喜！您的Reddit数据采集系统即将在Vercel上运行！**

*部署完成后，您将拥有一个全球可访问的Reddit数据采集平台！*

---

*最后更新：2025-05-23*  
*版本：1.0* 