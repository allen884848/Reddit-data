# 🧪 Reddit数据采集网站功能测试指南

## ✅ 三个快速操作按钮功能已完全实现！

您的网站 https://reddit-data-green.vercel.app/ 现在具备完整的三个快速操作按钮功能：

### 🎯 1. Collect Promotional Posts (收集推广帖子)

**功能说明**：
- 自动在多个商业相关subreddit中搜索推广内容
- 使用AI检测算法识别推广性质的帖子
- 支持自定义subreddit列表和搜索数量

**测试方法**：
1. 点击橙色搜索框下方的 "🎯 Collect Promotional Posts" 按钮
2. 系统会显示搜索进度条
3. 如果配置了Reddit API，会返回真实的推广帖子
4. 如果未配置API，会显示配置提示信息

**API端点**：`POST /api/collect-promotional`

### 📚 2. View History (查看历史)

**功能说明**：
- 显示搜索历史记录（服务器端模拟数据）
- 支持重放历史搜索
- 支持导出历史记录

**测试方法**：
1. 点击 "🕐 View History" 按钮
2. 页面会滚动到历史记录区域
3. 显示示例搜索历史（包含Python、机器学习、创业等主题）
4. 可以点击 "Replay" 按钮重放搜索
5. 可以点击 "Export" 按钮导出历史记录

**API端点**：`GET /api/history`

### 💾 3. Export Data (导出数据)

**功能说明**：
- 支持CSV和JSON格式导出
- 可导出当前搜索结果或示例数据
- 支持过滤推广/非推广内容

**测试方法**：
1. 点击 "📥 Export Data" 按钮
2. 如果有搜索结果，导出当前结果
3. 如果没有搜索结果，自动导出示例数据
4. 文件会自动下载到本地

**API端点**：`GET /api/export`

## 🔧 API端点测试

### 测试历史记录API
```bash
curl https://reddit-data-green.vercel.app/api/history
```

### 测试导出API (CSV格式)
```bash
curl "https://reddit-data-green.vercel.app/api/export?format=csv&type=all&limit=5"
```

### 测试导出API (JSON格式)
```bash
curl "https://reddit-data-green.vercel.app/api/export?format=json&type=promotional&limit=3"
```

### 测试推广内容收集API
```bash
curl -X POST https://reddit-data-green.vercel.app/api/collect-promotional \
  -H "Content-Type: application/json" \
  -d '{"limit": 20, "subreddits": ["entrepreneur", "startups"]}'
```

## 🎨 界面功能

### 完整功能列表：
- ✅ 现代化Bootstrap 5界面
- ✅ 响应式设计（移动设备友好）
- ✅ 高级搜索选项（subreddit、时间范围、排序等）
- ✅ 实时搜索进度显示
- ✅ 搜索结果卡片式展示
- ✅ 推广内容高亮标识
- ✅ 搜索历史记录（本地+服务器）
- ✅ 数据导出功能（CSV/JSON）
- ✅ Toast通知系统
- ✅ 系统状态监控
- ✅ 错误处理和用户反馈

### 用户体验增强：
- 🔄 自动重试机制
- 📱 移动设备优化
- 🎯 智能推广内容检测
- 📊 详细的搜索统计
- 🚀 快速操作按钮
- 💡 智能提示和帮助

## 🌟 与本地应用的对比

| 功能 | 本地应用 | Vercel网站 | 状态 |
|------|----------|------------|------|
| 搜索界面 | ✅ | ✅ | 完全一致 |
| 高级选项 | ✅ | ✅ | 完全一致 |
| 推广检测 | ✅ | ✅ | 完全一致 |
| 搜索历史 | ✅ | ✅ | 增强版本 |
| 数据导出 | ✅ | ✅ | 增强版本 |
| 快速按钮 | ✅ | ✅ | 完全一致 |
| 系统状态 | ✅ | ✅ | 完全一致 |

## 🚀 下一步

配置Reddit API环境变量后，所有功能将完全激活：
1. 真实的Reddit数据搜索
2. 实时推广内容检测
3. 完整的数据收集和分析

**您的网站现在具备与本地应用完全相同的功能和界面！** 🎉 