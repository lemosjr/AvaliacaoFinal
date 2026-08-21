# backend/config/database.py
"""
Database connection manager with connection pooling.
Handles PostgreSQL connections and automatic migrations.
"""

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Generator, Dict, Any
import logging

from backend.config.settings import Settings

logger = logging.getLogger(__name__)


class Database:
    """
    Singleton database manager with connection pooling.
    
    Features:
    - Connection pooling for better performance
    - Automatic migrations on startup
    - Context managers for safe connection handling
    - RealDictCursor support for dict results
    
    Usage:
        # Get connection
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM products")
                results = cur.fetchall()
        
        # Get cursor with dict results
        with db.get_cursor(dict_cursor=True) as cur:
            cur.execute("SELECT * FROM products")
            results = cur.fetchall()  # Returns list of dicts
    """
    
    _instance: Optional['Database'] = None
    _pool: Optional[pool.SimpleConnectionPool] = None
    _db_config: Optional[Dict[str, Any]] = None
    
    def __new__(cls) -> 'Database':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection pool and run migrations."""
        if self._pool is None:
            self._db_config = Settings.get_database_config()
            self._create_pool()
            self._run_migrations()
    
    def _create_pool(self) -> None:
        """
        Creates the connection pool.
        Uses SimpleConnectionPool with min/max connections.
        """
        try:
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,   # Minimum connections kept alive
                maxconn=20,  # Maximum connections in pool
                **self._db_config
            )
            logger.info("✅ Database connection pool created successfully")
            
            # Test connection
            conn = self._pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]
                    logger.info(f"✅ Connected to PostgreSQL: {version[:50]}...")
            finally:
                self._pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"❌ Failed to create connection pool: {str(e)}")
            raise
    
    def _run_migrations(self) -> None:
        """
        Runs pending migrations automatically on startup.
        Migrations are located in backend/migrations/ directory.
        """
        try:
            from backend.migrations.manager import MigrationManager
            
            migration_manager = MigrationManager(self._db_config)
            migration_manager.run_all_migrations()
            migration_manager.run_seeders()
            
            logger.info("✅ Migrations executed successfully")
            
        except ImportError as e:
            logger.warning(f"⚠️  Migration manager not found: {str(e)}")
            logger.warning("⚠️  Skipping automatic migrations")
        except Exception as e:
            logger.error(f"❌ Failed to run migrations: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager for getting a database connection.
        Automatically handles commit/rollback and returns to pool.
        
        Yields:
            psycopg2.connection: Database connection
        
        Example:
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users")
                    results = cur.fetchall()
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Database operation error: {str(e)}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = False) -> Generator:
        """
        Context manager for getting a database cursor.
        Handles connection automatically.
        
        Args:
            dict_cursor: If True, returns results as dictionaries.
                        If False, returns as tuples.
        
        Yields:
            psycopg2.cursor: Database cursor
        
        Example:
            with db.get_cursor(dict_cursor=True) as cur:
                cur.execute("SELECT id, name FROM users")
                users = cur.fetchall()  # List of dicts
        """
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            with conn.cursor(cursor_factory=cursor_factory) as cur:
                yield cur
    
    def get_raw_connection(self):
        """
        Gets a raw connection from pool without context manager.
        Must be manually returned to pool with putconn().
        
        Returns:
            psycopg2.connection: Raw database connection
        
        Warning:
            Use get_connection() context manager when possible.
            Only use this for special operations.
        """
        return self._pool.getconn()
    
    def close_all_connections(self) -> None:
        """
        Closes all connections in the pool.
        Should be called when shutting down the application.
        """
        if self._pool:
            self._pool.closeall()
            logger.info("✅ All database connections closed")
    
    def reset_database(self, confirm: bool = False) -> None:
        """
        Resets the entire database (drops all tables and recreates).
        
        Args:
            confirm: Must be True to actually execute reset.
        
        Warning:
            This will DELETE ALL DATA in the database!
        """
        if not confirm:
            logger.warning("⚠️  Database reset not confirmed. Use confirm=True to force.")
            return
        
        try:
            from backend.migrations.manager import MigrationManager
            
            migration_manager = MigrationManager(self._db_config)
            migration_manager.reset_database(confirm=True)
            
            logger.info("✅ Database reset completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to reset database: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returns pool statistics for monitoring.
        
        Returns:
            dict: Pool statistics
        """
        if self._pool:
            return {
                'min_connections': self._pool.minconn,
                'max_connections': self._pool.maxconn,
                'used_connections': len(self._pool._used),
                'available_connections': len(self._pool._pool),
                'total_connections': len(self._pool._used) + len(self._pool._pool)
            }
        return {
            'status': 'not_initialized',
            'message': 'Connection pool not created'
        }
    
    def is_connected(self) -> bool:
        """
        Checks if the database is reachable.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception:
            return False
    
    def execute_sql(self, sql_query: str, params: tuple = (), dict_cursor: bool = False):
        """
        Executes a raw SQL query directly.
        
        Args:
            sql_query: SQL query string
            params: Query parameters (for prepared statements)
            dict_cursor: If True, returns dict results
        
        Returns:
            list: Query results (empty list for INSERT/UPDATE/DELETE)
        """
        with self.get_cursor(dict_cursor=dict_cursor) as cur:
            cur.execute(sql_query, params)
            
            # Return results if SELECT
            if sql_query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            
            # Return number of rows affected for INSERT/UPDATE/DELETE
            return {'rows_affected': cur.rowcount}


# ============ SINGLETON INSTANCE ============
# Global database instance - import this everywhere
db = Database()


# ============ CONVENIENCE FUNCTIONS ============

def get_db() -> Database:
    """Returns the global database instance."""
    return db


def execute_sql(sql_query: str, params: tuple = (), dict_cursor: bool = False):
    """
    Convenience function to execute SQL directly.
    Uses the global database instance.
    """
    return db.execute_sql(sql_query, params, dict_cursor)