# romeo-gtp/romeo_gpt/utils/connectors/extract_docx.py
import io
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
import warnings


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
