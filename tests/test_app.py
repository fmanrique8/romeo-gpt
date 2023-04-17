from owl_vectores.database import create_redis_connection


def test_redis_connection() -> bool:
    redis_host = "vector-db"  # Use the service name from the docker-compose.yml
    redis_port = 6379
    _, connected = create_redis_connection(redis_host, redis_port)
    return connected
