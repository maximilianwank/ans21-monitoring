import sqlite3
import pytest
from ans21_monitoring.database import DatabaseManager
from ans21_monitoring.migrate import remove_consecutive_duplicates


def _create_old_schema_db(db_path, rows):
    """Create a DB with the old schema (id AUTOINCREMENT) and seed rows."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE bright_spots ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "timestamp INTEGER NOT NULL, "
            "count INTEGER NOT NULL)"
        )
        for ts, count in rows:
            cursor.execute(
                "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)",
                (ts, count),
            )
        conn.commit()
    return db_path


@pytest.fixture
def seeded_old_db(tmp_path):
    """DB with old schema and known consecutive duplicates."""
    return _create_old_schema_db(
        str(tmp_path / "migrate_old.db"),
        [
            (100, 3),
            (200, 3),  # dup
            (300, 2),
            (400, 2),  # dup
            (500, 2),  # dup
            (600, 3),
            (700, 3),  # dup
            (800, 2),
        ],
    )


@pytest.fixture
def seeded_new_db(tmp_path):
    """DB with new schema (timestamp PK) and known consecutive duplicates."""
    db_path = str(tmp_path / "migrate_new.db")
    manager = DatabaseManager(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
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


def test_migrate_old_schema(seeded_old_db):
    total, removed = remove_consecutive_duplicates(seeded_old_db)

    assert total == 8
    assert removed == 4

    with sqlite3.connect(seeded_old_db) as conn:
        cursor = conn.cursor()
        # Verify schema migrated: no 'id' column
        cursor.execute("PRAGMA table_info(bright_spots)")
        columns = {row[1] for row in cursor.fetchall()}
        assert columns == {"timestamp", "count"}

        cursor.execute("SELECT count FROM bright_spots ORDER BY timestamp ASC")
        remaining = [row[0] for row in cursor.fetchall()]

    assert remaining == [3, 2, 3, 2]


def test_migrate_new_schema(seeded_new_db):
    total, removed = remove_consecutive_duplicates(seeded_new_db)

    assert total == 8
    assert removed == 4

    with sqlite3.connect(seeded_new_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM bright_spots ORDER BY timestamp ASC")
        remaining = [row[0] for row in cursor.fetchall()]

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
