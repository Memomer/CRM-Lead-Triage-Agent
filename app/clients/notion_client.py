from __future__ import annotations

import json

import requests

from app.config import Settings
from app.schemas import LeadExtraction


class NotionClient:
    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.notion_api_key
        self._database_id = settings.notion_database_id

    def create_lead(self, extraction: LeadExtraction, raw_message: str, score: str) -> tuple[str, str]:
        if not self._api_key or not self._database_id:
            return "skipped", "Notion sync skipped because credentials are not configured."

        payload = {
            "parent": {"database_id": self._database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": extraction.name or "Unknown lead"}}]},
                "Company": {"rich_text": [{"text": {"content": extraction.company or "Unknown"}}]},
                "Role": {"rich_text": [{"text": {"content": extraction.role or "Unknown"}}]},
                "Intent": {"rich_text": [{"text": {"content": extraction.intent or "Unknown"}}]},
                "Lead Score": {"select": {"name": score.title()}},
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": raw_message[:1800]}}]
                    },
                }
            ],
        }

        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            },
            data=json.dumps(payload),
            timeout=15,
        )
        if response.ok:
            return "success", "Notion page created."
        return "failed", f"Notion request failed: {response.text[:500]}"
