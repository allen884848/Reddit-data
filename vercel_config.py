"""
Vercel Environment Configuration
===============================

Simplified configuration for Vercel deployment to avoid import issues.
"""

import os
from datetime import datetime

class VercelConfig:
    """Vercel环境专用配置"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'vercel-reddit-collector-key-2025')
    DEBUG = False
    TESTING = False
    
    # Reddit API配置
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', 'eyB_HEwp6ttuc0UInIv_og')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', 'tHIoRB0ucx0Q95XdxSg2-WyD5F01_w')
    REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME', 'Aware-Blueberry-3586')
    REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD', 'Liu@8848')
    REDDIT_USER_AGENT = 'RedditDataCollector/1.0 by /u/Aware-Blueberry-3586'
    
    # 数据库配置（Vercel环境使用内存数据库）
    DATABASE_PATH = '/tmp/reddit_data_vercel.db'
    
    # 搜索配置
    DEFAULT_LIMIT = 25
    MAX_LIMIT = 100
    DEFAULT_TIME_FILTER = 'week'
    
    # 安全配置
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 3600  # 1小时
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def get_reddit_config(cls):
        """获取Reddit API配置"""
        return {
            'client_id': cls.REDDIT_CLIENT_ID,
            'client_secret': cls.REDDIT_CLIENT_SECRET,
            'username': cls.REDDIT_USERNAME,
            'password': cls.REDDIT_PASSWORD,
            'user_agent': cls.REDDIT_USER_AGENT
        }
    
    @classmethod
    def get_database_config(cls):
        """获取数据库配置"""
        return {
            'database_path': cls.DATABASE_PATH,
            'backup_enabled': False,  # Vercel环境不支持持久化
            'auto_backup_interval': 0
        }

# 导出配置实例
vercel_config = VercelConfig()

# 兼容性函数
def get_config():
    """获取配置实例"""
    return vercel_config

# 配置字典（兼容原有代码）
REDDIT_CONFIG = vercel_config.get_reddit_config()
DATABASE_CONFIG = vercel_config.get_database_config()

# 日志配置
LOGGING_CONFIG = {
    'level': vercel_config.LOG_LEVEL,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_enabled': False,  # Vercel环境不支持文件日志
    'console_enabled': True
} 