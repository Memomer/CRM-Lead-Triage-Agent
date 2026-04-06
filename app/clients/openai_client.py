from __future__ import annotations

import json
from typing import Any

from app.config import Settings


class OpenAIExtractor:
    def __init__(self, settings: Settings) -> None:
        self._enabled = bool(settings.openai_api_key)
        self._model = settings.openai_model
        self._client = None
        if self._enabled:
            from openai import OpenAI

            self._client = OpenAI(api_key=settings.openai_api_key)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def extract_lead(self, message_text: str) -> dict[str, Any] | None:
        if not self._client:
            return None

        response = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Extract lead data from Slack messages. "
                                "Return strict JSON with keys: name, role, company, intent, raw_summary. "
                                "Use null when unknown."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": message_text}],
                },
            ],
        )

        text_output = "".join(
            item.text
            for output in getattr(response, "output", [])
            for item in getattr(output, "content", [])
            if getattr(item, "type", None) == "output_text"
        )
        if not text_output:
            return None
        return json.loads(text_output)
