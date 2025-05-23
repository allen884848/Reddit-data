"""
Vercel Enhanced Flask Application
===============================

Enhanced version of the Reddit Data Collector for Vercel deployment.
This version includes Reddit search functionality and a complete web interface.
"""

import os
import logging
import json
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-reddit-collector-key-2025')

# 增强的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Data Collector - Vercel Enhanced</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            background: #f5f5f5;
        }
        .header { 
            background: linear-gradient(135deg, #ff4500, #ff6b35); 
            color: white; 
            padding: 30px; 
            border-radius: 12px; 
            margin-bottom: 20px; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .card { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .search-section {
            grid-column: 1 / -1;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .api-endpoint { 
            margin: 10px 0; 
            padding: 12px; 
            background: #f8f9fa; 
            border-radius: 6px; 
            border-left: 4px solid #ff4500;
        }
        .success { color: #28a745; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .warning { color: #ffc107; font-weight: bold; }
        .search-form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .search-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .search-button {
            padding: 12px 24px;
            background: #ff4500;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        .search-button:hover {
            background: #e03d00;
        }
        .results {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            display: none;
        }
        .post-item {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ff4500;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            .search-form {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Reddit Data Collector</h1>
        <p>Vercel增强版 - 完整功能</p>
        <p>实时Reddit数据采集与分析平台</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>📊 系统状态</h2>
            <p><strong>部署环境:</strong> Vercel Serverless</p>
            <p><strong>状态:</strong> <span class="success">✅ 运行正常</span></p>
            <p><strong>时间:</strong> {{ timestamp }}</p>
            <p><strong>版本:</strong> Enhanced v2.0</p>
            <p><strong>Reddit API:</strong> <span id="reddit-status" class="warning">检测中...</span></p>
        </div>
        
        <div class="card">
            <h2>🔗 API端点</h2>
            <div class="api-endpoint">
                <strong>GET /api/health</strong> - 健康检查
            </div>
            <div class="api-endpoint">
                <strong>GET /api/status</strong> - 系统状态
            </div>
            <div class="api-endpoint">
                <strong>POST /api/search</strong> - Reddit搜索
            </div>
            <div class="api-endpoint">
                <strong>GET /api/reddit/test</strong> - Reddit连接测试
            </div>
        </div>
    </div>
    
    <div class="search-section">
        <h2>🔍 Reddit数据搜索</h2>
        <p>输入关键词搜索Reddit帖子，支持多个关键词（用逗号分隔）</p>
        
        <div class="search-form">
            <input type="text" id="keywords" class="search-input" placeholder="输入搜索关键词，例如：python, programming, AI" value="python">
            <input type="text" id="subreddit" class="search-input" placeholder="指定subreddit（可选）" value="">
            <input type="number" id="limit" class="search-input" placeholder="结果数量" value="10" min="1" max="100" style="flex: 0 0 120px;">
            <button onclick="searchReddit()" class="search-button">🔍 搜索</button>
        </div>
        
        <div id="results" class="results">
            <div id="loading" class="loading" style="display: none;">
                <p>🔄 正在搜索Reddit数据...</p>
            </div>
            <div id="search-results"></div>
        </div>
    </div>
    
    <div class="card">
        <h2>⚠️ 功能说明</h2>
        <p>这是Vercel环境的增强版本，包含以下功能：</p>
        <ul>
            <li>✅ 实时Reddit数据搜索</li>
            <li>✅ 多关键词搜索支持</li>
            <li>✅ 推广内容检测</li>
            <li>✅ RESTful API接口</li>
            <li>⚠️ 数据不持久化（无服务器限制）</li>
            <li>⚠️ 搜索结果有数量限制</li>
        </ul>
    </div>

    <script>
        // 检查Reddit API状态
        fetch('/api/reddit/test')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('reddit-status');
                if (data.status === 'success') {
                    statusElement.innerHTML = '<span class="success">✅ 已连接</span>';
                } else {
                    statusElement.innerHTML = '<span class="error">❌ 未配置</span>';
                }
            })
            .catch(error => {
                document.getElementById('reddit-status').innerHTML = '<span class="error">❌ 连接失败</span>';
            });

        // Reddit搜索功能
        async function searchReddit() {
            const keywords = document.getElementById('keywords').value.trim();
            const subreddit = document.getElementById('subreddit').value.trim();
            const limit = parseInt(document.getElementById('limit').value) || 10;
            
            if (!keywords) {
                alert('请输入搜索关键词');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            const loadingDiv = document.getElementById('loading');
            const searchResults = document.getElementById('search-results');
            
            // 显示加载状态
            resultsDiv.style.display = 'block';
            loadingDiv.style.display = 'block';
            searchResults.innerHTML = '';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        keywords: keywords.split(',').map(k => k.trim()),
                        subreddit: subreddit || null,
                        limit: limit
                    })
                });
                
                const data = await response.json();
                loadingDiv.style.display = 'none';
                
                if (data.status === 'success') {
                    displayResults(data.data);
                } else {
                    searchResults.innerHTML = `<div class="error">搜索失败: ${data.message}</div>`;
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                searchResults.innerHTML = `<div class="error">搜索出错: ${error.message}</div>`;
            }
        }
        
        function displayResults(data) {
            const searchResults = document.getElementById('search-results');
            
            if (!data.posts || data.posts.length === 0) {
                searchResults.innerHTML = '<div class="warning">未找到相关帖子</div>';
                return;
            }
            
            let html = `<h3>搜索结果 (${data.posts.length} 个帖子)</h3>`;
            html += `<p><strong>搜索时间:</strong> ${data.search_time}秒</p>`;
            
            data.posts.forEach(post => {
                const isPromotional = post.is_promotional ? '<span class="error">[推广]</span>' : '';
                html += `
                    <div class="post-item">
                        <h4>${isPromotional} ${post.title}</h4>
                        <p><strong>Subreddit:</strong> r/${post.subreddit}</p>
                        <p><strong>作者:</strong> u/${post.author}</p>
                        <p><strong>评分:</strong> ${post.score} | <strong>评论:</strong> ${post.num_comments}</p>
                        <p><strong>时间:</strong> ${new Date(post.created_utc * 1000).toLocaleString()}</p>
                        <p><strong>链接:</strong> <a href="${post.url}" target="_blank">查看原帖</a></p>
                    </div>
                `;
            });
            
            searchResults.innerHTML = html;
        }
        
        // 回车键搜索
        document.getElementById('keywords').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchReddit();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """主页"""
    try:
        return render_template_string(HTML_TEMPLATE, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        return jsonify({
            "status": "ok",
            "message": "Reddit Data Collector - Vercel Enhanced",
            "timestamp": datetime.now().isoformat(),
            "environment": "Vercel",
            "note": "Enhanced version with full functionality"
        })

@app.route('/api/health')
def health():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "Vercel",
        "version": "2.0-enhanced",
        "uptime": "Running",
        "features": ["reddit_search", "promotional_detection", "api_endpoints"]
    })

@app.route('/api/status')
def status():
    """系统状态端点"""
    return jsonify({
        "status": "ok",
        "application": "Reddit Data Collector Enhanced",
        "environment": "Vercel",
        "version": "2.0-enhanced",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "reddit_api": "available",
            "search": "enabled",
            "promotional_detection": "enabled",
            "web_interface": "enabled"
        },
        "capabilities": [
            "Real-time Reddit search",
            "Multi-keyword support",
            "Promotional content detection",
            "RESTful API",
            "Modern web interface"
        ]
    })

