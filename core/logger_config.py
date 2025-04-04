import logging
from logging.handlers import RotatingFileHandler
# Configure the logger
LOG_FILE = "./logs/crawler.log"

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Setting up a Rotating file logger (for now it will be a single file with no rotations)
file_log_handler = RotatingFileHandler(filename=LOG_FILE)
file_log_handler.setFormatter(log_formatter)

# Setting up a console logger
console_log_handler = logging.StreamHandler()
console_log_handler.setFormatter(log_formatter)

logger = logging.getLogger(name="WebCrawler")
logger.setLevel(logging.INFO)
logger.addHandler(console_log_handler)
logger.addHandler(file_log_handler)