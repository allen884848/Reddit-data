"""
Reddit Data Collection Website - Enhanced Flask Application
==========================================================

This is the enhanced Flask application file for the Reddit data collection website.
It provides a comprehensive web interface and RESTful API endpoints for collecting,
analyzing, and managing Reddit data with full integration of the Reddit scraper.

Features:
- Complete RESTful API for Reddit data collection
- Real-time Reddit post searching and collection
- Promotional content detection and analysis
- Advanced filtering and sorting options
- Data export functionality (CSV, JSON)
- Comprehensive error handling and logging
- Rate limiting and security features
- Real-time statistics and monitoring

Author: Reddit Data Collector Team
Version: 2.0
Last Updated: 2024
"""

from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import json
import threading
import time
from typing import Dict, Any, List, Optional
import traceback

# Import our custom modules
from config import (
    REDDIT_CONFIG, REDDIT_RATE_LIMIT, DATABASE_CONFIG, SEARCH_CONFIG,
    PROMOTIONAL_DETECTION, LOGGING_CONFIG, EXPORT_CONFIG, SECURITY_CONFIG,
    get_config
)
from database import get_database_manager, RedditPost, SearchHistory
from reddit_scraper import (
    RedditScraper, SearchParameters, create_search_parameters, 
    validate_search_parameters, ScrapingResult
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    datefmt=LOGGING_CONFIG['date_format']
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Enable CORS for API access
CORS(app)

# Initialize components
db_manager = get_database_manager()
reddit_scraper = None

# Global statistics tracking
app_stats = {
    'total_api_calls': 0,
    'successful_searches': 0,
    'failed_searches': 0,
    'posts_collected': 0,
    'promotional_posts_found': 0,
    'app_start_time': datetime.now(),
    'last_search_time': None
}

# Thread lock for statistics
stats_lock = threading.Lock()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def update_stats(stat_name: str, increment: int = 1) -> None:
    """Thread-safe statistics update."""
    with stats_lock:
        if stat_name in app_stats:
            app_stats[stat_name] += increment
        else:
            app_stats[stat_name] = increment

def get_reddit_scraper() -> RedditScraper:
    """Get or create Reddit scraper instance."""
    global reddit_scraper
    if reddit_scraper is None:
        try:
            reddit_scraper = RedditScraper()
            logger.info("Reddit scraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit scraper: {e}")
            raise
    return reddit_scraper

def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate request data for required fields."""
    errors = []
    
    if not data:
        errors.append("No data provided")
        return False, errors
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not data[field]:
            errors.append(f"Field '{field}' cannot be empty")
    
    return len(errors) == 0, errors

def handle_api_error(error: Exception, operation: str) -> tuple[Dict[str, Any], int]:
    """Standardized API error handling."""
    error_id = f"ERR_{int(time.time())}"
    error_msg = str(error)
    
    logger.error(f"API Error [{error_id}] in {operation}: {error_msg}")
    logger.debug(f"Traceback: {traceback.format_exc()}")
    
    update_stats('api_errors')
    
    return {
        'status': 'error',
        'error_id': error_id,
        'message': error_msg,
        'operation': operation,
        'timestamp': datetime.now().isoformat()
    }, 500

# =============================================================================
# ROUTE HANDLERS
# =============================================================================

@app.route('/')
def home():
    """Enhanced home page with comprehensive system overview."""
    try:
        update_stats('total_api_calls')
        
        # Get database statistics
        stats = db_manager.get_database_stats()
        
        # Check configuration status
        config_status = (
            REDDIT_CONFIG['client_id'] != 'your_client_id_here' and
            REDDIT_CONFIG['client_secret'] != 'your_client_secret_here'
        )
        
        # Calculate uptime
        uptime = datetime.now() - app_stats['app_start_time']
        uptime_hours = int(uptime.total_seconds() / 3600)
        
        if config_status:
            status_message = "🟢 System operational - Reddit API configured and ready for data collection"
        else:
            status_message = "🟡 System ready - Please configure Reddit API credentials to start collecting data"
        
        return render_template(
            'index.html',
            stats=stats,
            app_stats=app_stats,
            config_status=config_status,
            status_message=status_message,
            uptime_hours=uptime_hours,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        error_response, status_code = handle_api_error(e, "home_page_load")
        return render_template(
            'index.html',
            stats={'total_posts': 0, 'promotional_posts': 0, 'unique_subreddits': 0, 'total_searches': 0},
            app_stats=app_stats,
            config_status=False,
            status_message=f"🔴 System error: {str(e)}",
            uptime_hours=0,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ), 500

@app.route('/api/health')
def api_health():
    """Health check endpoint for monitoring."""
    try:
        update_stats('total_api_calls')
        
        # Test database connection
        db_stats = db_manager.get_database_stats()
        
        # Test Reddit API if configured
        reddit_status = "not_configured"
        if (REDDIT_CONFIG['client_id'] != 'your_client_id_here' and 
            REDDIT_CONFIG['client_secret'] != 'your_client_secret_here'):
            try:
                scraper = get_reddit_scraper()
                reddit_status = "operational"
            except Exception:
                reddit_status = "error"
        
        uptime_seconds = (datetime.now() - app_stats['app_start_time']).total_seconds()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime_seconds,
            'components': {
                'database': 'operational',
                'reddit_api': reddit_status,
                'web_server': 'operational'
            },
            'metrics': {
                'total_posts': db_stats['total_posts'],
                'api_calls': app_stats['total_api_calls'],
                'memory_usage': 'available'  # Could add actual memory monitoring
            }
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "health_check")
        return jsonify(error_response), status_code

@app.route('/api/status')
def api_status():
    """Get comprehensive system status and statistics."""
    try:
        update_stats('total_api_calls')
        
        stats = db_manager.get_database_stats()
        
        config_status = (
            REDDIT_CONFIG['client_id'] != 'your_client_id_here' and
            REDDIT_CONFIG['client_secret'] != 'your_client_secret_here'
        )
        
        # Get Reddit scraper statistics if available
        reddit_stats = {}
        if config_status:
            try:
                scraper = get_reddit_scraper()
                reddit_stats = scraper.get_session_statistics()
            except Exception as e:
                logger.warning(f"Could not get Reddit scraper stats: {e}")
        
        uptime_seconds = (datetime.now() - app_stats['app_start_time']).total_seconds()
        
        return jsonify({
            'status': 'success',
            'message': 'System is operational',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime_seconds,
            'configuration': {
                'reddit_api_configured': config_status,
                'database_connected': True,
                'promotional_detection_enabled': True
            },
            'statistics': {
                'database': stats,
                'application': app_stats,
                'reddit_scraper': reddit_stats
            }
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "status_check")
        return jsonify(error_response), status_code

@app.route('/api/search', methods=['POST'])
def api_search_posts():
    """Enhanced Reddit post search with full scraper integration."""
    try:
        update_stats('total_api_calls')
        
        data = request.get_json()
        
        # Validate request data
        is_valid, errors = validate_request_data(data, ['keywords'])
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': 'Invalid request data',
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Create search parameters
        try:
            search_params = create_search_parameters(
                keywords=data['keywords'],
                subreddits=data.get('subreddits', ['all']),
                time_filter=data.get('time_filter', 'week'),
                sort=data.get('sort', 'relevance'),
                limit=min(int(data.get('limit', 100)), 1000),
                include_nsfw=data.get('include_nsfw', False),
                min_score=data.get('min_score', 0),
                min_comments=data.get('min_comments', 0)
            )
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Invalid search parameters: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Validate search parameters
        is_valid, validation_errors = validate_search_parameters(search_params)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': 'Invalid search parameters',
                'errors': validation_errors,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Perform the search
        scraper = get_reddit_scraper()
        app_stats['last_search_time'] = datetime.now()
        
        logger.info(f"Starting Reddit search with keywords: {search_params.keywords}")
        result = scraper.search_posts(search_params)
        
        # Update statistics
        if result.errors:
            update_stats('failed_searches')
        else:
            update_stats('successful_searches')
        
        update_stats('posts_collected', result.total_processed)
        update_stats('promotional_posts_found', result.promotional_count)
        
        # Convert posts to dictionaries for JSON response
        posts_data = []
        for post in result.posts:
            post_dict = {
                'id': post.id,
                'reddit_id': post.reddit_id,
                'title': post.title,
                'content': post.content,
                'author': post.author,
                'subreddit': post.subreddit,
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': post.created_utc.isoformat() if post.created_utc else None,
                'url': post.url,
                'is_promotional': post.is_promotional,
                'collected_at': post.collected_at.isoformat() if post.collected_at else None
            }
            posts_data.append(post_dict)
        
        response_data = {
            'status': 'success',
            'message': f'Search completed successfully. Found {result.total_processed} posts.',
            'search_id': result.search_id,
            'results': {
                'posts': posts_data,
                'total_found': result.total_found,
                'total_processed': result.total_processed,
                'promotional_count': result.promotional_count,
                'execution_time': result.execution_time
            },
            'search_parameters': {
                'keywords': search_params.keywords,
                'subreddits': search_params.subreddits,
                'time_filter': search_params.time_filter,
                'sort': search_params.sort,
                'limit': search_params.limit,
                'filters_applied': {
                    'min_score': search_params.min_score,
                    'min_comments': search_params.min_comments,
                    'include_nsfw': search_params.include_nsfw
                }
            },
            'errors': result.errors,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        update_stats('failed_searches')
        error_response, status_code = handle_api_error(e, "reddit_search")
        return jsonify(error_response), status_code

@app.route('/api/collect-promotional', methods=['POST'])
def api_collect_promotional():
    """Collect posts specifically targeting promotional content."""
    try:
        update_stats('total_api_calls')
        
        data = request.get_json() or {}
        
        subreddits = data.get('subreddits', ['all'])
        limit = min(int(data.get('limit', 100)), 1000)
        
        # Perform promotional post collection
        scraper = get_reddit_scraper()
        app_stats['last_search_time'] = datetime.now()
        
        logger.info(f"Starting promotional post collection in subreddits: {subreddits}")
        result = scraper.collect_promotional_posts(subreddits, limit)
        
        # Update statistics
        if result.errors:
            update_stats('failed_searches')
        else:
            update_stats('successful_searches')
        
        update_stats('posts_collected', result.total_processed)
        update_stats('promotional_posts_found', result.promotional_count)
        
        # Convert posts to dictionaries
        posts_data = []
        for post in result.posts:
            post_dict = {
                'id': post.id,
                'reddit_id': post.reddit_id,
                'title': post.title,
                'content': post.content,
                'author': post.author,
                'subreddit': post.subreddit,
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': post.created_utc.isoformat() if post.created_utc else None,
                'url': post.url,
                'is_promotional': post.is_promotional,
                'collected_at': post.collected_at.isoformat() if post.collected_at else None
            }
            posts_data.append(post_dict)
        
        return jsonify({
            'status': 'success',
            'message': f'Promotional post collection completed. Found {result.promotional_count} promotional posts out of {result.total_processed} total posts.',
            'search_id': result.search_id,
            'results': {
                'posts': posts_data,
                'total_found': result.total_found,
                'total_processed': result.total_processed,
                'promotional_count': result.promotional_count,
                'promotional_percentage': (result.promotional_count / max(result.total_processed, 1)) * 100,
                'execution_time': result.execution_time
            },
            'collection_parameters': {
                'subreddits': subreddits,
                'limit': limit,
                'target': 'promotional_content'
            },
            'errors': result.errors,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        update_stats('failed_searches')
        error_response, status_code = handle_api_error(e, "promotional_collection")
        return jsonify(error_response), status_code

@app.route('/api/posts')
def api_get_posts():
    """Get collected posts with enhanced filtering and pagination."""
    try:
        update_stats('total_api_calls')
        
        # Get query parameters with validation
        try:
            limit = min(int(request.args.get('limit', 50)), 1000)
            offset = max(int(request.args.get('offset', 0)), 0)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid limit or offset parameter',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        subreddit = request.args.get('subreddit')
        is_promotional = request.args.get('is_promotional')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert parameters
        if is_promotional is not None:
            is_promotional = is_promotional.lower() in ('true', '1', 'yes')
        
        # Parse dates
        start_date_obj = None
        end_date_obj = None
        if start_date:
            try:
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        if end_date:
            try:
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        # Get posts from database
        posts = db_manager.get_posts(
            limit=limit,
            offset=offset,
            subreddit=subreddit,
            is_promotional=is_promotional,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        
        # Convert posts to dictionaries
        posts_data = []
        for post in posts:
            post_dict = {
                'id': post.id,
                'reddit_id': post.reddit_id,
                'title': post.title,
                'content': post.content,
                'author': post.author,
                'subreddit': post.subreddit,
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': post.created_utc.isoformat() if post.created_utc else None,
                'url': post.url,
                'is_promotional': post.is_promotional,
                'collected_at': post.collected_at.isoformat() if post.collected_at else None
            }
            posts_data.append(post_dict)
        
        return jsonify({
            'status': 'success',
            'data': posts_data,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_returned': len(posts_data),
                'has_more': len(posts_data) == limit
            },
            'filters_applied': {
                'subreddit': subreddit,
                'is_promotional': is_promotional,
                'start_date': start_date,
                'end_date': end_date
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_posts")
        return jsonify(error_response), status_code

@app.route('/api/posts/<reddit_id>')
def api_get_post_details(reddit_id: str):
    """Get detailed information about a specific post."""
    try:
        update_stats('total_api_calls')
        
        post = db_manager.get_post_by_reddit_id(reddit_id)
        
        if not post:
            return jsonify({
                'status': 'error',
                'message': f'Post with Reddit ID "{reddit_id}" not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        post_dict = {
            'id': post.id,
            'reddit_id': post.reddit_id,
            'title': post.title,
            'content': post.content,
            'author': post.author,
            'subreddit': post.subreddit,
            'score': post.score,
            'num_comments': post.num_comments,
            'created_utc': post.created_utc.isoformat() if post.created_utc else None,
            'url': post.url,
            'is_promotional': post.is_promotional,
            'collected_at': post.collected_at.isoformat() if post.collected_at else None
        }
        
        return jsonify({
            'status': 'success',
            'data': post_dict,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_post_details")
        return jsonify(error_response), status_code

@app.route('/api/history')
def api_get_history():
    """Get search history with enhanced information."""
    try:
        update_stats('total_api_calls')
        
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        
        history = db_manager.get_search_history(limit=limit, offset=offset)
        
        # Convert history to dictionaries
        history_data = []
        for record in history:
            record_dict = {
                'id': record.id,
                'keywords': record.keywords,
                'subreddits': record.subreddits,
                'time_filter': record.time_filter,
                'post_limit': record.post_limit,
                'results_count': record.results_count,
                'search_date': record.search_date.isoformat() if record.search_date else None,
                'status': record.status
            }
            history_data.append(record_dict)
        
        return jsonify({
            'status': 'success',
            'data': history_data,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total_returned': len(history_data)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_search_history")
        return jsonify(error_response), status_code

@app.route('/api/export')
def api_export_data():
    """Enhanced data export with advanced filtering."""
    try:
        update_stats('total_api_calls')
        
        export_format = request.args.get('format', 'csv').lower()
        
        if export_format not in ['csv', 'json']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid format. Supported formats: csv, json',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Build filters
        filters = {}
        if request.args.get('subreddit'):
            filters['subreddit'] = request.args.get('subreddit')
        
        if request.args.get('is_promotional'):
            filters['is_promotional'] = request.args.get('is_promotional').lower() in ('true', '1', 'yes')
        
        if request.args.get('start_date'):
            try:
                filters['start_date'] = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid start_date format',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        if request.args.get('end_date'):
            try:
                filters['end_date'] = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid end_date format',
                    'timestamp': datetime.now().isoformat()
                }), 400
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_data_export_{timestamp}.{export_format}"
        
        # Export data
        if export_format == 'csv':
            filepath = db_manager.export_posts_to_csv(filename, filters)
        else:
            filepath = db_manager.export_posts_to_json(filename, filters)
        
        return jsonify({
            'status': 'success',
            'message': 'Data exported successfully',
            'export_info': {
                'filename': filename,
                'filepath': filepath,
                'format': export_format,
                'filters_applied': filters,
                'download_url': f'/api/download/{filename}'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "data_export")
        return jsonify(error_response), status_code

@app.route('/api/download/<filename>')
def api_download_file(filename: str):
    """Download exported files."""
    try:
        update_stats('total_api_calls')
        
        # Security check - only allow files from export directory
        if not filename or '..' in filename or '/' in filename:
            return jsonify({
                'status': 'error',
                'message': 'Invalid filename',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        from config import EXPORT_CONFIG
        filepath = os.path.join(EXPORT_CONFIG['export_directory'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'File not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "file_download")
        return jsonify(error_response), status_code

@app.route('/api/statistics')
def api_get_statistics():
    """Get comprehensive system and collection statistics."""
    try:
        update_stats('total_api_calls')
        
        # Get database statistics
        db_stats = db_manager.get_database_stats()
        
        # Get Reddit scraper statistics if available
        reddit_stats = {}
        try:
            if reddit_scraper:
                reddit_stats = reddit_scraper.get_session_statistics()
        except Exception as e:
            logger.debug(f"Could not get Reddit scraper stats: {e}")
        
        # Calculate additional metrics
        uptime_seconds = (datetime.now() - app_stats['app_start_time']).total_seconds()
        
        success_rate = 0
        if app_stats['successful_searches'] + app_stats['failed_searches'] > 0:
            success_rate = (app_stats['successful_searches'] / 
                          (app_stats['successful_searches'] + app_stats['failed_searches'])) * 100
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'database': db_stats,
                'application': {
                    **app_stats,
                    'uptime_seconds': uptime_seconds,
                    'uptime_hours': uptime_seconds / 3600,
                    'search_success_rate': round(success_rate, 2),
                    'avg_posts_per_search': (app_stats['posts_collected'] / 
                                           max(app_stats['successful_searches'], 1))
                },
                'reddit_scraper': reddit_stats,
                'performance': {
                    'api_calls_per_hour': (app_stats['total_api_calls'] / max(uptime_seconds / 3600, 1)),
                    'posts_per_hour': (app_stats['posts_collected'] / max(uptime_seconds / 3600, 1)),
                    'promotional_detection_rate': (app_stats['promotional_posts_found'] / 
                                                 max(app_stats['posts_collected'], 1)) * 100
                }
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_response, status_code = handle_api_error(e, "get_statistics")
        return jsonify(error_response), status_code

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    update_stats('total_api_calls')
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': [
            '/api/status', '/api/search', '/api/posts', '/api/history',
            '/api/export', '/api/statistics', '/api/health'
        ],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    update_stats('total_api_calls')
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed for this endpoint',
        'timestamp': datetime.now().isoformat()
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    update_stats('total_api_calls')
    update_stats('api_errors')
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

def initialize_application():
    """Initialize application components."""
    try:
        logger.info("Initializing Reddit Data Collection Website...")
        
        # Test database connection
        db_stats = db_manager.get_database_stats()
        logger.info(f"Database connected successfully. Total posts: {db_stats['total_posts']}")
        
        # Test Reddit API if configured
        if (REDDIT_CONFIG['client_id'] != 'your_client_id_here' and 
            REDDIT_CONFIG['client_secret'] != 'your_client_secret_here'):
            try:
                scraper = get_reddit_scraper()
                logger.info("Reddit API client initialized successfully")
            except Exception as e:
                logger.warning(f"Reddit API initialization failed: {e}")
        else:
            logger.warning("Reddit API not configured - some features will be unavailable")
        
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise

# Vercel deployment support
def create_app():
    """Create and configure the Flask application for deployment."""
    return app

# For Vercel deployment
application = app

if __name__ == '__main__':
    try:
        # Get configuration
        config_class = get_config()
        
        # For local development
        if os.getenv('VERCEL') != '1':
            logger.info("Starting Reddit Data Collection Website...")
            logger.info(f"Configuration: {type(config_class).__name__}")
            logger.info(f"Database path: {DATABASE_CONFIG['database_path']}")
            logger.info(f"Server will run on {config_class.HOST}:{config_class.PORT}")
            
            app.run(
                host=config_class.HOST,
                port=config_class.PORT,
                debug=config_class.DEBUG,
                threaded=True
            )
        else:
            # For Vercel deployment
            logger.info("Application configured for Vercel deployment")
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Cleanup
        try:
            if 'scraper' in globals():
                scraper.cleanup()
            if 'db_manager' in globals():
                db_manager.close_connections()
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 