"""
Reddit Data Collection Core Module
=================================

This module provides comprehensive Reddit data collection functionality using the PRAW library.
It handles Reddit API integration, post searching, promotional content detection, and data processing.

Features:
- Reddit API integration with rate limiting
- Advanced keyword search with multiple sorting options
- Automatic promotional content detection
- Batch data processing and storage
- Error handling and retry mechanisms
- Comprehensive logging and monitoring

Author: Reddit Data Collector Team
Version: 1.0
Last Updated: 2024
"""

import praw
import prawcore
import time
import re
import logging
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Generator
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import urlparse

# Import project modules
from config import (
    REDDIT_CONFIG, REDDIT_RATE_LIMIT, SEARCH_CONFIG, 
    PROMOTIONAL_DETECTION, LOGGING_CONFIG
)
from database import get_database_manager, RedditPost, SearchHistory

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    datefmt=LOGGING_CONFIG['date_format']
)
logger = logging.getLogger(__name__)

# =============================================================================
# DATA MODELS AND ENUMS
# =============================================================================

@dataclass
class SearchParameters:
    """Data model for search parameters"""
    keywords: List[str]
    subreddits: List[str] = None
    time_filter: str = 'week'  # hour, day, week, month, year, all
    sort: str = 'relevance'    # relevance, hot, top, new, comments
    limit: int = 100
    include_nsfw: bool = False
    min_score: int = 0
    min_comments: int = 0

@dataclass
class ScrapingResult:
    """Data model for scraping results"""
    posts: List[RedditPost]
    total_found: int
    total_processed: int
    promotional_count: int
    errors: List[str]
    execution_time: float
    search_id: Optional[int] = None

@dataclass
class PromotionalAnalysis:
    """Data model for promotional content analysis"""
    is_promotional: bool
    confidence_score: float
    detected_keywords: List[str]
    suspicious_urls: List[str]
    analysis_details: Dict[str, Any]

# =============================================================================
# REDDIT API CLIENT
# =============================================================================

