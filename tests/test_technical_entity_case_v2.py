from app.services.structured_rag_service import StructuredRAGService


def test_lowercase_flask_not_supported_by_django_source():
    assert StructuredRAGService._technical_entities_supported(
        None,
        "The project uses flask.",
        "The project uses Django.",
    ) is False


def test_postgresql_not_supported_by_sqlite_source():
    assert StructuredRAGService._technical_entities_supported(
        None,
        "The project uses PostgreSQL.",
        "The project uses SQLite.",
    ) is False


def test_matching_technology_case_insensitive():
    assert StructuredRAGService._technical_entities_supported(
        None,
        "The project uses flask.",
        "The project uses Flask.",
    ) is True
