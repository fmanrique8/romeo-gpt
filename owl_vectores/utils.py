# owl-vectores/owl_vectores/utils.py
import io
import openai
import pandas as pd
import warnings
from PyPDF2 import PdfReader
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from chardet.universaldetector import UniversalDetector
from owl_vectores.models import get_embedding
from langchain.text_splitter import TokenTextSplitter


def extract_text_from_pdf(file_content):
    try:
        with io.BytesIO(file_content) as f:
            reader = PdfReader(f)
            page = reader.pages[0]
            return page.extract_text().encode("utf-8")
    except Exception as e:
        warnings.warn(f"Failed to read the PDF file. Error: {str(e)}")
        return b""


def extract_text_from_docx(file_content):
    try:
        with io.BytesIO(file_content) as f:
            document = Document(f)
            text = ""
            for para in document.paragraphs:
                text += para.text
        return text.encode("utf-8")
    except PackageNotFoundError:
        warnings.warn("Failed to read the DOCX file.")
        return b""


def extract_text_from_txt(file_content):
    try:
        encoding = detect_encoding(file_content)
        with io.BytesIO(file_content) as f:
            text = f.read()
        return text
    except Exception as e:
        warnings.warn(f"Failed to read the TXT file. Error: {str(e)}")
        return b""


def detect_encoding(file_content):
    detector = UniversalDetector()
    detector.feed(file_content)
    detector.close()
    return detector.result["encoding"]


def extract_text_from_files(df, file_contents):
    for file_content, file_extension in file_contents:
        if file_extension == "pdf":
            text = extract_text_from_pdf(file_content)
        elif file_extension == "docx":
            text = extract_text_from_docx(file_content)
        elif file_extension == "txt":
            text = extract_text_from_txt(file_content)
        else:
            text = b""
            warnings.warn(f"Unsupported file format: {file_extension}")
        new_row = pd.DataFrame(
            {"document_name": [file_content], "text_extracted": [text]}
        )
        df = pd.concat([df, new_row], ignore_index=True)
    return df


def encode_text(text):
    if text is None or len(text) == 0:
        return None
    return text.replace(b"\n", b" ")


def split_text_chunks(df):
    text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)
    df["text_chunks"] = ""  # Initialize the text_chunks column with empty strings

    for index, row in df.iterrows():
        document_name = row["document_name"]
        text_extracted = row["text_extracted"]
        print(
            f"Document: {document_name}, Text Extracted: {text_extracted}"
        )  # Add print statement here
        if isinstance(text_extracted, bytes):
            text_extracted = text_extracted.decode("utf-8")
        text_chunks = text_splitter.split_text(text_extracted)

        # Join text_chunks with commas
        comma_separated_chunks = ", ".join(text_chunks)

        # Assign the comma-separated chunks to the row
        df.at[index, "text_chunks"] = comma_separated_chunks

    return df


def intermediate_processor(file_contents: list):
    df = pd.DataFrame({"document_name": [], "text_extracted": [], "text_chunks": []})
    df = df.pipe(extract_text_from_files, file_contents).pipe(split_text_chunks)
    return df


def primary_processor(df, api_key):
    openai.api_key = api_key

    def embed_text(text, model="text-embedding-ada-002"):
        # Replace the existing embed_text function with a call to get_embedding
        return get_embedding(text, api_key, model=model)

    def assign_vector_id():
        return list(range(len(df)))

    df["text_embeddings"] = df["text_chunks"].apply(embed_text)
    df["document_name_embeddings"] = df["document_name"].apply(embed_text)
    df["vector_id"] = assign_vector_id()
    return df
