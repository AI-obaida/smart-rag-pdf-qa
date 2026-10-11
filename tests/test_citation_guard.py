import pytest

from app.services.citation_guard import validate_citations


def test_valid_citations():
    result = validate_citations(
        "GitHub (page 13), presentation (page 14).",
        [5, 6, 12, 13, 14],
    )
    assert result.valid
    assert result.invalid_pages == ()


def test_invalid_citation():
    result = validate_citations(
        "Evaluation (page 15).",
        [5, 6, 12, 13, 14],
    )
    assert not result.valid
    assert result.invalid_pages == (15,)


def test_missing_citations():
    result = validate_citations(
        "The document discusses project requirements.",
        [12, 13, 14],
    )
    assert not result.valid
    assert result.cited_pages == ()


def test_empty_allowed_pages():
    with pytest.raises(ValueError):
        validate_citations("Test (page 1)", [])


def test_invalid_answer_type():
    with pytest.raises(TypeError):
        validate_citations(None, [1, 2])


def test_duplicate_citations():
    result = validate_citations(
        "First (page 13), second (page 13).",
        [13],
    )
    assert result.valid
    assert result.cited_pages == (13, 13)
