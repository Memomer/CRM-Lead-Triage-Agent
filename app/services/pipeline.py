from __future__ import annotations

import hashlib
import json

from app.db import Database
from app.schemas import AgentResponse, ProcessedLeadRecord
from app.services.classifier import Classifier
from app.services.executor import Executor
from app.services.extractor import Extractor
from app.services.planner import Planner
from app.services.validator import Validator


class AgentPipeline:
    def __init__(
        self,
        db: Database,
        extractor: Extractor,
        validator: Validator,
        classifier: Classifier,
        planner: Planner,
        executor: Executor,
    ) -> None:
        self._db = db
        self._extractor = extractor
        self._validator = validator
        self._classifier = classifier
        self._planner = planner
        self._executor = executor

    def process_slack_message(self, event_id: str | None, event: dict) -> AgentResponse:
        raw_message = event.get("text", "").strip()
        normalized_event_id = event_id or self._fallback_event_id(event)

        if self._db.has_event(normalized_event_id):
            return AgentResponse(status="duplicate", detail="Event already processed.")

        extraction = self._extractor.extract(raw_message)
        validation = self._validator.validate(extraction, raw_message)
        classification = self._classifier.classify(extraction) if validation.is_valid else self._classifier.classify(extraction)
        plan = self._planner.plan(validation, classification)
        execution_results = self._executor.execute(
            plan.actions,
            extraction,
            raw_message,
            classification.lead_score,
        )

        record = ProcessedLeadRecord(
            event_id=normalized_event_id,
            source="slack",
            raw_message=raw_message,
            extraction=extraction,
            validation=validation,
            classification=classification,
            plan=plan,
            execution_results=execution_results,
        )
        self._db.save_record(record)

        if not validation.is_valid and not plan.actions:
            return AgentResponse(status="ignored", record=record, detail="Message did not qualify as a lead.")
        return AgentResponse(status="processed", record=record)

    def _fallback_event_id(self, event: dict) -> str:
        stable_payload = json.dumps(event, sort_keys=True).encode("utf-8")
        return hashlib.sha256(stable_payload).hexdigest()
