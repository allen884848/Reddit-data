# 🔑 Reddit API 配置详细指南

**解决Reddit API认证问题的完整指南**

---

## 🚨 当前状态

您提供的Reddit API凭据遇到了401认证错误。这通常是由以下原因造成的：

- Client ID或Client Secret不正确
- Reddit应用配置有问题
- 用户名或密码不正确
- 需要启用两步验证

---

## 📋 Reddit API配置步骤

### 第一步：创建Reddit应用

1. **登录Reddit账户**
   - 访问：https://www.reddit.com/prefs/apps
   - 使用您的Reddit账户登录

2. **创建新应用**
   - 点击"Create App"或"Create Another App"
   - 填写应用信息：
     ```
     名称: Reddit Data Collector
     应用类型: script (重要！)
     描述: Data collection for research purposes
     关于URL: 留空
     重定向URI: http://localhost:8080
     ```

3. **获取凭据**
   - **Client ID**: 应用名称下方的短字符串
   - **Client Secret**: 标记为"secret"的长字符串

### 第二步：验证凭据

您提供的凭据：
```
Client ID: eyB_HEwp6ttucOUInIv_og
Client Secret: tHIoRBOucxOQ95XdxSg2-WyD5FO1_w
用户名: Aware-Blueberry-3586
密码: Liu@8848
```

### 第三步：常见问题排查

#### 问题1：401 Unauthorized错误
**可能原因：**
- Client ID或Secret复制错误
- 应用类型不是"script"
- 用户名或密码错误

**解决方案：**
1. 重新检查Reddit应用页面的凭据
2. 确保应用类型设置为"script"
3. 验证用户名和密码是否正确
4. 检查是否启用了两步验证

#### 问题2：两步验证
如果您的Reddit账户启用了两步验证：
1. 生成应用专用密码
2. 使用应用密码替代普通密码

#### 问题3：应用权限
确保您的Reddit应用有以下权限：
- read (读取帖子)
- identity (获取用户信息)

---

## 🔧 测试API连接

### 方法1：使用我们的测试脚本
```bash
python -c "
from reddit_scraper import RedditScraper
try:
    scraper = RedditScraper()
    print('✅ Reddit API连接成功！')
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

### 方法2：直接使用PRAW测试
```python
import praw

reddit = praw.Reddit(
    client_id='your_client_id',
    client_secret='your_client_secret',
    user_agent='test/1.0',
    username='your_username',
    password='your_password'
)

try:
    user = reddit.user.me()
    print(f'认证成功，用户: {user.name}')
except Exception as e:
    print(f'认证失败: {e}')
```

---

## 🛠️ 配置文件更新

当您获得正确的凭据后，更新`config.py`文件：

```python
REDDIT_CONFIG = {
    'client_id': 'your_correct_client_id',
    'client_secret': 'your_correct_client_secret',
    'user_agent': 'RedditDataCollector/2.0 by /u/your_username',
    'username': 'your_reddit_username',
    'password': 'your_reddit_password',
}
```

---

## 🔄 临时解决方案

在解决API问题期间，系统可以在演示模式下运行：

### 启动演示模式
```bash
python app.py --demo
```

演示模式功能：
- ✅ 完整的Web界面
- ✅ 模拟数据展示
- ✅ 所有功能测试
- ❌ 无法收集真实Reddit数据

---

## 📞 获取帮助

### 检查清单
- [ ] Reddit应用类型设置为"script"
- [ ] Client ID和Secret正确复制
- [ ] 用户名和密码正确
- [ ] 没有启用两步验证（或使用应用密码）
- [ ] Reddit账户状态正常

### 常见错误代码
- **401 Unauthorized**: 认证凭据错误
- **403 Forbidden**: 权限不足
- **429 Too Many Requests**: 请求过于频繁
- **500 Internal Server Error**: Reddit服务器问题

### 联系支持
如果问题持续存在：
1. 检查Reddit API状态页面
2. 查看Reddit开发者文档
3. 联系Reddit支持团队

---

## 🎯 下一步行动

1. **重新检查Reddit应用设置**
2. **验证所有凭据信息**
3. **测试API连接**
4. **更新配置文件**
5. **重启应用程序**

---

**💡 提示：即使没有Reddit API，您仍然可以使用系统的所有其他功能，包括数据分析、导出和界面测试。**

---

*最后更新：2024年*  
*如有问题，请参考README.md中的故障排除部分* 