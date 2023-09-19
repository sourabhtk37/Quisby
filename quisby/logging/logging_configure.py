import logging
import configparser
import os
from logging.handlers import RotatingFileHandler

home_dir = os.getenv("HOME")
config_location = home_dir + "/.config/quisby/"

def configure_logging():
    # Load configuration
    config = configparser.ConfigParser()
    config.read(config_location+"config.ini")

    log_level = config['LOGGING']['level']
    log_filename = config['LOGGING']['filename']
    log_file_max_bytes = config['LOGGING']['max_bytes_log_file']
    log_backup_count = config['LOGGING']['backup_count']

    # Create a rotating file handler
    rotating_handler = RotatingFileHandler(log_filename, maxBytes=int(log_file_max_bytes) * 1024 * 1024, backupCount=int(log_backup_count))
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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
