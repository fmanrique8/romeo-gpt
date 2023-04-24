# owl-vectores/owl_vectores/api/endpoints/upload_files.py
import json
from fastapi import File, UploadFile, APIRouter
from typing import List

from owl_vectores.preprocess import intermediate_processor, primary_processor
from owl_vectores import API_KEY, redis_conn, index_name, session_id
from owl_vectores.database import (
    load_documents,
    create_index,
)

router = APIRouter()

documents_uploaded = False


@router.post("/")
async def upload_files_endpoint(files: List[UploadFile] = File(...)):
    global documents_uploaded
    file_contents = []

    for file in files:
        content = await file.read()
        file_contents.append((content, file.filename.split(".")[-1]))

    df = intermediate_processor(file_contents)
    df = primary_processor(df, API_KEY)

    create_index(redis_conn, index_name)
    load_documents(redis_conn, df)
    documents_uploaded = True

    log_key = f"document:{session_id}"
    log_data = {
        "session_id": session_id,
        "document_uploaded": documents_uploaded,
        "text_chunks": df["text_chunks"].tolist(),
        "text_embedded": [emb.tolist() for emb in df.get("text_embeddings", [])],
    }
    redis_conn.execute_command("JSON.SET", log_key, ".", json.dumps(log_data))

    return {"status": "success", "message": "Files uploaded and stored in Redis"}
