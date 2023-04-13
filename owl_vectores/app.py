from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import Dict
import redis
import os
import shutil
from owl_vectores.utils import intermediate_processor, grulla_processor

app = FastAPI()


class VectorData(BaseModel):
    key: str
    value: str


class PreprocessData(BaseModel):
    files: Dict[str, bytes]


redis_client = redis.Redis(host="vector-db", port=6379, decode_responses=True)


@app.get("/")
def read_root():
    return {"Hello": "Owl Vectores DB Service"}


@app.post("/vector/")
def create_vector_data(vector_data: VectorData):
    redis_client.set(vector_data.key, vector_data.value)
    return {"result": "Vector data created"}


@app.get("/vector/{key}")
def read_vector_data(key: str):
    value = redis_client.get(key)
    if value:
        return {"key": key, "value": value}
    else:
        return {"error": "Key not found"}


@app.put("/vector/{key}")
def update_vector_data(key: str, vector_data: VectorData):
    if redis_client.get(key):
        redis_client.set(key, vector_data.value)
        return {"result": "Vector data updated"}
    else:
        return {"error": "Key not found"}


@app.delete("/vector/{key}")
def delete_vector_data(key: str):
    if redis_client.get(key):
        redis_client.delete(key)
        return {"result": "Vector data deleted"}
    else:
        return {"error": "Key not found"}


@app.post("/preprocess/")
async def preprocess_pdf_files(preprocess_data: PreprocessData):
    temp_dir = "temp_pdf_files"
    os.makedirs(temp_dir, exist_ok=True)

    for file_name, file_content in preprocess_data.files.items():
        with open(os.path.join(temp_dir, file_name), "wb") as f:
            f.write(file_content)

    df = intermediate_processor(temp_dir)
    api_key = "your_openai_api_key"
    result_df = grulla_processor(df, api_key)

    shutil.rmtree(temp_dir)
    return result_df.to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
