import pytest
from unittest.mock import patch, MagicMock, call
import sys
from io import StringIO
from ans21_monitoring.__main__ import main


@patch("ans21_monitoring.__main__.time.sleep")
@patch("ans21_monitoring.__main__.count_bright_spots")
@patch("ans21_monitoring.__main__.take_picture")
def test_main_loop_success(mock_take_picture, mock_count, mock_sleep, capsys):
    # Setup mocks
    mock_take_picture.return_value = "fake_image"
    mock_count.return_value = 5

    # Mock sleep to raise KeyboardInterrupt to break the indefinite loop
    # We let it run once, then break
    mock_sleep.side_effect = KeyboardInterrupt

    # Execute
    main()

    # Assertions
    mock_take_picture.assert_called_once()
    mock_count.assert_called_once_with("fake_image")
    mock_sleep.assert_called_once_with(5)

    # Check output
    captured = capsys.readouterr()
    assert "Starting monitoring process" in captured.out
    assert "Bright spots detected: 5" in captured.out
    assert "Monitoring stopped by user" in captured.out


@patch("ans21_monitoring.__main__.time.sleep")
@patch("ans21_monitoring.__main__.count_bright_spots")
@patch("ans21_monitoring.__main__.take_picture")
def test_main_loop_handles_exception(mock_take_picture, mock_count, mock_sleep, capsys):
    # Setup mocks to simulate an error during picture taking
    mock_take_picture.side_effect = RuntimeError("Camera error")

    # Loop should continue after error, so we break it at sleep
    mock_sleep.side_effect = KeyboardInterrupt

    # Execute
    main()

    # Assertions
    mock_take_picture.assert_called_once()
    mock_count.assert_not_called()
    mock_sleep.assert_called_once_with(5)

    # Check output for error message
    captured = capsys.readouterr()
    assert "Error: Camera error" in captured.out
    assert "Monitoring stopped by user" in captured.out
