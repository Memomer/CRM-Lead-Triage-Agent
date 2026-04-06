from __future__ import annotations

from app.schemas import ClassificationResult, PlanResult, ValidationResult


class Planner:
    def plan(self, validation: ValidationResult, classification: ClassificationResult) -> PlanResult:
        if not validation.is_valid:
            return PlanResult(actions=[])

        if classification.lead_score == "high":
            return PlanResult(actions=["create_notion_page", "send_slack_alert"])
        if classification.lead_score == "medium":
            return PlanResult(actions=["create_notion_page"])
        return PlanResult(actions=[])
