# romeo-gpt/__init__.py
import os
import yaml
import logging
import colorlog
from dotenv import load_dotenv
from romeo_gpt.utils.database.database import init

# Load environment variables from .env file
load_dotenv(".env")
API_KEY = os.environ["OPENAI_API_KEY"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]

# Set index name
index_name = f"romeo-db-index"

# Initialize Redis connection
redis_conn = init()

# Define the log format
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(log_color)s%(message)s"

# Define the colors for different log levels
colorlog_format = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}


def setup_logger(level=logging.INFO):
    # Create a color formatter
    formatter = colorlog.ColoredFormatter(
        log_format, datefmt="%Y-%m-%d %H:%M:%S", log_colors=colorlog_format
    )

    # Create a console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Set up the root logger and add the console handler
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
