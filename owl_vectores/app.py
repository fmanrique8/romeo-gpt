# owl-vectores/owl_vectores/app.py
import os
import yaml
from uuid import uuid4
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
from owl_vectores.database import (
    init,
    load_documents,
    search_redis,
    list_docs,
    create_index,
)
from owl_vectores.utils import intermediate_processor, primary_processor
from owl_vectores.models import get_embedding, get_completion
from langdetect import detect
import logging

load_dotenv(".env")
documents_uploaded = False

session_id = str(uuid4())
index_name = f"index-{session_id}"

app = FastAPI()

API_KEY = os.environ["OPENAI_API_KEY"]

logging.basicConfig(filename="ask_question.log", level=logging.INFO)

with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

ALLOWED_ORIGINS = config["cors"]["allowed_origins"]  # Replace with your front end link

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis_conn = init()


@app.post("/upload-files/")
async def upload_files(files: List[UploadFile] = File(...)):
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

    return {"status": "success", "message": "Files uploaded and stored in Redis"}


class Question(BaseModel):
    question: str


@app.post("/ask-question/")
async def ask_question(q: Question):
    global documents_uploaded
    if not documents_uploaded:
        raise HTTPException(
            status_code=400, detail="Please upload a document before asking a question"
        )
    question = q.question
    if not question:
        raise HTTPException(status_code=400, detail="Please provide a question")

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

    prompt = f"As an AI assistant, I have analyzed the following text chunks from the most relevant document to answer your question in {language}:\n\n{text_chunks}\n\nYour question: {question}\n\nAnswer:"

    answer = get_completion(prompt=prompt, api_key=API_KEY)

    return {"question": question, "answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
