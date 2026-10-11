import re


class ExplicitConflictDetector:
    """Detect narrow, explicit English modality conflicts."""

    @staticmethod
    def _normalize(text):
        return " ".join(text.strip().casefold().split())

    @staticmethod
    def _features(text):
        text = ExplicitConflictDetector._normalize(text)

        entity_match = re.search(
            r"\b(?:flask|django)\b",
            text,
        )

        entity = (
            entity_match.group(0)
            if entity_match
            else None
        )

        must = bool(re.search(r"\bmust\b", text))
        should = bool(re.search(r"\bshould\b", text))

        negated = bool(
            re.search(r"\bmust\s+not\b", text)
        )

        conditional = bool(
            re.search(r"\b(?:if|only\s+if)\b", text)
        )

        exception = bool(
            re.search(r"\bunless\b", text)
        )

        no_exceptions = bool(
            re.search(r"\bwithout\s+exceptions\b", text)
        )

        return {
            "entity": entity,
            "must": must,
            "should": should,
            "negated": negated,
            "conditional": conditional,
            "exception": exception,
            "no_exceptions": no_exceptions,
        }

    def evaluate(self, source_text, fact):
        if not isinstance(source_text, str):
            raise TypeError("source_text must be a string")

        if not isinstance(fact, str):
            raise TypeError("fact must be a string")

        if not source_text.strip():
            raise ValueError("source_text cannot be empty")

        if not fact.strip():
            raise ValueError("fact cannot be empty")

        source = self._features(source_text)
        claim = self._features(fact)

        source_normalized = self._normalize(source_text)
        claim_normalized = self._normalize(fact)

        def action_of(text):
            match = re.search(
                r"\b(?:use|install|delete)\s+(?:flask|django)\b",
                text,
            )
            return match.group(0) if match else None

        def qualifier_of(text):
            match = re.search(
                r"\b(?:only\s+if|if|unless)\b.*",
                text,
            )
            return match.group(0).rstrip(".!? ") if match else None

        source_action = action_of(source_normalized)
        claim_action = action_of(claim_normalized)

        source_qualifier = qualifier_of(source_normalized)
        claim_qualifier = qualifier_of(claim_normalized)

        if (
            source_action is None
            or claim_action is None
            or source_action != claim_action
        ):
            return {
                "verdict": "UNKNOWN",
                "source_features": source,
                "claim_features": claim,
            }

        if (
            source_qualifier is not None
            and claim_qualifier is not None
            and source_qualifier != claim_qualifier
        ):
            return {
                "verdict": "UNKNOWN",
                "source_features": source,
                "claim_features": claim,
            }

        if (
            source["entity"] is None
            or claim["entity"] is None
        ):
            verdict = "UNKNOWN"

        elif source["entity"] != claim["entity"]:
            verdict = "UNKNOWN"

        elif source["negated"] != claim["negated"]:
            verdict = "CONFLICT"

        elif source["should"] and claim["must"]:
            verdict = "CONFLICT"

        elif (
            source["conditional"]
            and not claim["conditional"]
            and not claim["exception"]
        ):
            verdict = "CONFLICT"

        elif (
            source["exception"]
            and claim["no_exceptions"]
        ):
            verdict = "CONFLICT"

        elif (
            source["conditional"] != claim["conditional"]
            or source["exception"] != claim["exception"]
        ):
            verdict = "UNKNOWN"

        elif (
            source["must"] == claim["must"]
            and source["should"] == claim["should"]
            and source["negated"] == claim["negated"]
            and source["conditional"] == claim["conditional"]
            and source["exception"] == claim["exception"]
        ):
            source_full = self._normalize(source_text).rstrip(".!? ")
            claim_full = self._normalize(fact).rstrip(".!? ")
            verdict = (
                "NO_CONFLICT"
                if source_full == claim_full
                else "UNKNOWN"
            )

        else:
            verdict = "UNKNOWN"

        return {
            "verdict": verdict,
            "source_features": source,
            "claim_features": claim,
        }
