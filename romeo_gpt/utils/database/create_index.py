# romeo-gtp/romeo_gpt/database.py
import redis
import logging

from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import VectorField, TextField, NumericField

from . import (
    PREFIX,
    VECTOR_DIM,
    DISTANCE_METRIC,
)


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
            "INITIAL_CAP": 255,
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
