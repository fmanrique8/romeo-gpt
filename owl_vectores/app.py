# owl-vectores/owl_vectores/app.py
import os
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from uuid import uuid4
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
import logging
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
session_id = str(uuid4())
INDEX_NAME = f"embedding-index-{session_id}-{timestamp}"

load_dotenv(".env")
app = FastAPI()

API_KEY = os.environ["OPENAI_API_KEY"]

logging.basicConfig(filename="ask_question.log", level=logging.INFO)

# Replace `your-nextjs-app-url` with the actual URL of your deployed Next.js app
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # For local development
    "https://your-nextjs-app-url.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_conn = init()


# New root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Owl Vectores API!"}


@app.post("/upload-files/")
async def upload_files(files: List[UploadFile] = File(...)):
    file_contents = []

    for file in files:
        content = await file.read()
        file_contents.append((content, file.filename.split(".")[-1]))

    # Process and store the uploaded files in Redis
    df = intermediate_processor(file_contents)
    print(f"Intermediate Processor DataFrame: \n{df.head()}\n{df.dtypes}")
    df = primary_processor(df, API_KEY)
    print(f"Primary Processor DataFrame: \n{df.head()}\n{df.dtypes}")

    create_index(redis_conn, INDEX_NAME)  # Pass index_name here
    # Load documents
    load_documents(redis_conn, df, INDEX_NAME)

    return {"status": "success", "message": "Files uploaded and stored in Redis"}


class Question(BaseModel):
    question: str


@app.post("/ask-question/")
async def ask_question(q: Question):  # Add session_id as a parameter
    question = q.question
    if not question:
        raise HTTPException(status_code=400, detail="Please provide a question")

    # Get embeddings for the question
    query_vector = get_embedding(question, API_KEY)

    all_documents = list_docs(redis_conn, INDEX_NAME)

    # Perform semantic search
    search_results = search_redis(
        redis_conn,
        INDEX_NAME,  # Pass INDEX_NAME here
        query_vector,
        return_fields=["document_name", "text_chunks"],
        k=1,
    )

    # If no document is found, use all documents
    if len(search_results) == 0:
        search_results = all_documents

    # Get the most relevant document
    relevant_doc = search_results[0]

    # Retrieve the text chunks from the document
    text_chunks = relevant_doc["text_chunks"]

    # Create a prompt using the text_chunks and the question
    prompt = f"As an AI assistant, I have analyzed the following text chunks from the most relevant document to answer your question:\n\n{text_chunks}\n\nYour question: {question}\n\nAnswer:"

    # Use get_completion to answer the original question
    answer = get_completion(prompt=prompt, api_key=API_KEY)

    return {"question": question, "answer": answer, "session_id": session_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
