# ANS21 Monitoring

This project automates the monitoring of an ANS21 controller by taking photos, evaluating them, and exposing the results via a lightweight web server.

## Hardware Requirements

- Raspberry Pi Zero W (or similar)
- USB Webcam (Generic/Cheap)

## Features

- Automated Capture: Periodically captures images of the ANS21 controller.
- Image Evaluation: Processes the captured images to extract relevant status or metrics from the controller display.
- Web Interface: A small built-in web server provides access to the latest results and images.

## Installation & Setup

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd ans21-monitoring
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Install the package:
    ```bash
    pip install -e .
    ```

## Usage

Run the monitoring application:

```bash
python -m ans21_monitoring
```
