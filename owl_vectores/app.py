from fastapi import FastAPI
from pydantic import BaseModel
import redis

app = FastAPI()


class VectorData(BaseModel):
    key: str
    value: str


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
