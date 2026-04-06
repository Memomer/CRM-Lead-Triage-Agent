from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.schemas import ProcessedLeadRecord


class Database:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _initialize(self) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_messages (
                    event_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    raw_message TEXT NOT NULL,
                    extraction_json TEXT NOT NULL,
                    validation_json TEXT NOT NULL,
                    classification_json TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    execution_results_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def has_event(self, event_id: str) -> bool:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT event_id FROM processed_messages WHERE event_id = ?",
                (event_id,),
            ).fetchone()
        return row is not None

    def save_record(self, record: ProcessedLeadRecord) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO processed_messages (
                    event_id,
                    source,
                    raw_message,
                    extraction_json,
                    validation_json,
                    classification_json,
                    plan_json,
                    execution_results_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.event_id,
                    record.source,
                    record.raw_message,
                    json.dumps(record.extraction.model_dump()),
                    json.dumps(record.validation.model_dump()),
                    json.dumps(record.classification.model_dump()),
                    json.dumps(record.plan.model_dump()),
                    json.dumps([item.model_dump() for item in record.execution_results]),
                ),
            )
