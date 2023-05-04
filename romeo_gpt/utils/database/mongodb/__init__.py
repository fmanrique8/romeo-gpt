# romeo_gpt/utils/database/__init__.py
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()


# Database Connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri, server_api=ServerApi("1"))
db = client["romeo-mongo-db"]

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
