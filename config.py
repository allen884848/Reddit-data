"""
Reddit Data Collection Website Configuration
===========================================

This configuration file contains all the necessary settings for the Reddit data collection application.
Please update the values according to your environment and Reddit API credentials.

Author: Reddit Data Collector Team
Version: 1.0
Last Updated: 2024
"""

import os
from datetime import timedelta

# =============================================================================
# REDDIT API CONFIGURATION
# =============================================================================

# Reddit API credentials - REQUIRED
# Get these from: https://www.reddit.com/prefs/apps
REDDIT_CONFIG = {
    # Your Reddit app client ID (found under your app name)
    'client_id': os.getenv('REDDIT_CLIENT_ID', 'eyB_HEwp6ttuc0UInIv_og'),
    
    # Your Reddit app client secret
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET', 'tHIoRB0ucx0Q95XdxSg2-WyD5F01_w'),
    
    # User agent string - should be unique and descriptive
    # Format: <platform>:<app ID>:<version string> (by /u/<reddit username>)
    'user_agent': 'RedditDataCollector/2.0 by /u/Aware-Blueberry-3586',
    
    # Reddit username (required for script applications)
    'username': os.getenv('REDDIT_USERNAME', 'Aware-Blueberry-3586'),
    
    # Reddit password (required for script applications)
    'password': os.getenv('REDDIT_PASSWORD', 'Liu@8848'),
}

# Reddit API rate limiting settings
REDDIT_RATE_LIMIT = {
    # Maximum requests per minute (Reddit allows 60/minute)
    'requests_per_minute': 60,
    
    # Delay between requests in seconds
    'request_delay': 1.0,
    
    # Maximum retries for failed requests
    'max_retries': 3,
    
    # Exponential backoff multiplier for retries
    'backoff_factor': 2,
    
    # Timeout for API requests in seconds
    'timeout': 30,
}

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DATABASE_CONFIG = {
    # SQLite database file path
    'database_path': os.path.join(os.path.dirname(__file__), 'reddit_data.db'),
    
    # Enable automatic database backups
    'backup_enabled': True,
    
    # Backup interval in hours
    'backup_interval': 24,
    
    # Maximum number of backup files to keep
    'max_backups': 7,
    
    # Backup directory path
    'backup_directory': os.path.join(os.path.dirname(__file__), 'backups'),
    
    # Database connection timeout in seconds
    'connection_timeout': 30,
    
    # Enable WAL mode for better concurrent access
    'enable_wal_mode': True,
    
    # Database pragma settings for optimization
    'pragma_settings': {
        'journal_mode': 'WAL',
        'synchronous': 'NORMAL',
        'cache_size': -64000,  # 64MB cache
        'temp_store': 'MEMORY',
        'mmap_size': 268435456,  # 256MB memory map
    }
}

# =============================================================================
# FLASK APPLICATION CONFIGURATION
# =============================================================================

class Config:
    """Base configuration class for Flask application"""
    
    # Flask secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Debug mode - set to False in production
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Testing mode
    TESTING = False
    
    # Application host and port
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # JSON configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Use environment variables for sensitive data in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Validate that SECRET_KEY is set in production
    def __init__(self):
        if not self.SECRET_KEY:
            import warnings
            warnings.warn("SECRET_KEY environment variable should be set in production")
            self.SECRET_KEY = 'fallback-secret-key-change-this-in-production'

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory database for testing
    DATABASE_CONFIG = {
        'database_path': ':memory:',
        'backup_enabled': False,
    }

# =============================================================================
# VERCEL DEPLOYMENT CONFIGURATION
# =============================================================================

class VercelConfig(Config):
    """Vercel deployment configuration"""
    DEBUG = False
    TESTING = False
    
    # Use environment variables for all sensitive data
    SECRET_KEY = os.getenv('SECRET_KEY', 'vercel-production-secret-key')
    
    # Vercel-specific settings
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 3000))
    
    # Database configuration for Vercel
    # Note: Vercel functions are stateless, so we'll use a different approach
    DATABASE_PATH = '/tmp/reddit_data.db'  # Temporary storage in Vercel
    
    def __init__(self):
        # Ensure required environment variables are set
        required_env_vars = [
            'REDDIT_CLIENT_ID',
            'REDDIT_CLIENT_SECRET',
            'REDDIT_USERNAME',
            'REDDIT_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            import warnings
            warnings.warn(f"Missing environment variables for Vercel deployment: {', '.join(missing_vars)}")

# Configuration mapping
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'vercel': VercelConfig,
    'default': DevelopmentConfig
}

# =============================================================================
# SEARCH AND COLLECTION SETTINGS
# =============================================================================

SEARCH_CONFIG = {
    # Default search parameters
    'default_limit': 100,
    'max_limit': 1000,
    'default_time_filter': 'week',  # hour, day, week, month, year, all
    'default_sort': 'relevance',    # relevance, hot, top, new, comments
    
    # Subreddit filtering
    'default_subreddits': ['all'],
    'blocked_subreddits': [],  # Add subreddits to exclude from searches
    
    # Content filtering
    'min_score': 0,
    'min_comments': 0,
    'max_title_length': 300,
    'max_content_length': 10000,
    
    # Search history settings
    'max_search_history': 1000,
    'cleanup_history_days': 30,
}

# =============================================================================
# PROMOTIONAL CONTENT DETECTION
# =============================================================================

