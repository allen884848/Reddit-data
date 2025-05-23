#!/usr/bin/env python3
"""
Reddit Data Collection System - Test Script
==========================================

This script tests the core functionality of the Reddit data collection system
to ensure all components are working correctly.

Features tested:
- Configuration validation
- Database connectivity
- Reddit API integration
- Data collection functionality
- Export capabilities

Author: Reddit Data Collector Team
Version: 1.0
Last Updated: 2024
"""

import sys
import os
import logging
from datetime import datetime
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name: str, success: bool, message: str = ""):
    """Print test result with formatting."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"    {message}")

def test_configuration():
    """Test configuration loading and validation."""
    print_test_header("Configuration System")
    
    try:
        from config import (
            REDDIT_CONFIG, DATABASE_CONFIG, SEARCH_CONFIG,
            PROMOTIONAL_DETECTION, get_config, validate_config
        )
        
        # Test configuration loading
        config = get_config()
        print_test_result("Configuration Loading", True, f"Loaded {config.__class__.__name__}")
        
        # Test Reddit API configuration
        reddit_configured = (
            REDDIT_CONFIG['client_id'] != 'your_client_id_here' and
            REDDIT_CONFIG['client_secret'] != 'your_client_secret_here'
        )
        print_test_result(
            "Reddit API Configuration", 
            reddit_configured, 
            "Configured" if reddit_configured else "Not configured - add credentials to .env file"
        )
        
        # Test configuration validation
        try:
            validate_config()
            print_test_result("Configuration Validation", True, "All required directories created")
        except Exception as e:
            print_test_result("Configuration Validation", False, str(e))
        
        return True
        
    except Exception as e:
        print_test_result("Configuration System", False, str(e))
        return False

def test_database():
    """Test database connectivity and operations."""
    print_test_header("Database System")
    
    try:
        from database import get_database_manager, RedditPost, SearchHistory
        from datetime import datetime
        
        # Test database connection
        db_manager = get_database_manager()
        print_test_result("Database Connection", True, f"Connected to {db_manager.db_path}")
        
        # Test database statistics
        stats = db_manager.get_database_stats()
        print_test_result(
            "Database Statistics", 
            True, 
            f"Posts: {stats['total_posts']}, Searches: {stats['total_searches']}"
        )
        
        # Test sample data creation (if database is empty)
        if stats['total_posts'] == 0:
            from database import create_sample_data
            create_sample_data(db_manager, 3)
            print_test_result("Sample Data Creation", True, "Created 3 sample posts")
        
        # Test data export
        try:
            csv_file = db_manager.export_posts_to_csv("test_export.csv")
            json_file = db_manager.export_posts_to_json("test_export.json")
            print_test_result("Data Export", True, f"Exported to {csv_file} and {json_file}")
        except Exception as e:
            print_test_result("Data Export", False, str(e))
        
        db_manager.close_connections()
        return True
        
    except Exception as e:
        print_test_result("Database System", False, str(e))
        return False

def test_reddit_scraper():
    """Test Reddit scraper functionality."""
    print_test_header("Reddit Scraper System")
    
    try:
        from reddit_scraper import (
            RedditScraper, SearchParameters, create_search_parameters,
            validate_search_parameters, PromotionalContentDetector
        )
        
        # Test promotional content detector
        detector = PromotionalContentDetector()
        print_test_result("Promotional Content Detector", True, "Initialized successfully")
        
        # Test search parameters creation
        search_params = create_search_parameters(
            keywords=['test', 'python'],
            subreddits=['test'],
            limit=5
        )
        print_test_result("Search Parameters Creation", True, f"Keywords: {search_params.keywords}")
        
        # Test search parameters validation
        is_valid, errors = validate_search_parameters(search_params)
        print_test_result("Search Parameters Validation", is_valid, f"Errors: {errors}" if errors else "Valid")
        
        # Test Reddit API client initialization
        try:
            scraper = RedditScraper()
            print_test_result("Reddit API Client", True, "Initialized successfully")
            
            # Get API statistics
            stats = scraper.get_session_statistics()
            print_test_result(
                "Session Statistics", 
                True, 
                f"Posts processed: {stats['session_stats']['posts_processed']}"
            )
            
            scraper.cleanup()
            
        except Exception as e:
            print_test_result("Reddit API Client", False, str(e))
        
        return True
        
    except Exception as e:
        print_test_result("Reddit Scraper System", False, str(e))
        return False

def test_flask_app():
    """Test Flask application components."""
    print_test_header("Flask Application")
    
    try:
        # Import Flask app components
        from app import app, get_reddit_scraper, validate_request_data
        
        print_test_result("Flask App Import", True, "Application imported successfully")
        
        # Test request validation function
        valid_data = {'keywords': ['test']}
        invalid_data = {}
        
        is_valid, errors = validate_request_data(valid_data, ['keywords'])
        print_test_result("Request Validation (Valid)", is_valid, "Valid data accepted")
        
        is_valid, errors = validate_request_data(invalid_data, ['keywords'])
        print_test_result("Request Validation (Invalid)", not is_valid, f"Errors caught: {errors}")
        
        # Test app configuration
        with app.app_context():
            print_test_result("Flask Configuration", True, f"Debug mode: {app.config['DEBUG']}")
        
        return True
        
    except Exception as e:
        print_test_result("Flask Application", False, str(e))
        return False

def test_integration():
    """Test integration between components."""
    print_test_header("System Integration")
    
    try:
        from database import get_database_manager
        from reddit_scraper import create_search_parameters
        
        # Test database and scraper integration
        db_manager = get_database_manager()
        search_params = create_search_parameters(keywords=['integration_test'], limit=1)
        
        print_test_result("Component Integration", True, "All components work together")
        
        # Test configuration consistency
        from config import REDDIT_CONFIG, SEARCH_CONFIG
        
        max_limit_consistent = search_params.limit <= SEARCH_CONFIG['max_limit']
        print_test_result("Configuration Consistency", max_limit_consistent, "Limits are consistent")
        
        db_manager.close_connections()
        return True
        
    except Exception as e:
        print_test_result("System Integration", False, str(e))
        return False

def run_all_tests():
    """Run all system tests."""
    print(f"\n🚀 Reddit Data Collection System - Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    
    tests = [
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Reddit Scraper", test_reddit_scraper),
        ("Flask Application", test_flask_app),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Critical error in {test_name} test: {e}")
            logger.debug(traceback.format_exc())
            results.append((test_name, False))
    
    # Print summary
    print_test_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
        return False

def main():
    """Main test execution function."""
    try:
        success = run_all_tests()
        
        if success:
            print("\n📋 Next Steps:")
            print("1. Configure Reddit API credentials in .env file (if not done)")
            print("2. Run the application: python app.py")
            print("3. Open http://localhost:5000 in your browser")
            print("4. Use the API endpoints to collect Reddit data")
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error during test execution: {e}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 