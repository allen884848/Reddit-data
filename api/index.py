"""
Vercel API Entry Point for Reddit Data Collector
===============================================

This file serves as the entry point for Vercel deployment.
It imports and exposes the Flask application for serverless deployment.
"""

import sys
import os
import logging
import traceback

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Vercel环境变量
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'production'

# 创建一个简单的Flask应用作为备用
from flask import Flask, jsonify

def create_emergency_app():
    """创建紧急备用Flask应用"""
    emergency_app = Flask(__name__)
    
    @emergency_app.route('/')
    def home():
        return jsonify({
            "status": "emergency_mode",
            "message": "Reddit Data Collector - Emergency Mode",
            "timestamp": "2025-05-23T19:30:00Z",
            "environment": "Vercel",
            "note": "All imports failed, running in emergency mode"
        })
    
    @emergency_app.route('/api/health')
    def health():
        return jsonify({
            "status": "emergency",
            "message": "Emergency mode active",
            "timestamp": "2025-05-23T19:30:00Z"
        })
    
    @emergency_app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Endpoint not found - Emergency mode",
            "available": ["/", "/api/health"]
        }), 404
    
    return emergency_app

# 尝试导入应用（按优先级顺序）
app = None

# 第一优先级：尝试导入简化的Vercel应用
try:
    logger.info("Attempting to import simplified Vercel application...")
    from vercel_app import app
    logger.info("✅ Simplified Vercel application imported successfully")
    
except ImportError as e:
    logger.warning(f"Failed to import simplified Vercel app: {e}")
    
    # 第二优先级：尝试导入完整的主应用
    try:
        logger.info("Attempting to import full Flask application...")
        
        # 首先尝试导入配置模块
        try:
            from vercel_config import get_config, DATABASE_CONFIG, REDDIT_CONFIG
            logger.info("Vercel config imported successfully")
        except ImportError:
            try:
                from config import get_config, DATABASE_CONFIG, REDDIT_CONFIG
                logger.info("Main config imported successfully")
            except ImportError as config_error:
                logger.error(f"Failed to import any config: {config_error}")
        
        # 然后尝试导入主应用
        from app import app
        logger.info("✅ Full Flask application imported successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import full application: {e}")
        logger.error(f"Import traceback: {traceback.format_exc()}")
        
        # 第三优先级：创建紧急备用应用
        logger.info("Creating emergency fallback application...")
        app = create_emergency_app()
        logger.info("✅ Emergency application created")

except Exception as e:
    logger.error(f"Unexpected error during application import: {e}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    
    # 创建紧急备用应用
    logger.info("Creating emergency fallback application due to unexpected error...")
    app = create_emergency_app()
    logger.info("✅ Emergency application created")

# 确保app变量存在
if app is None:
    logger.error("No app variable defined, creating emergency fallback")
    app = create_emergency_app()

# 验证应用是否可以正常工作
try:
    with app.test_client() as client:
        response = client.get('/api/health')
        logger.info(f"Health check response status: {response.status_code}")
        if response.status_code == 200:
            logger.info("✅ Application health check passed")
        else:
            logger.warning(f"⚠️ Application health check returned status {response.status_code}")
except Exception as e:
    logger.error(f"Application health check failed: {e}")

logger.info("🚀 Vercel application initialization completed")

if __name__ == "__main__":
    app.run(debug=False) 