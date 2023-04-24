# owl-vectores/owl_vectores/api/endpoints/ask_question.py
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from uuid import uuid4
from langdetect import detect
from owl_vectores import (
    API_KEY,
    redis_conn,
    index_name,
    session_id,
    question_key_prefix,
)
from owl_vectores.models import get_embedding, get_completion
from owl_vectores.database import search_redis, list_docs
from owl_vectores.utils.agents.prompt_template import get_prompt


class Question(BaseModel):
    question: str


router = APIRouter()

documents_uploaded = False


@router.post("/")
async def ask_question_endpoint(q: Question):
    global documents_uploaded
    question = q.question
    if not question:
        raise HTTPException(status_code=400, detail="Please provide a question")

    log_key = f"document:{session_id}"
    uploaded_docs = redis_conn.execute_command("JSON.GET", log_key)
    if uploaded_docs:
        uploaded_docs_data = json.loads(uploaded_docs)
        documents_uploaded = uploaded_docs_data.get("document_uploaded", False)

    if not documents_uploaded:
        raise HTTPException(
            status_code=400, detail="Please upload a document before asking a question"
        )

    language = detect(question)

    query_vector = get_embedding(question, API_KEY)

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

    prompt = get_prompt(language, text_chunks, question)

    answer = get_completion(prompt=prompt, api_key=API_KEY)

    question_key = f"{question_key_prefix}:{uuid4()}"

    log_data = {
        "session_id": session_id,
        "question_asked": question,
        "question_embedded": query_vector.tolist(),
        "answer": answer,
    }
    redis_conn.execute_command("JSON.SET", question_key, ".", json.dumps(log_data))

    return {"question": question, "answer": answer}
