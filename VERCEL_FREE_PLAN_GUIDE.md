# 🚀 Vercel免费计划部署指南

## ✅ 问题已解决

**原问题**: "Deploying Serverless Functions to multiple regions is restricted to the Pro and Enterprise plans"

**解决方案**: 已移除多区域配置，优化为免费计划兼容配置

## 📋 修复内容

### 1. 优化后的 `vercel.json` 配置
```json
{
  "version": 2,
  "name": "reddit-data-collector",
  "functions": {
    "api/index.py": {
      "runtime": "python3.9",
      "maxDuration": 30
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production",
    "PYTHONPATH": ".",
    "VERCEL": "1"
  }
}
```

### 2. 关键变化
- ❌ 移除了 `regions` 配置（多区域部署）
- ✅ 使用默认区域（通常是美国东部）
- ✅ 保持所有核心功能不变
- ✅ 完全兼容Vercel免费计划

## 🆓 Vercel免费计划限制

### 免费计划包含：
- ✅ 100GB带宽/月
- ✅ 100个无服务器函数调用/天
- ✅ 单个区域部署
- ✅ 自定义域名
- ✅ SSL证书
- ✅ 基本分析

### 免费计划限制：
- ❌ 多区域部署（需要Pro计划）
- ❌ 函数执行时间超过10秒（我们设置了30秒，可能需要Pro）
- ❌ 高级分析功能
- ❌ 团队协作功能

## 🚀 重新部署步骤

### 方法一：自动重新部署
1. **删除旧部署**（如果存在）
   - 在Vercel Dashboard中删除之前的项目

2. **重新连接GitHub**
   - 访问 [Vercel Dashboard](https://vercel.com/dashboard)
   - 点击 "New Project"
   - 选择您的GitHub仓库：`allen884848/Reddit-data`

3. **使用默认配置**
   - Framework Preset: `Other`
   - Root Directory: `./` (保持默认)
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: `pip install -r requirements-vercel.txt`

### 方法二：使用Vercel CLI
```bash
# 安装Vercel CLI
npm i -g vercel

# 登录Vercel
vercel login

# 部署项目
vercel --prod
```

## 🔧 环境变量配置

在Vercel Dashboard中设置以下环境变量：
```
REDDIT_CLIENT_ID=eyB_HEwp6ttuc0UInIv_og
REDDIT_CLIENT_SECRET=tHIoRB0ucx0Q95XdxSg2-WyD5F01_w
REDDIT_USERNAME=Aware-Blueberry-3586
REDDIT_PASSWORD=Liu@8848
FLASK_ENV=production
VERCEL=1
```

## ⚠️ 性能优化建议

### 针对免费计划的优化：
1. **函数执行时间**
   - 如果遇到10秒超时，考虑减少数据收集量
   - 或者升级到Pro计划获得30秒执行时间

2. **带宽使用**
   - 100GB/月对于大多数使用场景足够
   - 监控使用情况避免超限

3. **函数调用次数**
   - 100次/天的限制可能需要注意
   - 考虑缓存策略减少API调用

## 📊 部署后验证

部署成功后，访问以下端点验证：

- **主页**: `https://your-app.vercel.app/`
- **健康检查**: `https://your-app.vercel.app/api/health`
- **API状态**: `https://your-app.vercel.app/api/status`

## 🎉 成功指标

- ✅ 部署状态：成功
- ✅ 函数运行：正常
- ✅ API响应：200 OK
- ✅ Reddit API：连接正常
- ✅ 无区域限制错误

## 💡 升级建议

如果需要以下功能，考虑升级到Pro计划（$20/月）：
- 多区域部署（更快的全球访问）
- 更长的函数执行时间（30秒+）
- 更多的带宽和函数调用
- 高级分析和监控

现在您可以重新尝试部署到Vercel了！🚀 