class RedditAPIClient:
    """
    Enhanced Reddit API client with rate limiting and error handling.
    
    This class provides a robust interface to the Reddit API using PRAW,
    with built-in rate limiting, retry mechanisms, and comprehensive error handling.
    """
    
    def __init__(self):
        """Initialize the Reddit API client."""
        self.reddit = None
        self.rate_limiter = RateLimiter()
        self.last_request_time = 0
        self.request_count = 0
        self.session_start = datetime.now()
        
        # Initialize Reddit instance
        self._initialize_reddit()
        
        logger.info("Reddit API client initialized successfully")
    
    def _initialize_reddit(self) -> None:
        """Initialize the PRAW Reddit instance with configuration."""
        try:
            # 首先尝试script模式（需要用户名和密码）
            try:
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CONFIG['client_id'],
                    client_secret=REDDIT_CONFIG['client_secret'],
                    user_agent=REDDIT_CONFIG['user_agent'],
                    username=REDDIT_CONFIG.get('username', ''),
                    password=REDDIT_CONFIG.get('password', ''),
                    timeout=REDDIT_RATE_LIMIT['timeout']
                )
                
                # 测试script模式连接
                self._test_connection()
                logger.info("Reddit API initialized in script mode (authenticated)")
                return
                
            except Exception as script_error:
                logger.warning(f"Script mode authentication failed: {script_error}")
                logger.info("Attempting to initialize in read-only mode...")
                
                # 如果script模式失败，尝试只读模式
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CONFIG['client_id'],
                    client_secret=REDDIT_CONFIG['client_secret'],
                    user_agent=REDDIT_CONFIG['user_agent'],
                    timeout=REDDIT_RATE_LIMIT['timeout']
                )
                
                # 测试只读模式连接
                self._test_readonly_connection()
                logger.info("Reddit API initialized in read-only mode")
                return
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API client: {e}")
            raise
    
    def _test_connection(self) -> None:
        """Test the Reddit API connection with authentication."""
        try:
            # Try to access user info to test authentication
            user = self.reddit.user.me()
            if user:
                logger.info(f"Authenticated as Reddit user: {user.name}")
            else:
                logger.info("Reddit API connection established (read-only mode)")
                
        except prawcore.exceptions.ResponseException as e:
            if e.response.status_code == 401:
                logger.warning("Reddit API authentication failed - trying read-only mode")
                raise
            else:
                logger.error(f"Reddit API connection test failed: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during Reddit API connection test: {e}")
            raise
    
    def _test_readonly_connection(self) -> None:
        """Test the Reddit API connection in read-only mode."""
        try:
            # Test basic API access without authentication
            subreddit = self.reddit.subreddit('python')
            # Just access the display name to test connection
            _ = subreddit.display_name
            logger.info("Reddit API read-only connection test successful")
                
        except Exception as e:
            logger.error(f"Reddit API read-only connection test failed: {e}")
            raise
    
    def _wait_for_rate_limit(self) -> None:
        """Implement rate limiting to comply with Reddit API limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < REDDIT_RATE_LIMIT['request_delay']:
            sleep_time = REDDIT_RATE_LIMIT['request_delay'] - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def search_subreddit(self, subreddit_name: str, query: str, 
                        sort: str = 'relevance', time_filter: str = 'week',
                        limit: int = 100) -> Generator[praw.models.Submission, None, None]:
        """
        Search posts in a specific subreddit.
        
        Args:
            subreddit_name (str): Name of the subreddit to search
            query (str): Search query string
            sort (str): Sort method (relevance, hot, top, new, comments)
            time_filter (str): Time filter (hour, day, week, month, year, all)
            limit (int): Maximum number of posts to retrieve
            
        Yields:
            praw.models.Submission: Reddit submission objects
        """
        try:
            self._wait_for_rate_limit()
            
            subreddit = self.reddit.subreddit(subreddit_name)
            
            if sort == 'relevance':
                submissions = subreddit.search(query, sort=sort, time_filter=time_filter, limit=limit)
            elif sort == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort == 'top':
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            else:
                submissions = subreddit.search(query, sort='relevance', time_filter=time_filter, limit=limit)
            
            for submission in submissions:
                yield submission
                
        except prawcore.exceptions.NotFound:
            logger.error(f"Subreddit '{subreddit_name}' not found")
            raise
        except prawcore.exceptions.Forbidden:
            logger.error(f"Access forbidden to subreddit '{subreddit_name}'")
            raise
        except Exception as e:
            logger.error(f"Error searching subreddit '{subreddit_name}': {e}")
            raise
    
    def search_all_reddit(self, query: str, sort: str = 'relevance', 
                         time_filter: str = 'week', limit: int = 100) -> Generator[praw.models.Submission, None, None]:
        """
        Search posts across all of Reddit.
        
        Args:
            query (str): Search query string
            sort (str): Sort method (relevance, hot, top, new, comments)
            time_filter (str): Time filter (hour, day, week, month, year, all)
            limit (int): Maximum number of posts to retrieve
            
        Yields:
            praw.models.Submission: Reddit submission objects
        """
        try:
            self._wait_for_rate_limit()
            
            if sort == 'relevance':
                submissions = self.reddit.subreddit('all').search(
                    query, sort=sort, time_filter=time_filter, limit=limit
                )
            elif sort == 'hot':
                submissions = self.reddit.subreddit('all').hot(limit=limit)
            elif sort == 'new':
                submissions = self.reddit.subreddit('all').new(limit=limit)
            elif sort == 'top':
                submissions = self.reddit.subreddit('all').top(time_filter=time_filter, limit=limit)
            else:
                submissions = self.reddit.subreddit('all').search(
                    query, sort='relevance', time_filter=time_filter, limit=limit
                )
            
            for submission in submissions:
                yield submission
                
        except Exception as e:
            logger.error(f"Error searching all Reddit: {e}")
            raise
    
    def get_submission_details(self, submission_id: str) -> Optional[praw.models.Submission]:
        """
        Get detailed information about a specific submission.
        
        Args:
            submission_id (str): Reddit submission ID
            
        Returns:
            Optional[praw.models.Submission]: Submission object or None if not found
        """
        try:
            self._wait_for_rate_limit()
            return self.reddit.submission(id=submission_id)
        except prawcore.exceptions.NotFound:
            logger.warning(f"Submission '{submission_id}' not found")
            return None
        except Exception as e:
            logger.error(f"Error getting submission details for '{submission_id}': {e}")
            return None
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics.
        
        Returns:
            Dict[str, Any]: API usage statistics
        """
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            'requests_made': self.request_count,
            'session_duration_seconds': session_duration,
            'requests_per_minute': (self.request_count / session_duration) * 60 if session_duration > 0 else 0,
            'rate_limit_compliant': self.request_count <= (session_duration / 60) * REDDIT_RATE_LIMIT['requests_per_minute']
        }

# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Rate limiter to ensure compliance with Reddit API limits.
    """
    
    def __init__(self):
        self.requests = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self) -> None:
        """Wait if necessary to comply with rate limits."""
        with self.lock:
            now = time.time()
            
            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            # Check if we're at the limit
            if len(self.requests) >= REDDIT_RATE_LIMIT['requests_per_minute']:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                    # Remove the old request
                    self.requests.pop(0)
            
            # Add current request
            self.requests.append(now)

# =============================================================================
# PROMOTIONAL CONTENT DETECTOR
# =============================================================================

class PromotionalContentDetector:
    """
    Advanced promotional content detection system.
    
    This class analyzes Reddit posts to identify promotional or advertising content
    using multiple detection methods including keyword analysis, URL analysis,
    and behavioral patterns.
    """
    
    def __init__(self):
        """Initialize the promotional content detector."""
        self.promotional_keywords = PROMOTIONAL_DETECTION['promotional_keywords']
        self.suspicious_url_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in PROMOTIONAL_DETECTION['suspicious_url_patterns']
        ]
        self.confidence_threshold = PROMOTIONAL_DETECTION['confidence_threshold']
        self.weight_factors = PROMOTIONAL_DETECTION['weight_factors']
        
        logger.info("Promotional content detector initialized")
    
    def analyze_post(self, submission: praw.models.Submission) -> PromotionalAnalysis:
        """
        Analyze a Reddit post for promotional content.
        
        Args:
            submission (praw.models.Submission): Reddit submission to analyze
            
        Returns:
            PromotionalAnalysis: Analysis results
        """
        try:
            # Combine title and content for analysis
            text_content = f"{submission.title} {submission.selftext}".lower()
            
            # Perform different types of analysis
            keyword_analysis = self._analyze_keywords(text_content)
            url_analysis = self._analyze_urls(submission)
            author_analysis = self._analyze_author_behavior(submission)
            content_structure_analysis = self._analyze_content_structure(text_content)
            
            # Calculate weighted confidence score
            confidence_score = (
                keyword_analysis['score'] * self.weight_factors['keyword_density'] +
                url_analysis['score'] * self.weight_factors['url_analysis'] +
                author_analysis['score'] * self.weight_factors['author_behavior'] +
                content_structure_analysis['score'] * self.weight_factors['content_structure']
            )
            
            # Determine if content is promotional
            is_promotional = confidence_score >= self.confidence_threshold
            
            # Collect detected indicators
            detected_keywords = keyword_analysis['detected_keywords']
            suspicious_urls = url_analysis['suspicious_urls']
            
            analysis_details = {
                'keyword_analysis': keyword_analysis,
                'url_analysis': url_analysis,
                'author_analysis': author_analysis,
                'content_structure_analysis': content_structure_analysis,
                'final_confidence': confidence_score
            }
            
            return PromotionalAnalysis(
                is_promotional=is_promotional,
                confidence_score=confidence_score,
                detected_keywords=detected_keywords,
                suspicious_urls=suspicious_urls,
                analysis_details=analysis_details
            )
            
        except Exception as e:
            logger.error(f"Error analyzing post for promotional content: {e}")
            # Return safe default
            return PromotionalAnalysis(
                is_promotional=False,
                confidence_score=0.0,
                detected_keywords=[],
                suspicious_urls=[],
                analysis_details={'error': str(e)}
            )
    
    def _analyze_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze text for promotional keywords."""
        detected_keywords = []
        keyword_count = 0
        
        for keyword in self.promotional_keywords:
            if keyword.lower() in text:
                detected_keywords.append(keyword)
                keyword_count += text.count(keyword.lower())
        
        # Calculate keyword density score
        word_count = len(text.split())
        keyword_density = keyword_count / max(word_count, 1)
        
        # Normalize score (0-1)
        score = min(keyword_density * 10, 1.0)
        
        return {
            'score': score,
            'detected_keywords': detected_keywords,
            'keyword_count': keyword_count,
            'keyword_density': keyword_density
        }
    
    def _analyze_urls(self, submission: praw.models.Submission) -> Dict[str, Any]:
        """Analyze URLs for suspicious patterns."""
        suspicious_urls = []
        url_score = 0.0
        
        # Check submission URL
        if submission.url and submission.url != submission.permalink:
            for pattern in self.suspicious_url_patterns:
                if pattern.search(submission.url):
                    suspicious_urls.append(submission.url)
                    url_score += 0.3
        
        # Check URLs in post content
        if submission.selftext:
            url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            urls_in_text = url_pattern.findall(submission.selftext)
            
            for url in urls_in_text:
                for pattern in self.suspicious_url_patterns:
                    if pattern.search(url):
                        suspicious_urls.append(url)
                        url_score += 0.2
        
        # Normalize score
        score = min(url_score, 1.0)
        
        return {
            'score': score,
            'suspicious_urls': suspicious_urls,
            'total_suspicious_count': len(suspicious_urls)
        }
    
    def _analyze_author_behavior(self, submission: praw.models.Submission) -> Dict[str, Any]:
        """Analyze author behavior patterns."""
        score = 0.0
        analysis = {}
        
        try:
            author = submission.author
            if author is None:
                return {'score': 0.0, 'analysis': 'deleted_user'}
            
            # Account age analysis
            account_age_days = (datetime.now() - datetime.fromtimestamp(author.created_utc)).days
            if account_age_days < 30:
                score += 0.3
                analysis['new_account'] = True
            
            # Karma analysis
            if hasattr(author, 'link_karma') and hasattr(author, 'comment_karma'):
                total_karma = author.link_karma + author.comment_karma
                if total_karma < 100:
                    score += 0.2
                    analysis['low_karma'] = True
            
            analysis['account_age_days'] = account_age_days
            
        except Exception as e:
            logger.debug(f"Error analyzing author behavior: {e}")
            analysis['error'] = str(e)
        
        return {
            'score': min(score, 1.0),
            'analysis': analysis
        }
    
    def _analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze content structure for promotional patterns."""
        score = 0.0
        analysis = {}
        
        # Check for excessive capitalization
        if text.isupper() and len(text) > 20:
            score += 0.2
            analysis['excessive_caps'] = True
        
        # Check for excessive exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score += 0.1
            analysis['excessive_exclamation'] = True
        
        # Check for call-to-action phrases
        cta_phrases = ['click here', 'buy now', 'limited time', 'act now', 'don\'t miss']
        cta_found = [phrase for phrase in cta_phrases if phrase in text.lower()]
        if cta_found:
            score += 0.3
            analysis['call_to_action'] = cta_found
        
        # Check for promotional formatting
        if '**' in text or '*' in text:  # Bold/italic formatting
            score += 0.1
            analysis['promotional_formatting'] = True
        
        return {
            'score': min(score, 1.0),
            'analysis': analysis
        }

# =============================================================================
# MAIN REDDIT SCRAPER CLASS
# =============================================================================

class RedditScraper:
    """
    Main Reddit data collection and processing class.
    
    This class orchestrates the entire Reddit data collection process,
    including searching, analyzing, and storing Reddit posts.
    """
    
    def __init__(self):
        """Initialize the Reddit scraper."""
        self.api_client = RedditAPIClient()
        self.promotional_detector = PromotionalContentDetector()
        self.db_manager = get_database_manager()
        
        # Statistics tracking
        self.session_stats = {
            'posts_processed': 0,
            'posts_saved': 0,
            'promotional_posts_found': 0,
            'errors_encountered': 0,
            'session_start': datetime.now()
        }
        
        logger.info("Reddit scraper initialized successfully")
    
    def search_posts(self, search_params: SearchParameters) -> ScrapingResult:
        """
        Search for Reddit posts based on given parameters.
        
        Args:
            search_params (SearchParameters): Search configuration
            
        Returns:
            ScrapingResult: Results of the scraping operation
        """
        start_time = time.time()
        posts = []
        errors = []
        total_found = 0
        promotional_count = 0
        
        try:
            # Create search history record
            search_record = SearchHistory(
                keywords=', '.join(search_params.keywords),
                subreddits=', '.join(search_params.subreddits) if search_params.subreddits else None,
                time_filter=search_params.time_filter,
                post_limit=search_params.limit,
                status='in_progress'
            )
            search_id = self.db_manager.insert_search_history(search_record)
            
            # Build search query
            query = ' '.join(search_params.keywords)
            
            # Determine search scope
            if search_params.subreddits and search_params.subreddits != ['all']:
                # Search specific subreddits
                submissions = self._search_multiple_subreddits(
                    search_params.subreddits, query, search_params
                )
            else:
                # Search all of Reddit
                submissions = self.api_client.search_all_reddit(
                    query, search_params.sort, search_params.time_filter, search_params.limit
                )
            
            # Process submissions
            for submission in submissions:
                try:
                    total_found += 1
                    
                    # Apply filters
                    if not self._passes_filters(submission, search_params):
                        continue
                    
                    # Convert to RedditPost object
                    reddit_post = self._submission_to_reddit_post(submission)
                    
                    # Analyze for promotional content
                    if PROMOTIONAL_DETECTION['enabled']:
                        promotional_analysis = self.promotional_detector.analyze_post(submission)
                        reddit_post.is_promotional = promotional_analysis.is_promotional
                        if promotional_analysis.is_promotional:
                            promotional_count += 1
                    
                    posts.append(reddit_post)
                    self.session_stats['posts_processed'] += 1
                    
                    # Break if we've reached the limit
                    if len(posts) >= search_params.limit:
                        break
                        
                except Exception as e:
                    error_msg = f"Error processing submission {getattr(submission, 'id', 'unknown')}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    self.session_stats['errors_encountered'] += 1
            
            # Save posts to database
            if posts:
                saved_count = self.db_manager.insert_posts_batch(posts)
                self.session_stats['posts_saved'] += saved_count
                self.session_stats['promotional_posts_found'] += promotional_count
            
            # Update search history
            self.db_manager.update_search_status(search_id, 'completed', len(posts))
            
            execution_time = time.time() - start_time
            
            logger.info(f"Search completed: {len(posts)} posts collected, "
                       f"{promotional_count} promotional posts found, "
                       f"{len(errors)} errors, {execution_time:.2f}s")
            
            return ScrapingResult(
                posts=posts,
                total_found=total_found,
                total_processed=len(posts),
                promotional_count=promotional_count,
                errors=errors,
                execution_time=execution_time,
                search_id=search_id
            )
            
        except Exception as e:
            error_msg = f"Critical error during search operation: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            # Update search history with error status
            if 'search_id' in locals():
                self.db_manager.update_search_status(search_id, 'failed', 0)
            
            return ScrapingResult(
                posts=[],
                total_found=0,
                total_processed=0,
                promotional_count=0,
                errors=errors,
                execution_time=time.time() - start_time
            )
    
    def _search_multiple_subreddits(self, subreddits: List[str], query: str, 
                                   search_params: SearchParameters) -> Generator[praw.models.Submission, None, None]:
        """Search multiple subreddits and yield submissions."""
        posts_per_subreddit = max(1, search_params.limit // len(subreddits))
        
        for subreddit_name in subreddits:
            try:
                submissions = self.api_client.search_subreddit(
                    subreddit_name, query, search_params.sort, 
                    search_params.time_filter, posts_per_subreddit
                )
                
                for submission in submissions:
                    yield submission
                    
            except Exception as e:
                logger.error(f"Error searching subreddit '{subreddit_name}': {e}")
                continue
    
    def _passes_filters(self, submission: praw.models.Submission, 
                       search_params: SearchParameters) -> bool:
        """Check if submission passes the configured filters."""
        try:
            # Score filter
            if submission.score < search_params.min_score:
                return False
            
            # Comments filter
            if submission.num_comments < search_params.min_comments:
                return False
            
            # NSFW filter
            if submission.over_18 and not search_params.include_nsfw:
                return False
            
            # Content length filters
            if len(submission.title) > SEARCH_CONFIG['max_title_length']:
                return False
            
            if submission.selftext and len(submission.selftext) > SEARCH_CONFIG['max_content_length']:
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Error applying filters to submission: {e}")
            return False
    
    def _submission_to_reddit_post(self, submission: praw.models.Submission) -> RedditPost:
        """Convert a PRAW submission to a RedditPost object."""
        try:
            return RedditPost(
                reddit_id=submission.id,
                title=submission.title,
                content=submission.selftext if submission.selftext else None,
                author=submission.author.name if submission.author else '[deleted]',
                subreddit=submission.subreddit.display_name,
                score=submission.score,
                num_comments=submission.num_comments,
                created_utc=datetime.fromtimestamp(submission.created_utc),
                url=submission.url,
                is_promotional=False,  # Will be set by promotional analysis
                collected_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error converting submission to RedditPost: {e}")
            # Return a minimal post object
            return RedditPost(
                reddit_id=getattr(submission, 'id', 'unknown'),
                title=getattr(submission, 'title', 'Error loading title'),
                content=None,
                author='[error]',
                subreddit='unknown',
                score=0,
                num_comments=0,
                created_utc=datetime.now(),
                url='',
                is_promotional=False,
                collected_at=datetime.now()
            )
    
    def collect_promotional_posts(self, subreddits: List[str] = None, 
                                 limit: int = 100) -> ScrapingResult:
        """
        Specifically collect posts that are likely to be promotional.
        
        Args:
            subreddits (List[str], optional): Subreddits to search
            limit (int): Maximum number of posts to collect
            
        Returns:
            ScrapingResult: Results of the promotional post collection
        """
        # Use promotional keywords as search terms
        promotional_keywords = PROMOTIONAL_DETECTION['promotional_keywords'][:5]  # Use top 5
        
        search_params = SearchParameters(
            keywords=promotional_keywords,
            subreddits=subreddits or ['all'],
            time_filter='week',
            sort='new',  # New posts more likely to be promotional
            limit=limit,
            min_score=0,
            min_comments=0
        )
        
        logger.info(f"Starting promotional post collection with keywords: {promotional_keywords}")
        return self.search_posts(search_params)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive session statistics.
        
        Returns:
            Dict[str, Any]: Session statistics
        """
        session_duration = (datetime.now() - self.session_stats['session_start']).total_seconds()
        api_stats = self.api_client.get_api_stats()
        
        return {
            'session_stats': {
                **self.session_stats,
                'session_duration_seconds': session_duration,
                'posts_per_minute': (self.session_stats['posts_processed'] / session_duration) * 60 if session_duration > 0 else 0
            },
            'api_stats': api_stats,
            'database_stats': self.db_manager.get_database_stats()
        }
    
    def cleanup(self) -> None:
        """Clean up resources and close connections."""
        try:
            self.db_manager.close_connections()
            logger.info("Reddit scraper cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_search_parameters(keywords: List[str], **kwargs) -> SearchParameters:
    """
    Create SearchParameters object with defaults from configuration.
    
    Args:
        keywords (List[str]): Search keywords
        **kwargs: Additional parameters
        
    Returns:
        SearchParameters: Configured search parameters
    """
    return SearchParameters(
        keywords=keywords,
        subreddits=kwargs.get('subreddits', SEARCH_CONFIG['default_subreddits']),
        time_filter=kwargs.get('time_filter', SEARCH_CONFIG['default_time_filter']),
        sort=kwargs.get('sort', SEARCH_CONFIG['default_sort']),
        limit=kwargs.get('limit', SEARCH_CONFIG['default_limit']),
        include_nsfw=kwargs.get('include_nsfw', False),
        min_score=kwargs.get('min_score', SEARCH_CONFIG['min_score']),
        min_comments=kwargs.get('min_comments', SEARCH_CONFIG['min_comments'])
    )

def validate_search_parameters(search_params: SearchParameters) -> Tuple[bool, List[str]]:
    """
    Validate search parameters.
    
    Args:
        search_params (SearchParameters): Parameters to validate
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    errors = []
    
    if not search_params.keywords:
        errors.append("Keywords are required")
    
    if len(search_params.keywords) > SEARCH_CONFIG.get('max_keywords_count', 20):
        errors.append(f"Too many keywords (max: {SEARCH_CONFIG.get('max_keywords_count', 20)})")
    
    if search_params.limit > SEARCH_CONFIG['max_limit']:
        errors.append(f"Limit too high (max: {SEARCH_CONFIG['max_limit']})")
    
    if search_params.time_filter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        errors.append("Invalid time filter")
    
    if search_params.sort not in ['relevance', 'hot', 'top', 'new', 'comments']:
        errors.append("Invalid sort method")
    
    return len(errors) == 0, errors

# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    # Example usage and testing
    try:
        scraper = RedditScraper()
        
        # Test search
        search_params = create_search_parameters(
            keywords=['python', 'programming'],
            subreddits=['python', 'programming'],
            limit=10
        )
        
        result = scraper.search_posts(search_params)
        
        print(f"Search completed:")
        print(f"  Posts found: {result.total_found}")
        print(f"  Posts processed: {result.total_processed}")
        print(f"  Promotional posts: {result.promotional_count}")
        print(f"  Execution time: {result.execution_time:.2f}s")
        print(f"  Errors: {len(result.errors)}")
        
        # Print session statistics
        stats = scraper.get_session_statistics()
        print(f"\nSession Statistics:")
        for key, value in stats['session_stats'].items():
            print(f"  {key}: {value}")
        
        scraper.cleanup()
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise 