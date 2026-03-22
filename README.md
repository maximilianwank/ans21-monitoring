# ANS21 Monitoring

This project automates the monitoring of an ANS21 controller by taking photos, evaluating them, and exposing the results via a lightweight web server.

## Used Hardware

- Raspberry Pi Zero W
- USB Webcam

## Installation & Setup

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd ans21-monitoring
    ```

2.  Install System Dependencies (Raspberry Pi/Linux):
    OpenCV requires several system libraries that are often missing on minimal installations (like Raspberry Pi OS).
    ```bash
    sudo apt-get update
    sudo apt-get install -y libwebpdemux2 libtiff6 libopenjp2-7 libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
    ```

3.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4.  Install the package:
    ```bash
    pip install -e .
    ```

## Usage

Run the monitoring application:

```bash
python -m ans21_monitoring
```

## Web Interface

To view the pump status history (last 3 days):

```bash
python -m ans21_monitoring.web
```
Access the interface at `http://<pi-ip-address>:5000`.

## Automatic Startup (Systemd)

To run the monitoring service automatically when the Raspberry Pi boots, use a systemd service.

1.  Create a service file:

    ```bash
    sudo nano /etc/systemd/system/ans21-monitoring.service
    ```

2.  Paste the following configuration:
    (Adjust the `User` and `WorkingDirectory` paths if your username or installation path differs)

    ```ini
    [Unit]
    Description=ANS21 Monitoring Service
    After=network.target

    [Service]
    Type=simple
    # Replace with your actual username (e.g., pi)
    User=pi
    # Replace with the actual path to your project directory
    WorkingDirectory=/home/pi/ans21-monitoring
    # Replace with the path to the python executable in your virtual environment
    ExecStart=/home/pi/ans21-monitoring/.venv/bin/python -m ans21_monitoring
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```

3.  Enable and start the service:

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable ans21-monitoring.service
    sudo systemctl start ans21-monitoring.service
    ```

4.  check status and logs:

    ```bash
    sudo systemctl status ans21-monitoring.service
    # To follow logs provided by systemd (stdout/stderr)
    journalctl -u ans21-monitoring.service -f
    ```

    Note: The application also writes its own application logs to `.logs/ans21_monitoring.log` inside the project folder.
