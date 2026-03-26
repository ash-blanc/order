"""GitHub gatherer using GitHub API"""
from datetime import datetime
from typing import AsyncIterator

import httpx

from ..core.models import Commitment, Source
from ..core.config import settings
from .base import BaseGatherer


class GitHubGatherer(BaseGatherer):
    """Gather commitments from GitHub issues, PRs, discussions"""
    
    def __init__(self, token: str | None = None, repos: list[str] | None = None):
        self.token = token or settings.github_token
        self.repos = repos or []  # Format: ["owner/repo"]
        self.base_url = "https://api.github.com"
    
    @property
    def source(self) -> Source:
        return Source.GITHUB
    
    async def test_connection(self) -> bool:
        """Test if GitHub API is accessible"""
        if not self.token:
            return False
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.base_url}/user",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=10
                )
                return resp.status_code == 200
            except:
                return False
    
    async def gather(self) -> AsyncIterator[Commitment]:
        """Gather commitments from GitHub"""
        if not self.token:
            return
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            # Get issues assigned to user
            async for item in self._gather_issues(client, headers):
                yield item
            
            # Get PRs awaiting review
            async for item in self._gather_prs(client, headers):
                yield item
    
    async def _gather_issues(self, client: httpx.AsyncClient, headers: dict) -> AsyncIterator[Commitment]:
        """Gather issues assigned to user"""
        # Get user's login first
        user_resp = await client.get(f"{self.base_url}/user", headers=headers)
        if user_resp.status_code != 200:
            return
        username = user_resp.json().get("login", "")
        
        # Search for issues assigned to user
        query = f"assignee:{username} is:open"
        resp = await client.get(
            f"{self.base_url}/search/issues",
            params={"q": query},
            headers=headers
        )
        
        if resp.status_code != 200:
            return
        
        data = resp.json()
        for item in data.get("items", []):
            yield Commitment(
                source=Source.GITHUB,
                text=item.get("title", ""),
                extracted_task=f"Resolve: {item.get('title', 'GitHub issue')}",
                platform_id=str(item.get("id", "")),
                platform_url=item.get("html_url", ""),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                deadline=None,
                priority=2 if "urgent" in item.get("title", "").lower() else 1,
                raw_data={"type": "issue", "number": item.get("number"), "repo": item.get("repository_url")}
            )
    
    async def _gather_prs(self, client: httpx.AsyncClient, headers: dict) -> AsyncIterator[Commitment]:
        """Gather PRs awaiting user's review"""
        user_resp = await client.get(f"{self.base_url}/user", headers=headers)
        if user_resp.status_code != 200:
            return
        username = user_resp.json().get("login", "")
        
        # Search for PRs where user is requested reviewer
        query = f"review-requested:{username} is:open is:pr"
        resp = await client.get(
            f"{self.base_url}/search/issues",
            params={"q": query},
            headers=headers
        )
        
        if resp.status_code != 200:
            return
        
        data = resp.json()
        for item in data.get("items", []):
            yield Commitment(
                source=Source.GITHUB,
                text=f"PR Review: {item.get('title', '')}",
                extracted_task=f"Review PR: {item.get('title', 'GitHub PR')}",
                platform_id=str(item.get("id", "")),
                platform_url=item.get("html_url", ""),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                deadline=None,
                priority=2,  # PR reviews are usually higher priority
                raw_data={"type": "pr", "number": item.get("number")}
            )
    
    async def gather_repo(self, owner: str, repo: str) -> AsyncIterator[Commitment]:
        """Gather from a specific repository"""
        async for commitment in self.gather():
            if repo in commitment.platform_url:
                yield commitment