from unittest.mock import Mock, patch

from app.services.structured_rag_service import StructuredRAGService


def test_arabic_question_uses_validated_translation_for_relevance():
    question_ar = (
        "\u0645\u0627 \u0627\u0644\u0641\u0631\u0642 "
        "\u0628\u064a\u0646 \u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0622\u0644\u064a \u0648\u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0639\u0645\u064a\u0642\u061f"
    )

    question_en = (
        "What is the difference between machine learning and deep learning?"
    )

    fact = (
        "Traditional machine learning uses manual feature extraction, "
        "while deep learning learns features automatically."
    )

    llm = Mock()
    relevance = Mock()
    relevance.evaluate.return_value = {
        "verdict": "RELEVANT",
        "relevant": True,
    }

    service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=llm,
        relevance_guard=relevance,
    )

    service.rag = Mock()
    service.expansion = Mock()

    service.rag.retrieve.return_value = [{"chunk_id": 10}]
    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 2,
            "chunk_text": fact,
        }
    ]

    llm.generate.return_value = {
        "items": [
            {
                "fact": fact,
                "source_id": "S1",
                "page_number": 2,
            }
        ],
        "source_count": 1,
        "model": "mock-model",
    }

    with patch(
        "app.services.structured_rag_service.SearchQueryTranslator"
    ) as translator:
        translator.return_value.translate.return_value = question_en

        result = service.ask(
            question=question_ar,
            document_id=1,
            top_k=3,
        )

    service.rag.retrieve.assert_called_once_with(
        question=question_en,
        document_id=1,
        top_k=3,
    )

    llm.generate.assert_called_once_with(
        question=question_ar,
        chunks=service.expansion.expand_forward.return_value,
    )

    relevance.evaluate.assert_called_once_with(
        question=question_en,
        fact=fact,
    )

    assert result["question"] == question_ar
    assert result["status"] == "answered"


def test_rejected_translation_uses_original_question():
    question_ar = (
        "\u0645\u0627 \u0627\u0644\u0641\u0631\u0642 "
        "\u0628\u064a\u0646 \u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0622\u0644\u064a \u0648\u0627\u0644\u062a\u0639\u0644\u0645 "
        "\u0627\u0644\u0639\u0645\u064a\u0642\u061f"
    )

    llm = Mock()
    relevance = Mock()
    relevance.evaluate.return_value = {
        "verdict": "RELEVANT",
        "relevant": True,
    }

    service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=llm,
        relevance_guard=relevance,
    )

    service.rag = Mock()
    service.expansion = Mock()

    service.rag.retrieve.return_value = [{"chunk_id": 10}]
    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 2,
            "chunk_text": "Machine learning and deep learning.",
        }
    ]

    llm.generate.return_value = {
        "items": [
            {
                "fact": "Machine learning and deep learning.",
                "source_id": "S1",
                "page_number": 2,
            }
        ],
        "source_count": 1,
        "model": "mock-model",
    }

    with patch(
        "app.services.structured_rag_service.SearchQueryTranslator"
    ) as translator:
        translator.return_value.translate.return_value = (
            "What is the difference between cars and trucks?"
        )

        result = service.ask(
            question=question_ar,
            document_id=1,
        )

    service.rag.retrieve.assert_called_once_with(
        question=question_ar,
        document_id=1,
        top_k=3,
    )

    relevance.evaluate.assert_called_once_with(
        question=question_ar,
        fact="Machine learning and deep learning.",
    )

    assert result["question"] == question_ar
