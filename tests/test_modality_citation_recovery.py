from unittest.mock import Mock, patch

from app.services.modality_guard import ModalityGuard
from app.services.structured_rag_service import StructuredRAGService


def test_modality_uses_corrected_citation_source():
    llm = Mock()
    llm.generate.return_value = {
        "items": [
            {
                "fact": "Students must use Flask.",
                "source_id": "S1",
            }
        ],
        "source_count": 2,
        "model": "test-model",
    }

    validator = Mock()

    def evaluate_citation(fact, source_text):
        if source_text == "Students must use Flask.":
            verdict = "SUPPORTED"
        else:
            verdict = "INSUFFICIENT"

        return {
            "verdict": verdict,
            "verified": verdict == "SUPPORTED",
            "model": "test-validator",
        }

    validator.evaluate.side_effect = evaluate_citation

    modality = Mock(wraps=ModalityGuard())

    with patch(
        "app.services.structured_rag_service.RAGService"
    ), patch(
        "app.services.structured_rag_service.ChunkExpansionService"
    ):
        service = StructuredRAGService(
            embedding_model=Mock(),
            llm_service=llm,
            citation_validator=validator,
            modality_guard=modality,
        )

    service.rag.retrieve.return_value = [
        {"chunk_id": 1},
    ]

    service.expansion.expand_forward.return_value = [
        {
            "id": 1,
            "chunk_index": 1,
            "page_number": 1,
            "chunk_text": "Students should discuss the project idea.",
        },
        {
            "id": 2,
            "chunk_index": 2,
            "page_number": 1,
            "chunk_text": "Students must use Flask.",
        },
    ]

    result = service.ask(
        question="What framework must students use?",
        document_id=1,
    )

    assert result["status"] == "answered"
    assert len(result["items"]) == 1
    assert result["items"][0]["source_id"] == "S2"
    assert result["items"][0]["page_number"] == 1

    modality.evaluate.assert_called_once_with(
        fact="Students must use Flask.",
        source_text="Students must use Flask.",
    )
