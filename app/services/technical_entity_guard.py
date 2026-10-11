import re


class TechnicalEntityGuard:
    """Check whether a complete technical entity occurs in source text."""

    def contains_entity(self, source_text: str, entity: str) -> bool:
        if not isinstance(source_text, str):
            raise ValueError("source_text must be a string")

        if not isinstance(entity, str) or not entity.strip():
            raise ValueError("entity must be a non-empty string")

        entity = entity.strip()

        pattern = (
            r"(?<!\w)"
            + re.escape(entity)
            + r"(?!\w)"
        )

        return re.search(
            pattern,
            source_text,
            flags=re.IGNORECASE,
        ) is not None
