# romeo-gpt/romeo_gpt/app/main.py
import uvicorn
from romeo_gpt.app import app

if __name__ == "__main__":
    # Run the app using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
