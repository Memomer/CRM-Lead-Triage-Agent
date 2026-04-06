from __future__ import annotations

from app.schemas import LeadExtraction, ValidationResult


class Validator:
    def validate(self, extraction: LeadExtraction, raw_message: str) -> ValidationResult:
        reasons: list[str] = []
        confidence = 0.2

        if extraction.name:
            confidence += 0.2
            reasons.append("Detected a person name.")
        if extraction.role:
            confidence += 0.2
            reasons.append("Detected a job role.")
        if extraction.company:
            confidence += 0.2
            reasons.append("Detected a company.")
        if extraction.intent:
            confidence += 0.2
            reasons.append("Detected intent or buying signal.")

        lead_keywords = ["met", "interested", "looking for", "automation", "follow up", "intro"]
        if any(keyword in raw_message.lower() for keyword in lead_keywords):
            confidence += 0.1
            reasons.append("Message contains lead-like language.")

        is_valid = confidence >= 0.5 and bool(extraction.company or extraction.role or extraction.intent)
        if not is_valid:
            reasons.append("Not enough evidence to treat this as a lead.")

        return ValidationResult(
            is_valid=is_valid,
            confidence=min(confidence, 1.0),
            reasons=reasons,
        )
