import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


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
    logger.debug("Taking picture on camera %d", camera_index)
    # Initialize the camera
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        error_msg = f"Could not open camera with index {camera_index}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    try:
        # Read a frame
        ret, frame = cap.read()

        if not ret:
            error_msg = "Failed to capture image frame"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.debug("Successfully captured frame.")
        return frame
    finally:
        # Release the camera resource
        cap.release()
