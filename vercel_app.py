"""
Vercel Simplified Flask Application
==================================

A simplified version of the Reddit Data Collector for Vercel deployment.
This version includes only essential features to ensure reliable deployment.
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-reddit-collector-key-2025')

# 简单的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reddit Data Collector - Vercel</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #ff4500; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status { background: #f0f0f0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .api-list { background: #f9f9f9; padding: 15px; border-radius: 8px; }
        .api-endpoint { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Reddit Data Collector</h1>
        <p>Vercel部署版本 - 简化功能</p>
    </div>
    
    <div class="status">
        <h2>📊 系统状态</h2>
        <p><strong>部署环境:</strong> Vercel</p>
        <p><strong>状态:</strong> <span class="success">✅ 运行正常</span></p>
        <p><strong>时间:</strong> {{ timestamp }}</p>
        <p><strong>版本:</strong> Vercel Simplified v1.0</p>
    </div>
    
    <div class="api-list">
        <h2>🔗 API端点</h2>
        <div class="api-endpoint">
            <strong>GET /api/health</strong> - 健康检查
        </div>
        <div class="api-endpoint">
            <strong>GET /api/status</strong> - 系统状态
        </div>
        <div class="api-endpoint">
            <strong>GET /api/info</strong> - 应用信息
        </div>
        <div class="api-endpoint">
            <strong>POST /api/test</strong> - 测试端点
        </div>
    </div>
    
    <div class="status">
        <h2>⚠️ 注意事项</h2>
        <p>这是Vercel环境的简化版本，包含以下限制：</p>
        <ul>
            <li>数据库使用临时存储，重启后数据会丢失</li>
            <li>某些高级功能可能不可用</li>
            <li>Reddit API功能需要正确的环境变量配置</li>
        </ul>
    </div>
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
            "message": "Reddit Data Collector - Vercel",
            "timestamp": datetime.now().isoformat(),
            "environment": "Vercel",
            "note": "Simplified version for reliable deployment"
        })

@app.route('/api/health')
def health():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "Vercel",
        "version": "1.0-simplified",
        "uptime": "Running"
    })

@app.route('/api/status')
def status():
    """系统状态端点"""
    return jsonify({
        "status": "ok",
        "application": "Reddit Data Collector",
        "environment": "Vercel",
        "version": "1.0-simplified",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "reddit_api": "available",
            "database": "temporary",
            "search": "limited",
            "export": "basic"
        },
        "limitations": [
            "Temporary database storage",
            "Limited Reddit API functionality",
            "No persistent data storage"
        ]
    })

@app.route('/api/info')
def info():
    """应用信息端点"""
    return jsonify({
        "name": "Reddit Data Collector",
        "version": "1.0-simplified",
        "environment": "Vercel",
        "deployment": "Serverless",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            {"path": "/", "method": "GET", "description": "主页"},
            {"path": "/api/health", "method": "GET", "description": "健康检查"},
            {"path": "/api/status", "method": "GET", "description": "系统状态"},
            {"path": "/api/info", "method": "GET", "description": "应用信息"},
            {"path": "/api/test", "method": "POST", "description": "测试端点"}
        ],
        "reddit_config": {
            "client_id_set": bool(os.environ.get('REDDIT_CLIENT_ID')),
            "client_secret_set": bool(os.environ.get('REDDIT_CLIENT_SECRET')),
            "username_set": bool(os.environ.get('REDDIT_USERNAME')),
            "password_set": bool(os.environ.get('REDDIT_PASSWORD'))
        }
    })

@app.route('/api/test', methods=['POST'])
def test():
    """测试端点"""
    try:
        data = request.get_json() if request.is_json else {}
        return jsonify({
            "status": "success",
            "message": "Test endpoint working",
            "timestamp": datetime.now().isoformat(),
            "received_data": data,
            "environment": "Vercel"
        })
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": "Test endpoint error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

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
                user_agent='RedditDataCollector/1.0 by /u/Aware-Blueberry-3586'
            )
            
            # 测试只读访问
            subreddit = reddit.subreddit('test')
            post_count = len(list(subreddit.hot(limit=1)))
            
            return jsonify({
                "status": "success",
                "message": "Reddit API connection successful",
                "mode": "read-only",
                "test_result": f"Retrieved {post_count} post(s)",
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