# owl-vectores/owl_vectores/utils/connectors/extract_pdf.py
import io
from PyPDF2 import PdfReader
import warnings


def extract_text_from_pdf(file_content):
    try:
        with io.BytesIO(file_content) as f:
            reader = PdfReader(f)
            page = reader.pages[0]
            return page.extract_text().encode("utf-8")
    except Exception as e:
        warnings.warn(f"Failed to read the PDF file. Error: {str(e)}")
        return b""
