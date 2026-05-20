import base64
import requests
from PyPDF2 import PdfReader
from docx import Document
import io


def extract_from_url(url: str) -> str:
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url,timeout=30)
    response.raise_for_status()
    return response.text


def extract_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()


def extract_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join([pagraphe.text for pagraphe in doc.paragraphs])
    return text.strip()


def encode_image_to_base64(file_bytes: bytes) -> str:
    encoded_string = base64.b64encode(file_bytes).decode("utf-8")
    return encoded_string
