from unittest.mock import Mock

from app.services.structured_rag_service import StructuredRAGService


def make_service(
    citation_verdict="SUPPORTED",
    relevance_verdict="RELEVANT",
):
    citation_validator = Mock()
    citation_validator.evaluate.return_value = {
        "verdict": citation_verdict,
        "verified": citation_verdict == "SUPPORTED",
    }

    relevance_guard = Mock()
    relevance_guard.evaluate.return_value = {
        "verdict": relevance_verdict,
        "relevant": relevance_verdict == "RELEVANT",
    }

    service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=Mock(),
        citation_validator=citation_validator,
        relevance_guard=relevance_guard,
    )

    service.rag = Mock()
    service.expansion = Mock()

    service.rag.retrieve.return_value = [
        {"chunk_id": 10}
    ]

    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 1,
            "chunk_text": "Django and Flask are backend frameworks.",
        }
    ]

    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "Django and Flask are backend frameworks.",
                "source_id": "S1",
                "page_number": 1,
            }
        ],
        "source_count": 1,
        "model": "mock-model",
    }

    return service, relevance_guard


def test_accepts_supported_and_relevant_fact():
    service, guard = make_service()

    result = service.ask(
        "Which backend frameworks are mentioned?",
        1,
    )

    assert result["status"] == "answered"
    assert len(result["items"]) == 1
    guard.evaluate.assert_called_once()


def test_rejects_supported_but_irrelevant_fact():
    service, guard = make_service(
        relevance_verdict="IRRELEVANT",
    )

    result = service.ask(
        "Which backend frameworks are mentioned?",
        1,
    )

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    guard.evaluate.assert_called_once()


def test_rejects_relevant_but_unsupported_fact():
    service, guard = make_service(
        citation_verdict="CONTRADICTED",
    )

    result = service.ask(
        "Which backend frameworks are mentioned?",
        1,
    )

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    guard.evaluate.assert_not_called()


def test_preserves_corrected_citation():
    service, guard = make_service(
        citation_verdict="INSUFFICIENT",
    )

    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 1,
            "chunk_text": "The project uses a backend.",
        },
        {
            "id": 11,
            "chunk_index": 2,
            "page_number": 1,
            "chunk_text": "Django and Flask are backend frameworks.",
        },
    ]

    service.citation_validator.evaluate.side_effect = [
        {"verdict": "INSUFFICIENT"},
        {"verdict": "SUPPORTED"},
    ]

    result = service.ask(
        "Which backend frameworks are mentioned?",
        1,
    )

    assert result["status"] == "answered"
    assert result["items"][0]["source_id"] == "S2"
    assert result["items"][0]["page_number"] == 1
    guard.evaluate.assert_called_once()
