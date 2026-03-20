import time
import logging
import signal
import sys
from ans21_monitoring import __version__
from ans21_monitoring.camera import take_picture
from ans21_monitoring.image_analysis import count_bright_spots
from ans21_monitoring.logger import setup_logging
from ans21_monitoring.database import DatabaseManager

# Configuration
CHECK_INTERVAL_SECONDS = 60
FORCE_LOG_INTERVAL_SECONDS = 300  # 5 minutes


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting ANS21 Monitoring Service v{__version__}")

    try:
        db_manager = DatabaseManager()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}. Exiting.")
        sys.exit(1)

    # Initialize state
    last_stored_count = -1
    last_stored_time = 0.0

    monitor_running = True

    # Graceful shutdown handler
    def signal_handler(sig, frame):
        nonlocal monitor_running
        logger.info("Monitoring stopped by user (signal).")
        monitor_running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Monitoring loop started. Press Ctrl+C to stop.")

    while monitor_running:
        start_time = time.time()
        try:
            # Capture and analyze
            try:
                image = take_picture()
                current_count = count_bright_spots(image)
                logger.debug(f"Bright spots detected: {current_count}")
            except Exception as e:
                logger.error(f"Error during image capture or analysis: {e}")
                # Wait entire interval on error to avoid rapid looping
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            current_time = time.time()
            should_save = False

            # Check if count changed
            if current_count != last_stored_count:
                logger.info(
                    f"Count changed from {last_stored_count} to {current_count}"
                )
                should_save = True

            # Check 5-minute interval
            elif (current_time - last_stored_time) >= FORCE_LOG_INTERVAL_SECONDS:
                logger.info(
                    f"Periodic logging (every {FORCE_LOG_INTERVAL_SECONDS}s). Count: {current_count}"
                )
                should_save = True

            if should_save:
                db_manager.save_reading(current_count)
                last_stored_count = current_count
                last_stored_time = current_time

        except Exception as e:
            logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)

        # Sleep for the remainder of the interval
        if monitor_running:
            elapsed = time.time() - start_time
            sleep_time = max(0, CHECK_INTERVAL_SECONDS - elapsed)
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
