import pytest
from backend.app.document_parser import parse_document, SUPPORTED_EXTENSIONS


class TestParseDocument:
    def test_parse_txt(self):
        content = b"Hello world, this is a test document."
        result = parse_document("test.txt", content)
        assert result == "Hello world, this is a test document."

    def test_parse_txt_utf8(self):
        content = "你好世界，这是一个测试文档。".encode("utf-8")
        result = parse_document("test.txt", content)
        assert "你好世界" in result

    def test_parse_csv(self):
        content = b"name,phone,email\nJohn,1234567890,john@test.com\n"
        result = parse_document("data.csv", content)
        assert "John" in result
        assert "1234567890" in result

    def test_parse_xlsx(self, tmp_path):
        import pandas as pd
        df = pd.DataFrame({"name": ["Alice"], "phone": ["9876543210"]})
        path = tmp_path / "test.xlsx"
        df.to_excel(path, index=False)
        with open(path, "rb") as f:
            content = f.read()
        result = parse_document("test.xlsx", content)
        assert "Alice" in result
        assert "9876543210" in result

    def test_parse_docx(self, tmp_path):
        from docx import Document
        doc = Document()
        doc.add_paragraph("This is a test paragraph with PII: John Smith")
        path = tmp_path / "test.docx"
        doc.save(path)
        with open(path, "rb") as f:
            content = f.read()
        result = parse_document("test.docx", content)
        assert "John Smith" in result

    def test_parse_pdf(self, tmp_path):
        # Create a minimal PDF for testing
        from PyPDF2 import PdfWriter
        import io
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        buf = io.BytesIO()
        writer.write(buf)
        content = buf.getvalue()
        # PDF with blank page should return empty or minimal text
        result = parse_document("test.pdf", content)
        assert isinstance(result, str)

    def test_unsupported_file_type(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_document("test.exe", b"binary data")

    def test_unsupported_file_no_extension(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_document("noext", b"data")

    def test_supported_extensions(self):
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".docx" in SUPPORTED_EXTENSIONS
        assert ".csv" in SUPPORTED_EXTENSIONS
        assert ".xlsx" in SUPPORTED_EXTENSIONS
