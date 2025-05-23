"""
Reddit Data Collection Database Module
=====================================

This module provides comprehensive database operations for the Reddit data collection application.
It handles SQLite database connections, table creation, data insertion, querying, and maintenance.

Features:
- Automatic database initialization and schema creation
- CRUD operations for posts and search history
- Data export functionality
- Database backup and maintenance
- Connection pooling and optimization
- Error handling and logging

Author: Reddit Data Collector Team
Version: 1.0
Last Updated: 2024
"""

import sqlite3
import json
import csv
import logging
import os
import shutil
import threading
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict

# Import configuration
from config import DATABASE_CONFIG, EXPORT_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    datefmt=LOGGING_CONFIG['date_format']
)
logger = logging.getLogger(__name__)

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class RedditPost:
    """Data model for Reddit posts"""
    reddit_id: str
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    subreddit: Optional[str] = None
    score: int = 0
    num_comments: int = 0
    created_utc: Optional[datetime] = None
    url: Optional[str] = None
    is_promotional: bool = False
    collected_at: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class SearchHistory:
    """Data model for search history"""
    keywords: str
    subreddits: Optional[str] = None
    time_filter: str = 'week'
    post_limit: int = 100
    results_count: int = 0
    search_date: Optional[datetime] = None
    status: str = 'completed'
    id: Optional[int] = None

# =============================================================================
# DATABASE MANAGER CLASS
# =============================================================================

