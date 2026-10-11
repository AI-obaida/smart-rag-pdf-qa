import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceValidationResult:
    valid: bool
    cited_sources: tuple[str, ...]
    invalid_sources: tuple[str, ...]
    referenced_pages: tuple[int, ...]


def validate_source_citations(
    answer: str,
    chunks: list[dict],
) -> SourceValidationResult:
    if not isinstance(answer, str):
        raise TypeError("answer must be a string")

    if not chunks:
        raise ValueError("chunks must not be empty")

    source_map = {
        f"S{index}": chunk["page_number"]
        for index, chunk in enumerate(chunks, 1)
    }

    cited = tuple(
        re.findall(r"\[S\d+\]", answer)
    )

    cited_sources = tuple(
        citation[1:-1]
        for citation in cited
    )

    invalid_sources = tuple(
        sorted(
            set(cited_sources) - set(source_map)
        )
    )

    referenced_pages = tuple(
        sorted({
            source_map[source]
            for source in cited_sources
            if source in source_map
        })
    )

    return SourceValidationResult(
        valid=bool(cited_sources) and not invalid_sources,
        cited_sources=cited_sources,
        invalid_sources=invalid_sources,
        referenced_pages=referenced_pages,
    )
