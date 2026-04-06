from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SlackWebhookPayload(BaseModel):
    event_id: str | None = None
    type: str | None = None
    challenge: str | None = None
    event: dict[str, Any] = Field(default_factory=dict)


class LeadExtraction(BaseModel):
    name: str | None = None
    role: str | None = None
    company: str | None = None
    intent: str | None = None
    raw_summary: str | None = None


class ValidationResult(BaseModel):
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    lead_score: Literal["high", "medium", "low"]
    reasons: list[str] = Field(default_factory=list)


class PlanResult(BaseModel):
    actions: list[str] = Field(default_factory=list)


class ToolExecutionResult(BaseModel):
    tool: str
    status: Literal["success", "skipped", "failed"]
    detail: str


class ProcessedLeadRecord(BaseModel):
    event_id: str
    source: str
    raw_message: str
    extraction: LeadExtraction
    validation: ValidationResult
    classification: ClassificationResult
    plan: PlanResult
    execution_results: list[ToolExecutionResult]


class AgentResponse(BaseModel):
    status: Literal["processed", "duplicate", "ignored"]
    record: ProcessedLeadRecord | None = None
    detail: str | None = None
