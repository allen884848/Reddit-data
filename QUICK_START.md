# 🚀 Reddit数据采集系统 - 快速开始指南

## 📋 系统概述
这是一个功能完备的Reddit数据采集网站后端系统，可以帮助您：
- 搜索和收集Reddit帖子数据
- 自动识别推广内容
- 导出数据为CSV或JSON格式
- 管理搜索历史和统计信息

## ⚡ 快速启动（3分钟上手）

### 第1步：启动系统
```bash
# 进入项目目录
cd reddit数据采集

# 激活虚拟环境
source venv/bin/activate

# 启动应用程序
python app.py
```

### 第2步：访问系统
打开浏览器访问：`http://localhost:5001`

### 第3步：测试API
使用以下命令测试系统是否正常运行：
```bash
curl http://localhost:5001/api/health
```

## 🔧 主要功能使用

### 1. 查看系统状态
```bash
curl http://localhost:5001/api/status
```
返回：系统运行状态、数据库统计信息

### 2. 获取已收集的帖子
```bash
curl http://localhost:5001/api/posts
```
返回：数据库中的所有帖子数据

### 3. 导出数据
```bash
# 导出为CSV格式
curl "http://localhost:5001/api/export?format=csv" -o posts.csv

# 导出为JSON格式
curl "http://localhost:5001/api/export?format=json" -o posts.json
```

### 4. 搜索Reddit帖子（需要API配置）
```bash
curl -X POST http://localhost:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["technology", "AI"],
    "subreddits": ["technology"],
    "limit": 10,
    "time_filter": "week"
  }'
```

## 🔑 Reddit API配置（可选）

如果您想使用实时Reddit数据收集功能，需要配置Reddit API：

### 1. 获取Reddit API凭证
1. 访问 [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. 点击 "Create App" 或 "Create Another App"
3. 选择 "script" 作为应用类型
4. 记录您的 Client ID 和 Client Secret

### 2. 配置系统
创建 `.env` 文件：
```bash
# 在项目根目录创建 .env 文件
echo "REDDIT_CLIENT_ID=your_client_id_here" > .env
echo "REDDIT_CLIENT_SECRET=your_client_secret_here" >> .env
echo "REDDIT_USER_AGENT=RedditDataCollector/1.0" >> .env
```

## 📊 系统测试

运行完整系统测试：
```bash
python test_system.py
```

预期结果：所有5个测试模块应该通过

## 🌐 API端点总览

| 端点 | 方法 | 功能 | 示例 |
|------|------|------|------|
| `/api/health` | GET | 系统健康检查 | `curl http://localhost:5001/api/health` |
| `/api/status` | GET | 系统状态和统计 | `curl http://localhost:5001/api/status` |
| `/api/posts` | GET | 获取帖子列表 | `curl http://localhost:5001/api/posts` |
| `/api/posts/{id}` | GET | 获取特定帖子 | `curl http://localhost:5001/api/posts/abc123` |
| `/api/search` | POST | 搜索Reddit帖子 | 见上方示例 |
| `/api/history` | GET | 搜索历史 | `curl http://localhost:5001/api/history` |
| `/api/export` | GET | 导出数据 | `curl "http://localhost:5001/api/export?format=csv"` |
| `/api/statistics` | GET | 详细统计信息 | `curl http://localhost:5001/api/statistics` |

## 🔍 常见问题

### Q: 系统启动失败怎么办？
A: 检查虚拟环境是否激活，运行 `pip install -r requirements.txt` 确保依赖已安装

### Q: 端口5001被占用怎么办？
A: 编辑 `app.py` 文件，修改最后一行的端口号：`app.run(debug=True, port=5002)`

### Q: 没有Reddit API也能使用吗？
A: 可以！系统包含示例数据，您可以测试所有功能除了实时数据收集

### Q: 如何查看系统日志？
A: 系统会在控制台输出详细日志，您也可以检查 `logs/` 目录（如果存在）

## 📈 数据示例

系统包含3个示例帖子数据，您可以立即测试：
- 1个技术相关帖子
- 1个推广内容帖子  
- 1个普通讨论帖子

## 🎯 下一步

1. **熟悉API**：使用上述curl命令测试各个端点
2. **配置Reddit API**：如果需要实时数据收集
3. **数据导出**：尝试导出数据到CSV或JSON
4. **自定义搜索**：使用POST /api/search端点进行自定义搜索

## 📞 获取帮助

- 查看完整文档：`README.md`
- 运行系统测试：`python test_system.py`
- 检查系统状态：访问 `/api/health` 端点

---

🎉 **恭喜！您已经成功启动了Reddit数据采集系统！**

现在您可以开始收集和分析Reddit数据了。如果遇到任何问题，请参考完整的README.md文档或运行系统测试进行诊断。 