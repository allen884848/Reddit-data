# 🚀 Vercel部署指南 - 修复版

## ✅ 问题已解决

**原问题**: "The `functions` property cannot be used in conjunction with the `builds` property"

**解决方案**: 已移除`builds`属性，使用现代的`functions`配置

## 📋 修复内容

### 1. 更新的 `vercel.json` 配置
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
  },
  "regions": ["hkg1", "sin1", "sfo1"]
}
```

### 2. 关键变化
- ❌ 移除了 `builds` 属性
- ✅ 保留了 `functions` 属性
- ✅ 使用 `api/index.py` 作为入口点
- ✅ 添加了 `VERCEL=1` 环境变量

## 🚀 部署步骤

### 方法一：自动化脚本部署
```bash
./deploy-to-vercel.sh
```

### 方法二：手动部署
1. **连接GitHub仓库**
   - 访问 [Vercel Dashboard](https://vercel.com/dashboard)
   - 点击 "New Project"
   - 选择您的GitHub仓库：`allen884848/Reddit-data`

2. **配置项目**
   - Framework Preset: `Other`
   - Root Directory: `./` (保持默认)
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: `pip install -r requirements-vercel.txt`

3. **设置环境变量**
   ```
   REDDIT_CLIENT_ID=eyB_HEwp6ttuc0UInIv_og
   REDDIT_CLIENT_SECRET=tHIoRB0ucx0Q95XdxSg2-WyD5F01_w
   REDDIT_USERNAME=Aware-Blueberry-3586
   REDDIT_PASSWORD=Liu@8848
   FLASK_ENV=production
   VERCEL=1
   ```

4. **部署**
   - 点击 "Deploy"
   - 等待部署完成

## 🔧 故障排除

### 常见问题

1. **部署失败**
   - 检查 `requirements-vercel.txt` 是否存在
   - 确认所有环境变量已设置

2. **函数超时**
   - 已设置 `maxDuration: 30` 秒
   - 如需更长时间，升级Vercel计划

3. **模块导入错误**
   - 确认 `api/index.py` 正确导入了 `app`
   - 检查 `PYTHONPATH` 环境变量

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

## 📝 注意事项

1. **数据库限制**
   - Vercel无服务器环境不支持持久化SQLite
   - 建议使用外部数据库服务（如PlanetScale、Supabase）

2. **文件存储**
   - 导出文件将存储在临时目录
   - 建议使用云存储服务

3. **性能优化**
   - 函数冷启动时间约1-3秒
   - 频繁访问可保持函数热启动

现在您可以重新尝试部署到Vercel了！🚀 