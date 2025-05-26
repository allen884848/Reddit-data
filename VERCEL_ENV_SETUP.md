# 🔧 Vercel环境变量配置指南

## 🚨 问题解决

您遇到的错误 "Reddit API credentials not configured in Vercel environment variables" 是因为Vercel环境中没有配置Reddit API凭据。

## 📋 解决步骤

### 第1步：访问Vercel项目设置

1. 打开 [Vercel Dashboard](https://vercel.com/dashboard)
2. 找到您的项目 `reddit-data-green`
3. 点击项目名称进入项目详情
4. 点击顶部的 **Settings** 标签
5. 在左侧菜单中选择 **Environment Variables**

### 第2步：添加Reddit API环境变量

点击 **Add New** 按钮，逐一添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `REDDIT_CLIENT_ID` | `eyB_HEwp6ttuc0UInIv_og` | Reddit应用客户端ID |
| `REDDIT_CLIENT_SECRET` | `tHIoRB0ucx0Q95XdxSg2-WyD5F01_w` | Reddit应用客户端密钥 |
| `REDDIT_USERNAME` | `Aware-Blueberry-3586` | Reddit用户名 |
| `REDDIT_PASSWORD` | `Liu@8848` | Reddit密码 |

**重要提示**：
- 每个变量都要选择所有环境：✅ Production ✅ Preview ✅ Development
- 确保值完全正确，不要有多余的空格

### 第3步：重新部署

配置完所有环境变量后：

1. 回到项目的 **Deployments** 标签
2. 找到最新的部署记录
3. 点击右侧的三个点菜单 **⋯**
4. 选择 **Redeploy** 重新部署

### 第4步：验证配置

重新部署完成后（通常需要1-2分钟）：

1. 访问 https://reddit-data-green.vercel.app/api/reddit/test
2. 如果配置正确，应该看到成功状态
3. 返回主页面测试搜索功能

## 🎯 功能说明

配置完成后，您的网站将具备以下增强功能：

### ✅ 核心功能
1. **用户自定义关键词采集**
   - 支持多关键词搜索
   - 高级过滤选项（时间、评分、评论数等）
   - 支持指定subreddit搜索

2. **Reddit官方推广内容检测**
   - 自动识别Reddit标记为"Promoted"的广告帖子
   - 检测"Sponsored"标记的内容
   - 识别管理员置顶的推广内容

### 🔍 推广内容检测特征

系统会检测以下推广标记：
- **Reddit官方标记**：`Promoted`、`Sponsored`、`[Ad]`
- **管理员标记**：管理员发布或置顶的内容
- **内容分析**：包含推广关键词的帖子
- **URL分析**：包含联盟链接或追踪参数的帖子

### 🎨 界面显示

- **Reddit官方推广**：红色边框 + "Reddit Promoted" 红色标签
- **一般推广内容**：橙色边框 + "Promotional Content" 橙色标签
- **普通内容**：默认样式

## 🔧 故障排除

### 问题1：API连接失败
**症状**：搜索时显示"Reddit API credentials not configured"
**解决**：
1. 检查环境变量是否正确配置
2. 确认变量名拼写正确
3. 重新部署项目

### 问题2：认证失败
**症状**：API测试返回401错误
**解决**：
1. 验证Reddit用户名和密码是否正确
2. 检查Reddit账户是否启用了两步验证
3. 确认Client ID和Secret是否匹配

### 问题3：搜索无结果
**症状**：搜索完成但没有找到帖子
**解决**：
1. 尝试更常见的关键词
2. 调整时间范围（选择"Past Month"或"All Time"）
3. 降低最小评分要求

### 问题4：推广内容检测不准确
**说明**：
- 系统使用多种算法检测推广内容
- Reddit官方推广标记最准确
- 内容分析可能有误判，这是正常现象

## 📊 使用建议

### 搜索推广内容的最佳实践：

1. **使用推广相关关键词**：
   ```
   deal, discount, sale, promo, offer, coupon
   ```

2. **选择商业相关subreddit**：
   ```
   deals, entrepreneur, startups, business, marketing
   ```

3. **调整搜索参数**：
   - 时间范围：Past Week 或 Past Month
   - 排序方式：New 或 Hot
   - 帖子数量：50-100

4. **使用"Collect Promotional Posts"按钮**：
   - 自动搜索多个商业subreddit
   - 专门收集推广内容
   - 结果更精准

## 🎉 完成确认

配置完成后，您应该能够：

- ✅ 成功搜索Reddit内容
- ✅ 看到推广内容的特殊标记
- ✅ 区分Reddit官方推广和一般推广内容
- ✅ 导出搜索结果
- ✅ 查看搜索历史

如果仍有问题，请检查Vercel项目的Function Logs获取详细错误信息。 