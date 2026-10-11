from pathlib import Path
import io
from unittest.mock import patch

import fitz


def make_pdf():
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "Indexing integration test")
        return document.tobytes()


def test_upload_invokes_indexing(client):
    with patch(
        "app.endpoints.upload.get_embedding_model"
    ) as model_factory, patch(
        "app.endpoints.upload.DocumentIndexingService"
    ) as indexing_class:

        service = indexing_class.return_value

        service.prepare_chunks.return_value = [
            {
                "page_number": 1,
                "chunk_index": 1,
                "chunk_text": "Indexing integration test",
                "embedding": [0.1] * 384,
            }
        ]

        response = client.post(
            "/api/upload",
            data={
                "file": (
                    io.BytesIO(make_pdf()),
                    "integration.pdf",
                )
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 201

        data = response.get_json()

        model_factory.assert_called_once()
        indexing_class.assert_called_once()

        service.prepare_chunks.assert_called_once()

        prepared_pages = service.prepare_chunks.call_args.args[0]

        assert len(prepared_pages) == 1
        assert prepared_pages[0][0] == 1
        assert prepared_pages[0][1].strip() == "Indexing integration test"


        service.store_chunks.assert_called_once()

        kwargs = service.store_chunks.call_args.kwargs

        assert kwargs["document_id"] == data["document_id"]
        assert len(kwargs["chunks"]) == 1


def test_upload_rolls_back_when_indexing_fails(client, app):
    from app import db
    from app.models import Document

    with patch(
        "app.endpoints.upload.get_embedding_model"
    ), patch(
        "app.endpoints.upload.DocumentIndexingService"
    ) as indexing_class:

        service = indexing_class.return_value
        service.prepare_chunks.side_effect = RuntimeError(
            "Simulated embedding failure"
        )

        response = client.post(
            "/api/upload",
            data={
                "file": (
                    io.BytesIO(make_pdf()),
                    "failed_indexing.pdf",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 500

    with app.app_context():
        assert db.session.query(Document).count() == 0

    upload_dir = Path(app.config["UPLOAD_FOLDER"])

    assert list(upload_dir.glob("*.pdf")) == []

