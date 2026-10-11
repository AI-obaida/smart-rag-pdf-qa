from unittest.mock import Mock, patch

from app.services.structured_rag_service import StructuredRAGService


def test_not_applicable_is_not_automatically_accepted():
    llm = Mock()
    llm.generate.return_value = {
        "items": [{
            "fact": "Students must use Flask.",
            "source_id": "S1",
        }],
        "source_count": 1,
        "model": "test-model",
    }

    citation = Mock()
    citation.evaluate.return_value = {
        "verdict": "SUPPORTED",
        "verified": True,
        "model": "test-validator",
    }

    modality = Mock()
    modality.evaluate.return_value = {
        "verdict": "NOT_APPLICABLE",
        "allowed": True,
        "reason": "no_matching_source_statement",
    }

    with patch(
        "app.services.structured_rag_service.RAGService"
    ), patch(
        "app.services.structured_rag_service.ChunkExpansionService"
    ):
        service = StructuredRAGService(
            embedding_model=Mock(),
            llm_service=llm,
            citation_validator=citation,
            modality_guard=modality,
        )

    service.rag.retrieve.return_value = [
        {"chunk_id": 1},
    ]

    service.expansion.expand_forward.return_value = [{
        "id": 1,
        "chunk_index": 1,
        "page_number": 1,
        "chunk_text": "Students must use Flask.",
    }]

    result = service.ask(
        question="What must students use?",
        document_id=1,
    )

    assert result["items"] == []
    assert result["status"] == "insufficient_context"
    assert result["modality_validation"]["rejected_count"] == 1
