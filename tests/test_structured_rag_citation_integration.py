from unittest.mock import Mock

import pytest

from app.services.structured_rag_service import StructuredRAGService


@pytest.fixture
def service():
    validator = Mock()

    rag_service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=Mock(),
        citation_validator=validator,
    )

    rag_service.rag = Mock()
    rag_service.expansion = Mock()

    rag_service.rag.retrieve.return_value = [
        {"chunk_id": 10}
    ]

    rag_service.expansion.expand_forward.return_value = [
        {
            "chunk_id": 10,
            "chunk_text": "The project must use Django or Flask.",
            "page_number": 1,
        },
        {
            "chunk_id": 11,
            "chunk_text": "The project must evaluate performance.",
            "page_number": 6,
        },
    ]

    return rag_service


def test_accept_supported_fact(service):
    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "The project must use Django or Flask.",
                "source_id": "S1",
                "page_number": 1,
            }
        ],
        "source_count": 2,
        "model": "mock-model",
    }

    service.citation_validator.evaluate.return_value = {
        "verdict": "SUPPORTED",
        "verified": True,
    }

    result = service.ask("What is required?", 1)

    assert result["status"] == "answered"
    assert len(result["items"]) == 1
    assert result["citation_validation"]["accepted_count"] == 1
    assert result["citation_validation"]["rejected_count"] == 0

    service.citation_validator.evaluate.assert_called_once_with(
        fact="The project must use Django or Flask.",
        source_text="The project must use Django or Flask.",
    )


@pytest.mark.parametrize(
    "verdict",
    ["CONTRADICTED", "INSUFFICIENT"],
)
def test_reject_unverified_fact(service, verdict):
    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "The project does not require evaluation.",
                "source_id": "S2",
                "page_number": 6,
            }
        ],
        "source_count": 2,
        "model": "mock-model",
    }

    service.citation_validator.evaluate.return_value = {
        "verdict": verdict,
        "verified": False,
    }

    result = service.ask("Is evaluation required?", 1)

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    assert result["citation_validation"]["accepted_count"] == 0
    assert result["citation_validation"]["rejected_count"] == 1


def test_reject_unknown_source(service):
    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "An unsupported claim.",
                "source_id": "S99",
                "page_number": 99,
            }
        ],
        "source_count": 2,
        "model": "mock-model",
    }

    result = service.ask("What is required?", 1)

    assert result["items"] == []
    assert result["citation_validation"]["rejected_count"] == 1

    service.citation_validator.evaluate.assert_not_called()


def test_validator_failure_does_not_accept_fact(service):
    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "The project must use Django or Flask.",
                "source_id": "S1",
                "page_number": 1,
            }
        ],
        "source_count": 2,
        "model": "mock-model",
    }

    service.citation_validator.evaluate.side_effect = ConnectionError(
        "Ollama unavailable"
    )

    with pytest.raises(ConnectionError):
        service.ask("What is required?", 1)
