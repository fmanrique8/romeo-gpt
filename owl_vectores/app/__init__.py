# owl-vectores/owl_vectores/app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from owl_vectores.api import router
from owl_vectores import ALLOWED_ORIGINS

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
