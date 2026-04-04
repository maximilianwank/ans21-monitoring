#!/usr/bin/env python3
"""
Standalone script to visualize ans21_monitoring.db data using Plotly.
Creates horizontal bar charts with one bar per day, colored by count value.
"""

import sqlite3
import datetime
from pathlib import Path
import plotly.graph_objects as go
from collections import defaultdict

# Database path
DB_PATH = "ans21_monitoring.db"


def get_all_readings():
    """Fetch all readings from the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, count FROM bright_spots ORDER BY timestamp"
            )
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading database: {e}")
        return []


def organize_by_day(readings):
    """Organize readings by date and time of day."""
    data_by_day = defaultdict(list)

    for timestamp, count in readings:
        dt = datetime.datetime.fromtimestamp(timestamp)
        date_str = dt.date().isoformat()
        time_of_day = dt.time()
        hours = dt.hour + dt.minute / 60  # Convert to decimal hours for positioning

        data_by_day[date_str].append(
            {
                "time": time_of_day.strftime("%H:%M"),
                "hours": hours,
                "count": count,
                "timestamp": timestamp,
            }
        )

    return data_by_day


def get_color(count):
    """Return color based on count value."""
    if count == 2:
        return "red"
    elif count == 3:
        return "green"
    else:
        return "grey"


def create_visualization(data_by_day):
    """Create horizontal bar chart visualization."""
    if not data_by_day:
        print("No data to visualize!")
        return

    # Sort dates for consistent ordering
    sorted_dates = sorted(data_by_day.keys(), reverse=True)

    fig = go.Figure()

    # Add a bar for each day
    for date_str in sorted_dates:
        day_data = data_by_day[date_str]

        # Sort by time of day
        day_data_sorted = sorted(day_data, key=lambda x: x["hours"])

        times = [d["time"] for d in day_data_sorted]
        hours = [d["hours"] for d in day_data_sorted]
        counts = [d["count"] for d in day_data_sorted]
        colors = [get_color(c) for c in counts]

        # Add a horizontal bar for this day
        fig.add_trace(
            go.Bar(
                y=[date_str] * len(hours),
                x=hours,
                orientation="h",
                name=date_str,
                marker=dict(color=colors),
                text=times,
                textposition="outside",
                textfont=dict(size=9),
                showlegend=False,
                hovertemplate="<b>%{y}</b><br>Time: %{text}<br>Count: "
                + "<extra></extra>"
                + ",".join([f"{t}: {c}" for t, c in zip(times, counts)]).split(",")[0],
            )
        )

    # Update layout
    fig.update_layout(
        title="Bright Spots Monitoring Data",
        xaxis_title="Time of Day (hours)",
        yaxis_title="Date",
        height=max(400, len(sorted_dates) * 100),
        hovermode="closest",
        barmode="overlay",
        xaxis=dict(
            range=[0, 24],
            tickvals=[0, 3, 6, 9, 12, 15, 18, 21, 24],
            ticktext=[
                "00:00",
                "03:00",
                "06:00",
                "09:00",
                "12:00",
                "15:00",
                "18:00",
                "21:00",
                "24:00",
            ],
        ),
        template="plotly_white",
    )

    # Save and show
    output_file = "monitoring_visualization.html"
    fig.write_html(output_file)
    print(f"Visualization saved to {output_file}")
    fig.show()


def main():
    """Main function."""
    print(f"Reading data from {DB_PATH}...")
    readings = get_all_readings()

    if not readings:
        print("No readings found in database!")
        return

    print(f"Found {len(readings)} readings")

    data_by_day = organize_by_day(readings)
    print(f"Data organized for {len(data_by_day)} days")

    create_visualization(data_by_day)


if __name__ == "__main__":
    main()
