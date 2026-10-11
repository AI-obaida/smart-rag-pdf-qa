from unittest.mock import Mock

import pytest

from app.services.structured_rag_service import StructuredRAGService


def make_service():
    llm = Mock()
    service = StructuredRAGService(
        embedding_model=Mock(),
        llm_service=llm,
    )

    service.rag = Mock()
    service.expansion = Mock()

    return service, llm


def test_successful_answer():
    service, llm = make_service()

    service.rag.retrieve.return_value = [
        {"chunk_id": 10}
    ]

    chunks = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 2,
            "chunk_text": "Django or Flask",
        }
    ]

    service.expansion.expand_forward.return_value = chunks

    llm.generate.return_value = {
        "items": [
            {
                "fact": "يمكن استخدام Django أو Flask",
                "source_id": "S1",
                "page_number": 2,
            }
        ],
        "source_count": 1,
        "model": "qwen2.5:3b",
    }

    result = service.ask(
        question="ما متطلبات Backend؟",
        document_id=1,
        top_k=3,
    )

    assert result["status"] == "answered"
    assert result["document_id"] == 1
    assert result["source_count"] == 1
    assert result["items"][0]["page_number"] == 2

    service.rag.retrieve.assert_called_once_with(
        question="What are the requirements for Backend?",
        document_id=1,
        top_k=3,
    )

    service.expansion.expand_forward.assert_called_once_with(
        document_id=1,
        seed_chunk_ids=[10],
    )

    llm.generate.assert_called_once_with(
        question="ما متطلبات Backend؟",
        chunks=chunks,
    )


def test_no_context():
    service, llm = make_service()

    service.rag.retrieve.return_value = []

    result = service.ask(
        question="سؤال غير موجود",
        document_id=1,
    )

    assert result["status"] == "no_context"
    assert result["items"] == []
    assert result["source_count"] == 0

    service.expansion.expand_forward.assert_not_called()
    llm.generate.assert_not_called()


def test_empty_generated_answer():
    service, llm = make_service()

    service.rag.retrieve.return_value = [
        {"chunk_id": 10}
    ]

    service.expansion.expand_forward.return_value = [
        {
            "id": 10,
            "chunk_index": 1,
            "page_number": 2,
            "chunk_text": "Some document content",
        }
    ]

    llm.generate.return_value = {
        "items": [],
        "source_count": 1,
        "model": "qwen2.5:3b",
    }

    result = service.ask(
        question="ما المعلومات؟",
        document_id=1,
    )

    assert result["status"] == "insufficient_context"
    assert result["items"] == []


@pytest.mark.parametrize(
    "question,document_id,top_k",
    [
        ("", 1, 3),
        ("   ", 1, 3),
        (None, 1, 3),
        ("سؤال", 0, 3),
        ("سؤال", -1, 3),
        ("سؤال", True, 3),
        ("سؤال", 1, 0),
        ("سؤال", 1, 21),
        ("سؤال", 1, True),
    ],
)
def test_invalid_inputs(question, document_id, top_k):
    service, _ = make_service()

    with pytest.raises(ValueError):
        service.ask(
            question=question,
            document_id=document_id,
            top_k=top_k,
        )

    service.rag.retrieve.assert_not_called()
