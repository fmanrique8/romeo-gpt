import yaml
from dotenv import load_dotenv
import os
from uuid import uuid4
from owl_vectores.database import init

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
