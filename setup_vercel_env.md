# Vercel环境变量配置指南

## 为什么需要配置环境变量？

您的Reddit数据采集网站现在已经成功部署到Vercel，但是需要配置Reddit API凭据才能使用搜索功能。

## 配置步骤

### 1. 访问Vercel项目设置

1. 打开 [Vercel Dashboard](https://vercel.com/dashboard)
2. 找到您的项目 `reddit-data-green`
3. 点击项目名称进入项目详情页
4. 点击顶部的 `Settings` 标签
5. 在左侧菜单中选择 `Environment Variables`

### 2. 添加Reddit API环境变量

添加以下环境变量（使用您的实际Reddit API凭据）：

| 变量名 | 值 | 环境 |
|--------|-----|------|
| `REDDIT_CLIENT_ID` | `eyB_HEwp6ttuc0UInIv_og` | Production, Preview, Development |
| `REDDIT_CLIENT_SECRET` | `tHIoRB0ucx0Q95XdxSg2-WyD5F01_w` | Production, Preview, Development |
| `REDDIT_USERNAME` | `Aware-Blueberry-3586` | Production, Preview, Development |
| `REDDIT_PASSWORD` | `Liu@8848` | Production, Preview, Development |

### 3. 配置方法

对于每个环境变量：

1. 点击 `Add New` 按钮
2. 在 `Name` 字段输入变量名（如 `REDDIT_CLIENT_ID`）
3. 在 `Value` 字段输入对应的值
4. 在 `Environments` 部分选择所有环境：
   - ✅ Production
   - ✅ Preview  
   - ✅ Development
5. 点击 `Save` 保存

### 4. 重新部署

配置完所有环境变量后：

1. 回到项目的 `Deployments` 标签
2. 找到最新的部署
3. 点击右侧的三个点菜单
4. 选择 `Redeploy` 重新部署

或者，您可以推送一个新的提交到GitHub来触发自动重新部署。

## 验证配置

配置完成并重新部署后，您可以：

1. 访问 https://reddit-data-green.vercel.app/api/reddit/test
2. 如果配置正确，应该返回成功状态
3. 在主页面尝试搜索功能

## 功能说明

配置完成后，您的网站将具备以下功能：

### ✅ 已实现的功能
- 🌐 现代化响应式Web界面
- 🔍 实时Reddit数据搜索
- 🏷️ 多关键词搜索支持
- 🛡️ 推广内容自动检测
- 📊 搜索结果统计和分析
- 🔗 RESTful API接口
- 📱 移动设备友好界面

### 🔧 API端点
- `GET /` - 主页面（包含搜索界面）
- `GET /api/health` - 健康检查
- `GET /api/status` - 系统状态
- `GET /api/reddit/test` - Reddit API连接测试
- `POST /api/search` - Reddit数据搜索

### 📝 搜索功能使用方法

1. **基本搜索**：输入关键词，如 `python`
2. **多关键词搜索**：用逗号分隔，如 `python, programming, AI`
3. **指定subreddit**：在subreddit字段输入，如 `programming`
4. **限制结果数量**：设置1-100之间的数字

### ⚠️ 注意事项

- Vercel是无服务器环境，数据不会持久化存储
- 每次搜索都是实时从Reddit获取数据
- 搜索结果有数量限制（最多100个）
- 推广内容会被自动标记

## 故障排除

如果遇到问题：

1. **API连接失败**：检查环境变量是否正确配置
2. **搜索无结果**：尝试不同的关键词或检查网络连接
3. **页面加载慢**：这是正常的，Vercel冷启动需要时间

## 技术架构

- **前端**：现代化HTML5 + CSS3 + JavaScript
- **后端**：Python Flask + PRAW (Reddit API)
- **部署**：Vercel无服务器平台
- **API**：RESTful设计，JSON响应格式

配置完成后，您就拥有了一个功能完整的Reddit数据采集平台！ 