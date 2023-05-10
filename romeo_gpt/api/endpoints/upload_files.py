# romeo_gpt/api/endpoints/upload_files.py
import logging
from fastapi import File, UploadFile, APIRouter
from typing import List
from romeo_gpt import API_KEY, redis_conn
from romeo_gpt.utils.database.redis.database import load_documents, delete_index
from romeo_gpt.utils.database.redis.create_index import create_index
from romeo_gpt.utils.preprocess.preprocess import (
    intermediate_processor,
    primary_processor,
)

router = APIRouter()


def index_exists(index_name):
    indices = redis_conn.execute_command("FT._LIST")
    return index_name in indices


@router.post("/")
async def upload_files_endpoint(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload files.

    :param files: List of files to be uploaded.
    :return: Dictionary containing status and message.
    """
    # Set the index_name using the client's IP address
    index_name = f"romeo-db-index"
    prefix = f"document"

    # Read the contents of the files and store them in a list
    file_contents = []

    for file in files:
        content = await file.read()
        file_contents.append((content, file.filename.split(".")[-1]))

    # Process the file contents using intermediate and primary processors
    df = intermediate_processor(file_contents)
    df = primary_processor(df, API_KEY)

    if index_exists(index_name):
        delete_result = delete_index(redis_conn, index_name)
        if delete_result["status"] == "warning":
            logging.warning(delete_result["message"])

    # Create index in Redis and load documents into the index
    create_index(redis_conn, index_name, prefix)
    load_documents(redis_conn, df, prefix)

    return {
        "status": "success",
        "message": "Files uploaded and stored in Redis",
        "index_name": index_name,
    }
