import pytest
import numpy as np
import cv2
import os
from pathlib import Path
from ans21_monitoring.image_analysis import count_bright_spots


def test_count_bright_spots_basic():
    # Create a dummy image: black background with white spots
    # 100x100 black image
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

    # Draw two white circles (bright spots)
    # Brightness needs to be > threshold (200)
    # (255, 255, 255) is white
    cv2.circle(dummy_img, (25, 25), 10, (255, 255, 255), -1)
    cv2.circle(dummy_img, (75, 75), 10, (255, 255, 255), -1)

    # Call the function directly with the image
    count = count_bright_spots(dummy_img, threshold_value=200)

    # Assert that 2 spots are found
    assert count == 2


def test_invalid_input():
    # Test with None input
    with pytest.raises(ValueError, match="Image cannot be None"):
        count_bright_spots(None)


def get_sample_images():
    base_path = Path(__file__).parent / "sample_images"
    if not base_path.exists():
        return []
    return list(base_path.glob("*.jpg"))


@pytest.mark.parametrize("img_path", get_sample_images(), ids=lambda p: p.name)
def test_sample_images_jpg(img_path):
    # Read the image
    img = cv2.imread(str(img_path))

    # Ensure image was loaded successfully
    if img is None:
        pytest.fail(f"Failed to load image: {img_path}")

    # Run the analysis
    count = count_bright_spots(img, threshold_value=200)

    # Basic assertion: result must be a non-negative integer
    assert isinstance(count, int)
    assert count >= 0
