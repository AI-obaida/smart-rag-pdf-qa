import fitz
import pytest

from app.services.pdf_extraction import (
    PDFExtractionError,
    extract_text_with_pages,
)


def test_extract_text_success(tmp_path):
    path = tmp_path / "sample.pdf"

    with fitz.open() as document:
        page1 = document.new_page()
        page1.insert_text((72, 72), "Page 1 text")

        page2 = document.new_page()
        page2.insert_text((72, 72), "Page 2 text")

        document.save(str(path))

    pages = extract_text_with_pages(str(path))

    assert len(pages) == 2
    assert pages[0][0] == 1
    assert pages[1][0] == 2
    assert "Page 1 text" in pages[0][1]
    assert "Page 2 text" in pages[1][1]


def test_extract_text_invalid_pdf(tmp_path):
    path = tmp_path / "invalid.pdf"
    path.write_bytes(b"not a valid PDF")

    with pytest.raises(PDFExtractionError):
        extract_text_with_pages(str(path))


def test_extract_text_missing_file(tmp_path):
    path = tmp_path / "missing.pdf"

    with pytest.raises(PDFExtractionError):
        extract_text_with_pages(str(path))


def test_extract_text_empty_pdf(tmp_path):
    path = tmp_path / "empty.pdf"

    with fitz.open() as document:
        document.new_page()
        document.save(str(path))

    pages = extract_text_with_pages(str(path))

    assert len(pages) == 1
    assert pages[0][0] == 1
    assert pages[0][1].strip() == ""