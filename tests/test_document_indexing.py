from unittest.mock import Mock

from app.services.document_indexing import DocumentIndexingService


def test_indexing_prepares_page_chunks_and_embeddings():
    embedding_model = Mock()

    embedding_model.encode.return_value = [
        [0.1] * 384,
        [0.2] * 384,
    ]

    service = DocumentIndexingService(
        embedding_model=embedding_model,
    )

    chunks = service.prepare_chunks([
        (1, "First page content"),
        (2, "Second page content"),
    ])

    assert len(chunks) == 2
    assert [chunk["page_number"] for chunk in chunks] == [1, 2]
    assert [chunk["chunk_index"] for chunk in chunks] == [1, 2]

    assert all(
        len(chunk["embedding"]) == 384
        for chunk in chunks
    )

    encoded_texts = embedding_model.encode.call_args.args[0]

    assert encoded_texts == [
        "passage: First page content",
        "passage: Second page content",
    ]
