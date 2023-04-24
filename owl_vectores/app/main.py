# owl-vectores/owl_vectores/app/main.py
import uvicorn
from owl_vectores.app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
