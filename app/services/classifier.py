from __future__ import annotations

from app.schemas import ClassificationResult, LeadExtraction


HIGH_VALUE_ROLES = {"CEO", "CTO", "CFO", "COO", "FOUNDER", "OWNER", "VP", "HEAD", "DIRECTOR"}


class Classifier:
    def classify(self, extraction: LeadExtraction) -> ClassificationResult:
        score = 0
        reasons: list[str] = []

        if extraction.role in HIGH_VALUE_ROLES:
            score += 2
            reasons.append("Senior decision-maker role detected.")
        elif extraction.role:
            score += 1
            reasons.append("Relevant business role detected.")

        if extraction.intent:
            score += 2
            reasons.append("Explicit interest or intent detected.")

        if extraction.company:
            score += 1
            reasons.append("Company identified.")

        if score >= 4:
            lead_score = "high"
        elif score >= 2:
            lead_score = "medium"
        else:
            lead_score = "low"

        return ClassificationResult(lead_score=lead_score, reasons=reasons)
