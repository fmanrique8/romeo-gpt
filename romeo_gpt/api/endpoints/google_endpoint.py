# concierge_app/api/endpoints/google_endpoint.py
from fastapi import APIRouter
from pydantic import BaseModel
from romeo_gpt.utils.agents.google_agent import google_agent


# Define the task model with a single 'task' field
class Task(BaseModel):
    task: str


# Create FastAPI router
router = APIRouter()


# Define create_task endpoint
@router.post("/")
async def google_endpoint(t: Task):
    """
    Endpoint to create a task for Google search.

    :param t: Task object containing a task string.
    :return: Dictionary containing the task and its answer.
    """
    task = t.task

    answer = google_agent(task)

    # Return the task and its answer
    return {"task": task, "answer": answer}
