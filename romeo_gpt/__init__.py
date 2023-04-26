# romeo-gpt/__init__.py
import os
import yaml
import logging
import colorlog

from dotenv import load_dotenv
from uuid import uuid4
from romeo_gpt.database import init

# Load configuration from YAML file
with open("config.yml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)

# Set global configurations from YAML file
ALLOWED_ORIGINS = CONFIG["cors"]["allowed_origins"]

# Load environment variables from .env file
load_dotenv(".env")
API_KEY = os.environ["OPENAI_API_KEY"]

# Generate unique session ID
session_id = str(uuid4())

# Set index name
index_name = f"index-{session_id}"

# Initialize Redis connection
redis_conn = init()

# Question prefix
question_key_prefix = "question"

# Define the log format
log_format = (
    "%(asctime)s - " "%(name)s - " "%(levelname)s - " "%(log_color)s%(message)s"
)

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

# Log messages
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
