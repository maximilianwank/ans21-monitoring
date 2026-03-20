import cv2
import numpy as np


def count_bright_spots(img: np.ndarray, threshold_value: int = 225) -> int:
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

    # 1. In Graustufen umwandeln
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Leichtes Weichzeichnen (filtert Sensor-Rauschen)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Schwellenwert anwenden
    # Alles über 'threshold_value' wird 255 (weiß), der Rest 0 (schwarz)
    _, thresh = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY)

    # 4. Konturen finden
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Optional: Filter nach Mindestgröße, um winzige Lichtpunkte zu ignorieren
    min_area = 5
    valid_spots = [c for c in contours if cv2.contourArea(c) > min_area]

    return len(valid_spots)
