# Slack Lead Agent MVP

This repo contains a simple agent that mirrors your manual workflow:

`Slack message -> extract -> validate -> classify -> decide -> act -> log`

The goal is to keep the MVP small and practical:

- `Slack` delivers the message
- `OpenAI` optionally improves extraction
- `Notion` stores qualified leads
- `Slack` sends alerts for high-priority leads
- `SQLite` logs every processed decision for debugging and evaluation

## Architecture

### Core flow

1. `Ingestion`: receive a Slack event through `POST /slack/events`
2. `Extraction`: pull `name`, `role`, `company`, and `intent`
3. `Validation`: determine if the message is lead-like and assign confidence
4. `Classification`: score the lead as `high`, `medium`, or `low`
5. `Planning`: choose actions based on score
6. `Execution`: call Notion and Slack
7. `Logging`: persist the full decision trail in SQLite

### Current design choices

- Deterministic fallback exists even if OpenAI is unavailable
- Duplicate events are blocked with an idempotent `event_id` check
- External tools are separated from the agent logic
- The database doubles as an observability/debugging layer

## Project structure

```text
app/
  clients/       # Slack, Notion, OpenAI wrappers
  services/      # Extract, validate, classify, plan, execute
  config.py      # Environment settings
  db.py          # SQLite persistence
  main.py        # FastAPI entrypoint
  schemas.py     # Typed models
```

## Setup

1. Create and activate a virtual environment
2. Install dependencies
3. Copy `.env.example` to `.env`
4. Fill in the API credentials you want to use
5. Start the server

Example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
uvicorn app.main:app --reload
```

## Environment variables

```env
APP_ENV=development
DATABASE_PATH=agent.db
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
SLACK_SIGNING_SECRET=
SLACK_BOT_TOKEN=
SLACK_ALERT_CHANNEL=
NOTION_API_KEY=
NOTION_DATABASE_ID=
```

## Example

Input Slack message:

```text
Met Rahul, CTO at FinEdge. Interested in automation.
```

Likely output:

- Extraction:
  - `Rahul`
  - `CTO`
  - `FinEdge`
  - `Interested in automation`
- Classification: `high`
- Plan:
  - `create_notion_page`
  - `send_slack_alert`

## Slack notes

For Slack Events API:

- point Slack to `POST /slack/events`
- Slack may first send a `url_verification` request, which this app handles
- if `SLACK_SIGNING_SECRET` is set, signature verification is enforced

## Notion notes

This MVP assumes your Notion database has properties named:

- `Name` as a title property
- `Company` as rich text
- `Role` as rich text
- `Intent` as rich text
- `Lead Score` as a select property

If your property names differ, update [`app/clients/notion_client.py`]
## Persistence

Every processed event is saved into SQLite in the `processed_messages` table with:

- raw message
- extracted fields
- validation result
- classification result
- planned actions
- execution results

This gives you a simple evaluation and debugging dataset from day one.

## Next upgrades

- Add a queue and retry handling
- Move from SQLite to Postgres
- Add a human review path for borderline messages
- Replace hardcoded tools with MCP-style tool registration
- Add test coverage and end-to-end fixtures
