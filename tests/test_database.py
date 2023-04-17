import os
import numpy as np
import pandas as pd
from owl_vectores.database import RedisSearchEngine

# Set your OpenAI API Key
API_KEY = "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"

# Create sample data
sample_data = {
    "vector_id": [1, 2],
    "document_name": ["Doc 1", "Doc 2"],
    "text_extracted": ["Sample text for doc 1.", "Sample text for doc 2."],
    "document_name_embeddings": [
        np.random.random(768),
        np.random.random(768),
    ],
    "text_embeddings": [
        np.random.random(768),
        np.random.random(768),
    ],
}
sample_df = pd.DataFrame(sample_data)

# Create an instance of RedisSearchEngine
search_engine = RedisSearchEngine(sample_df, API_KEY)

# Search for documents similar to a query
query = "Sample text"
search_results = search_engine.search_redis(query)
print(search_results)

# Ask a question
question = "What is the content of Doc 1?"
answers = search_engine.ask_question(question)
print(answers)
