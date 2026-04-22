from flask import Flask, render_template_string, request
import datetime
from collections import defaultdict

import plotly.graph_objects as go


COUNT_COLORS = {
    2: "#d9a1a1",
    3: "#8fbf8f",
}
DEFAULT_COLOR = "#9b9b9b"

COUNT_LABELS = {
    2: "pump not running",
    3: "pump running",
}
DEFAULT_LABEL = "unknown"


def create_app(db_manager):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return _render_chart(db_manager, days=3)

    @app.route("/chart")
    def chart():
        days = _get_requested_days(request.args.get("days"))
        return _render_chart(db_manager, days=days)

    return app


def _get_color(count):
    return COUNT_COLORS.get(count, DEFAULT_COLOR)


def _get_label(count):
    return COUNT_LABELS.get(count, DEFAULT_LABEL)


def _get_requested_days(days_value, default=15):
    try:
        days = int(days_value)
    except (TypeError, ValueError):
        return default

    return days if days > 0 else default


def _build_segments(readings, days=15):
    """Turn point readings into (start, end, count) segments per day."""
    by_day = defaultdict(list)
    for ts, count in readings:
        dt = datetime.datetime.fromtimestamp(ts)
        by_day[dt.date()].append((dt, count))

    segments = []
    today = datetime.date.today()
    now = datetime.datetime.now()
    all_dates = [
        today - datetime.timedelta(days=offset) for offset in range(days - 1, -1, -1)
    ]

    for date in all_dates:
        points = by_day.get(date, [])
        points.sort()
        if not points:
            end_h = (
                now.hour + now.minute / 60 + now.second / 3600
                if date == today
                else 24.0
            )
            segments.append((date, 0.0, end_h, 2))
            continue

        day_start = datetime.datetime.combine(date, datetime.time.min)
        if points[0][0] > day_start:
            points.insert(0, (day_start, 2))

        for i, (dt, count) in enumerate(points):
            start_h = dt.hour + dt.minute / 60 + dt.second / 3600
            if i + 1 < len(points):
                nxt = points[i + 1][0]
                end_h = nxt.hour + nxt.minute / 60 + nxt.second / 3600
            else:
                # Last reading of the day extends to end-of-day (or now if today).
                if date == today:
                    end_h = now.hour + now.minute / 60 + now.second / 3600
                else:
                    end_h = 24.0
            segments.append((date, start_h, end_h, count))

    return segments


def _build_chart_html(readings, days=15):
    segments = _build_segments(readings, days=days)

    today = datetime.date.today()
    all_dates = [today - datetime.timedelta(days=i) for i in range(days)]
    date_labels = [d.strftime("%a %Y-%m-%d") for d in all_dates]

    fig = go.Figure()

    for date, start_h, end_h, count in segments:
        label = date.strftime("%a %Y-%m-%d")
        if label not in date_labels:
            continue
        status = _get_label(count)
        fig.add_trace(
            go.Bar(
                y=[label],
                x=[end_h - start_h],
                base=[start_h],
                orientation="h",
                marker_color=_get_color(count),
                showlegend=False,
                hovertemplate=(
                    f"<b>{label}</b><br>"
                    f"Status: {status}<br>"
                    f"{int(start_h):02d}:{int((start_h % 1) * 60):02d} - "
                    f"{int(end_h):02d}:{int((end_h % 1) * 60):02d}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=f"Bright Spots - Last {days} Days",
        dragmode="zoom",
        selectdirection="h",
        xaxis=dict(
            title="Time of Day",
            range=[7, 18],
            tickvals=list(range(25)),
            ticktext=[f"{h:02d}:00" for h in range(25)],
            fixedrange=False,
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=list(reversed(date_labels)),
            fixedrange=True,
        ),
        barmode="overlay",
        height=500,
        template="plotly_white",
        bargap=0.3,
    )

    return fig.to_html(
        full_html=False, include_plotlyjs="cdn", config={"scrollZoom": True}
    )


def _render_chart(db_manager, days=15):
    readings = db_manager.get_readings(days=days)
    chart_html = _build_chart_html(readings, days=days)

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pump Chart</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            body { font-family: sans-serif; margin: 0; padding: 20px; background: #f8fafc; }
            .container { max-width: 1100px; margin: 0 auto; }
            h1 { margin: 0 0 16px; text-align: center; }
            .controls { display: flex; justify-content: center; margin-bottom: 16px; }
            .controls form { display: flex; gap: 8px; align-items: center; background: white; padding: 12px 14px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.08); }
            .controls input { width: 90px; padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 6px; }
            .controls button { padding: 8px 14px; border: 0; border-radius: 6px; background: #2563eb; color: white; cursor: pointer; }
            .panel { background: white; border-radius: 10px; padding: 12px; box-shadow: 0 0 20px rgba(0,0,0,0.08); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Pump Status Chart (Last {{ days }} Days)</h1>
            <div class="controls">
                <form method="get" action="/chart">
                    <label for="days">Days</label>
                    <input id="days" name="days" type="number" min="1" value="{{ days }}" />
                    <button type="submit">Update</button>
                </form>
            </div>
            <div class="panel">
                {{ chart_html | safe }}
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(template, chart_html=chart_html, days=days)
