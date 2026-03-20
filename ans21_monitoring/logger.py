import logging
import logging.handlers
import sys


def setup_logging(log_file="ans21_monitoring.log"):
    """
    Sets up a rotating file logger and a console logger.
    """
    # Create the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Format for logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Rotating File Handler (1MB max, 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Keep console cleaner
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup complete.")
