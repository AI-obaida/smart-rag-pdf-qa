import pytest

from app.services.explicit_conflict_detector import ExplicitConflictDetector


@pytest.mark.parametrize(
    "source, claim, expected",
    [
        (
            "Students must use Flask.",
            "Students must not use Flask.",
            "CONFLICT",
        ),
        (
            "Students must not use Flask.",
            "Students must use Flask.",
            "CONFLICT",
        ),
        (
            "Students must use Flask only if approved.",
            "Students must use Flask.",
            "CONFLICT",
        ),
        (
            "Students must use Flask unless exempted.",
            "Students must use Flask without exceptions.",
            "CONFLICT",
        ),
        (
            "Students should use Flask.",
            "Students must use Flask.",
            "CONFLICT",
        ),
        (
            "Students must use Flask.",
            "Students must use Django.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask if approved.",
            "Students must use Flask if approved.",
            "NO_CONFLICT",
        ),
        (
            "Students must use Flask.",
            "Students must use Flask.",
            "NO_CONFLICT",
        ),
        (
            "Students must use Flask if approved.",
            "Students must use Flask unless exempted.",
            "UNKNOWN",
        ),
    ],
)
def test_explicit_conflicts(source, claim, expected):
    result = ExplicitConflictDetector().evaluate(
        source_text=source,
        fact=claim,
    )

    assert result["verdict"] == expected
    assert result["verdict"] in {
        "CONFLICT",
        "NO_CONFLICT",
        "UNKNOWN",
    }


@pytest.mark.parametrize(
    "source, claim",
    [
        ("", "Students must use Flask."),
        ("Students must use Flask.", ""),
        (None, "Students must use Flask."),
        ("Students must use Flask.", None),
    ],
)
def test_invalid_inputs(source, claim):
    with pytest.raises((TypeError, ValueError)):
        ExplicitConflictDetector().evaluate(
            source_text=source,
            fact=claim,
        )
