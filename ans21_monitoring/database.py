import sqlite3
import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path="ans21_monitoring.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bright_spots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp INTEGER NOT NULL,
                        count INTEGER NOT NULL
                    )
                """
                )
                conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def save_reading(self, count):
        """Save a new reading with the current timestamp."""
        try:
            timestamp = int(datetime.datetime.now().timestamp())
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)",
                    (timestamp, count),
                )
                conn.commit()
            logger.debug(f"Saved reading: {count} spots at {timestamp}")
        except sqlite3.Error as e:
            logger.error(f"Failed to save reading: {e}")

    def get_readings(self, days=3):
        """Get readings from the last n days."""
        try:
            timestamp_threshold = int(
                (datetime.datetime.now() - datetime.timedelta(days=days)).timestamp()
            )
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT timestamp, count FROM bright_spots WHERE timestamp >= ?",
                    (timestamp_threshold,),
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to get readings: {e}")
            return []