PROMOTIONAL_DETECTION = {
    # Enable automatic promotional content detection
    'enabled': True,
    
    # Promotional keywords and phrases
    'promotional_keywords': [
        'buy now', 'click here', 'limited time', 'special offer', 'discount',
        'promo code', 'affiliate', 'sponsored', 'advertisement', 'ad',
        'sale', 'deal', 'coupon', 'free trial', 'sign up', 'register',
        'download now', 'get started', 'learn more', 'visit our',
        'check out our', 'follow us', 'subscribe', 'join our'
    ],
    
    # Suspicious URL patterns
    'suspicious_url_patterns': [
        r'bit\.ly', r'tinyurl', r'goo\.gl', r't\.co', r'ow\.ly',
        r'affiliate', r'ref=', r'utm_', r'tracking', r'campaign'
    ],
    
    # Minimum confidence score for promotional classification (0.0 - 1.0)
    'confidence_threshold': 0.7,
    
    # Weight factors for different detection criteria
    'weight_factors': {
        'keyword_density': 0.4,
        'url_analysis': 0.3,
        'author_behavior': 0.2,
        'content_structure': 0.1
    }
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING_CONFIG = {
    # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    
    # Log file path
    'file_path': os.path.join(os.path.dirname(__file__), 'logs', 'reddit_collector.log'),
    
    # Log file rotation settings
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    
    # Log format
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    
    # Enable console logging
    'console_logging': True,
    
    # Enable file logging
    'file_logging': True,
}

# =============================================================================
# EXPORT CONFIGURATION
# =============================================================================

EXPORT_CONFIG = {
    # Supported export formats
    'supported_formats': ['csv', 'json', 'xlsx'],
    
    # Default export format
    'default_format': 'csv',
    
    # Export file settings
    'max_export_size': 50000,  # Maximum number of records per export
    'export_directory': os.path.join(os.path.dirname(__file__), 'exports'),
    
    # CSV export settings
    'csv_settings': {
        'delimiter': ',',
        'quotechar': '"',
        'encoding': 'utf-8-sig',  # UTF-8 with BOM for Excel compatibility
        'include_headers': True,
    },
    
    # JSON export settings
    'json_settings': {
        'indent': 2,
        'ensure_ascii': False,
        'sort_keys': True,
    }
}

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

SECURITY_CONFIG = {
    # Enable CSRF protection
    'csrf_enabled': True,
    
    # Allowed file extensions for uploads
    'allowed_extensions': {'txt', 'csv', 'json'},
    
    # Rate limiting for web requests
    'rate_limit': {
        'enabled': True,
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
    },
    
    # Input validation settings
    'validation': {
        'max_keyword_length': 100,
        'max_keywords_count': 20,
        'max_subreddit_length': 50,
        'max_subreddits_count': 10,
    }
}

# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

CACHE_CONFIG = {
    # Enable caching
    'enabled': True,
    
    # Cache type (simple, redis, memcached)
    'cache_type': 'simple',
    
    # Cache timeout in seconds
    'default_timeout': 300,  # 5 minutes
    
    # Cache key prefix
    'key_prefix': 'reddit_collector_',
    
    # Redis configuration (if using Redis cache)
    'redis_config': {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': int(os.getenv('REDIS_DB', 0)),
        'password': os.getenv('REDIS_PASSWORD', None),
    }
}

# =============================================================================
# ENVIRONMENT DETECTION
# =============================================================================

def get_config():
    """
    Get the appropriate configuration based on the environment.
    
    Returns:
        Config: Configuration class instance
    """
    # Check if running on Vercel
    if os.getenv('VERCEL') == '1':
        return VercelConfig()
    
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config_mapping.get(env, config_mapping['default'])
    return config_class()

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_config():
    """
    Validate the configuration settings and check for required values.
    
    Raises:
        ValueError: If required configuration values are missing or invalid
    """
    # Check Reddit API credentials
    if REDDIT_CONFIG['client_id'] == 'your_client_id_here':
        raise ValueError("Reddit client_id must be configured")
    
    if REDDIT_CONFIG['client_secret'] == 'your_client_secret_here':
        raise ValueError("Reddit client_secret must be configured")
    
    # Check database path
    db_dir = os.path.dirname(DATABASE_CONFIG['database_path'])
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Check backup directory
    if DATABASE_CONFIG['backup_enabled']:
        backup_dir = DATABASE_CONFIG['backup_directory']
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
    
    # Check export directory
    export_dir = EXPORT_CONFIG['export_directory']
    if not os.path.exists(export_dir):
        os.makedirs(export_dir, exist_ok=True)
    
    # Check log directory
    log_dir = os.path.dirname(LOGGING_CONFIG['file_path'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

# =============================================================================
# INITIALIZATION
# =============================================================================

# Validate configuration on import
if __name__ != '__main__':
    try:
        validate_config()
    except Exception as e:
        print(f"Configuration validation warning: {e}")

# Export commonly used configurations
__all__ = [
    'REDDIT_CONFIG',
    'REDDIT_RATE_LIMIT',
    'DATABASE_CONFIG',
    'SEARCH_CONFIG',
    'PROMOTIONAL_DETECTION',
    'LOGGING_CONFIG',
    'EXPORT_CONFIG',
    'SECURITY_CONFIG',
    'CACHE_CONFIG',
    'Config',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'get_config',
    'validate_config'
] 