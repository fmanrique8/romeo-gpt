# romeo-gtp/romeo_gpt/app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from romeo_gpt.api import router
from romeo_gpt import ALLOWED_ORIGINS

app = FastAPI()

# Add CORS middleware to app
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
