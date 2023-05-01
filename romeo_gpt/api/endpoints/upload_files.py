from fastapi import File, UploadFile, APIRouter
from typing import List

from romeo_gpt import API_KEY, redis_conn, index_name
from romeo_gpt.utils.database.database import (
    load_documents,
    create_index,
)

from romeo_gpt.utils.preprocess.preprocess import (
    intermediate_processor,
    primary_processor,
)

router = APIRouter()


@router.post("/")
async def upload_files_endpoint(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload files.

    :param files: List of files to be uploaded.
    :return: Dictionary containing status and message.
    """

    # Read the contents of the files and store them in a list
    file_contents = []

    for file in files:
        content = await file.read()
        file_contents.append((content, file.filename.split(".")[-1]))

    # Process the file contents using intermediate and primary processors
    df = intermediate_processor(file_contents)
    df = primary_processor(df, API_KEY)

    # Create index in Redis and load documents into the index
    create_index(redis_conn, index_name)
    load_documents(redis_conn, df)

    return {"status": "success", "message": "Files uploaded and stored in Redis"}
