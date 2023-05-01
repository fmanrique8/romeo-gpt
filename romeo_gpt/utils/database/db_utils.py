# romeo-gtp/romeo_gpt/database.py
import redis
import pandas as pd

from redis.commands.search.query import Query

from . import (
    NUM_VECTORS,
    PREFIX,
)


def process_doc(doc) -> dict:
    d = doc.__dict__
    if "vector_score" in d:
        d["vector_score"] = 1 - float(d["vector_score"])

    if isinstance(d["document_name"], bytes):
        d["document_name"] = d["document_name"].decode("utf-8", errors="ignore")
    if isinstance(d["text_chunks"], bytes):
        d["text_chunks"] = d["text_chunks"].decode("utf-8", errors="ignore")

    return d


def index_documents(redis_conn: redis.Redis, df: pd.DataFrame):
    pipe = redis_conn.pipeline()
    for index, row in df.iterrows():
        key = f"{PREFIX}:{row['vector_id']}"
        document_data = {
            "document_name": row["document_name"],
            "text_chunks": row["text_chunks"],
            "text_embeddings": row["text_embeddings"].tobytes(),
        }
        pipe.hset(key, mapping=document_data)
        print(f"Indexing document: {key}, document_data: {document_data}")
    pipe.execute()


def load_documents(redis_conn: redis.Redis, df: pd.DataFrame):
    print(f"Indexing {len(df)} Documents")
    index_documents(redis_conn, df)
    print("Redis Vector Index Created!")


def list_docs(
    redis_conn: redis.Redis,
    index_name: str,
    k: int = NUM_VECTORS,
) -> list[dict]:
    base_query = f"*"
    return_fields = ["document_name", "text_chunks"]
    query = Query(base_query).paging(0, k).return_fields(*return_fields).dialect(2)
    results = redis_conn.ft(index_name).search(query)
    return [process_doc(doc) for doc in results.docs]


def delete_index(redis_conn: redis.Redis, index_name: str):
    try:
        redis_conn.execute_command("FT.DROPINDEX", index_name)
        print(f"Index {index_name} has been deleted.")
    except redis.exceptions.ResponseError as e:
        if "Unknown index name" in str(e):
            print(f"Index {index_name} does not exist.")
        else:
            raise e
