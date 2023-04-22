# owl-vectores/owl_vectores/utils/connectors/extract_txt.py
import io
from chardet.universaldetector import UniversalDetector
import warnings


def extract_text_from_txt(file_content):
    try:
        detect_encoding(file_content)
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
