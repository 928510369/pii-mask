import io
import pandas as pd
from PyPDF2 import PdfReader
from docx2python import docx2python


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
    """解析DOCX文件内容并去除重复段落"""
    # 直接使用docx2python处理bytes内容
    from docx2python import docx2python
    import io
    
    # 创建BytesIO对象供docx2python使用
    file_stream = io.BytesIO(content)
    
    with docx2python(file_stream) as docx_content:
        full_text = docx_content.text

        # 按段落去重
        paragraphs = full_text.split('\n')

        # 使用字典保持顺序的去重
        seen = {}
        unique_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if para and para not in seen:
                seen[para] = True
                unique_paragraphs.append(para)

        cleaned_text = '\n'.join(unique_paragraphs)
        return cleaned_text


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
