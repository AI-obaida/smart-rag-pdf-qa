from unittest.mock import Mock, patch

from app.services.structured_rag_service import StructuredRAGService
from app.services.modality_guard import ModalityGuard


def make_service(fact, source_id="S1", validator_verdict="SUPPORTED"):
    embedding = Mock()
    llm = Mock()
    llm.generate.return_value = {
        "items": [{"fact": fact, "source_id": source_id}],
        "source_count": 2,
        "model": "test-model",
    }

    validator = Mock()
    validator.evaluate.return_value = {
        "verdict": validator_verdict,
        "verified": validator_verdict == "SUPPORTED",
        "model": "test-validator",
    }

    with patch(
        "app.services.structured_rag_service.RAGService"
    ), patch(
        "app.services.structured_rag_service.ChunkExpansionService"
    ):
        service = StructuredRAGService(
            embedding_model=embedding,
            llm_service=llm,
            citation_validator=validator,
            modality_guard=ModalityGuard(),
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

    return service


def test_rejects_mandatory_overstatement():
    service = make_service(
        "Students must discuss the project idea."
    )

    result = service.ask(
        question="Is project discussion mandatory?",
        document_id=1,
    )

    assert result["items"] == []
    assert result["status"] == "insufficient_context"


def test_preserves_correct_mandatory_requirement():
    service = make_service(
        "Students must use Flask.",
        source_id="S2",
    )

    result = service.ask(
        question="What framework must students use?",
        document_id=1,
    )

    assert len(result["items"]) == 1
    assert result["items"][0]["source_id"] == "S2"


def test_not_applicable_does_not_override_citation_rejection():
    service = make_service(
        "The project uses PostgreSQL.",
        validator_verdict="INSUFFICIENT",
    )

    result = service.ask(
        question="What database does the project use?",
        document_id=1,
    )

    assert result["items"] == []
    assert result["status"] == "insufficient_context"
