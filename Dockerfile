# romeo-gpt/Dockerfile
FROM python:3.10

WORKDIR /romeo_gpt

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry export -f requirements.txt --output requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY romeo_gpt romeo_gpt
COPY config.yml config.yml
COPY .env .env

EXPOSE 8000

CMD ["uvicorn", "romeo_gpt.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
