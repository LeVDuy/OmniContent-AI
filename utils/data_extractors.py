import base64
import requests
from PyPDF2 import PdfReader
from docx import Document
import io


def extract_from_url(url: str) -> str:
    try:
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url,timeout=30)
        response.raise_for_status()
        if response.status_code == 200:
            return response.text
        return f"Failed to extract content from URL: {str(response.status_code)}"
    except Exception as e:
        return f"Failed to extract content from URL: {str(e)}"


def extract_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        return f"Failed to extract content from PDF: {str(e)}"


def extract_from_docx(file_bytes: bytes) -> str:
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([pagraphe.text for pagraphe in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Failed to extract content from DOCX: {str(e)}"


def encode_image_to_base64(file_bytes: bytes) -> str:
    try:
        encoded_string = base64.b64encode(file_bytes).decode("utf-8")
        return encoded_string
    except Exception as e:
        return f"Failed to encode image: {str(e)}"
