"""Just-in-Time mode: Ask and receive, no storage"""
from datetime import datetime
from typing import List
from litellm import acompletion

from ..core.models import Commitment, Source
from ..core.store import store
from ..core.config import settings


class JustInTimeMode:
    """No inbox maintenance. Just ask, get answer."""
    
    async def search(self, query: str) -> List[Commitment]:
        """Search commitments by query"""
        all_commitments = await store.get_all()
        
        # Use LLM to match query
        prompt = f"""You are searching through commitments.

Query: {query}

Commitments:
{self._format_commitments(all_commitments)}

Return JSON array of indices that match the query:
{{"matches": [0, 1, 3, ...]}}"""
        
        response = await acompletion(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            indices = result.get("matches", [])
            return [all_commitments[i] for i in indices if i < len(all_commitments)]
        except:
            return []
    
    async def what_did_i_promise(self, timeframe: str = "this week") -> List[Commitment]:
        """Find promises made in timeframe"""
        pending = await store.get_pending()
        
        # Filter by deadline if exists
        now = datetime.now()
        results = []
        
        for c in pending:
            if c.deadline:
                # Has deadline
                if timeframe == "this week":
                    if c.deadline <= now.replace(day=now.day + 7):
                        results.append(c)
                elif timeframe == "today":
                    if c.deadline.date() == now.date():
                        results.append(c)
                else:
                    results.append(c)
            else:
                # No deadline, include
                results.append(c)
        
        return results
    
    async def what_about_x(self, topic: str) -> List[Commitment]:
        """Find commitments related to topic"""
        all = await store.get_all()
        
        prompt = f"""Find commitments related to: {topic}

Commitments:
{self._format_commitments(all)}

Return JSON array of matching indices:
{{"matches": [0, 1, ...]}}"""
        
        response = await acompletion(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            indices = result.get("matches", [])
            return [all[i] for i in indices if i < len(all)]
        except:
            return []
    
    def _format_commitments(self, commitments: List[Commitment]) -> str:
        if not commitments:
            return "None"
        return "\n".join([
            f"{i}. [{c.source.value}] {c.extracted_task}"
            for i, c in enumerate(commitments[:20])
        ])


# Singleton instance
just_in_time = JustInTimeMode()