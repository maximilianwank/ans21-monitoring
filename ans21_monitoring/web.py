from flask import Flask, render_template_string
import datetime


def create_app(db_manager):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return _render_index(db_manager)

    return app


def _render_index(db_manager):
    # Fetch readings for the last 3 days
    readings = db_manager.get_readings(days=3)

    # Process readings
    processed_data = []

    for timestamp, count in readings:
        if count not in [2, 3]:
            continue

        status = "Pump running" if count == 3 else "Pump not running"
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

        processed_data.append(
            {
                "timestamp": formatted_time,
                "timestamp_raw": timestamp,
                "status": status,
                "count": count,
            }
        )

    # Sort by timestamp descending
    processed_data.sort(key=lambda x: x["timestamp_raw"], reverse=True)

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pump Monitor</title>
        <style>
            body { font-family: sans-serif; margin: 2rem; max-width: 800px; margin: 0 auto; padding: 20px;}
            h1 { text-align: center; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #007bff; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .running { color: green; font-weight: bold; }
            .stopped { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Pump Status (Last 3 Days)</h1>
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Bright Spots</th>
                </tr>
            </thead>
            <tbody>
                {% for item in data %}
                <tr>
                    <td>{{ item.timestamp }}</td>
                    <td class="{{ 'running' if item.count == 3 else 'stopped' }}">
                        {{ item.status }}
                    </td>
                    <td>{{ item.count }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="3" style="text-align: center;">No data available for the last 3 days.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    return render_template_string(template, data=processed_data)
