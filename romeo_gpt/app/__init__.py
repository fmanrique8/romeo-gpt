# romeo-gtp/romeo_gpt/app/__init__.py
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from romeo_gpt.api import router

# Load configuration from YAML file
with open("config.yml", "r") as config_file:
    CONFIG = yaml.safe_load(config_file)

app = FastAPI()

# Add CORS middleware to app
app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFIG["cors"]["allowed_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router from the api module
app.include_router(router)
