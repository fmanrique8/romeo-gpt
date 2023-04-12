# Owl Vectores DB Service

Owl Vectores DB Service is a microservice providing a simple key-value store using FastAPI, Poetry, Redis, and Docker Compose. It allows users to create, read, update, and delete values in the Vector DB.

## Prerequisites

- Docker installed on your system
- Python 3.10 or later installed on your system
- Basic understanding of FastAPI, Docker Compose, and Redis

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/fmanrique8/owl-vectores.git
   cd owl-vectores
2. Build and run the application using Docker Compose:
   ```
   docker-compose up --build
   ```
   This will start the Vector DB Service on port 8000 and the Redis service on port 6379. 
3. Access the API documentation at http://localhost:8000/docs

## Available Endpoints
- GET /: Root endpoint, returns a welcome message.
- POST /vector/: Create a new key-value pair.
- GET /vector/{key}: Retrieve the value associated with the given key.
- PUT /vector/{key}: Update the value associated with the given key.
- DELETE /vector/{key}: Delete the key-value pair associated with the given key.

## Running tests

Tests can be added in the tests directory. To run tests, you can use a test runner like pytest. Make sure to install the required dev dependencies with Poetry:
```
poetry install
```
Then, run the tests using pytest:
```
poetry run pytest
```

## License
MIT
```
https://github.com/fmanrique8/owl-vectores-db.git
```