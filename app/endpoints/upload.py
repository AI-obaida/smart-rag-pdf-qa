import os
import tempfile
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from app import db
from app.models import Document
from functools import lru_cache

from app.services.document_indexing import DocumentIndexingService
from app.services.pdf_extraction import (
    PDFExtractionError,
    extract_text_with_pages,
)

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        "intfloat/multilingual-e5-small",
        device="cpu",
    )



@upload_bp.post("")
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    uploaded = request.files["file"]

    if not uploaded.filename:
        return jsonify({"error": "No filename provided"}), 400

    filename = secure_filename(uploaded.filename)

    if not filename or Path(filename).suffix.lower() != ".pdf":
        return jsonify({"error": "Only PDF files are allowed"}), 400

    upload_dir = Path(
        current_app.config.get("UPLOAD_FOLDER", "uploads")
    ).resolve()

    upload_dir.mkdir(parents=True, exist_ok=True)

    filepath = None
    committed = False

    try:
        # Create a unique file without overwriting existing uploads.
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix="pdf_",
            suffix=".pdf",
            dir=upload_dir,
            delete=False,
        ) as destination:
            filepath = Path(destination.name)
            uploaded.save(destination)

        # Check PDF signature before parsing.
        with filepath.open("rb") as source:
            if not source.read(5) == b"%PDF-":
                return jsonify({
                    "error": "Invalid PDF file"
                }), 400

        pages = extract_text_with_pages(str(filepath))

        extracted_text = "\n\n".join(
            f"[Page {page_number}]\n{text}"
            for page_number, text in pages
        )

        document = Document(
            filename=filename,
            pages=len(pages),
            extracted_text=extracted_text,
        )

        db.session.add(document)
        db.session.flush()

        embedding_model = get_embedding_model()

        indexing_service = DocumentIndexingService(
            embedding_model=embedding_model,
        )

        prepared_chunks = indexing_service.prepare_chunks(pages)

        if not prepared_chunks:
            raise ValueError("PDF contains no indexable text")

        indexing_service.store_chunks(
            document_id=document.id,
            chunks=prepared_chunks,
            session=db.session,
        )

        db.session.commit()
        committed = True

        return jsonify({
            "message": "File uploaded successfully",
            "document_id": document.id,
            "filename": filename,
            "pages": len(pages),
        }), 201

    except PDFExtractionError:
        db.session.rollback()
        return jsonify({
            "error": "Unable to read PDF file"
        }), 400

    except Exception:
        db.session.rollback()
        current_app.logger.exception("PDF upload failed")
        return jsonify({
            "error": "Unable to process uploaded file"
        }), 500

    finally:
        # Keep the uploaded PDF only after a successful DB commit.
        # If the request fails, remove the temporary file.
        if filepath is not None and not committed:
            filepath.unlink(missing_ok=True)