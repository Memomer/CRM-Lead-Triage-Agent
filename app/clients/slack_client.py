from __future__ import annotations

import hashlib
import hmac
import json
import time

import requests

from app.config import Settings


class SlackClient:
    def __init__(self, settings: Settings) -> None:
        self._bot_token = settings.slack_bot_token
        self._signing_secret = settings.slack_signing_secret
        self._alert_channel = settings.slack_alert_channel

    def verify_signature(self, headers: dict[str, str], raw_body: bytes) -> bool:
        if not self._signing_secret:
            return True

        timestamp = headers.get("x-slack-request-timestamp", "")
        slack_signature = headers.get("x-slack-signature", "")

        if not timestamp or not slack_signature:
            return False

        # Reject stale requests to reduce replay risk.
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False

        basestring = f"v0:{timestamp}:{raw_body.decode('utf-8')}".encode("utf-8")
        computed = "v0=" + hmac.new(
            self._signing_secret.encode("utf-8"),
            basestring,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed, slack_signature)

    def send_alert(self, text: str) -> tuple[str, str]:
        if not self._bot_token or not self._alert_channel:
            return "skipped", "Slack alert skipped because credentials are not configured."

        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {self._bot_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps({"channel": self._alert_channel, "text": text}),
            timeout=15,
        )
        payload = response.json()
        if response.ok and payload.get("ok"):
            return "success", "Slack alert sent."
        return "failed", f"Slack alert failed: {payload}"
