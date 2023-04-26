# romeo-gtp/romeo_gpt/utils/connectors/extract_docx.py
import io
import warnings
import docx2txt
from romeo_gpt import logger


def extract_text_from_docx(file_content):
    try:
        with io.BytesIO(file_content) as f:
            text = docx2txt.process(f)
        logger.info("Successfully extracted text from DOCX or DOC file")
        return text.encode("utf-8")
    except Exception as e:
        logger.warning(f"Failed to read the DOCX or DOC file. Reason: {str(e)}")
        warnings.warn(f"Failed to read the DOCX or DOC file. Reason: {str(e)}")
        return b""
