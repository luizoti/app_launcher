import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    log_path = os.path.join(os.getcwd(), "app_launcher.log")
    file_handler = RotatingFileHandler(
        log_path, maxBytes=1024 * 1024 * 2, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
