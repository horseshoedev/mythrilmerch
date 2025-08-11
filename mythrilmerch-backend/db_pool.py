"""
Database connection pooling for MythrilMerch API
"""

import psycopg2
from psycopg2 import pool
import logging
import os
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)

class DatabasePool:
    """Database connection pool manager"""
    
    def __init__(self, min_connections=1, max_connections=20):
        self.pool = None
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.stats = {
            'connections_created': 0,
            'connections_used': 0,
            'connections_failed': 0,
            'pool_full_count': 0
        }
    
    def initialize(self, host, database, user, password, port=5432):
        """Initialize the connection pool"""
        try:
            self.pool = pool.ThreadedConnectionPool(
                minconn=self.min_connections,
                maxconn=self.max_connections,
                host=host,
                database=database,
                user=user,
                password=password,
                port=port,
                connect_timeout=10
            )
            logger.info(f"Database pool initialized: {self.min_connections}-{self.max_connections} connections")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            return False
    
    def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return None
        
        try:
            conn = self.pool.getconn()
            if conn:
                self.stats['connections_used'] += 1
                logger.debug("Connection acquired from pool")
            return conn
        except Exception as e:
            self.stats['connections_failed'] += 1
            logger.error(f"Failed to get connection from pool: {e}")
            return None
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if not self.pool or not conn:
            return
        
        try:
            self.pool.putconn(conn)
            logger.debug("Connection returned to pool")
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")
    
    def close_pool(self):
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")
    
    def get_stats(self):
        """Get pool statistics"""
        if self.pool:
            pool_stats = {
                'min_connections': self.min_connections,
                'max_connections': self.max_connections,
                'current_connections': len(self.pool._used),
                'available_connections': len(self.pool._pool),
                'total_connections': len(self.pool._used) + len(self.pool._pool)
            }
        else:
            pool_stats = {
                'min_connections': self.min_connections,
                'max_connections': self.max_connections,
                'current_connections': 0,
                'available_connections': 0,
                'total_connections': 0
            }
        
        return {**pool_stats, **self.stats}

# Global database pool instance
db_pool = DatabasePool()

def init_db_pool():
    """Initialize the global database pool"""
    host = os.environ.get("DB_HOST", "localhost")
    database = os.environ.get("DB_NAME", "ecommerce_db")
    user = os.environ.get("DB_USER", "ecommerce_user")
    password = os.environ.get("DB_PASSWORD", "your_strong_password")
    port = int(os.environ.get("DB_PORT", "5432"))
    
    min_conn = int(os.environ.get("DB_MIN_CONNECTIONS", "1"))
    max_conn = int(os.environ.get("DB_MAX_CONNECTIONS", "20"))
    
    db_pool.min_connections = min_conn
    db_pool.max_connections = max_conn
    
    return db_pool.initialize(host, database, user, password, port)

def get_db_connection():
    """Get a database connection from the pool"""
    return db_pool.get_connection()

@contextmanager
def get_db_cursor():
    """Context manager for database operations"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Failed to get database connection")
        
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if conn:
            db_pool.return_connection(conn)

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a database query with automatic connection management"""
    with get_db_cursor() as cur:
        cur.execute(query, params or ())
        
        if fetch_one:
            return cur.fetchone()
        elif fetch_all:
            return cur.fetchall()
        else:
            return cur.rowcount

def health_check():
    """Check database pool health"""
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False 