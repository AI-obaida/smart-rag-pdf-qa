from unittest.mock import Mock

from app.services.structured_rag_service import StructuredRAGService


def make_service(source_text, fact):
    validator = Mock()
    validator.evaluate.return_value = {
        "verdict": "SUPPORTED",
        "verified": True,
    }

    service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=Mock(),
        citation_validator=validator,
    )

    service.rag = Mock()
    service.expansion = Mock()

    service.rag.retrieve.return_value = [{"chunk_id": 10}]

    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 1,
            "chunk_text": source_text,
        }
    ]

    service.llm.generate.return_value = {
        "items": [
            {
                "fact": fact,
                "source_id": "S1",
                "page_number": 1,
            }
        ],
        "source_count": 1,
        "model": "mock-model",
    }

    return service


def test_rejects_truncated_django_even_if_llm_supports():
    service = make_service(
        "Allowed frameworks: Dja",
        "Django is an allowed framework.",
    )

    result = service.ask("Which frameworks?", 1)

    assert result["status"] == "insufficient_context"
    assert result["items"] == []


def test_accepts_complete_django():
    service = make_service(
        "Allowed frameworks: Django",
        "Django is an allowed framework.",
    )

    result = service.ask("Which frameworks?", 1)

    assert result["status"] == "answered"
    assert len(result["items"]) == 1


def test_rejects_truncated_flask_even_if_llm_supports():
    service = make_service(
        "Allowed frameworks: Fla",
        "Flask is an allowed framework.",
    )

    result = service.ask("Which frameworks?", 1)

    assert result["status"] == "insufficient_context"
    assert result["items"] == []


def test_accepts_complete_flask():
    service = make_service(
        "Allowed frameworks: Flask",
        "Flask is an allowed framework.",
    )

    result = service.ask("Which frameworks?", 1)

    assert result["status"] == "answered"
    assert len(result["items"]) == 1


def test_does_not_block_negative_answer():
    service = make_service(
        "Only Django is required.",
        "Flask is not required.",
    )

    result = service.ask("Is Flask required?", 1)

    assert result["status"] == "answered"
    assert len(result["items"]) == 1
