import cv2
import numpy as np


def take_picture(camera_index: int = 0) -> np.ndarray:
    """
    Captures an image from the specified camera device.

    Args:
        camera_index (int): The index of the camera device (default is 0).

    Returns:
        numpy.ndarray: The captured image in BGR format.

    Raises:
        RuntimeError: If the camera cannot be opened or reading the frame fails.
    """
    # Initialize the camera
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera with index {camera_index}")

    try:
        # Read a frame
        ret, frame = cap.read()

        if not ret:
            raise RuntimeError("Failed to capture image frame")

        return frame
    finally:
        # Release the camera resource
        cap.release()
