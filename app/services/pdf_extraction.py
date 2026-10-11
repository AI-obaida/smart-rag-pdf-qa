import fitz


class PDFExtractionError(Exception):
    pass


def extract_text_with_pages(pdf_path):
    """
    Extract PDF text while preserving 1-based page numbers.

    Returns a list of (page_number, text) tuples.
    """
    try:
        with fitz.open(pdf_path) as document:
            if not document.is_pdf:
                raise PDFExtractionError("File is not a PDF")

            pages = []

            for index, page in enumerate(document, start=1):
                pages.append((index, page.get_text("text")))

            return pages

    except PDFExtractionError:
        raise
    except Exception as exc:
        raise PDFExtractionError(
            "Unable to extract text from PDF"
        ) from exc