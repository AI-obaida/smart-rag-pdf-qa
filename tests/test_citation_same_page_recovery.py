from unittest.mock import Mock

from app.services.structured_rag_service import StructuredRAGService


def make_service(verdicts):
    validator = Mock()
    validator.evaluate.side_effect = [
        {"verdict": verdict, "verified": verdict == "SUPPORTED"}
        for verdict in verdicts
    ]

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
            "chunk_text": "The project must use one of the following: Dja",
        },
        {
            "id": 11,
            "chunk_index": 2,
            "page_number": 1,
            "chunk_text": "The project must use Django or Flask.",
        },
        {
            "id": 12,
            "chunk_index": 3,
            "page_number": 2,
            "chunk_text": "Unrelated information.",
        },
    ]

    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "The project must use Django or Flask.",
                "source_id": "S1",
                "page_number": 99,
            }
        ],
        "source_count": 3,
        "model": "mock-model",
    }

    return service


def test_recovers_from_same_page_source():
    service = make_service(["INSUFFICIENT", "SUPPORTED"])

    result = service.ask("Which framework?", 1)

    assert result["status"] == "answered"
    assert result["items"][0]["source_id"] == "S2"
    assert result["items"][0]["page_number"] == 1
    assert result["citation_validation"]["accepted_count"] == 1
    assert service.citation_validator.evaluate.call_count == 2


def test_does_not_recover_from_contradiction():
    service = make_service(["CONTRADICTED"])

    result = service.ask("Which framework?", 1)

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    assert service.citation_validator.evaluate.call_count == 1


def test_does_not_search_other_pages():
    service = make_service(["INSUFFICIENT", "INSUFFICIENT"])

    result = service.ask("Which framework?", 1)

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    assert service.citation_validator.evaluate.call_count == 2
