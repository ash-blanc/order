"""Executor mode: Agents handle tasks"""
from typing import List
from litellm import acompletion

from ..core.models import Commitment, CommitmentStatus
from ..core.store import store
from ..core.config import settings


class ExecutorMode:
    """Agents that execute tasks for you"""
    
    async def handle_subscriptions(self) -> dict:
        """Find and manage subscriptions"""
        # This would use TinyFish to log into accounts
        # For MVP, return mock data
        return {
            "status": "ready",
            "message": "Subscription handler ready. Connect your accounts to begin."
        }
    
    async def handle_email(self) -> dict:
        """Process email inbox"""
        # Would use TinyFish for Gmail
        return {
            "status": "ready",
            "message": "Email handler ready. Connect Gmail to begin."
        }
    
    async def draft_response(self, commitment: Commitment) -> str:
        """Draft a response for a commitment"""
        prompt = f"""Draft a brief, professional response for this commitment:

Task: {commitment.extracted_task}
Source: {commitment.source.value}
Original text: {commitment.text}

Draft a response that acknowledges and handles this commitment."""
        
        response = await acompletion(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    async def propose_action(self, commitment: Commitment) -> dict:
        """Propose an action for a commitment"""
        prompt = f"""What action should be taken for this commitment?

Task: {commitment.extracted_task}
Source: {commitment.source.value}
Original text: {commitment.text}

Return JSON:
{{
    "action": "mark_done/snooze/delegate/respond",
    "details": "explanation",
    "suggested_response": "if respond, the response text"
}}"""
        
        response = await acompletion(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"action": "mark_done", "details": "Unable to determine action"}
    
    async def commit(self, commitment_id: str, action: str) -> Commitment:
        """Execute an action on a commitment"""
        # Get commitment
        all = await store.get_all()
        commitment = next((c for c in all if c.id == commitment_id), None)
        
        if not commitment:
            raise ValueError("Commitment not found")
        
        # Update status based on action
        if action == "mark_done":
            await store.update_status(commitment_id, CommitmentStatus.DONE)
        elif action == "snooze":
            # Keep pending
            pass
        elif action == "delegate":
            await store.update_status(commitment_id, CommitmentStatus.IGNORED)
        
        return commitment


# Singleton instance
executor = ExecutorMode()