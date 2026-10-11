from app import create_app, db
from app.models import Document
from sqlalchemy import text


def make_client():
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()

        db.session.add_all([
            Document(filename="ready.pdf", pages=3),
            Document(filename="pending.pdf", pages=2),
        ])

        db.session.commit()

    return app.test_client()


def test_documents_endpoint_exists():
    client = make_client()

    response = client.get("/api/documents")

    assert response.status_code == 200


def test_documents_endpoint_returns_json():
    client = make_client()

    response = client.get("/api/documents")

    assert response.is_json

    data = response.get_json()

    assert isinstance(data, dict)
    assert isinstance(data.get("documents"), list)


def test_documents_include_required_fields():
    client = make_client()

    response = client.get("/api/documents")

    assert response.status_code == 200

    documents = response.get_json()["documents"]

    assert len(documents) == 2

    for document in documents:
        assert isinstance(document["id"], int)
        assert isinstance(document["filename"], str)
        assert isinstance(document["pages"], int)
        assert isinstance(document["chunk_count"], int)
        assert isinstance(document["ready"], bool)


def test_documents_are_not_modified_by_listing():
    client = make_client()

    with client.application.app_context():
        before = db.session.execute(
            text("SELECT COUNT(*) FROM documents")
        ).scalar_one()

    client.get("/api/documents")

    with client.application.app_context():
        after = db.session.execute(
            text("SELECT COUNT(*) FROM documents")
        ).scalar_one()

    assert before == after == 2
