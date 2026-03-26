"""Reduce mode: Filter noise, show what matters"""
from ..core.models import Commitment, ReduceResult, CommitmentStatus
from ..core.store import store
from ..core.config import settings
from ..synthesis.llm import filter_commitments, prioritize_commitments


class ReduceMode:
    """Filter and prioritize commitments"""
    
    async def reduce(self) -> ReduceResult:
        """Reduce pending commitments"""
        pending = await store.get_pending()
        
        if not pending:
            return ReduceResult(
                total_before=0,
                total_after=0,
                ignored=[],
                kept=[]
            )
        
        # Filter noise
        filtered = await filter_commitments(pending)
        
        # Prioritize
        prioritized = await prioritize_commitments(filtered)
        
        # Determine ignored
        kept_ids = {c.id for c in prioritized}
        ignored = [c for c in pending if c.id not in kept_ids]
        
        # Mark ignored
        for c in ignored:
            await store.update_status(c.id, CommitmentStatus.IGNORED)
        
        return ReduceResult(
            total_before=len(pending),
            total_after=len(prioritized),
            ignored=ignored,
            kept=prioritized
        )
    
    async def get_stats(self) -> dict:
        """Get current statistics"""
        counts = await store.count_by_status()
        return {
            "pending": counts.get("pending", 0),
            "done": counts.get("done", 0),
            "ignored": counts.get("ignored", 0),
            "expired": counts.get("expired", 0)
        }


# Singleton instance
reduce_mode = ReduceMode()