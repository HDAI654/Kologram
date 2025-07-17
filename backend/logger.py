import logging
from logging.handlers import RotatingFileHandler

# Create a logger
logger = logging.getLogger("logs")
logger.setLevel(logging.DEBUG) 

# Log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# handler for writing logs to a file with a maximum size
file_handler = RotatingFileHandler(
    'logs.log',
    maxBytes = 1024 * 1024 * 20, # 20 MB
    backupCount = 1, # number of backup files to keep
    encoding = 'utf-8'
)
file_handler.setFormatter(formatter)

# handler for writing logs to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)