from PyPDF2 import PdfReader
import openai
import os
import numpy as np
import pandas as pd
import warnings
from langchain.text_splitter import TokenTextSplitter


def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        page = reader.pages[0]
        return page.extract_text()


def extract_text_from_directory(df, directory_path):
    data = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(directory_path, file_name)
            text = extract_text_from_pdf(file_path)
            data.append({"document_name": file_name, "text_extracted": text})
    return pd.concat([df, pd.DataFrame(data)])


def split_text_chunks(df):
    text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)
    new_data = []
    for index, row in df.iterrows():
        document_name = row["document_name"]
        text_extracted = row["text_extracted"]
        text_chunks = text_splitter.split_text(text_extracted)

        # Join text_chunks with commas
        comma_separated_chunks = ", ".join(text_chunks)

        # Assign the comma-separated chunks to the row
        row["text_chunks"] = comma_separated_chunks
        new_data.append(row)
    return pd.DataFrame(new_data)


def intermediate_processor(directory_path):
    df = pd.DataFrame({"document_name": [], "text_extracted": [], "text_chunks": []})
    df = df.pipe(extract_text_from_directory, directory_path).pipe(split_text_chunks)
    return df


def grulla_processor(df, api_key):
    openai.api_key = api_key

    def embed_text(text, model="text-embedding-ada-002"):
        try:
            text = text.replace("\n", " ")
            response = openai.Embedding.create(input=[text], model=model)
            return np.array(response["data"][0]["embedding"])
        except Exception as e:
            warnings.warn(f"Embedding failed for text: {text}. Error: {str(e)}")
            return None

    def assign_vector_id():
        vector_id = 0
        vector_ids = []
        for i in range(len(df)):
            vector_ids.append(vector_id)
            vector_id += 1
        return vector_ids

    df["text_embeddings"] = df["text_chunks"].apply(embed_text)
    df["document_name_embeddings"] = df["document_name"].apply(embed_text)
    df["vector_id"] = assign_vector_id()
    return df
