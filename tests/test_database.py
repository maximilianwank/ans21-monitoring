import pytest
import sqlite3
import datetime
from ans21_monitoring.database import DatabaseManager


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_ans21_monitoring.db"
    manager = DatabaseManager(str(db_file))
    yield manager


def test_get_readings(temp_db):
    # Insert some data
    now = int(datetime.datetime.now().timestamp())
    one_day_ago = int(
        (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()
    )
    four_days_ago = int(
        (datetime.datetime.now() - datetime.timedelta(days=4)).timestamp()
    )

    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)", (now, 3)
        )
        cursor.execute(
            "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)",
            (one_day_ago, 2),
        )
        cursor.execute(
            "INSERT INTO bright_spots (timestamp, count) VALUES (?, ?)",
            (four_days_ago, 3),
        )
        conn.commit()

    # Get readings for last 3 days
    readings = temp_db.get_readings(days=3)

    # Should get 2 readings (now and one_day_ago)
    assert len(readings) == 2

    timestamps = [r[0] for r in readings]
    assert now in timestamps
    assert one_day_ago in timestamps
    assert four_days_ago not in timestamps
