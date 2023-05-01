# romeo_gpt/utils/database/__init__.py
import os
import yaml
from dotenv import load_dotenv

with open("config.yml", "r") as vector_settings:
    CONFIG = yaml.safe_load(vector_settings)


NUM_VECTORS = CONFIG["vector_settings"]["num_vectors"]
PREFIX = CONFIG["vector_settings"]["prefix"]
VECTOR_DIM = CONFIG["vector_settings"]["vector_dim"]
DISTANCE_METRIC = CONFIG["vector_settings"]["distance_metric"]

load_dotenv()

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")
