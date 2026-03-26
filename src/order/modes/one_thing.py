"""One-Thing mode: Radical simplicity"""
from ..core.models import Commitment, CommitmentStatus
from ..core.store import store
from ..synthesis.llm import pick_one_thing, explain_why


class OneThingMode:
    """Radical simplicity: show only ONE commitment"""
    
    async def get_one_thing(self) -> Commitment | None:
        """Get the ONE thing to focus on"""
        pending = await store.get_pending()
        
        if not pending:
            return None
        
        return await pick_one_thing(pending)
    
    async def mark_done(self, commitment_id: str):
        """Mark commitment as done"""
        await store.update_status(commitment_id, CommitmentStatus.DONE)
    
    async def skip(self, commitment_id: str):
        """Mark commitment as ignored"""
        await store.update_status(commitment_id, CommitmentStatus.IGNORED)
    
    async def get_next(self) -> Commitment | None:
        """Get next ONE thing after current is done"""
        return await self.get_one_thing()
    
    async def explain(self, commitment: Commitment) -> str:
        """Explain why this was chosen"""
        return await explain_why(commitment)


# Singleton instance
one_thing = OneThingMode()