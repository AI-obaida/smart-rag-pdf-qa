from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

import pytest
from sqlalchemy.exc import OperationalError

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


def post_question(client):
    return client.post(
        "/api/ask",
        json={
            "question": "What are the requirements?",
            "document_id": 1,
        },
    )


def test_database_failure(client):
    error = OperationalError(
        "SELECT * FROM documents",
        {},
        Exception("database unavailable"),
    )

    with patch(
        "app.endpoints.ask.db.session.get",
        side_effect=error,
    ):
        response = post_question(client)

    assert response.status_code == 503
    assert response.get_json()["error"] == "Database operation failed"


@pytest.mark.parametrize(
    "error",
    [
        URLError("connection refused"),
        HTTPError(
            url="http://127.0.0.1:11434/api/chat",
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=None,
        ),
        TimeoutError("request timed out"),
        ConnectionError("connection failed"),
    ],
)
def test_ollama_unavailable(client, error):
    with (
        patch(
            "app.endpoints.ask.db.session.get",
            return_value=Mock(id=1),
        ),
        patch(
            "app.endpoints.ask.get_embedding_model",
            return_value=Mock(),
        ),
        patch(
            "app.endpoints.ask.StructuredRAGService",
        ) as service_class,
    ):
        service_class.return_value.ask.side_effect = error
        response = post_question(client)

    assert response.status_code == 503
    assert response.get_json()["error"] == "AI model service unavailable"

