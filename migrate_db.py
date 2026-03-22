import sqlite3
import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "ans21_monitoring.db"


def migrate_database(db_path=DB_PATH):
    """Migrates the timestamp column from ISO string to Unix timestamp (int)."""

    if not Path(db_path).exists():
        logger.warning(f"Database file {db_path} not found. Skipping migration.")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='bright_spots'"
            )
            if cursor.fetchone()[0] == 0:
                logger.info("Table bright_spots does not exist. No migration needed.")
                # But wait, if table doesn't exist, we might want to ensure it's created correctly next time app runs.
                # The app logic handles creation.
                return

            # Check schema
            cursor.execute("PRAGMA table_info(bright_spots)")
            columns = cursor.fetchall()

            timestamp_col = next(
                (col for col in columns if col[1] == "timestamp"), None
            )

            if not timestamp_col:
                logger.error("Timestamp column not found in bright_spots table.")
                return

            col_type = timestamp_col[2]

            if "INT" in col_type.upper():
                logger.info(
                    "Database already uses INTEGER for timestamp. No migration needed."
                )
                return

            logger.info(
                f"Current timestamp column type is {col_type}. Starting migration..."
            )

            # Start transaction explicitly
            conn.execute("BEGIN TRANSACTION")

            try:
                # Rename existing table
                cursor.execute("ALTER TABLE bright_spots RENAME TO bright_spots_old")

                # Create new table
                cursor.execute(
                    """
                    CREATE TABLE bright_spots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp INTEGER NOT NULL,
                        count INTEGER NOT NULL
                    )
                """
                )

                # Migrate data
                cursor.execute("SELECT id, timestamp, count FROM bright_spots_old")
                rows = cursor.fetchall()

                new_rows = []
                for row in rows:
                    row_id, old_ts, count = row
                    new_ts = 0

                    if isinstance(old_ts, int):
                        new_ts = old_ts
                    elif isinstance(old_ts, str):
                        try:
                            # Try parsing as ISO format
                            dt = datetime.datetime.fromisoformat(old_ts)
                            new_ts = int(dt.timestamp())
                        except ValueError:
                            # Try parsing as integer string
                            try:
                                new_ts = int(old_ts)
                            except ValueError:
                                logger.error(
                                    f"Could not parse timestamp '{old_ts}' for row id {row_id}. Skipping."
                                )
                                continue
                    else:
                        try:
                            new_ts = int(old_ts)
                        except (ValueError, TypeError):
                            logger.error(
                                f"Unknown type {type(old_ts)} for timestamp '{old_ts}' for row id {row_id}. Skipping."
                            )
                            continue

                    new_rows.append((row_id, new_ts, count))

                if new_rows:
                    cursor.executemany(
                        "INSERT INTO bright_spots (id, timestamp, count) VALUES (?, ?, ?)",
                        new_rows,
                    )
                    logger.info(f"Migrated {len(new_rows)} rows.")
                else:
                    logger.info("No rows to migrate.")

                # Drop old table
                cursor.execute("DROP TABLE bright_spots_old")

                conn.commit()
                logger.info("Migration completed successfully.")

            except Exception as e:
                conn.rollback()
                logger.error(f"Error during migration transaction: {e}")
                # Restore original state if needed (though rollback should handle DB part)
                raise

    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")


if __name__ == "__main__":
    migrate_database()
