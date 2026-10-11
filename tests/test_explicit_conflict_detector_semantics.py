import pytest

from app.services.explicit_conflict_detector import ExplicitConflictDetector


@pytest.mark.parametrize(
    "source, claim, expected",
    [
        (
            "Students must install Flask.",
            "Students must use Flask.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask.",
            "Students must delete Flask.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask if approved.",
            "Students must use Flask if rejected.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask only if approved.",
            "Students must use Flask only if rejected.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask unless exempted.",
            "Students must use Flask unless approved.",
            "UNKNOWN",
        ),
        (
            "Students must use Flask.",
            "Students must use Flask.",
            "NO_CONFLICT",
        ),
        (
            "Students must not use Flask.",
            "Students must not use Flask.",
            "NO_CONFLICT",
        ),
        (
            "Students should install Flask.",
            "Students must use Flask.",
            "UNKNOWN",
        ),
    ],
)
def test_semantic_distinctions(source, claim, expected):
    result = ExplicitConflictDetector().evaluate(
        source_text=source,
        fact=claim,
    )
    assert result["verdict"] == expected
