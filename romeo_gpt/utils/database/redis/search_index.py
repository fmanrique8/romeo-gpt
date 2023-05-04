# romeo-gtp/romeo_gpt/database.py
import redis
import numpy as np
import typing as t

from redis.commands.search.query import Query
from .database import process_doc


def search_index(
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
