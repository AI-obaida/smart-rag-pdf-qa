from unittest.mock import Mock

from app.services.structured_rag_service import StructuredRAGService
from app.services.question_fact_consistency_guard import (
    QuestionFactConsistencyGuard,
)


def make_service(fact, citation_verdict="SUPPORTED"):
    citation_validator = Mock()
    citation_validator.evaluate.return_value = {
        "verdict": citation_verdict,
        "verified": citation_verdict == "SUPPORTED",
    }

    relevance_guard = Mock()
    relevance_guard.evaluate.return_value = {
        "verdict": "RELEVANT",
        "relevant": True,
    }

    service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=Mock(),
        citation_validator=citation_validator,
        relevance_guard=relevance_guard,
    )

    service.consistency_guard = QuestionFactConsistencyGuard()
    service.rag = Mock()
    service.expansion = Mock()

    service.rag.retrieve.return_value = [{"chunk_id": 10}]
    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 1,
            "chunk_text": fact,
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

    return service, relevance_guard


def test_rejects_accuracy_when_question_asks_recall():
    service, relevance_guard = make_service(
        "The model accuracy is 95 percent."
    )

    result = service.ask(
        "What is the recall of the model?",
        1,
    )

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    relevance_guard.evaluate.assert_called_once()


def test_accepts_matching_recall_fact():
    service, relevance_guard = make_service(
        "The model recall is 82 percent."
    )

    result = service.ask(
        "What is the recall of the model?",
        1,
    )

    assert result["status"] == "answered"
    assert len(result["items"]) == 1
    relevance_guard.evaluate.assert_called_once()


def test_unsupported_fact_stays_rejected():
    service, relevance_guard = make_service(
        "The model recall is 82 percent.",
        citation_verdict="CONTRADICTED",
    )

    result = service.ask(
        "What is the recall of the model?",
        1,
    )

    assert result["status"] == "insufficient_context"
    assert result["items"] == []
    relevance_guard.evaluate.assert_not_called()
