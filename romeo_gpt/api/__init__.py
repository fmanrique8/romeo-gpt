# romeo-gtp/romeo_gpt/api/__init__.py
from fastapi import APIRouter

from .endpoints.upload_files import router as upload_files_router
from .endpoints.create_task import router as create_task_router

router = APIRouter()

# Include the upload_files_router with prefix and tags
router.include_router(
    upload_files_router, prefix="/upload-files", tags=["upload-files"]
)

# Include the create_task_router with prefix and tags
router.include_router(create_task_router, prefix="/create-task", tags=["create-task"])
