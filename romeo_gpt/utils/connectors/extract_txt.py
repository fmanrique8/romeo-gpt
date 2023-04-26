# romeo-gtp/romeo_gpt/utils/connectors/extract_txt.py
import io
import warnings
from chardet.universaldetector import UniversalDetector
from romeo_gpt import logger


def extract_text_from_txt(file_content):
    try:
        encoding = detect_encoding(file_content)
        with io.BytesIO(file_content) as f:
            text = f.read().decode(encoding)
        logger.info("Successfully extracted text from TXT file")
        return text
    except Exception as e:
        logger.warning(f"Failed to read the TXT file. Error: {str(e)}")
        warnings.warn(f"Failed to read the TXT file. Error: {str(e)}")
        return ""


def detect_encoding(file_content):
    detector = UniversalDetector()
    for line in io.BytesIO(file_content):
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    encoding = detector.result["encoding"]
    logger.info(f"Detected encoding: {encoding}")
    return encoding
