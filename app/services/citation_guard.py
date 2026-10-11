import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CitationValidationResult:
    valid: bool
    cited_pages: tuple[int, ...]
    allowed_pages: tuple[int, ...]
    invalid_pages: tuple[int, ...]


def validate_citations(
    answer: str,
    allowed_pages: Iterable[int],
) -> CitationValidationResult:
    if not isinstance(answer, str):
        raise TypeError("answer must be a string")

    allowed = tuple(sorted(set(allowed_pages)))

    if not allowed or any(
        not isinstance(page, int)
        or isinstance(page, bool)
        or page < 1
        for page in allowed
    ):
        raise ValueError(
            "allowed_pages must contain positive page numbers"
        )

    cited = tuple(
        int(page)
        for page in re.findall(
            r"\bpage\s+(\d+)\b",
            answer,
            flags=re.IGNORECASE,
        )
    )

    invalid = tuple(
        sorted(set(cited) - set(allowed))
    )

    return CitationValidationResult(
        valid=bool(cited) and not invalid,
        cited_pages=cited,
        allowed_pages=allowed,
        invalid_pages=invalid,
    )
