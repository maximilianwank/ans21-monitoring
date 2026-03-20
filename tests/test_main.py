import pytest
from unittest.mock import patch
from ans21_monitoring.__main__ import main


@pytest.fixture
def mock_dependencies():
    with (
        patch("ans21_monitoring.__main__.setup_logging") as mock_setup,
        patch("ans21_monitoring.__main__.DatabaseManager") as mock_db_cls,
        patch("ans21_monitoring.__main__.take_picture") as mock_take_picture,
        patch("ans21_monitoring.__main__.count_bright_spots") as mock_count,
        patch("ans21_monitoring.__main__.time.sleep") as mock_sleep,
        patch("ans21_monitoring.__main__.signal.signal") as mock_signal,
    ):

        mock_db_instance = mock_db_cls.return_value
        yield {
            "setup_logging": mock_setup,
            "db_cls": mock_db_cls,
            "db_instance": mock_db_instance,
            "take_picture": mock_take_picture,
            "count": mock_count,
            "sleep": mock_sleep,
            "signal": mock_signal,
        }


def test_main_initialization(mock_dependencies):
    # Retrieve mocks
    mock_db_cls = mock_dependencies["db_cls"]
    mock_sleep = mock_dependencies["sleep"]
    mock_setup = mock_dependencies["setup_logging"]
    mock_sig = mock_dependencies["signal"]

    # We need to break the infinite loop.
    mock_sleep.side_effect = KeyboardInterrupt

    try:
        main()
    except KeyboardInterrupt:
        pass

    # Assertions
    mock_setup.assert_called_once()
    mock_db_cls.assert_called_once()
    assert mock_sig.call_count >= 2  # SIGINT and SIGTERM were registered


def test_main_loop_logic(mock_dependencies):
    mocks = mock_dependencies

    # Setup mocks
    mocks["take_picture"].return_value = "img"
    mocks["count"].return_value = 10

    # Force the loop to break after one iteration
    mocks["sleep"].side_effect = KeyboardInterrupt

    try:
        main()
    except KeyboardInterrupt:
        pass

    # Verification
    mocks["take_picture"].assert_called()
    mocks["count"].assert_called_with("img")
    # Should save because initial count (-1) differs from new count (10)
    mocks["db_instance"].save_reading.assert_called_with(10)


def test_main_loop_no_change_short_interval(mock_dependencies):
    mocks = mock_dependencies
    mocks["take_picture"].return_value = "img"
    mocks["count"].return_value = 10

    # We want to simulate multiple iterations
    # 1. First iteration: count 10 (change from -1). Save.
    # 2. Second iteration: count 10 (no change). Time check fails. No save.

    # Use side_effect on sleep to count iterations and eventually break
    call_count = 0

    def sleep_side_effect(*args):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            raise KeyboardInterrupt

    mocks["sleep"].side_effect = sleep_side_effect

    try:
        main()
    except KeyboardInterrupt:
        pass

    # Verify save_reading was called exactly once (for the first iteration only)
    assert mocks["db_instance"].save_reading.call_count == 1


def test_main_db_failure(mock_dependencies):
    # Test initialization failure
    mocks = mock_dependencies
    mocks["db_cls"].side_effect = Exception("DB Init Failed")

    # Should exit with code 1
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1


def test_main_handle_exception_in_loop(mock_dependencies):
    mocks = mock_dependencies
    # First call raises error, Second call succeeds
    # Note: main() catches Exception inside the loop and continues

    # We need take_picture to be called twice.
    # First time: raises RuntimeError
    # Second time: returns "img"

    call_count = 0

    def take_pic_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("Camera Fail")
        return "img"

    mocks["take_picture"].side_effect = take_pic_side_effect
    mocks["count"].return_value = 5

    # Run loop for 2 iterations
    sleep_calls = 0

    def sleep_side_effect(*args):
        nonlocal sleep_calls
        sleep_calls += 1
        if sleep_calls >= 2:
            raise KeyboardInterrupt

    mocks["sleep"].side_effect = sleep_side_effect

    try:
        main()
    except KeyboardInterrupt:
        pass

    # Verification:
    # 1. take_picture called twice (once failed, once success)
    assert mocks["take_picture"].call_count == 2
    # 2. save_reading called ONCE (only for second iteration)
    assert mocks["db_instance"].save_reading.call_count == 1
    mocks["db_instance"].save_reading.assert_called_with(5)
