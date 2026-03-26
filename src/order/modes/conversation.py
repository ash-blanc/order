"""Conversation mode: Thinking partner"""
from typing import AsyncIterator

from litellm import acompletion

from ..core.models import Commitment
from ..core.store import store
from ..core.config import settings
from ..synthesis.llm import pick_one_thing


class ConversationMode:
    """Chat-based thinking partner"""
    
    def __init__(self):
        self.history: list[dict] = []
    
    async def chat(self, message: str) -> str:
        """Handle conversation message"""
        # Add user message
        self.history.append({"role": "user", "content": message})
        
        # Get context
        pending = await store.get_pending()
        context = self._build_context(pending)
        
        # Build system prompt
        system = f"""You are a helpful thinking partner. Your goal is to help the user find clarity and focus.

Current context:
{context}

Guidelines:
- Be concise and warm
- Ask clarifying questions to help them think
- Don't overwhelm with information
- Help them find ONE thing to focus on
- If they seem overwhelmed, help them reduce and prioritize
- If they're stuck, ask what's weighing on them"""
        
        # Call LLM
        response = await acompletion(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system},
                *self.history
            ]
        )
        
        assistant_message = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def _build_context(self, commitments: list[Commitment]) -> str:
        """Build context string"""
        if not commitments:
            return "No pending commitments found."
        
        lines = [f"Pending commitments: {len(commitments)}"]
        for c in commitments[:5]:
            lines.append(f"- {c.extracted_task} ({c.source.value})")
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset conversation"""
        self.history = []


# Singleton instance
conversation = ConversationMode()