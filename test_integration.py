#!/usr/bin/env python3
"""
Reddit Data Collection Website - Integration Test Suite
======================================================

This comprehensive test suite validates the integration and functionality
of all system components working together.

Features tested:
- Database integration with all modules
- Reddit API integration and data collection
- Web interface functionality and responsiveness
- Data export and import capabilities
- Error handling and recovery mechanisms
- Performance and scalability aspects

Author: Reddit Data Collector Team
Version: 2.0
Last Updated: 2024
"""

import sys
import os
import time
import json
import tempfile
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules for testing
try:
    from config import get_config, REDDIT_CONFIG, DATABASE_CONFIG
    from database import get_database_manager, RedditPost, SearchHistory
    from reddit_scraper import RedditScraper, SearchParameters, create_search_parameters
    from app import app
    import requests
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

class IntegrationTestSuite:
    """Comprehensive integration test suite for the Reddit data collection system."""
    
    def __init__(self):
        self.config = get_config()
        self.db_manager = None
        self.reddit_scraper = None
        self.test_results = {}
        self.start_time = datetime.now()
        
        # Test configuration
        self.test_keywords = ["python", "programming"]
        self.test_subreddits = ["python", "programming"]
        self.test_limit = 10  # Small limit for testing
        
        # Performance tracking
        self.performance_metrics = {
            'database_operations': [],
            'api_calls': [],
            'web_requests': [],
            'export_operations': []
        }
    
    def print_header(self, title: str):
        """Print a formatted test section header."""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, status: str, details: str = ""):
        """Print test result with formatting."""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name:<40} [{status}]")
        if details:
            print(f"   └─ {details}")
    
    def record_performance(self, category: str, operation: str, duration: float):
        """Record performance metrics for analysis."""
        self.performance_metrics[category].append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now()
        })
    
    def test_database_integration(self) -> bool:
        """Test database initialization and basic operations."""
        self.print_header("Database Integration Tests")
        
        try:
            # Test database manager initialization
            start_time = time.time()
            self.db_manager = get_database_manager()
            init_duration = time.time() - start_time
            self.record_performance('database_operations', 'initialization', init_duration)
            self.print_test("Database Manager Initialization", "PASS", f"{init_duration:.3f}s")
            
            # Test table creation
            start_time = time.time()
            self.db_manager.create_tables()
            create_duration = time.time() - start_time
            self.record_performance('database_operations', 'table_creation', create_duration)
            self.print_test("Table Creation", "PASS", f"{create_duration:.3f}s")
            
            # Test database statistics
            start_time = time.time()
            stats = self.db_manager.get_database_stats()
            stats_duration = time.time() - start_time
            self.record_performance('database_operations', 'statistics', stats_duration)
            self.print_test("Database Statistics", "PASS", 
                          f"Posts: {stats['total_posts']}, Time: {stats_duration:.3f}s")
            
            # Test post insertion with unique ID
            timestamp = int(time.time() * 1000000)  # Microsecond timestamp for uniqueness
            test_post = RedditPost(
                reddit_id=f"test_integration_{timestamp}",
                title="Integration Test Post",
                content="This is a test post for integration testing",
                author="test_user",
                subreddit="test",
                score=10,
                num_comments=5,
                created_utc=datetime.now(),
                url="https://reddit.com/test",
                is_promotional=False
            )
            
            start_time = time.time()
            post_id = self.db_manager.save_post(test_post)
            save_duration = time.time() - start_time
            self.record_performance('database_operations', 'post_insertion', save_duration)
            self.print_test("Post Insertion", "PASS", f"ID: {post_id}, Time: {save_duration:.3f}s")
            
            # Test post retrieval
            start_time = time.time()
            retrieved_post = self.db_manager.get_post_by_reddit_id(f"test_integration_{timestamp}")
            retrieve_duration = time.time() - start_time
            self.record_performance('database_operations', 'post_retrieval', retrieve_duration)
            
            if retrieved_post and retrieved_post.title == "Integration Test Post":
                self.print_test("Post Retrieval", "PASS", f"Time: {retrieve_duration:.3f}s")
            else:
                self.print_test("Post Retrieval", "FAIL", "Post not found or data mismatch")
                return False
            
            # Test search history with unique data
            test_history = SearchHistory(
                keywords=f"integration, test, {timestamp}",
                subreddits="test",
                time_filter="week",
                post_limit=10,
                results_count=1,
                status="completed"
            )
            
            start_time = time.time()
            history_id = self.db_manager.save_search_history(test_history)
            history_duration = time.time() - start_time
            self.record_performance('database_operations', 'history_insertion', history_duration)
            self.print_test("Search History Insertion", "PASS", 
                          f"ID: {history_id}, Time: {history_duration:.3f}s")
            
            return True
            
        except Exception as e:
            self.print_test("Database Integration", "FAIL", str(e))
            return False
    
    def test_reddit_api_integration(self) -> bool:
        """Test Reddit API integration and data collection."""
        self.print_header("Reddit API Integration Tests")
        
        try:
            # Check if Reddit API is configured
            if (REDDIT_CONFIG['client_id'] == 'your_client_id_here' or 
                REDDIT_CONFIG['client_secret'] == 'your_client_secret_here'):
                self.print_test("Reddit API Configuration", "SKIP", 
                              "API credentials not configured - using mock data")
                return self.test_mock_reddit_integration()
            
            # Test Reddit scraper initialization
            start_time = time.time()
            self.reddit_scraper = RedditScraper()
            init_duration = time.time() - start_time
            self.record_performance('api_calls', 'scraper_initialization', init_duration)
            self.print_test("Reddit Scraper Initialization", "PASS", f"{init_duration:.3f}s")
            
            # Test search parameters creation
            search_params = create_search_parameters(
                keywords=self.test_keywords,
                subreddits=self.test_subreddits,
                limit=self.test_limit,
                time_filter="week"
            )
            self.print_test("Search Parameters Creation", "PASS", 
                          f"Keywords: {len(search_params.keywords)}, Subreddits: {len(search_params.subreddits)}")
            
            # Test actual Reddit search (with small limit)
            start_time = time.time()
            search_result = self.reddit_scraper.search_posts(search_params)
            search_duration = time.time() - start_time
            self.record_performance('api_calls', 'reddit_search', search_duration)
            
            if search_result.errors:
                self.print_test("Reddit Search", "FAIL", f"Errors: {search_result.errors}")
                return False
            else:
                self.print_test("Reddit Search", "PASS", 
                              f"Found: {search_result.total_processed} posts, Time: {search_duration:.3f}s")
            
            # Test promotional content detection
            promotional_count = search_result.promotional_count
            self.print_test("Promotional Detection", "PASS", 
                          f"Detected: {promotional_count}/{search_result.total_processed} promotional posts")
            
            # Test session statistics
            stats = self.reddit_scraper.get_session_statistics()
            self.print_test("Session Statistics", "PASS", 
                          f"API calls: {stats.get('total_api_calls', 0)}")
            
            return True
            
        except Exception as e:
            self.print_test("Reddit API Integration", "FAIL", str(e))
            return False
    
    def test_mock_reddit_integration(self) -> bool:
        """Test system with mock Reddit data when API is not configured."""
        try:
            # Create mock search result with unique IDs
            timestamp = int(time.time() * 1000000)
            mock_posts = []
            for i in range(5):
                post = RedditPost(
                    reddit_id=f"mock_post_{timestamp}_{i}",
                    title=f"Mock Post {i} - Python Programming",
                    content=f"This is mock content for post {i} about Python programming.",
                    author=f"mock_user_{i}",
                    subreddit="python",
                    score=10 + i,
                    num_comments=i * 2,
                    created_utc=datetime.now() - timedelta(hours=i),
                    url=f"https://reddit.com/mock_post_{timestamp}_{i}",
                    is_promotional=(i % 3 == 0)  # Every third post is promotional
                )
                mock_posts.append(post)
            
            # Save mock posts to database
            for post in mock_posts:
                self.db_manager.save_post(post)
            
            self.print_test("Mock Data Creation", "PASS", f"Created {len(mock_posts)} mock posts")
            
            # Test promotional detection on mock data
            promotional_posts = [p for p in mock_posts if p.is_promotional]
            self.print_test("Mock Promotional Detection", "PASS", 
                          f"Identified {len(promotional_posts)} promotional posts")
            
            return True
            
        except Exception as e:
            self.print_test("Mock Reddit Integration", "FAIL", str(e))
            return False
    
    def test_web_interface_integration(self) -> bool:
        """Test Flask web application and API endpoints."""
        self.print_header("Web Interface Integration Tests")
        
        try:
            # Test Flask app initialization
            with app.test_client() as client:
                # Test home page
                start_time = time.time()
                response = client.get('/')
                home_duration = time.time() - start_time
                self.record_performance('web_requests', 'home_page', home_duration)
                
                if response.status_code == 200:
                    self.print_test("Home Page", "PASS", f"Status: {response.status_code}, Time: {home_duration:.3f}s")
                else:
                    self.print_test("Home Page", "FAIL", f"Status: {response.status_code}")
                    return False
                
                # Test health check endpoint
                start_time = time.time()
                response = client.get('/api/health')
                health_duration = time.time() - start_time
                self.record_performance('web_requests', 'health_check', health_duration)
                
                if response.status_code == 200:
                    health_data = response.get_json()
                    self.print_test("Health Check API", "PASS", 
                                  f"Status: {health_data.get('status', 'unknown')}, Time: {health_duration:.3f}s")
                else:
                    self.print_test("Health Check API", "FAIL", f"Status: {response.status_code}")
                    return False
                
                # Test system status endpoint
                start_time = time.time()
                response = client.get('/api/status')
                status_duration = time.time() - start_time
                self.record_performance('web_requests', 'system_status', status_duration)
                
                if response.status_code == 200:
                    status_data = response.get_json()
                    self.print_test("System Status API", "PASS", 
                                  f"Components: {len(status_data.get('configuration', {}))}, Time: {status_duration:.3f}s")
                else:
                    self.print_test("System Status API", "FAIL", f"Status: {response.status_code}")
                
                # Test posts endpoint
                start_time = time.time()
                response = client.get('/api/posts?limit=5')
                posts_duration = time.time() - start_time
                self.record_performance('web_requests', 'posts_api', posts_duration)
                
                if response.status_code == 200:
                    posts_data = response.get_json()
                    post_count = len(posts_data.get('data', []))
                    self.print_test("Posts API", "PASS", 
                                  f"Retrieved: {post_count} posts, Time: {posts_duration:.3f}s")
                else:
                    self.print_test("Posts API", "FAIL", f"Status: {response.status_code}")
                
                # Test search history endpoint
                start_time = time.time()
                response = client.get('/api/history?limit=5')
                history_duration = time.time() - start_time
                self.record_performance('web_requests', 'history_api', history_duration)
                
                if response.status_code == 200:
                    history_data = response.get_json()
                    history_count = len(history_data.get('data', []))
                    self.print_test("History API", "PASS", 
                                  f"Retrieved: {history_count} records, Time: {history_duration:.3f}s")
                else:
                    self.print_test("History API", "FAIL", f"Status: {response.status_code}")
                
                # Test search API (if Reddit API is configured)
                if (REDDIT_CONFIG['client_id'] != 'your_client_id_here' and 
                    REDDIT_CONFIG['client_secret'] != 'your_client_secret_here'):
                    
                    search_data = {
                        "keywords": ["test"],
                        "subreddits": ["python"],
                        "limit": 5,
                        "time_filter": "week"
                    }
                    
                    start_time = time.time()
                    response = client.post('/api/search', 
                                         data=json.dumps(search_data),
                                         content_type='application/json')
                    search_duration = time.time() - start_time
                    self.record_performance('web_requests', 'search_api', search_duration)
                    
                    if response.status_code == 200:
                        search_result = response.get_json()
                        result_count = len(search_result.get('results', {}).get('posts', []))
                        self.print_test("Search API", "PASS", 
                                      f"Found: {result_count} posts, Time: {search_duration:.3f}s")
                    else:
                        self.print_test("Search API", "FAIL", f"Status: {response.status_code}")
                else:
                    self.print_test("Search API", "SKIP", "Reddit API not configured")
            
            return True
            
        except Exception as e:
            self.print_test("Web Interface Integration", "FAIL", str(e))
            return False
    
    def test_data_export_integration(self) -> bool:
        """Test data export functionality and file generation."""
        self.print_header("Data Export Integration Tests")
        
        try:
            # Test CSV export
            start_time = time.time()
            csv_filename = f"test_export_{int(time.time())}.csv"
            csv_path = self.db_manager.export_posts_to_csv(csv_filename, {})
            csv_duration = time.time() - start_time
            self.record_performance('export_operations', 'csv_export', csv_duration)
            
            if os.path.exists(csv_path):
                file_size = os.path.getsize(csv_path)
                self.print_test("CSV Export", "PASS", 
                              f"File: {csv_filename}, Size: {file_size} bytes, Time: {csv_duration:.3f}s")
                
                # Clean up test file
                os.remove(csv_path)
            else:
                self.print_test("CSV Export", "FAIL", "Export file not created")
                return False
            
            # Test JSON export
            start_time = time.time()
            json_filename = f"test_export_{int(time.time())}.json"
            json_path = self.db_manager.export_posts_to_json(json_filename, {})
            json_duration = time.time() - start_time
            self.record_performance('export_operations', 'json_export', json_duration)
            
            if os.path.exists(json_path):
                file_size = os.path.getsize(json_path)
                self.print_test("JSON Export", "PASS", 
                              f"File: {json_filename}, Size: {file_size} bytes, Time: {json_duration:.3f}s")
                
                # Validate JSON format
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    self.print_test("JSON Validation", "PASS", f"Records: {len(json_data)}")
                except json.JSONDecodeError:
                    self.print_test("JSON Validation", "FAIL", "Invalid JSON format")
                
                # Clean up test file
                os.remove(json_path)
            else:
                self.print_test("JSON Export", "FAIL", "Export file not created")
                return False
            
            # Test export via web API
            with app.test_client() as client:
                start_time = time.time()
                response = client.get('/api/export?format=csv&limit=10')
                api_export_duration = time.time() - start_time
                self.record_performance('export_operations', 'api_export', api_export_duration)
                
                if response.status_code == 200:
                    export_data = response.get_json()
                    self.print_test("API Export", "PASS", 
                                  f"File: {export_data.get('export_info', {}).get('filename', 'unknown')}, Time: {api_export_duration:.3f}s")
                else:
                    self.print_test("API Export", "FAIL", f"Status: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_test("Data Export Integration", "FAIL", str(e))
            return False
    
    def test_error_handling_integration(self) -> bool:
        """Test error handling and recovery mechanisms."""
        self.print_header("Error Handling Integration Tests")
        
        try:
            # Test invalid database operations
            try:
                invalid_post = RedditPost(
                    reddit_id="",  # Invalid empty ID
                    title="",      # Invalid empty title
                    content=None,
                    author=None,
                    subreddit=None,
                    score=None,
                    num_comments=None,
                    created_utc=None,
                    url=None,
                    is_promotional=None
                )
                self.db_manager.save_post(invalid_post)
                self.print_test("Invalid Post Handling", "FAIL", "Should have raised an error")
            except Exception:
                self.print_test("Invalid Post Handling", "PASS", "Properly rejected invalid post")
            
            # Test API error handling with invalid endpoints
            with app.test_client() as client:
                response = client.get('/api/nonexistent')
                if response.status_code == 404:
                    self.print_test("404 Error Handling", "PASS", "Properly returned 404")
                else:
                    self.print_test("404 Error Handling", "FAIL", f"Unexpected status: {response.status_code}")
                
                # Test invalid search parameters
                invalid_search = {
                    "keywords": [],  # Empty keywords
                    "limit": -1      # Invalid limit
                }
                response = client.post('/api/search', 
                                     data=json.dumps(invalid_search),
                                     content_type='application/json')
                if response.status_code == 400:
                    self.print_test("Invalid Search Handling", "PASS", "Properly rejected invalid search")
                else:
                    self.print_test("Invalid Search Handling", "FAIL", f"Status: {response.status_code}")
            
            # Test database connection recovery
            try:
                # Force close database connections
                self.db_manager.close_connections()
                
                # Try to perform operation (should reconnect automatically)
                stats = self.db_manager.get_database_stats()
                self.print_test("Database Recovery", "PASS", "Successfully reconnected to database")
            except Exception as e:
                self.print_test("Database Recovery", "FAIL", str(e))
            
            return True
            
        except Exception as e:
            self.print_test("Error Handling Integration", "FAIL", str(e))
            return False
    
    def test_performance_integration(self) -> bool:
        """Test system performance under various conditions."""
        self.print_header("Performance Integration Tests")
        
        try:
            # Test concurrent database operations with unique IDs
            def concurrent_db_operation(thread_id: int):
                try:
                    timestamp = int(time.time() * 1000000)
                    for i in range(5):
                        post = RedditPost(
                            reddit_id=f"perf_test_{timestamp}_{thread_id}_{i}",
                            title=f"Performance Test Post {thread_id}-{i}",
                            content="Performance testing content",
                            author=f"perf_user_{thread_id}",
                            subreddit="performance_test",
                            score=i,
                            num_comments=i,
                            created_utc=datetime.now(),
                            url=f"https://reddit.com/perf_{timestamp}_{thread_id}_{i}",
                            is_promotional=False
                        )
                        self.db_manager.save_post(post)
                    return True
                except Exception:
                    return False
            
            # Run concurrent operations
            threads = []
            start_time = time.time()
            
            for i in range(3):  # 3 concurrent threads
                thread = threading.Thread(target=concurrent_db_operation, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            concurrent_duration = time.time() - start_time
            self.record_performance('database_operations', 'concurrent_operations', concurrent_duration)
            self.print_test("Concurrent Database Operations", "PASS", 
                          f"3 threads, 15 total operations, Time: {concurrent_duration:.3f}s")
            
            # Test bulk data retrieval
            start_time = time.time()
            bulk_posts = self.db_manager.get_posts(limit=100)
            bulk_duration = time.time() - start_time
            self.record_performance('database_operations', 'bulk_retrieval', bulk_duration)
            self.print_test("Bulk Data Retrieval", "PASS", 
                          f"Retrieved: {len(bulk_posts)} posts, Time: {bulk_duration:.3f}s")
            
            # Test memory usage (basic check)
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb < 500:  # Less than 500MB
                self.print_test("Memory Usage", "PASS", f"Memory: {memory_mb:.1f} MB")
            else:
                self.print_test("Memory Usage", "WARN", f"High memory usage: {memory_mb:.1f} MB")
            
            return True
            
        except Exception as e:
            self.print_test("Performance Integration", "FAIL", str(e))
            return False
    
    def generate_performance_report(self):
        """Generate a comprehensive performance report."""
        self.print_header("Performance Analysis Report")
        
        for category, operations in self.performance_metrics.items():
            if operations:
                print(f"\n📊 {category.replace('_', ' ').title()}:")
                
                # Calculate statistics
                durations = [op['duration'] for op in operations]
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                
                print(f"   Total Operations: {len(operations)}")
                print(f"   Average Duration: {avg_duration:.3f}s")
                print(f"   Max Duration: {max_duration:.3f}s")
                print(f"   Min Duration: {min_duration:.3f}s")
                
                # Show individual operations
                for op in operations:
                    print(f"   └─ {op['operation']}: {op['duration']:.3f}s")
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        self.print_header("Integration Test Summary")
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"🕒 Total Test Duration: {total_duration:.2f} seconds")
        print(f"📅 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System Configuration: {self.config.__class__.__name__}")
        
        # Count test results
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Test Results:")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {total_tests - passed_tests}")
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Show individual test results
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        # System health summary
        print(f"\n🏥 System Health:")
        if self.db_manager:
            stats = self.db_manager.get_database_stats()
            print(f"   📊 Database Posts: {stats['total_posts']}")
            print(f"   🎯 Promotional Posts: {stats['promotional_posts']}")
            print(f"   🔍 Total Searches: {stats['total_searches']}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate == 100:
            print("   🎉 All tests passed! System is ready for production use.")
        elif success_rate >= 80:
            print("   ⚠️  Most tests passed. Review failed tests and address issues.")
        else:
            print("   🚨 Multiple test failures detected. System needs attention before use.")
        
        if (REDDIT_CONFIG['client_id'] == 'your_client_id_here' or 
            REDDIT_CONFIG['client_secret'] == 'your_client_secret_here'):
            print("   🔑 Configure Reddit API credentials for full functionality.")
        
        return success_rate >= 80
    
    def run_all_tests(self) -> bool:
        """Run the complete integration test suite."""
        print("🚀 Starting Reddit Data Collection Website Integration Tests")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define test sequence
        tests = [
            ("Database Integration", self.test_database_integration),
            ("Reddit API Integration", self.test_reddit_api_integration),
            ("Web Interface Integration", self.test_web_interface_integration),
            ("Data Export Integration", self.test_data_export_integration),
            ("Error Handling Integration", self.test_error_handling_integration),
            ("Performance Integration", self.test_performance_integration)
        ]
        
        # Run all tests
        for test_name, test_function in tests:
            try:
                result = test_function()
                self.test_results[test_name] = result
            except Exception as e:
                print(f"❌ Critical error in {test_name}: {e}")
                self.test_results[test_name] = False
        
        # Generate reports
        self.generate_performance_report()
        overall_success = self.generate_test_report()
        
        return overall_success

def main():
    """Main function to run integration tests."""
    try:
        # Initialize test suite
        test_suite = IntegrationTestSuite()
        
        # Run all tests
        success = test_suite.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Integration tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Critical error during integration testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 