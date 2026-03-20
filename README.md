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
