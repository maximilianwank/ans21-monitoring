import cv2
import numpy as np


def count_bright_spots(img: np.ndarray, threshold_value: int = 174) -> int:
    """
    Counts the number of bright spots in an image.

    Args:
        img (numpy.ndarray): The image to analyze (BGR format expected).
        threshold_value (int): Threshold value for binarization (0-255). Default optimized to 225.

    Returns:
        int: Number of bright spots found.
    """
    if img is None:
        raise ValueError("Image cannot be None")

    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Slight blurring (filters sensor noise)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Apply threshold
    # Everything above 'threshold_value' becomes 255 (white), the rest 0 (black)
    _, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY)

    # 4. Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Optional: Filter by minimum size to ignore tiny light points
    min_area = 5
    valid_spots = [c for c in contours if cv2.contourArea(c) > min_area]

    return len(valid_spots)


if __name__ == "__main__":
    # Example usage (for testing purposes)
    test_image_path = "/home/max/Code/ans21-monitoring/tests/sample_images/2026-03-20T08:15:02+01:00.jpg"  # Replace with your test image path
    img = cv2.imread(test_image_path)
    valid = []
    for i in range(1, 255):
        count = count_bright_spots(img, threshold_value=i)
        if count == 2:
            valid.append(i)
    print(f"Valid thresholds for 2 bright spots: {valid}")
