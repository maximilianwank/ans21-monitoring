import sqlite3
import pytest
from ans21_monitoring.database import DatabaseManager
from ans21_monitoring.migrate import remove_consecutive_duplicates


@pytest.fixture
def seeded_db(tmp_path):
    """Create a DB with known consecutive duplicates."""
    db_path = str(tmp_path / "migrate_test.db")
    manager = DatabaseManager(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # id:  1  2  3  4  5  6  7  8
        # cnt: 3  3  2  2  2  3  3  2
        for ts, count in [
            (100, 3),
            (200, 3),  # dup
            (300, 2),
            (400, 2),  # dup
            (500, 2),  # dup
            (600, 3),
            (700, 3),  # dup
            (800, 2),
        ]:
            cursor.execute(
                "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)",
                (ts, count),
            )
        conn.commit()

    return db_path


def test_remove_consecutive_duplicates(seeded_db):
    total, removed = remove_consecutive_duplicates(seeded_db)

    assert total == 8
    assert removed == 4

    with sqlite3.connect(seeded_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM bright_spots ORDER BY id ASC")
        remaining = [row[0] for row in cursor.fetchall()]

    # Only change-boundary records remain: 3, 2, 3, 2
    assert remaining == [3, 2, 3, 2]


def test_remove_consecutive_duplicates_empty(tmp_path):
    db_path = str(tmp_path / "empty.db")
    DatabaseManager(db_path)

    total, removed = remove_consecutive_duplicates(db_path)
    assert total == 0
    assert removed == 0


def test_remove_consecutive_duplicates_no_dupes(tmp_path):
    db_path = str(tmp_path / "no_dupes.db")
    DatabaseManager(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for ts, count in [(100, 2), (200, 3), (300, 2)]:
            cursor.execute(
                "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)",
                (ts, count),
            )
        conn.commit()

    total, removed = remove_consecutive_duplicates(db_path)
    assert total == 3
    assert removed == 0
