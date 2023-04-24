# romeo-gtp/romeo_gpt/database.py
import yaml
import redis
import pandas as pd
import numpy as np
import typing as t
import logging

from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, TextField, NumericField


with open("config.yml", "r") as vector_settings:
    CONFIG = yaml.safe_load(vector_settings)


NUM_VECTORS = CONFIG["vector_settings"]["num_vectors"]
PREFIX = CONFIG["vector_settings"]["prefix"]
VECTOR_DIM = CONFIG["vector_settings"]["vector_dim"]
DISTANCE_METRIC = CONFIG["vector_settings"]["distance_metric"]


def create_index(redis_conn: redis.Redis, index_name: str):
    document_name = TextField(name="document_name")
    text_chunks = TextField(name="text_chunks")
    vector_score = NumericField(name="vector_score")
    embedding = VectorField(
        "text_embeddings",
        "FLAT",
        {
            "TYPE": "FLOAT64",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": NUM_VECTORS,
        },
    )

    try:
        redis_conn.ft(index_name).create_index(
            fields=[
                document_name,
                text_chunks,
                embedding,
                vector_score,
            ],
            definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH),
        )
    except redis.exceptions.ResponseError as e:
        if "Index already exists" in str(e):
            logging.warning(f"Index {index_name} already exists.")
        else:
            raise e


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


def search_redis(
    redis_conn: redis.Redis,
    index_name: str,
    query_vector: t.List[float],
    return_fields=None,
    k: int = 5,
) -> t.List[dict]:
    if return_fields is None:
        return_fields = []
    base_query = f"*=>[KNN {k} @embedding $vector AS vector_score]"
    query = (
        Query(base_query)
        .sort_by("vector_score")
        .return_fields(*return_fields)
        .paging(0, k)
        .dialect(2)
    )
    params_dict = {"vector": np.array(query_vector, dtype=np.float64).tobytes()}
    results = redis_conn.ft(index_name).search(query, params_dict)
    return [process_doc(doc) for doc in results.docs]


def init():
    with open("config.yml", "r") as redis_config:
        config = yaml.safe_load(redis_config)

    redis_conn = redis.Redis(
        host=config["redis"]["host"],
        port=config["redis"]["port"],
        password=config["redis"]["password"],
        decode_responses=False,
    )
    return redis_conn
