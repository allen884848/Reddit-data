# 🚀 Vercel环境变量配置指南

## ✅ 网站已成功更新！

您的Reddit数据采集网站现在已经显示完整功能界面，就像本地运行时一样！

**🌐 网站地址**: https://reddit-data-green.vercel.app/

## 🔧 需要配置Reddit API才能使用搜索功能

### 第1步：访问Vercel项目设置

1. 打开 [Vercel Dashboard](https://vercel.com/dashboard)
2. 找到您的项目 `reddit-data-green`
3. 点击项目名称
4. 点击顶部的 `Settings` 标签
5. 在左侧菜单选择 `Environment Variables`

### 第2步：添加环境变量

点击 `Add New` 按钮，添加以下4个环境变量：

| 变量名 | 值 |
|--------|-----|
| `REDDIT_CLIENT_ID` | `eyB_HEwp6ttuc0UInIv_og` |
| `REDDIT_CLIENT_SECRET` | `tHIoRB0ucx0Q95XdxSg2-WyD5F01_w` |
| `REDDIT_USERNAME` | `Aware-Blueberry-3586` |
| `REDDIT_PASSWORD` | `Liu@8848` |

**重要**：每个变量都要选择所有环境：
- ✅ Production
- ✅ Preview  
- ✅ Development

### 第3步：重新部署

配置完成后：
1. 回到项目的 `Deployments` 标签
2. 点击最新部署右侧的三个点
3. 选择 `Redeploy`

### 第4步：测试功能

重新部署完成后，访问网站：
- 🔍 尝试搜索功能
- 📊 查看系统状态
- 🎯 测试推广内容收集

## 🎉 完成后您将拥有：

- ✅ 完整的Reddit搜索界面
- ✅ 高级搜索选项
- ✅ 搜索历史记录
- ✅ 数据导出功能
- ✅ 推广内容检测
- ✅ 响应式设计

## 🆘 如果遇到问题：

1. **API连接失败**：检查环境变量是否正确配置
2. **搜索无结果**：尝试不同的关键词
3. **页面加载慢**：这是正常的，Vercel冷启动需要时间

配置完成后，您的网站将具备与本地应用完全相同的功能！ 