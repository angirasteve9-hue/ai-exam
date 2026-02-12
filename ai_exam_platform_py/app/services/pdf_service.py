import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts all text from a PDF file provided as bytes.
    """
    text_content = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_content += text + "\n"
    return text_content
