"""Gather mode: Pull from all sources"""
from typing import List
from ..core.models import Commitment, GatherResult, Source
from ..core.store import store
from ..gatherers import DiscordGatherer, GitHubGatherer, XGatherer, GmailGatherer


class GatherMode:
    """Gather commitments from all sources"""
    
    def __init__(self):
        self.gatherers = {
            Source.DISCORD: DiscordGatherer(),
            Source.GITHUB: GitHubGatherer(),
            Source.X_DM: XGatherer(),
            Source.GMAIL: GmailGatherer(),
        }
    
    async def gather_all(self) -> List[GatherResult]:
        """Gather from all sources"""
        results = []
        
        for source, gatherer in self.gatherers.items():
            if await gatherer.test_connection():
                result = await gatherer.run()
                results.append(result)
                
                # Store commitments
                if result.commitments:
                    await store.add_many(result.commitments)
        
        return results
    
    async def gather_source(self, source: Source) -> GatherResult:
        """Gather from specific source"""
        gatherer = self.gatherers.get(source)
        if gatherer and await gatherer.test_connection():
            result = await gatherer.run()
            if result.commitments:
                await store.add_many(result.commitments)
            return result
        
        return GatherResult(
            source=source,
            total_found=0,
            commitments=[],
            error="Gatherer not configured or unavailable"
        )
    
    async def test_connections(self) -> dict[str, bool]:
        """Test all connections"""
        results = {}
        for source, gatherer in self.gatherers.items():
            results[source.value] = await gatherer.test_connection()
        return results


# Singleton instance
gather = GatherMode()
