class ModalityDecisionResolver:
    """Conservatively combine modality and conflict verdicts."""

    VALID_MODALITY = {
        "PASS",
        "REJECT",
        "NOT_APPLICABLE",
    }

    VALID_CONFLICT = {
        "CONFLICT",
        "NO_CONFLICT",
        "UNKNOWN",
    }

    EXPLICIT_REJECTION_REASONS = {
        "mandatory_overstatement",
        "negation_conflict",
    }

    def resolve(
        self,
        modality_result,
        conflict_result,
        source_features=None,
        fact_features=None,
    ):
        if not isinstance(modality_result, dict):
            raise TypeError("modality_result must be a dict")

        if not isinstance(conflict_result, dict):
            raise TypeError("conflict_result must be a dict")

        modality_verdict = modality_result.get("verdict")
        modality_reason = modality_result.get("reason")
        conflict_verdict = conflict_result.get("verdict")

        if modality_verdict not in self.VALID_MODALITY:
            raise ValueError("Invalid modality verdict")

        if not isinstance(modality_reason, str):
            raise ValueError("Invalid modality reason")

        if not modality_reason.strip():
            raise ValueError("Empty modality reason")

        if conflict_verdict not in self.VALID_CONFLICT:
            raise ValueError("Invalid conflict verdict")

        if conflict_verdict == "CONFLICT":
            verdict = "REJECT"
            reason = "explicit_conflict_detected"

        elif (
            modality_verdict == "REJECT"
            and modality_reason in self.EXPLICIT_REJECTION_REASONS
        ):
            verdict = "REJECT"
            reason = modality_reason

        elif (
            modality_verdict == "REJECT"
            and modality_reason == "no_matching_source_statement"
        ):
            verdict = "NOT_APPLICABLE"
            reason = "insufficient_evidence_for_explicit_conflict"

        else:
            verdict = modality_verdict
            reason = modality_reason

        if source_features is not None or fact_features is not None:
            if not isinstance(source_features, dict):
                raise TypeError("source_features must be a dict")

            if not isinstance(fact_features, dict):
                raise TypeError("fact_features must be a dict")

            source_modality = source_features.get("modality")
            fact_modality = fact_features.get("modality")

            if (
                type(source_features.get("negated")) is bool
                and type(fact_features.get("negated")) is bool
                and source_features["negated"] != fact_features["negated"]
            ):
                verdict = "REJECT"
                reason = "negation_conflict"

            elif (
                source_modality == "SHOULD"
                and fact_modality == "MUST"
            ):
                verdict = "REJECT"
                reason = "mandatory_overstatement"

            elif (
                source_features.get("conditional") is True
                and fact_features.get("conditional") is False
            ):
                verdict = "REJECT"
                reason = "missing_source_condition"

        return {
            "verdict": verdict,
            "reason": reason,
            "modality_verdict": modality_verdict,
            "conflict_verdict": conflict_verdict,
        }
