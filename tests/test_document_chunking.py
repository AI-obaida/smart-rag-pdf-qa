import pytest

from app.services.document_chunking import DocumentChunker


def test_chunking_basic():
    chunker = DocumentChunker(chunk_size=5, chunk_overlap=2)

    chunks = chunker.chunk_text([(1, "abcdefghij")])

    assert [item["chunk_text"] for item in chunks] == [
        "abcde",
        "defgh",
        "ghij",
    ]

    assert [item["page"] for item in chunks] == [1, 1, 1]
    assert [item["chunk_id"] for item in chunks] == [1, 2, 3]


def test_chunking_multiple_pages():
    chunker = DocumentChunker(chunk_size=5, chunk_overlap=2)

    chunks = chunker.chunk_text([
        (1, "abcdef"),
        (2, "uvwxyz"),
    ])

    assert [item["page"] for item in chunks] == [1, 1, 2, 2]
    assert chunks[0]["chunk_text"] == "abcde"
    assert chunks[2]["chunk_text"] == "uvwxy"


def test_chunking_empty():
    chunker = DocumentChunker()
    assert chunker.chunk_text([]) == []
    assert chunker.chunk_text([(1, "")]) == []


def test_chunking_small_text():
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)

    chunks = chunker.chunk_text([(1, "short text")])

    assert len(chunks) == 1
    assert chunks[0]["chunk_text"] == "short text"


@pytest.mark.parametrize(
    "size,overlap",
    [
        (0, 0),
        (-1, 0),
        (100, -1),
        (100, 100),
        (100, 101),
        (True, 0),
    ],
)
def test_invalid_chunk_settings(size, overlap):
    with pytest.raises(ValueError):
        DocumentChunker(chunk_size=size, chunk_overlap=overlap)