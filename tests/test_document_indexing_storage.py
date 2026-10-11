from unittest.mock import Mock

from app.services.document_indexing import DocumentIndexingService


def test_store_chunks_uses_parameters_without_committing():
    embedding_model = Mock()
    session = Mock()

    service = DocumentIndexingService(
        embedding_model=embedding_model,
    )

    chunks = [
        {
            "page_number": 2,
            "chunk_index": 1,
            "chunk_text": "Example content",
            "embedding": [0.1] * 384,
        }
    ]

    service.store_chunks(
        document_id=7,
        chunks=chunks,
        session=session,
    )

    assert session.execute.call_count == 1

    statement, parameters = session.execute.call_args.args

    sql = str(statement)

    assert "INSERT INTO document_chunks" in sql
    assert "CAST(:embedding AS vector(384))" in sql

    assert parameters["document_id"] == 7
    assert parameters["page_number"] == 2
    assert parameters["chunk_index"] == 1
    assert parameters["chunk_text"] == "Example content"

    assert isinstance(parameters["embedding"], str)
    assert parameters["embedding"].startswith("[")
    assert parameters["embedding"].endswith("]")

    session.commit.assert_not_called()
