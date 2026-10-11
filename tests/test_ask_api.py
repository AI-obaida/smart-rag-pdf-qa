from unittest.mock import Mock, patch

import pytest

from app import create_app
from app.endpoints.ask import ask_bp


@pytest.fixture
def client():
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    return app.test_client()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"question": "", "document_id": 1},
        {"question": "   ", "document_id": 1},
        {"question": None, "document_id": 1},
        {"question": "Hello", "document_id": 0},
        {"question": "Hello", "document_id": -1},
        {"question": "Hello", "document_id": True},
        {"question": "Hello", "document_id": "1"},
        {"question": "Hello", "document_id": 1, "top_k": 0},
        {"question": "Hello", "document_id": 1, "top_k": 21},
        {"question": "Hello", "document_id": 1, "top_k": True},
    ],
)
def test_invalid_inputs(client, payload):
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_non_json_content_type(client):
    response = client.post(
        "/api/ask",
        data="not json",
        content_type="text/plain",
    )
    assert response.status_code == 415


def test_json_array_rejected(client):
    response = client.post("/api/ask", json=[1, 2, 3])
    assert response.status_code == 400


def test_document_not_found(client):
    with patch("app.endpoints.ask.db.session.get", return_value=None):
        response = client.post(
            "/api/ask",
            json={"question": "Hello", "document_id": 999},
        )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Document not found"


def test_successful_answer(client):
    document = Mock(id=1)
    result = {
        "question": "Hello",
        "document_id": 1,
        "items": [
            {
                "fact": "Django or Flask",
                "source_id": "S1",
                "page_number": 1,
            }
        ],
        "source_count": 1,
        "model": "qwen2.5:3b",
        "status": "answered",
    }

    with (
        patch("app.endpoints.ask.db.session.get", return_value=document),
        patch("app.endpoints.ask.get_embedding_model", return_value=Mock()),
        patch("app.endpoints.ask.StructuredRAGService") as service_class,
    ):
        service_class.return_value.ask.return_value = result

        response = client.post(
            "/api/ask",
            json={
                "question": "Hello",
                "document_id": 1,
                "top_k": 3,
            },
        )

        service_class.return_value.ask.assert_called_once_with(
            question="Hello",
            document_id=1,
            top_k=3,
        )

    assert response.status_code == 200
    assert response.get_json() == result


def test_internal_error_returns_safe_message(client):
    with patch(
        "app.endpoints.ask.db.session.get",
        side_effect=RuntimeError("private internal detail"),
    ):
        response = client.post(
            "/api/ask",
            json={"question": "Hello", "document_id": 1},
        )

    assert response.status_code == 500
    assert response.get_json()["error"] == "Unable to answer the question"
    assert b"private internal detail" not in response.data

