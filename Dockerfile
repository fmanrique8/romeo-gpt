FROM python:3.10

WORKDIR /owl_vectores

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry export -f requirements.txt --output requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

COPY owl_vectores owl_vectores

EXPOSE 8000

CMD ["uvicorn", "owl_vectores.app:app", "--host", "0.0.0.0", "--port", "8000"]
