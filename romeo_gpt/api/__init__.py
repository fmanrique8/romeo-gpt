# romeo-gtp/romeo_gpt/api/__init__.py
from fastapi import APIRouter
from .endpoints.upload_files import router as upload_files_router
from .endpoints.create_task import router as create_task_router
from .endpoints.google_endpoint import router as google_endpoint_router

router = APIRouter()

router.include_router(
    upload_files_router,
    prefix="/upload-files",
    tags=["upload-files"],
)

router.include_router(
    create_task_router,
    prefix="/create-task",
    tags=["create-task"],
)


router.include_router(
    google_endpoint_router,
    prefix="/google-endpoint",
    tags=["google-endpoint"],
)
