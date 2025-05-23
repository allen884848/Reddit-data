"""
Vercel API Entry Point for Reddit Data Collector
===============================================

This file serves as the entry point for Vercel deployment.
It imports and exposes the Flask application for serverless deployment.
"""

import sys
import os
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Vercel环境变量
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'production'

try:
    # Import the Flask application
    from app import app
    logger.info("Flask application imported successfully")
    
    # Vercel expects the application to be named 'app'
    # This is the WSGI application that Vercel will use
    
except ImportError as e:
    logger.error(f"Failed to import Flask application: {e}")
    # 创建一个简单的备用应用
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "status": "error",
            "message": "Application import failed",
            "error": str(e)
        })
    
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "error",
            "message": "Application import failed",
            "timestamp": "2025-05-23T19:00:00Z"
        })

except Exception as e:
    logger.error(f"Unexpected error during application initialization: {e}")
    # 创建一个简单的备用应用
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            "status": "error",
            "message": "Application initialization failed",
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=False) 