@app.route('/api/search', methods=['POST'])
def search_reddit():
    """Reddit搜索端点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        keywords = data.get('keywords', [])
        subreddit = data.get('subreddit')
        limit = min(data.get('limit', 10), 100)  # 限制最大100个结果
        
        if not keywords:
            return jsonify({
                "status": "error",
                "message": "Keywords are required",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 检查Reddit API配置
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return jsonify({
                "status": "error",
                "message": "Reddit API credentials not configured",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 执行Reddit搜索
        search_start = datetime.now()
        posts = perform_reddit_search(keywords, subreddit, limit)
        search_time = (datetime.now() - search_start).total_seconds()
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(posts)} posts",
            "data": {
                "posts": posts,
                "search_time": round(search_time, 2),
                "keywords": keywords,
                "subreddit": subreddit,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

def perform_reddit_search(keywords, subreddit=None, limit=10):
    """执行Reddit搜索"""
    try:
        import praw
        
        # 初始化Reddit客户端
        reddit = praw.Reddit(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
        )
        
        posts = []
        search_query = ' OR '.join(keywords)
        
        # 选择搜索范围
        if subreddit:
            search_target = reddit.subreddit(subreddit)
        else:
            search_target = reddit.subreddit('all')
        
        # 执行搜索
        for submission in search_target.search(search_query, limit=limit, sort='relevance'):
            # 推广内容检测
            is_promotional = detect_promotional_content(submission.title, submission.selftext)
            
            post_data = {
                "reddit_id": submission.id,
                "title": submission.title,
                "author": str(submission.author) if submission.author else "[deleted]",
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "url": submission.url,
                "selftext": submission.selftext[:200] + "..." if len(submission.selftext) > 200 else submission.selftext,
                "is_promotional": is_promotional,
                "keywords_matched": [kw for kw in keywords if kw.lower() in submission.title.lower() or kw.lower() in submission.selftext.lower()]
            }
            posts.append(post_data)
        
        return posts
        
    except Exception as e:
        logger.error(f"Reddit search error: {e}")
        raise

def detect_promotional_content(title, content):
    """简单的推广内容检测"""
    promotional_keywords = [
        'buy', 'sale', 'discount', 'promo', 'deal', 'offer', 'free shipping',
        'limited time', 'click here', 'visit our', 'check out our',
        '购买', '销售', '折扣', '促销', '优惠', '免费', '限时', '点击'
    ]
    
    text = (title + ' ' + content).lower()
    return any(keyword in text for keyword in promotional_keywords)

@app.route('/api/reddit/test')
def reddit_test():
    """Reddit API连接测试"""
    try:
        # 检查环境变量
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return jsonify({
                "status": "error",
                "message": "Reddit API credentials not configured",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # 尝试导入praw并测试连接
        try:
            import praw
            
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent='RedditDataCollector/2.0 by /u/Aware-Blueberry-3586'
            )
            
            # 测试只读访问
            subreddit = reddit.subreddit('test')
            posts = list(subreddit.hot(limit=1))
            
            return jsonify({
                "status": "success",
                "message": "Reddit API connection successful",
                "mode": "read-only",
                "test_result": f"Successfully accessed r/test subreddit",
                "posts_found": len(posts),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as reddit_error:
            return jsonify({
                "status": "error",
                "message": "Reddit API connection failed",
                "error": str(reddit_error),
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error in reddit test: {e}")
        return jsonify({
            "status": "error",
            "message": "Reddit test endpoint error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": ["/", "/api/health", "/api/status", "/api/info", "/api/test"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat(),
        "note": "Check Vercel function logs for details"
    }), 500

if __name__ == '__main__':
    app.run(debug=False) 