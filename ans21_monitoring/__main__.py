import time
import logging
import signal
import sys
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional
from astral import Observer
from astral.sun import sun
from ans21_monitoring import __version__
from ans21_monitoring.camera import take_picture
from ans21_monitoring.image_analysis import count_bright_spots
from ans21_monitoring.logger import setup_logging
from ans21_monitoring.database import DatabaseManager
from ans21_monitoring.web import create_app

# Configuration
CHECK_INTERVAL_SECONDS = 60

LATITUDE = 47.5972
LONGITUDE = 11.1874


def _calculate_sleep_time(elapsed: float, now_utc: Optional[datetime] = None) -> float:
    interval_sleep = max(0.0, CHECK_INTERVAL_SECONDS - elapsed)
    now_utc = now_utc or datetime.now(timezone.utc)

    observer = Observer(latitude=LATITUDE, longitude=LONGITUDE)
    today_sun = sun(observer, date=now_utc.date(), tzinfo=timezone.utc)
    sunrise = today_sun["sunrise"]
    sunset = today_sun["sunset"]

    # Keep daytime behavior unchanged.
    if sunrise <= now_utc <= sunset:
        return interval_sleep

    if now_utc < sunrise:
        next_sunrise = sunrise
    else:
        tomorrow = now_utc.date() + timedelta(days=1)
        next_sunrise = sun(observer, date=tomorrow, tzinfo=timezone.utc)["sunrise"]

    sleep_time = (next_sunrise - now_utc).total_seconds()
    logger = logging.getLogger(__name__)
    logger.debug(
        f"Nighttime detected. Now: {now_utc}, next sunrise at: {next_sunrise}, sleeping for {sleep_time:.2f} seconds."
    )

    return max(0.0, sleep_time)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting ANS21 Monitoring Service v{__version__}")

    try:
        db_manager = DatabaseManager()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}. Exiting.")
        sys.exit(1)

    # Initialize state from DB so restarts don't duplicate the last value
    last_stored_count = db_manager.get_last_count()

    monitor_running = True

    # Graceful shutdown handler
    def signal_handler(sig, frame):
        nonlocal monitor_running
        logger.info("Monitoring stopped by user (signal).")
        monitor_running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start web server in a background thread
    flask_app = create_app(db_manager)
    web_thread = threading.Thread(
        target=flask_app.run,
        kwargs={"host": "0.0.0.0", "port": 5000},
        daemon=True,
    )
    web_thread.start()
    logger.info("Web interface started on http://0.0.0.0:5000")

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

            if current_count != last_stored_count:
                logger.info(
                    f"Count changed from {last_stored_count} to {current_count}"
                )
                db_manager.save_reading(current_count)
                last_stored_count = current_count

        except Exception as e:
            logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)

        # Sleep for the remainder of the interval
        if monitor_running:
            elapsed = time.time() - start_time
            try:
                sleep_time = _calculate_sleep_time(elapsed)
            except Exception as e:
                logger.warning(
                    f"Failed to calculate sunrise/sunset sleep time: {e}. Falling back to fixed interval."
                )
                sleep_time = max(0, CHECK_INTERVAL_SECONDS - elapsed)
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
