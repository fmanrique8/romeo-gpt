# romeo-gtp/romeo_gpt/api/endpoints/create_task.py
from fastapi import APIRouter
from pydantic import BaseModel
from romeo_gpt import (
    API_KEY,
    redis_conn,
)
from romeo_gpt.utils.models.models import get_embedding
from romeo_gpt.utils.database.redis.search_index import search_index
from romeo_gpt.utils.database.redis.database import list_docs
from romeo_gpt.utils.agents.docs_agent import documents_agent


# Define Task model with a single 'task' field
class Task(BaseModel):
    task: str


# Create FastAPI router
router = APIRouter()


# Define create_task endpoint
@router.post("/")
async def create_task(t: Task):
    """
    Endpoint to create a task.

    :param t: Task object containing a task string.
    :return: Dictionary containing the task and its answer.
    """

    # Set the index_name using the client's IP address
    index_name = f"romeo-db-index"

    # Get task from input
    task = t.task

    # Get the embedding of the task
    query_vector = get_embedding(task, API_KEY)

    # List all documents in Redis
    all_documents = list_docs(redis_conn, index_name)

    # Search Redis for relevant documents
    search_results = search_index(
        redis_conn,
        index_name,
        query_vector,
        return_fields=["document_name", "text_chunks"],
    )

    # If no search results, use all documents
    if len(search_results) == 0:
        search_results = all_documents

    # Get the most relevant document
    relevant_doc = search_results[0]

    # Extract text chunks from the relevant document
    text_chunks = relevant_doc["text_chunks"]

    # Use documents_agent to generate an answer
    answer = documents_agent(text_chunks, task)

    # Return the task and its answer
    return {"task": task, "answer": answer}
