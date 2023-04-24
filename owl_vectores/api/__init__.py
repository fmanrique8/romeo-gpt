# owl-vectores/owl_vectores/api/__init__.py
from fastapi import APIRouter

from .endpoints.upload_files import router as upload_files_router
from .endpoints.ask_question import router as ask_question_router

router = APIRouter()

router.include_router(
    upload_files_router, prefix="/upload-files", tags=["upload-files"]
)
router.include_router(
    ask_question_router, prefix="/ask-question", tags=["ask-question"]
)