class DatabaseManager:
    """
    Comprehensive database manager for Reddit data collection.
    
    This class handles all database operations including:
    - Connection management with pooling
    - Schema creation and migration
    - CRUD operations for posts and search history
    - Data export and backup functionality
    - Performance optimization and maintenance
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the database manager.
        
        Args:
            db_path (str, optional): Path to the SQLite database file.
                                   If None, uses the path from config.
        """
        self.db_path = db_path or DATABASE_CONFIG['database_path']
        self.backup_enabled = DATABASE_CONFIG['backup_enabled']
        self.backup_interval = DATABASE_CONFIG['backup_interval']
        self.backup_directory = DATABASE_CONFIG['backup_directory']
        self.max_backups = DATABASE_CONFIG['max_backups']
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Database manager initialized with database: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a thread-local database connection.
        
        Returns:
            sqlite3.Connection: Database connection for the current thread
        """
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                timeout=DATABASE_CONFIG['connection_timeout'],
                check_same_thread=False
            )
            
            # Configure connection
            self._configure_connection(self._local.connection)
        
        return self._local.connection
    
    def _configure_connection(self, conn: sqlite3.Connection) -> None:
        """
        Configure database connection with optimization settings.
        
        Args:
            conn (sqlite3.Connection): Database connection to configure
        """
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        # Apply pragma settings for optimization
        cursor = conn.cursor()
        for pragma, value in DATABASE_CONFIG['pragma_settings'].items():
            cursor.execute(f"PRAGMA {pragma} = {value}")
        
        cursor.close()
        conn.commit()
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor operations.
        
        Yields:
            sqlite3.Cursor: Database cursor for executing queries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            cursor.close()
    
    def _initialize_database(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        try:
            # Ensure database directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Create tables
            self._create_tables()
            
            # Create indexes for performance
            self._create_indexes()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        with self.get_cursor() as cursor:
            # Create posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reddit_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    subreddit TEXT,
                    score INTEGER DEFAULT 0,
                    num_comments INTEGER DEFAULT 0,
                    created_utc TIMESTAMP,
                    url TEXT,
                    is_promotional BOOLEAN DEFAULT FALSE,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create search history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keywords TEXT NOT NULL,
                    subreddits TEXT,
                    time_filter TEXT DEFAULT 'week',
                    post_limit INTEGER DEFAULT 100,
                    results_count INTEGER DEFAULT 0,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
            """)
            
            # Create metadata table for database versioning
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert database version
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value)
                VALUES ('schema_version', '1.0')
            """)
    
    def _create_indexes(self) -> None:
        """Create database indexes for improved query performance."""
        with self.get_cursor() as cursor:
            # Indexes for posts table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_reddit_id ON posts(reddit_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_utc ON posts(created_utc)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_is_promotional ON posts(is_promotional)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_collected_at ON posts(collected_at)")
            
            # Indexes for search history table
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_date ON search_history(search_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_history_status ON search_history(status)")
    
    # =============================================================================
    # POST OPERATIONS
    # =============================================================================
    
    def insert_post(self, post: RedditPost) -> int:
        """
        Insert a new post into the database.
        
        Args:
            post (RedditPost): Post data to insert
            
        Returns:
            int: ID of the inserted post
            
        Raises:
            sqlite3.IntegrityError: If post with same reddit_id already exists
        """
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO posts (
                    reddit_id, title, content, author, subreddit,
                    score, num_comments, created_utc, url, is_promotional
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.reddit_id, post.title, post.content, post.author,
                post.subreddit, post.score, post.num_comments,
                post.created_utc, post.url, post.is_promotional
            ))
            
            post_id = cursor.lastrowid
            logger.debug(f"Inserted post with ID: {post_id}")
            return post_id
    
    def insert_posts_batch(self, posts: List[RedditPost]) -> int:
        """
        Insert multiple posts in a single transaction for better performance.
        
        Args:
            posts (List[RedditPost]): List of posts to insert
            
        Returns:
            int: Number of posts successfully inserted
        """
        inserted_count = 0
        
        with self.get_cursor() as cursor:
            for post in posts:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO posts (
                            reddit_id, title, content, author, subreddit,
                            score, num_comments, created_utc, url, is_promotional
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post.reddit_id, post.title, post.content, post.author,
                        post.subreddit, post.score, post.num_comments,
                        post.created_utc, post.url, post.is_promotional
                    ))
                    
                    if cursor.rowcount > 0:
                        inserted_count += 1
                        
                except sqlite3.Error as e:
                    logger.warning(f"Failed to insert post {post.reddit_id}: {e}")
        
        logger.info(f"Batch inserted {inserted_count} posts out of {len(posts)}")
        return inserted_count
    
    def get_post_by_reddit_id(self, reddit_id: str) -> Optional[RedditPost]:
        """
        Retrieve a post by its Reddit ID.
        
        Args:
            reddit_id (str): Reddit post ID
            
        Returns:
            Optional[RedditPost]: Post data if found, None otherwise
        """
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE reddit_id = ?", (reddit_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_post(row)
            return None
    
    def get_posts(self, limit: int = 100, offset: int = 0, 
                  subreddit: str = None, is_promotional: bool = None,
                  start_date: datetime = None, end_date: datetime = None) -> List[RedditPost]:
        """
        Retrieve posts with optional filtering.
        
        Args:
            limit (int): Maximum number of posts to return
            offset (int): Number of posts to skip
            subreddit (str, optional): Filter by subreddit
            is_promotional (bool, optional): Filter by promotional status
            start_date (datetime, optional): Filter posts after this date
            end_date (datetime, optional): Filter posts before this date
            
        Returns:
            List[RedditPost]: List of matching posts
        """
        query = "SELECT * FROM posts WHERE 1=1"
        params = []
        
        if subreddit:
            query += " AND subreddit = ?"
            params.append(subreddit)
        
        if is_promotional is not None:
            query += " AND is_promotional = ?"
            params.append(is_promotional)
        
        if start_date:
            query += " AND collected_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND collected_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY collected_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_post(row) for row in rows]
    
    def search_posts(self, keywords: List[str], subreddits: List[str] = None) -> List[RedditPost]:
        """
        Search posts by keywords in title and content.
        
        Args:
            keywords (List[str]): Keywords to search for
            subreddits (List[str], optional): Limit search to specific subreddits
            
        Returns:
            List[RedditPost]: List of matching posts
        """
        # Build search query with FTS if available, otherwise use LIKE
        keyword_conditions = []
        params = []
        
        for keyword in keywords:
            keyword_conditions.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        query = f"SELECT * FROM posts WHERE ({' OR '.join(keyword_conditions)})"
        
        if subreddits:
            subreddit_placeholders = ",".join(["?" for _ in subreddits])
            query += f" AND subreddit IN ({subreddit_placeholders})"
            params.extend(subreddits)
        
        query += " ORDER BY score DESC, collected_at DESC"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_post(row) for row in rows]
    
    def update_post_promotional_status(self, reddit_id: str, is_promotional: bool) -> bool:
        """
        Update the promotional status of a post.
        
        Args:
            reddit_id (str): Reddit post ID
            is_promotional (bool): New promotional status
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        with self.get_cursor() as cursor:
            cursor.execute(
                "UPDATE posts SET is_promotional = ? WHERE reddit_id = ?",
                (is_promotional, reddit_id)
            )
            
            return cursor.rowcount > 0
    
    def delete_post(self, reddit_id: str) -> bool:
        """
        Delete a post from the database.
        
        Args:
            reddit_id (str): Reddit post ID
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM posts WHERE reddit_id = ?", (reddit_id,))
            return cursor.rowcount > 0
    
    # =============================================================================
    # SEARCH HISTORY OPERATIONS
    # =============================================================================
    
    def insert_search_history(self, search: SearchHistory) -> int:
        """
        Insert a new search history record.
        
        Args:
            search (SearchHistory): Search history data
            
        Returns:
            int: ID of the inserted record
        """
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO search_history (
                    keywords, subreddits, time_filter, post_limit,
                    results_count, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                search.keywords, search.subreddits, search.time_filter,
                search.post_limit, search.results_count, search.status
            ))
            
            return cursor.lastrowid
    
    def get_search_history(self, limit: int = 50, offset: int = 0) -> List[SearchHistory]:
        """
        Retrieve search history records.
        
        Args:
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip
            
        Returns:
            List[SearchHistory]: List of search history records
        """
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM search_history 
                ORDER BY search_date DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            return [self._row_to_search_history(row) for row in rows]
    
    def update_search_status(self, search_id: int, status: str, results_count: int = None) -> bool:
        """
        Update the status of a search history record.
        
        Args:
            search_id (int): Search history ID
            status (str): New status
            results_count (int, optional): Number of results found
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        query = "UPDATE search_history SET status = ?"
        params = [status]
        
        if results_count is not None:
            query += ", results_count = ?"
            params.append(results_count)
        
        query += " WHERE id = ?"
        params.append(search_id)
        
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    # =============================================================================
    # STATISTICS AND ANALYTICS
    # =============================================================================
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns:
            Dict[str, Any]: Database statistics including counts, sizes, etc.
        """
        stats = {}
        
        with self.get_cursor() as cursor:
            # Post statistics
            cursor.execute("SELECT COUNT(*) FROM posts")
            stats['total_posts'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM posts WHERE is_promotional = 1")
            stats['promotional_posts'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT subreddit) FROM posts")
            stats['unique_subreddits'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT author) FROM posts")
            stats['unique_authors'] = cursor.fetchone()[0]
            
            # Search history statistics
            cursor.execute("SELECT COUNT(*) FROM search_history")
            stats['total_searches'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(results_count) FROM search_history WHERE status = 'completed'")
            avg_results = cursor.fetchone()[0]
            stats['avg_results_per_search'] = round(avg_results, 2) if avg_results else 0
            
            # Date range statistics
            cursor.execute("SELECT MIN(collected_at), MAX(collected_at) FROM posts")
            date_range = cursor.fetchone()
            stats['date_range'] = {
                'earliest_post': date_range[0],
                'latest_post': date_range[1]
            }
            
            # Top subreddits
            cursor.execute("""
                SELECT subreddit, COUNT(*) as count 
                FROM posts 
                GROUP BY subreddit 
                ORDER BY count DESC 
                LIMIT 10
            """)
            stats['top_subreddits'] = [
                {'subreddit': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
        
        # Database file size
        if os.path.exists(self.db_path):
            stats['database_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
        
        return stats
    
    # =============================================================================
    # DATA EXPORT FUNCTIONALITY
    # =============================================================================
    
    def export_posts_to_csv(self, filename: str, filters: Dict[str, Any] = None) -> str:
        """
        Export posts to CSV format.
        
        Args:
            filename (str): Output filename
            filters (Dict[str, Any], optional): Filters to apply to the export
            
        Returns:
            str: Full path to the exported file
        """
        # Apply filters if provided
        posts = self.get_posts(
            limit=EXPORT_CONFIG['max_export_size'],
            subreddit=filters.get('subreddit') if filters else None,
            is_promotional=filters.get('is_promotional') if filters else None,
            start_date=filters.get('start_date') if filters else None,
            end_date=filters.get('end_date') if filters else None
        )
        
        # Ensure export directory exists
        export_dir = EXPORT_CONFIG['export_directory']
        os.makedirs(export_dir, exist_ok=True)
        
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            if not posts:
                # Create empty file with headers
                writer = csv.writer(csvfile)
                writer.writerow([
                    'ID', 'Reddit ID', 'Title', 'Content', 'Author', 'Subreddit',
                    'Score', 'Comments', 'Created UTC', 'URL', 'Is Promotional', 'Collected At'
                ])
                return filepath
            
            fieldnames = [
                'id', 'reddit_id', 'title', 'content', 'author', 'subreddit',
                'score', 'num_comments', 'created_utc', 'url', 'is_promotional', 'collected_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for post in posts:
                writer.writerow(asdict(post))
        
        logger.info(f"Exported {len(posts)} posts to {filepath}")
        return filepath
    
    def export_posts_to_json(self, filename: str, filters: Dict[str, Any] = None) -> str:
        """
        Export posts to JSON format.
        
        Args:
            filename (str): Output filename
            filters (Dict[str, Any], optional): Filters to apply to the export
            
        Returns:
            str: Full path to the exported file
        """
        # Apply filters if provided
        posts = self.get_posts(
            limit=EXPORT_CONFIG['max_export_size'],
            subreddit=filters.get('subreddit') if filters else None,
            is_promotional=filters.get('is_promotional') if filters else None,
            start_date=filters.get('start_date') if filters else None,
            end_date=filters.get('end_date') if filters else None
        )
        
        # Ensure export directory exists
        export_dir = EXPORT_CONFIG['export_directory']
        os.makedirs(export_dir, exist_ok=True)
        
        filepath = os.path.join(export_dir, filename)
        
        # Convert posts to dictionaries and handle datetime serialization
        posts_data = []
        for post in posts:
            post_dict = asdict(post)
            # Convert datetime objects to ISO format strings
            for key, value in post_dict.items():
                if isinstance(value, datetime):
                    post_dict[key] = value.isoformat() if value else None
            posts_data.append(post_dict)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_posts': len(posts_data),
                    'filters_applied': filters or {}
                },
                'posts': posts_data
            }, jsonfile, **EXPORT_CONFIG['json_settings'])
        
        logger.info(f"Exported {len(posts)} posts to {filepath}")
        return filepath
    
    # =============================================================================
    # DATABASE MAINTENANCE
    # =============================================================================
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """
        Clean up old search history records.
        
        Args:
            days (int): Number of days to keep
            
        Returns:
            int: Number of records deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM search_history WHERE search_date < ?",
                (cutoff_date,)
            )
            
            deleted_count = cursor.rowcount
            logger.info(f"Cleaned up {deleted_count} old search history records")
            return deleted_count
    
    def vacuum_database(self) -> None:
        """Optimize database by running VACUUM command."""
        with self.get_cursor() as cursor:
            cursor.execute("VACUUM")
            logger.info("Database vacuum completed")
    
    def backup_database(self, backup_path: str = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path (str, optional): Custom backup path
            
        Returns:
            str: Path to the backup file
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"reddit_data_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_directory, backup_filename)
        
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Create backup
        shutil.copy2(self.db_path, backup_path)
        
        # Clean up old backups
        self._cleanup_old_backups()
        
        logger.info(f"Database backed up to {backup_path}")
        return backup_path
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backup files to maintain the maximum backup count."""
        if not os.path.exists(self.backup_directory):
            return
        
        # Get all backup files
        backup_files = []
        for filename in os.listdir(self.backup_directory):
            if filename.startswith("reddit_data_backup_") and filename.endswith(".db"):
                filepath = os.path.join(self.backup_directory, filename)
                backup_files.append((filepath, os.path.getmtime(filepath)))
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups
        for filepath, _ in backup_files[self.max_backups:]:
            try:
                os.remove(filepath)
                logger.debug(f"Removed old backup: {filepath}")
            except OSError as e:
                logger.warning(f"Failed to remove old backup {filepath}: {e}")
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _row_to_post(self, row: sqlite3.Row) -> RedditPost:
        """Convert database row to RedditPost object."""
        return RedditPost(
            id=row['id'],
            reddit_id=row['reddit_id'],
            title=row['title'],
            content=row['content'],
            author=row['author'],
            subreddit=row['subreddit'],
            score=row['score'],
            num_comments=row['num_comments'],
            created_utc=datetime.fromisoformat(row['created_utc']) if row['created_utc'] else None,
            url=row['url'],
            is_promotional=bool(row['is_promotional']),
            collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None
        )
    
    def _row_to_search_history(self, row: sqlite3.Row) -> SearchHistory:
        """Convert database row to SearchHistory object."""
        return SearchHistory(
            id=row['id'],
            keywords=row['keywords'],
            subreddits=row['subreddits'],
            time_filter=row['time_filter'],
            post_limit=row['post_limit'],
            results_count=row['results_count'],
            search_date=datetime.fromisoformat(row['search_date']) if row['search_date'] else None,
            status=row['status']
        )
    
    def close_connections(self) -> None:
        """Close all database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
        
        logger.info("Database connections closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connections()

    def create_tables(self) -> None:
        """Create database tables if they don't exist."""
        self._create_tables()
    
    def save_post(self, post: RedditPost) -> int:
        """Save a post to the database."""
        return self.insert_post(post)
    
    def save_search_history(self, search: SearchHistory) -> int:
        """Save search history to the database."""
        return self.insert_search_history(search)

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_database_manager() -> DatabaseManager:
    """
    Get a configured database manager instance.
    
    Returns:
        DatabaseManager: Configured database manager
    """
    return DatabaseManager()

def create_sample_data(db_manager: DatabaseManager, count: int = 10) -> None:
    """
    Create sample data for testing purposes.
    
    Args:
        db_manager (DatabaseManager): Database manager instance
        count (int): Number of sample posts to create
    """
    sample_posts = []
    
    for i in range(count):
        post = RedditPost(
            reddit_id=f"sample_{i}",
            title=f"Sample Post {i}",
            content=f"This is sample content for post {i}",
            author=f"user_{i}",
            subreddit="test",
            score=i * 10,
            num_comments=i * 2,
            created_utc=datetime.now() - timedelta(days=i),
            url=f"https://reddit.com/r/test/comments/sample_{i}",
            is_promotional=(i % 3 == 0)
        )
        sample_posts.append(post)
    
    db_manager.insert_posts_batch(sample_posts)
    logger.info(f"Created {count} sample posts")

# =============================================================================
# MODULE INITIALIZATION
# =============================================================================

if __name__ == "__main__":
    # Example usage and testing
    with get_database_manager() as db:
        # Create sample data
        create_sample_data(db, 5)
        
        # Get statistics
        stats = db.get_database_stats()
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Export data
        csv_file = db.export_posts_to_csv("sample_export.csv")
        json_file = db.export_posts_to_json("sample_export.json")
        
        print(f"Exported data to: {csv_file} and {json_file}") 