"""X/Twitter gatherer using TinyFish for authenticated browser automation"""
import json
from datetime import datetime
from typing import AsyncIterator

import httpx

from ..core.models import Commitment, Source
from ..core.config import settings
from .base import BaseGatherer


class XGatherer(BaseGatherer):
    """Gather commitments from X (Twitter) DMs and Bookmarks via TinyFish"""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.tinyfish_api_key
        self.base_url = "https://agent.tinyfish.ai/v1/automation"
    
    @property
    def source(self) -> Source:
        return Source.X_DM
    
    async def test_connection(self) -> bool:
        """Test if TinyFish API is accessible"""
        if not self.api_key:
            return False
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.base_url.replace('/automation', '')}/health",
                    headers={"X-API-Key": self.api_key},
                    timeout=10
                )
                return resp.status_code == 200
            except:
                return False
    
    async def gather(self) -> AsyncIterator[Commitment]:
        """Gather commitments from X DMs"""
        async for c in self.gather_dms():
            yield c
        async for c in self.gather_bookmarks():
            yield c
    
    async def gather_dms(self) -> AsyncIterator[Commitment]:
        """Gather commitments from X DMs"""
        if not self.api_key:
            return
        
        goal = """You are logged into X (Twitter).
        
Go to your Direct Messages (DMs).
Look through recent conversations for:
- Messages where you promised to do something
- Messages where someone asked you for something and you haven't responded
- Any commitments, deadlines, or todo items mentioned

For each commitment found, return JSON:
{
    "text": "original message text",
    "task": "what was promised or asked",
    "deadline": "YYYY-MM-DD or null",
    "priority": 0-3,
    "from_user": "username you're talking to",
    "url": "link to DM if available"
}

Return a JSON array of commitments found."""
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/run-sse",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "url": "https://x.com/messages",
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
                                            commitments_data = json.loads(result)
                                        except:
                                            commitments_data = []
                                    else:
                                        commitments_data = result if isinstance(result, list) else []
                                    
                                    for item in commitments_data:
                                        yield Commitment(
                                            source=Source.X_DM,
                                            text=item.get("text", ""),
                                            extracted_task=item.get("task", ""),
                                            platform_id=f"x-dm-{item.get('from_user', 'unknown')}",
                                            platform_url=item.get("url", "https://x.com/messages"),
                                            created_at=datetime.now(),
                                            deadline=self._parse_deadline(item.get("deadline")),
                                            priority=item.get("priority", 0),
                                            raw_data=item
                                        )
                            except json.JSONDecodeError:
                                continue
    
    async def gather_bookmarks(self) -> AsyncIterator[Commitment]:
        """Gather from X bookmarks"""
        if not self.api_key:
            return
        
        goal = """You are logged into X (Twitter).
        
Go to your Bookmarks.
For each bookmarked tweet, determine:
- Is this something you need to read/review?
- Is this something you need to act on?
- Is this a resource to save for later?

For items that need action, return JSON:
{
    "text": "tweet text",
    "task": "what action is needed",
    "priority": 0-3,
    "author": "tweet author",
    "url": "link to tweet"
}

Return a JSON array of actionable bookmarks."""
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/run-sse",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "url": "https://x.com/i/bookmarks",
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
                                            bookmarks_data = json.loads(result)
                                        except:
                                            bookmarks_data = []
                                    else:
                                        bookmarks_data = result if isinstance(result, list) else []
                                    
                                    for item in bookmarks_data:
                                        yield Commitment(
                                            source=Source.X_BOOKMARK,
                                            text=item.get("text", ""),
                                            extracted_task=item.get("task", "Review bookmark"),
                                            platform_id=f"x-bm-{item.get('author', 'unknown')}",
                                            platform_url=item.get("url", "https://x.com"),
                                            created_at=datetime.now(),
                                            deadline=None,
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