import logging
import configparser
import os
from logging.handlers import RotatingFileHandler


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[0;37m',  # White
        'DEBUG': '\033[0;36m',   # Cyan
        'WARNING': '\033[0;33m',  # Yellow
        'ERROR': '\033[0;31m',  # Red
        'CRITICAL': '\033[1;31m',  # Bright Red
        'RESET': '\033[0m',  # Reset all
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, self.COLORS['RESET'])}{log_message}{self.COLORS['RESET']}"

def configure_logging(config_location):
    # Load configuration
    config = configparser.ConfigParser()
    config.read(config_location)

    log_level = config['LOGGING']['level']
    log_filename = config['LOGGING']['filename']
    log_file_max_bytes = config['LOGGING']['max_bytes_log_file']
    log_backup_count = config['LOGGING']['backup_count']

    # Define log and date format
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Create a rotating file handler
    rotating_handler = RotatingFileHandler(log_filename, maxBytes=int(log_file_max_bytes) * 1024 * 1024, backupCount=int(log_backup_count))
    formatter = ColoredFormatter(log_format, datefmt=date_format)
    rotating_handler.setFormatter(formatter)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            rotating_handler
        ]
    )
