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

    def resolve(self, modality_result, conflict_result):
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

        return {
            "verdict": verdict,
            "reason": reason,
            "modality_verdict": modality_verdict,
            "conflict_verdict": conflict_verdict,
        }
