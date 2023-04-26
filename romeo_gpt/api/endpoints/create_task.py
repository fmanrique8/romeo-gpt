# romeo-gtp/romeo_gpt/api/endpoints/create_task.py
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from uuid import uuid4
from langdetect import detect
from romeo_gpt import (
    API_KEY,
    redis_conn,
    index_name,
    session_id,
    task_key_prefix,
)
from romeo_gpt.models import get_embedding
from romeo_gpt.database import search_redis, list_docs
from romeo_gpt.utils.agents.docs_agent import documents_agent


class Task(BaseModel):
    task: str


router = APIRouter()

documents_uploaded = False


@router.post("/")
async def create_task(t: Task):
    global documents_uploaded
    task = t.task
    if not task:
        raise HTTPException(status_code=400, detail="Please provide a task")

    log_key = f"document:{session_id}"
    uploaded_docs = redis_conn.execute_command("JSON.GET", log_key)
    if uploaded_docs:
        uploaded_docs_data = json.loads(uploaded_docs)
        documents_uploaded = uploaded_docs_data.get("document_uploaded", False)

    if not documents_uploaded:
        raise HTTPException(
            status_code=400, detail="Please upload a document before asking a task"
        )

    language = detect(task)

    query_vector = get_embedding(task, API_KEY)

    all_documents = list_docs(redis_conn, index_name)

    search_results = search_redis(
        redis_conn,
        index_name,
        query_vector,
        return_fields=["document_name", "text_chunks"],
    )

    if len(search_results) == 0:
        search_results = all_documents

    relevant_doc = search_results[0]

    text_chunks = relevant_doc["text_chunks"]

    answer = documents_agent(language, text_chunks, task, API_KEY)

    task_key = f"{task_key_prefix}:{uuid4()}"

    log_data = {
        "session_id": session_id,
        "task_asked": task,
        "task_embedded": query_vector.tolist(),
        "answer": answer,
    }
    redis_conn.execute_command("JSON.SET", task_key, ".", json.dumps(log_data))

    return {"task": task, "answer": answer}
