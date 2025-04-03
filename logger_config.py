import logging
from logging.handlers import RotatingFileHandler
# Configure the logger
LOG_FILE = "crawler.log"

# Setting up a logger
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(filename=LOG_FILE)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger(name="WebCrawler")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)