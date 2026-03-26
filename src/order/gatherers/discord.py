"""Discord gatherer using TinyFish for authenticated browser automation"""
import json
from datetime import datetime
from typing import AsyncIterator

import httpx

from ..core.models import Commitment, Source, GatherResult
from ..core.config import settings
from .base import BaseGatherer


class DiscordGatherer(BaseGatherer):
    """Gather commitments from Discord via TinyFish authenticated browser"""
    
    def __init__(self, api_key: str | None = None, server_ids: list[str] | None = None):
        self.api_key = api_key or settings.tinyfish_api_key
        self.server_ids = server_ids or []
        self.base_url = "https://agent.tinyfish.ai/v1/automation"
    
    @property
    def source(self) -> Source:
        return Source.DISCORD
    
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
        """Gather commitments from Discord servers"""
        if not self.api_key:
            return
        
        goal = """You are logged into Discord. 
        
Find all messages where I (@me) mentioned or promised to do something.
Look for:
- Messages where someone asked me to do something and I said yes/agreed
- Messages where I said "I'll", "I will", "let me", "I can", "I should"
- Messages with @mentions of me that require action
- Any deadlines or time commitments mentioned

For each commitment found, return JSON:
{
    "text": "original message text",
    "task": "what was promised",
    "deadline": "YYYY-MM-DD or null",
    "priority": 0-3,
    "channel": "channel name",
    "server": "server name",
    "url": "link to message"
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
                    "url": "https://discord.com/channels/@me",
                    "goal": goal
                }
            ) as response:
                buffer = ""
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data:
                            try:
                                event = json.loads(data)
                                # Check for result in COMPLETED event
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
                                            source=Source.DISCORD,
                                            text=item.get("text", ""),
                                            extracted_task=item.get("task", ""),
                                            platform_id=f"discord-{item.get('channel', 'unknown')}",
                                            platform_url=item.get("url", "https://discord.com"),
                                            created_at=datetime.now(),
                                            deadline=self._parse_deadline(item.get("deadline")),
                                            priority=item.get("priority", 0),
                                            raw_data=item
                                        )
                            except json.JSONDecodeError:
                                continue
    
    def _parse_deadline(self, deadline_str: str | None) -> datetime | None:
        """Parse deadline string to datetime"""
        if not deadline_str or deadline_str == "null":
            return None
        try:
            return datetime.strptime(deadline_str, "%Y-%m-%d")
        except:
            return None
    
    async def gather_server(self, server_id: str) -> AsyncIterator[Commitment]:
        """Gather from a specific Discord server"""
        async for commitment in self.gather():
            if server_id in commitment.platform_id or not self.server_ids:
                yield commitment