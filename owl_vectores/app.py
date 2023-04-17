# owl-vectores/owl_vectores/app.py
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
from owl_vectores.database import init, load_documents, search_redis, list_docs
from owl_vectores.utils import intermediate_processor, primary_processor
from owl_vectores.models import get_embedding, get_completion
import logging

load_dotenv(".env")
app = FastAPI()

API_KEY = os.environ["OPENAI_API_KEY"]

logging.basicConfig(filename="ask_question.log", level=logging.INFO)

# Set up CORS for allowing file uploads from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_conn = init()


def print_redis_schema(redis_conn, num_docs=5):
    docs = list_docs(redis_conn, k=num_docs)
    if len(docs) > 0:
        print(f"Redis DB Schema: \n{docs[0].keys()}")
    else:
        print("No documents found in Redis")


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
    load_documents(redis_conn, df)

    # Print Redis schema
    print_redis_schema(redis_conn)

    return {"status": "success", "message": "Files uploaded and stored in Redis"}


@app.post("/ask-question/")
async def ask_question(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="Please provide a question")

    # Get embeddings for the question
    query_vector = get_embedding(question, API_KEY)

    # Reset the index by fetching all documents
    all_documents = list_docs(redis_conn)

    # Perform semantic search
    search_results = search_redis(
        redis_conn, query_vector, return_fields=["document_name", "text_chunks"], k=1
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

    return {"question": question, "answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
