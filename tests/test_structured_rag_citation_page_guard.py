from unittest.mock import Mock

from app.services.structured_rag_service import StructuredRAGService


def test_citation_page_must_match_source():
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

    service.rag.retrieve.return_value = [
        {"chunk_id": 10}
    ]

    service.expansion.expand_forward.return_value = [
        {
            "chunk_id": 10,
            "chunk_text": "The project must use Django or Flask.",
            "page_number": 1,
        }
    ]

    service.llm.generate.return_value = {
        "items": [
            {
                "fact": "The project must use Django or Flask.",
                "source_id": "S1",
                "page_number": 99,
            }
        ],
        "source_count": 1,
        "model": "mock-model",
    }

    result = service.ask(
        question="Which framework is required?",
        document_id=1,
    )

    assert result["items"] == [
        {
            "fact": "The project must use Django or Flask.",
            "source_id": "S1",
            "page_number": 1,
        }
    ]
