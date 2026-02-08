import io
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".csv", ".xlsx"}


def parse_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def parse_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def parse_csv(content: bytes) -> str:
    df = pd.read_csv(io.BytesIO(content))
    return df.to_string(index=False)


def parse_xlsx(content: bytes) -> str:
    df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    return df.to_string(index=False)


def parse_document(filename: str, content: bytes) -> str:
    """Parse document content based on file extension.

    Returns extracted plain text.
    Raises ValueError for unsupported file types.
    """
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {ext}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    parsers = {
        ".txt": parse_txt,
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".csv": parse_csv,
        ".xlsx": parse_xlsx,
    }

    return parsers[ext](content)
