#!/usr/bin/env python3
"""Visualize ans21_monitoring.db data as a Plotly Gantt chart (last 15 days)."""

import sqlite3
import datetime
from collections import defaultdict

import plotly.graph_objects as go

DB_PATH = "ans21_monitoring.db"

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


def get_color(count):
    return COUNT_COLORS.get(count, DEFAULT_COLOR)


def get_label(count):
    return COUNT_LABELS.get(count, DEFAULT_LABEL)


def get_readings(days=15):
    threshold = int(
        (
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            - datetime.timedelta(days=days - 1)
        ).timestamp()
    )
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, count FROM bright_spots "
            "WHERE timestamp >= ? ORDER BY timestamp",
            (threshold,),
        )
        return cursor.fetchall()


def build_segments(readings, days=15):
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
                # last reading of the day: extend to end of day (or now if today)
                if date == today:
                    end_h = now.hour + now.minute / 60 + now.second / 3600
                else:
                    end_h = 24.0
            segments.append((date, start_h, end_h, count))

    return segments


def create_chart(segments):
    today = datetime.date.today()
    # All 15 days, today first (top of chart)
    all_dates = [today - datetime.timedelta(days=i) for i in range(15)]
    date_labels = [d.strftime("%a %Y-%m-%d") for d in all_dates]

    fig = go.Figure()

    for date, start_h, end_h, count in segments:
        label = date.strftime("%a %Y-%m-%d")
        if label not in date_labels:
            continue
        status = get_label(count)
        fig.add_trace(
            go.Bar(
                y=[label],
                x=[end_h - start_h],
                base=[start_h],
                orientation="h",
                marker_color=get_color(count),
                showlegend=False,
                hovertemplate=(
                    f"<b>{label}</b><br>"
                    f"Status: {status}<br>"
                    f"{int(start_h):02d}:{int((start_h % 1) * 60):02d} – "
                    f"{int(end_h):02d}:{int((end_h % 1) * 60):02d}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Bright Spots – Last 15 Days",
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
            categoryarray=list(reversed(date_labels)),  # today on top
            fixedrange=True,
        ),
        barmode="overlay",
        height=500,
        template="plotly_white",
        bargap=0.3,
    )

    output_file = "monitoring_visualization.html"
    fig.write_html(output_file, config={"scrollZoom": True})
    print(f"Saved to {output_file}")
    fig.show()


def main():
    readings = get_readings(days=15)
    if not readings:
        print("No readings found!")
        return
    print(f"{len(readings)} readings loaded")
    segments = build_segments(readings, days=15)
    create_chart(segments)


if __name__ == "__main__":
    main()
