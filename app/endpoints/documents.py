from flask import Blueprint, jsonify
from sqlalchemy import text

from app import db
from app.models import Document


documents_bp = Blueprint(
    "documents",
    __name__,
    url_prefix="/api/documents",
)


@documents_bp.get("")
def list_documents():
    documents = Document.query.order_by(Document.id).all()

    dialect = db.session.get_bind().dialect.name

    chunk_counts = {}

    if dialect == "postgresql":
        rows = db.session.execute(
            text("""
                SELECT document_id, COUNT(*) AS chunk_count
                FROM document_chunks
                GROUP BY document_id
            """)
        ).all()

        chunk_counts = {
            row.document_id: row.chunk_count
            for row in rows
        }

    results = []

    for document in documents:
        count = int(chunk_counts.get(document.id, 0))

        results.append({
            "id": document.id,
            "filename": document.filename,
            "pages": document.pages,
            "chunk_count": count,
            "ready": count > 0,
        })

    return jsonify({"documents": results}), 200
