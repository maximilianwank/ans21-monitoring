import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from ans21_monitoring.camera import take_picture


@patch("ans21_monitoring.camera.cv2")
def test_take_picture_success(mock_cv2):
    # Setup mocks
    mock_cap = MagicMock()
    mock_cv2.VideoCapture.return_value = mock_cap

    # Configure mock behavior
    mock_cap.isOpened.return_value = True
    fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_cap.read.return_value = (True, fake_frame)

    # Execute
    result = take_picture(camera_index=0)

    # Assert
    assert result is fake_frame
    mock_cv2.VideoCapture.assert_called_once_with(0)
    mock_cap.isOpened.assert_called_once()
    mock_cap.read.assert_called_once()
    mock_cap.release.assert_called_once()


@patch("ans21_monitoring.camera.cv2")
def test_take_picture_cannot_open_camera(mock_cv2):
    # Setup mocks
    mock_cap = MagicMock()
    mock_cv2.VideoCapture.return_value = mock_cap

    # Return False for isOpened
    mock_cap.isOpened.return_value = False

    # Execute and Assert
    with pytest.raises(RuntimeError, match="Could not open camera with index 99"):
        take_picture(camera_index=99)

    mock_cv2.VideoCapture.assert_called_once_with(99)


@patch("ans21_monitoring.camera.cv2")
def test_take_picture_capture_failed(mock_cv2):
    # Setup mocks
    mock_cap = MagicMock()
    mock_cv2.VideoCapture.return_value = mock_cap

    # Opened successfully, but read failed
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)

    # Execute and Assert
    with pytest.raises(RuntimeError, match="Failed to capture image frame"):
        take_picture(camera_index=0)

    # In this case, it enters try block, so finally should execute
    mock_cap.release.assert_called_once()
