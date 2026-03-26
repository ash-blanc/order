"""Gmail gatherer using Gmail API"""
from datetime import datetime
from typing import AsyncIterator
import json

import httpx

from ..core.models import Commitment, Source
from ..core.config import settings
from .base import BaseGatherer


class GmailGatherer(BaseGatherer):
    """Gather commitments from Gmail"""
    
    def __init__(self, api_key: str | None = None):
        # For now, use TinyFish to scrape Gmail
        # In production, would use Gmail API
        self.api_key = api_key or settings.tinyfish_api_key
        self.base_url = "https://agent.tinyfish.ai/v1/automation"
    
    @property
    def source(self) -> Source:
        return Source.GMAIL
    
    async def test_connection(self) -> bool:
        """Test if TinyFish API is accessible"""
        if not self.api_key:
            return False
        return True
    
    async def gather(self) -> AsyncIterator[Commitment]:
        """Gather commitments from Gmail"""
        if not self.api_key:
            return
        
        goal = """You are logged into Gmail.
        
Go through your inbox and find emails that:
- Ask you to do something
- Require a response
- Have deadlines mentioned
- Are from people waiting on you

For each actionable email, return JSON:
{
    "text": "email subject or first line",
    "task": "what action is needed",
    "from": "sender email or name",
    "deadline": "YYYY-MM-DD or null",
    "priority": 0-3,
    "url": "link to email if available"
}

Return a JSON array of actionable emails."""
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/run-sse",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "url": "https://mail.google.com",
                    "goal": goal
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data:
                            try:
                                event = json.loads(data)
                                if event.get("type") == "COMPLETED":
                                    result = event.get("result", {})
                                    if isinstance(result, str):
                                        try:
                                            emails_data = json.loads(result)
                                        except:
                                            emails_data = []
                                    else:
                                        emails_data = result if isinstance(result, list) else []
                                    
                                    for item in emails_data:
                                        yield Commitment(
                                            source=Source.GMAIL,
                                            text=item.get("text", ""),
                                            extracted_task=item.get("task", ""),
                                            platform_id=f"gmail-{item.get('from', 'unknown')}",
                                            platform_url=item.get("url", "https://mail.google.com"),
                                            created_at=datetime.now(),
                                            deadline=self._parse_deadline(item.get("deadline")),
                                            priority=item.get("priority", 0),
                                            raw_data=item
                                        )
                            except json.JSONDecodeError:
                                continue
    
    def _parse_deadline(self, deadline_str: str | None) -> datetime | None:
        if not deadline_str or deadline_str == "null":
            return None
        try:
            return datetime.strptime(deadline_str, "%Y-%m-%d")
        except:
            return None
