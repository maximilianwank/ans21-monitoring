"""Migration: remove consecutive duplicate bright-spot readings from the database.

Usage:
    python -m ans21_monitoring.migrate [--db path/to/ans21_monitoring.db]
"""

import argparse
import sqlite3


def remove_consecutive_duplicates(db_path):
    """Delete rows whose count equals the immediately preceding row's count.

    Returns (total_rows, removed_count).
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, count FROM bright_spots ORDER BY id ASC")
        rows = cursor.fetchall()

        ids_to_delete = []
        prev_count = None
        for row_id, count in rows:
            if count == prev_count:
                ids_to_delete.append(row_id)
            prev_count = count

        if ids_to_delete:
            placeholders = ",".join("?" * len(ids_to_delete))
            cursor.execute(
                f"DELETE FROM bright_spots WHERE id IN ({placeholders})",
                ids_to_delete,
            )
            conn.commit()

    return len(rows), len(ids_to_delete)


def main():
    parser = argparse.ArgumentParser(
        description="Remove consecutive duplicate bright-spot readings."
    )
    parser.add_argument(
        "--db", default="ans21_monitoring.db", help="Path to the SQLite database"
    )
    args = parser.parse_args()

    total, removed = remove_consecutive_duplicates(args.db)
    print(f"Processed {total} records, removed {removed} consecutive duplicates.")


if __name__ == "__main__":
    main()
