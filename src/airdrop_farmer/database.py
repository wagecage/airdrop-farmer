"""
Database management for state persistence
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

from .utils.logger import setup_logger
from .config import config

logger = setup_logger()


class Database:
    """SQLite database manager for application state"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or config.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()
        self._initialize_tables()

    def _connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")

    def _initialize_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Activity log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                wallet_address TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                tx_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Wallet state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallet_state (
                wallet_address TEXT PRIMARY KEY,
                last_megaeth_activity TEXT,
                last_lighter_activity TEXT,
                last_polymarket_activity TEXT,
                total_transactions INTEGER DEFAULT 0,
                megaeth_tx_count INTEGER DEFAULT 0,
                lighter_points REAL DEFAULT 0,
                polymarket_trades INTEGER DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Platform stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS platform_stats (
                platform TEXT PRIMARY KEY,
                total_activities INTEGER DEFAULT 0,
                successful_activities INTEGER DEFAULT 0,
                failed_activities INTEGER DEFAULT 0,
                last_activity_time TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Scheduler runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduler_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TEXT NOT NULL,
                status TEXT NOT NULL,
                wallets_processed INTEGER DEFAULT 0,
                activities_completed INTEGER DEFAULT 0,
                errors TEXT,
                duration_seconds REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        logger.info("Database tables initialized")

    def log_activity(
        self,
        wallet_address: str,
        activity_type: str,
        platform: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        tx_hash: Optional[str] = None
    ) -> int:
        """
        Log an activity

        Args:
            wallet_address: Wallet address
            activity_type: Type of activity
            platform: Platform name
            status: Activity status (success/failed)
            details: Additional details
            tx_hash: Transaction hash if applicable

        Returns:
            Activity ID
        """
        cursor = self.conn.cursor()
        timestamp = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO activity_log (timestamp, wallet_address, activity_type, platform, status, details, tx_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            wallet_address,
            activity_type,
            platform,
            status,
            json.dumps(details) if details else None,
            tx_hash
        ))

        self.conn.commit()
        activity_id = cursor.lastrowid

        logger.info(f"Logged activity {activity_id}: {platform} - {activity_type} for {wallet_address}")
        return activity_id

    def update_wallet_state(self, wallet_address: str, updates: Dict[str, Any]):
        """
        Update wallet state

        Args:
            wallet_address: Wallet address
            updates: Dictionary of field updates
        """
        cursor = self.conn.cursor()

        # Insert or update
        cursor.execute("""
            INSERT INTO wallet_state (wallet_address) VALUES (?)
            ON CONFLICT(wallet_address) DO NOTHING
        """, (wallet_address,))

        # Build update query
        if updates:
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            set_clause += ", updated_at = ?"
            values = list(updates.values()) + [datetime.utcnow().isoformat(), wallet_address]

            cursor.execute(f"""
                UPDATE wallet_state
                SET {set_clause}
                WHERE wallet_address = ?
            """, values)

        self.conn.commit()

    def get_wallet_state(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """
        Get wallet state

        Args:
            wallet_address: Wallet address

        Returns:
            Wallet state dictionary
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM wallet_state WHERE wallet_address = ?
        """, (wallet_address,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def update_platform_stats(self, platform: str, success: bool):
        """
        Update platform statistics

        Args:
            platform: Platform name
            success: Whether activity was successful
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO platform_stats (platform, total_activities, successful_activities, failed_activities, last_activity_time)
            VALUES (?, 1, ?, ?, ?)
            ON CONFLICT(platform) DO UPDATE SET
                total_activities = total_activities + 1,
                successful_activities = successful_activities + ?,
                failed_activities = failed_activities + ?,
                last_activity_time = ?,
                updated_at = ?
        """, (
            platform,
            1 if success else 0,
            0 if success else 1,
            datetime.utcnow().isoformat(),
            1 if success else 0,
            0 if success else 1,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))

        self.conn.commit()

    def log_scheduler_run(self, status: str, wallets_processed: int, activities_completed: int,
                         errors: Optional[List[str]] = None, duration: Optional[float] = None) -> int:
        """
        Log a scheduler run

        Args:
            status: Run status
            wallets_processed: Number of wallets processed
            activities_completed: Number of activities completed
            errors: List of errors
            duration: Duration in seconds

        Returns:
            Run ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO scheduler_runs (run_time, status, wallets_processed, activities_completed, errors, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            status,
            wallets_processed,
            activities_completed,
            json.dumps(errors) if errors else None,
            duration
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_recent_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent activities

        Args:
            limit: Maximum number of activities to retrieve

        Returns:
            List of activity dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM activity_log
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_platform_stats(self) -> List[Dict[str, Any]]:
        """
        Get all platform statistics

        Returns:
            List of platform stats dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM platform_stats")
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
