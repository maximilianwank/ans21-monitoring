from unittest.mock import patch

from ans21_monitoring.web import create_app


class DummyDB:
    def __init__(self):
        self.requested_days = []

    def get_readings(self, days=3):
        self.requested_days.append(days)
        return []


def test_index_route_uses_default_3_days():
    db = DummyDB()
    app = create_app(db)
    client = app.test_client()

    with patch(
        "ans21_monitoring.web._build_chart_html", return_value="<div>chart</div>"
    ):
        response = client.get("/")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert db.requested_days == [3]
    assert "Pump Status Chart (Last 3 Days)" in body
    assert 'value="3"' in body


def test_index_route_accepts_custom_days():
    db = DummyDB()
    app = create_app(db)
    client = app.test_client()

    with patch(
        "ans21_monitoring.web._build_chart_html", return_value="<div>chart</div>"
    ):
        response = client.get("/?days=7")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert db.requested_days == [7]
    assert "Pump Status Chart (Last 7 Days)" in body
    assert 'value="7"' in body


def test_index_route_rejects_invalid_days():
    db = DummyDB()
    app = create_app(db)
    client = app.test_client()

    with patch(
        "ans21_monitoring.web._build_chart_html", return_value="<div>chart</div>"
    ):
        response = client.get("/?days=0")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert db.requested_days == [3]
    assert "Pump Status Chart (Last 3 Days)" in body


def test_index_route_rejects_non_numeric_days():
    db = DummyDB()
    app = create_app(db)
    client = app.test_client()

    with patch(
        "ans21_monitoring.web._build_chart_html", return_value="<div>chart</div>"
    ):
        response = client.get("/?days=abc")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert db.requested_days == [3]
    assert "Pump Status Chart (Last 3 Days)" in body
