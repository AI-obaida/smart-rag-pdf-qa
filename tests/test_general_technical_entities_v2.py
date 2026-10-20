from unittest.mock import Mock

import pytest

from app.services.structured_rag_service import StructuredRAGService


@pytest.fixture
def service():
    return StructuredRAGService(
        embedding_model=Mock(),
        llm_service=Mock(),
    )


@pytest.mark.parametrize(
    "fact, source, expected",
    [
        (
            "PostgreSQL stores the data.",
            "The database is PostgreSQL.",
            True,
        ),
        (
            "PostgreSQL stores the data.",
            "The database is MySQL.",
            False,
        ),
        (
            "TensorFlow is supported.",
            "The library is TensorFlow.",
            True,
        ),
        (
            "TensorFlow is supported.",
            "The library is PyTorch.",
            False,
        ),
        (
            "PyTorch is supported.",
            "The library is PyTorch.",
            True,
        ),
        (
            "PyTorch is supported.",
            "The library is TensorFlow.",
            False,
        ),
    ],
)
def test_general_technical_entity_support(
    service, fact, source, expected
):
    assert service._technical_entities_supported(
        fact, source
    ) is expected


@pytest.mark.parametrize(
    "fact, source, expected",
    [
        (
            "The database stores records.",
            "A database stores records.",
            True,
        ),
        (
            "Users can upload documents.",
            "Documents can be uploaded by users.",
            True,
        ),
        (
            "Python is supported.",
            "The system supports Python.",
            True,
        ),
        (
            "Python is supported.",
            "The system supports Java.",
            False,
        ),
        (
            "GPT-4 is supported.",
            "The system supports GPT-4.",
            True,
        ),
        (
            "GPT-4 is supported.",
            "The system supports GPT-3.",
            False,
        ),
    ],
)
def test_entity_detection_edge_cases(
    service, fact, source, expected
):
    assert service._technical_entities_supported(
        fact, source
    ) is expected


@pytest.mark.parametrize(
    "fact, source, expected",
    [
        ("C++ is supported.", "Languages: C++.", True),
        ("C++ is supported.", "Languages: Java.", False),
        ("Node.js is supported.", "Runtime: Node.js.", True),
        ("Node.js is supported.", "Runtime: Python.", False),
        ("SQL is required.", "Database language: SQL.", True),
        ("SQL is required.", "Database language: Python.", False),
    ],
)
def test_additional_technical_entities(
    service, fact, source, expected
):
    assert service._technical_entities_supported(
        fact, source
    ) is expected


@pytest.mark.parametrize(
    "fact, source, expected",
    [
        (
            "PostgreSQL is not supported.",
            "The database uses MySQL.",
            False,
        ),
        (
            "PostgreSQL is not supported.",
            "PostgreSQL is not supported.",
            True,
        ),
        (
            "TensorFlow is not required.",
            "The project uses PyTorch.",
            False,
        ),
        (
            "Python is supported without Java.",
            "Python is supported without Java.",
            True,
        ),
    ],
)
def test_negative_technical_entity_support(
    service, fact, source, expected
):
    assert service._technical_entities_supported(
        fact, source
    ) is expected


@pytest.mark.parametrize(
    "fact, source, expected",
    [
        (
            "Django is not required.",
            "Only Django is required.",
            False,
        ),
        (
            "Flask is not required.",
            "Only Django is required.",
            True,
        ),
    ],
)
def test_exclusive_requirement_negation(
    service, fact, source, expected
):
    assert service._technical_entities_supported(
        fact, source
    ) is expected
