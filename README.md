# ANS21 Monitoring

This project automates the monitoring of an ANS21 controller by taking photos, evaluating them, and exposing the results via a lightweight web server.

## Hardware Requirements

- **Raspberry Pi Zero W** (or similar)
- **USB Webcam** (Generic/Cheap)

## Features

- **Automated Capture**: Periodically captures images of the ANS21 controller.
- **Image Evaluation**: Processes the captured images to extract relevant status or metrics from the controller display.
- **Web Interface**: A small built-in web server provides access to the latest results and images.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ans21-monitoring
    ```

2.  **Install dependencies:**
    ```bash
    pip install .
    # Or install specific requirements if provided in requirements.txt
    ```

3.  **Run the application:**
    ```bash
    # Command to run the script (e.g., python main.py)
    ```

## Development

This is a Python project managed with `pyproject.toml`.
