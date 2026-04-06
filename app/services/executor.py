from __future__ import annotations

from app.clients.notion_client import NotionClient
from app.clients.slack_client import SlackClient
from app.schemas import LeadExtraction, ToolExecutionResult


class Executor:
    def __init__(self, notion_client: NotionClient, slack_client: SlackClient) -> None:
        self._notion_client = notion_client
        self._slack_client = slack_client

    def execute(self, actions: list[str], extraction: LeadExtraction, raw_message: str, score: str) -> list[ToolExecutionResult]:
        results: list[ToolExecutionResult] = []

        for action in actions:
            if action == "create_notion_page":
                status, detail = self._notion_client.create_lead(extraction, raw_message, score)
                results.append(ToolExecutionResult(tool=action, status=status, detail=detail))
            elif action == "send_slack_alert":
                alert_text = (
                    f"High-priority lead detected: {extraction.name or 'Unknown'}"
                    f" | {extraction.role or 'Unknown role'}"
                    f" | {extraction.company or 'Unknown company'}"
                    f" | {extraction.intent or 'No clear intent'}"
                )
                status, detail = self._slack_client.send_alert(alert_text)
                results.append(ToolExecutionResult(tool=action, status=status, detail=detail))
            else:
                results.append(
                    ToolExecutionResult(
                        tool=action,
                        status="failed",
                        detail="Unknown action requested by planner.",
                    )
                )

        return results
