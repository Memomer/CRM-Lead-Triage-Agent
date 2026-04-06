from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.clients.notion_client import NotionClient
from app.clients.openai_client import OpenAIExtractor
from app.clients.slack_client import SlackClient
from app.config import get_settings
from app.db import Database
from app.schemas import AgentResponse, SlackWebhookPayload
from app.services.classifier import Classifier
from app.services.executor import Executor
from app.services.extractor import Extractor
from app.services.pipeline import AgentPipeline
from app.services.planner import Planner
from app.services.validator import Validator

settings = get_settings()
db = Database(settings.database_path)
slack_client = SlackClient(settings)
notion_client = NotionClient(settings)
ai_extractor = OpenAIExtractor(settings)

pipeline = AgentPipeline(
    db=db,
    extractor=Extractor(ai_extractor),
    validator=Validator(),
    classifier=Classifier(),
    planner=Planner(),
    executor=Executor(notion_client, slack_client),
)

app = FastAPI(title="Slack Lead Agent", version="0.1.0")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/slack/events", response_model=None)
async def slack_events(
    request: Request,
    x_slack_signature: str | None = Header(default=None),
    x_slack_request_timestamp: str | None = Header(default=None),
) -> JSONResponse | AgentResponse:
    raw_body = await request.body()
    headers = {}
    if x_slack_signature:
        headers["x-slack-signature"] = x_slack_signature
    if x_slack_request_timestamp:
        headers["x-slack-request-timestamp"] = x_slack_request_timestamp

    if not slack_client.verify_signature(headers, raw_body):
        raise HTTPException(status_code=401, detail="Invalid Slack signature.")

    payload = SlackWebhookPayload.model_validate_json(raw_body)
    if payload.type == "url_verification" and payload.challenge:
        return JSONResponse(content={"challenge": payload.challenge})

    return pipeline.process_slack_message(payload.event_id, payload.event)
