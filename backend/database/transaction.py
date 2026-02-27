import sqlite3
import time
from contextlib import contextmanager
from typing import Optional, Any, List
import logging

logger = logging.getLogger(__name__)

class TransactionManager:
    """Transaction manager kanggo database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    @contextmanager
    def transaction(self):
        """Context manager kanggo database transaction"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            logger.debug("Transaction started")
            yield cursor
            self.connection.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_with_retry(self, query: str, params: tuple = (), max_retries: int = 3):
        """Execute query with automatic retry on failure"""
        for attempt in range(max_retries):
            try:
                with self.transaction() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                raise
            except Exception as e:
                logger.error(f"Query failed: {e}")
                raise
    
    def execute_transaction(self, queries: List[str]) -> bool:
        """Execute multiple queries in transaction"""
        try:
            with self.transaction() as cursor:
                for query in queries:
                    cursor.execute(query)
            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

# Global instance
tx_manager = TransactionManager("/home/dibs/dibs1/dibs1.db")
