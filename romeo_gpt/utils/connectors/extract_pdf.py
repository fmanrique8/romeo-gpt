# romeo-gtp/romeo_gpt/utils/connectors/extract_pdf.py
import io
import warnings
from PyPDF2 import PdfReader
from romeo_gpt import logger


def extract_text_from_pdf(file_content):
    try:
        with io.BytesIO(file_content) as f:
            reader = PdfReader(f)
            page = reader.pages[0]
            text = page.extract_text().encode("utf-8")
        logger.info("Successfully extracted text from PDF file")
        return text
    except Exception as e:
        logger.warning(f"Failed to read the PDF file. Reason: {str(e)}")
        warnings.warn(f"Failed to read the PDF file. Reason: {str(e)}")
        return b""
