from __future__ import annotations

import re

from app.clients.openai_client import OpenAIExtractor
from app.schemas import LeadExtraction


ROLE_PATTERN = re.compile(
    r"\b(ceo|cto|cfo|coo|vp|head|director|manager|founder|owner|lead|engineer)\b",
    re.IGNORECASE,
)
COMPANY_PATTERN = re.compile(r"\bat\s+([A-Z][A-Za-z0-9&.\- ]*?)(?=[,.]| interested| wants| looking for|$)")
NAME_PATTERN = re.compile(
    r"\b(?:met|spoke with|talked to|contacted)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?=,|\s)",
    re.IGNORECASE,
)


class Extractor:
    def __init__(self, ai_extractor: OpenAIExtractor) -> None:
        self._ai_extractor = ai_extractor

    def extract(self, message_text: str) -> LeadExtraction:
        if self._ai_extractor.enabled:
            try:
                ai_result = self._ai_extractor.extract_lead(message_text)
                if ai_result:
                    return LeadExtraction.model_validate(ai_result)
            except Exception:
                # Fall back to deterministic extraction.
                pass

        return self._rule_extract(message_text)

    def _rule_extract(self, message_text: str) -> LeadExtraction:
        lower = message_text.lower()
        name_match = NAME_PATTERN.search(message_text)
        role_match = ROLE_PATTERN.search(message_text)
        company_match = COMPANY_PATTERN.search(message_text)

        intent = None
        if "interested" in lower:
            intent = message_text[lower.index("interested") :].strip(". ")
        elif "wants" in lower:
            intent = message_text[lower.index("wants") :].strip(". ")
        elif "looking for" in lower:
            intent = message_text[lower.index("looking for") :].strip(". ")

        return LeadExtraction(
            name=name_match.group(1) if name_match else None,
            role=role_match.group(1).upper() if role_match else None,
            company=company_match.group(1).strip() if company_match else None,
            intent=intent,
            raw_summary=message_text[:240],
        )
