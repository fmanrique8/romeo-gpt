# romeo_gpt/api/endpoints/upload_files.py
import logging
from fastapi import File, UploadFile, APIRouter
from typing import List
from datetime import datetime

from romeo_gpt import API_KEY, redis_conn
from romeo_gpt.utils.database.redis.database import load_documents, delete_index
from romeo_gpt.utils.database.mongodb import db
from romeo_gpt.utils.database.redis.create_index import create_index
from romeo_gpt.utils.preprocess.preprocess import (
    intermediate_processor,
    primary_processor,
)

router = APIRouter()

# Access the MongoDB collection for log_data
log_data_collection = db["upload-files-endpoint"]


def index_exists(index_name):
    indices = redis_conn.execute_command("FT._LIST")
    return index_name in indices


@router.post("/")
async def upload_files_endpoint(client_ip: str, files: List[UploadFile] = File(...)):
    """
    Endpoint to upload files.

    :param client_ip:
    :param files: List of files to be uploaded.
    :return: Dictionary containing status and message.
    """

    # Set the index_name using the client's IP address
    index_name = f"romeo-db-index-{client_ip}"
    prefix = f"document"

    # Read the contents of the files and store them in a list
    file_contents = []

    for file in files:
        content = await file.read()
        file_contents.append((content, file.filename.split(".")[-1]))

    # Process the file contents using intermediate and primary processors
    df = intermediate_processor(file_contents)
    df = primary_processor(df, API_KEY)
    if index_exists(redis_conn):
        delete_result = delete_index(redis_conn, index_name)
        if delete_result["status"] == "warning":
            logging.warning(delete_result["message"])

    # Create index in Redis and load documents into the index
    create_index(redis_conn, index_name, prefix)
    load_documents(redis_conn, df, prefix)

    # Prepare log_data
    log_data = {
        "document_uploaded": len(df),
        "text_chunks": df["text_chunks"].tolist(),
        "text_embedded": [emb.tolist() for emb in df.get("text_embeddings", [])],
        "timestamp": datetime.utcnow(),
        "index_name": index_name,
        "client_ip": client_ip,
    }

    # Insert log_data into the MongoDB log_data collection
    log_data_collection.insert_one(log_data)

    return {
        "status": "success",
        "message": "Files uploaded and stored in Redis",
        "index_name": index_name,
    }
