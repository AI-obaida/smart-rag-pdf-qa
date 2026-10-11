import pytest
import io

import fitz

from app import db
from app.models import Document


def make_pdf():
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "Test PDF content")
        return document.tobytes()


def test_upload_success(client, app):
    response = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(make_pdf()), "test.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 201

    data = response.get_json()
    assert data["document_id"] > 0
    assert data["pages"] == 1
    assert data["filename"].endswith(".pdf")

    with app.app_context():
        assert db.session.get(Document, data["document_id"]) is not None


def test_upload_no_file(client):
    response = client.post("/api/upload", data={})
    assert response.status_code == 400


def test_upload_empty_filename(client):
    response = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(make_pdf()), "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_upload_invalid_extension(client):
    response = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(b"hello"), "test.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_upload_invalid_pdf_content(client, app):
    response = client.post(
        "/api/upload",
        data={"file": (io.BytesIO(b"not a pdf"), "invalid.pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert list((__import__("pathlib").Path(
        app.config["UPLOAD_FOLDER"]
    )).glob("*.pdf")) == []


def test_upload_oversized_file(client):
    response = client.post(
        "/api/upload",
        data={
            "file": (
                io.BytesIO(b"%PDF-" + b"x" * (3 * 1024 * 1024)),
                "large.pdf",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 413


def test_upload_unique_filenames(client):
    filenames = []
    document_ids = []

    for _ in range(2):
        response = client.post(
            "/api/upload",
            data={"file": (io.BytesIO(make_pdf()), "same.pdf")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        payload = response.get_json()
        filenames.append(payload["filename"])
        document_ids.append(payload["document_id"])

    assert filenames == ["same.pdf", "same.pdf"]
    assert document_ids[0] != document_ids[1]

@pytest.fixture(autouse=True)
def mock_upload_indexing(monkeypatch):
    from unittest.mock import Mock

    import app.endpoints.upload as upload_module

    model = Mock()
    indexing_service = Mock()

    indexing_service.prepare_chunks.return_value = [
        {
            "page_number": 1,
            "chunk_index": 1,
            "chunk_text": "Mock indexed PDF content",
            "embedding": [0.1] * 384,
        }
    ]

    monkeypatch.setattr(
        upload_module,
        "get_embedding_model",
        lambda: model,
    )

    monkeypatch.setattr(
        upload_module,
        "DocumentIndexingService",
        lambda embedding_model: indexing_service,
    )

