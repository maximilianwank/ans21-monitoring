"""Migration: deduplicate consecutive readings and migrate schema.

Removes consecutive duplicate bright-spot readings and migrates the table
from the old schema (id AUTOINCREMENT + timestamp + count) to the new
schema (timestamp PRIMARY KEY + count).

Usage:
    python -m ans21_monitoring.migrate [--db path/to/ans21_monitoring.db]
"""

import argparse
import sqlite3


def remove_consecutive_duplicates(db_path):
    """Deduplicate rows and migrate to timestamp-as-PK schema.

    Works on both old (id, timestamp, count) and new (timestamp, count)
    schemas.  Returns (total_rows, removed_count).
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Detect schema: check whether the 'id' column still exists.
        cursor.execute("PRAGMA table_info(bright_spots)")
        columns = {row[1] for row in cursor.fetchall()}
        has_id = "id" in columns

        order_col = "id" if has_id else "timestamp"
        cursor.execute(
            f"SELECT timestamp, count FROM bright_spots ORDER BY {order_col} ASC"
        )
        rows = cursor.fetchall()

        timestamps_to_delete = []
        prev_count = None
        for ts, count in rows:
            if count == prev_count:
                timestamps_to_delete.append(ts)
            prev_count = count

        if timestamps_to_delete:
            placeholders = ",".join("?" * len(timestamps_to_delete))
            cursor.execute(
                f"DELETE FROM bright_spots WHERE timestamp IN ({placeholders})",
                timestamps_to_delete,
            )

        # Migrate to new schema if the old 'id' column is present.
        if has_id:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bright_spots_new (
                    timestamp INTEGER PRIMARY KEY,
                    count INTEGER NOT NULL
                )
                """
            )
            cursor.execute(
                "INSERT OR IGNORE INTO bright_spots_new (timestamp, count) "
                "SELECT timestamp, count FROM bright_spots"
            )
            cursor.execute("DROP TABLE bright_spots")
            cursor.execute("ALTER TABLE bright_spots_new RENAME TO bright_spots")

        conn.commit()

    return len(rows), len(timestamps_to_delete)


def main():
    parser = argparse.ArgumentParser(
        description="Deduplicate readings and migrate to timestamp-PK schema."
    )
    parser.add_argument(
        "--db", default="ans21_monitoring.db", help="Path to the SQLite database"
    )
    args = parser.parse_args()

    total, removed = remove_consecutive_duplicates(args.db)
    print(f"Processed {total} records, removed {removed} consecutive duplicates.")


if __name__ == "__main__":
    main()
