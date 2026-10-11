from unittest.mock import patch

from app.services.chunk_expansion import ChunkExpansionService


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


def test_does_not_expand_across_pages():
    seeds = [{"id": 10, "chunk_index": 1}]
    chunks = [
        {"id": 10, "document_id": 1, "chunk_index": 1,
         "page_number": 1, "chunk_text": "Page one"},
        {"id": 11, "document_id": 1, "chunk_index": 2,
         "page_number": 2, "chunk_text": "Page two"},
    ]

    with patch(
        "app.services.chunk_expansion.db.session.execute",
        side_effect=[FakeResult(seeds), FakeResult(chunks)],
    ):
        result = ChunkExpansionService().expand_forward(1, [10])

    assert [row["id"] for row in result] == [10]


def test_expands_within_same_page():
    seeds = [{"id": 10, "chunk_index": 1}]
    chunks = [
        {"id": 10, "document_id": 1, "chunk_index": 1,
         "page_number": 1, "chunk_text": "First part"},
        {"id": 11, "document_id": 1, "chunk_index": 2,
         "page_number": 1, "chunk_text": "Second part"},
    ]

    with patch(
        "app.services.chunk_expansion.db.session.execute",
        side_effect=[FakeResult(seeds), FakeResult(chunks)],
    ):
        result = ChunkExpansionService().expand_forward(1, [10])

    assert [row["id"] for row in result] == [10, 11]
