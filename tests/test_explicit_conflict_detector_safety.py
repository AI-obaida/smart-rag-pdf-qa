import pytest

from app.services.explicit_conflict_detector import ExplicitConflictDetector


@pytest.mark.parametrize(
    "source, claim, expected",
    [
        (
            "Students must use Flask.",
            "Students must use Flask or Django.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask.",
            "Teachers must use Flask.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask.",
            "Students must not install Flask.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask if approved.",
            "Students must use Flask only if approved.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask.",
            "Students must use Flask for testing only.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask.",
            "Students must use Flask and Django.",
            "UNKNOWN",
        ),
    ],
)
def test_safety_cases(source, claim, expected):
    result = ExplicitConflictDetector().evaluate(
        source_text=source,
        fact=claim,
    )

    assert result["verdict"] == expected
