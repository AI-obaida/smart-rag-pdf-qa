import pytest

from app.services.modality_guard import ModalityGuard


@pytest.mark.parametrize(
    "source,claim,expected",
    [
        (
            "Students must not use Django.",
            "Students must use Django.",
            "REJECT",
        ),
        (
            "Students must not use Flask or Django.",
            "Students must use Django.",
            "REJECT",
        ),
        (
            "Students must not use Flask, Django, or FastAPI.",
            "Students must use FastAPI.",
            "REJECT",
        ),
        (
            "Students must not use Flask with Django.",
            "Students must use Django.",
            "REJECT",
        ),
        (
            "Students must not use Flask with Django.",
            "Students must use Flask with Django.",
            "REJECT",
        ),
        (
            "Students must not use Flask with Django. Students must use Django.",
            "Students must use Django.",
            "PASS",
        ),
    ],
)
def test_prohibition_scope(source, claim, expected):
    result = ModalityGuard().evaluate(
        fact=claim,
        source_text=source,
    )
    assert result["verdict"] == expected
