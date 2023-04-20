# owl-vectores/owl_vectores/app.py
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langdetect import detect

from owl_vectores.database import (
    init,
    load_documents,
    search_redis,
    create_index,
)
from owl_vectores.utils import intermediate_processor, primary_processor
from owl_vectores.models import get_embedding, get_completion
import logging

load_dotenv(".env")
documents_uploaded = False
app = FastAPI()

API_KEY = os.environ["OPENAI_API_KEY"]

logging.basicConfig(filename="ask_question.log", level=logging.INFO)

ALLOWED_ORIGINS = ["http://localhost:3000"]  # Replace with your front end link

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

    create_index(redis_conn)
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

    search_results = search_redis(
        redis_conn,
        query_vector,
        return_fields=["document_name", "text_chunks"],
        question=question,
    )

    if len(search_results) == 0:
        raise HTTPException(status_code=404, detail="No relevant documents found")

    relevant_doc = search_results[0]

    text_chunks = relevant_doc["text_chunks"]

    prompt = f"As an AI assistant, I have analyzed the following text chunks from the most relevant document to answer your question in {language}:\n\n{text_chunks}\n\nYour question: {question}\n\nAnswer:"

    answer = get_completion(prompt=prompt, api_key=API_KEY)

    return {"question": question, "answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
