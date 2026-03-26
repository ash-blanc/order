"""AI synthesis using LiteLLM"""
import json
from typing import List
from datetime import datetime

from ..core.models import Commitment
from ..core.config import settings

# Try to import litellm, fall back to simple mode if not configured
try:
    from litellm import acompletion
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False


async def extract_commitment(text: str, source: str) -> dict:
    """Extract commitment from raw text"""
    if not HAS_LITELLM or not settings.openrouter_api_key:
        # Simple extraction without LLM
        return {
            "is_commitment": "?" in text or "can you" in text.lower() or "please" in text.lower(),
            "task": text[:50],
            "deadline": None,
            "priority": 1
        }
    
    prompt = f"""Extract the commitment from this message.
    
Source: {source}
Message: {text}

Return JSON only:
{{
    "is_commitment": true/false,
    "task": "what was promised",
    "deadline": "YYYY-MM-DD or null",
    "priority": 0-3
}}"""
    
    from litellm import acompletion
    response = await acompletion(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {"is_commitment": False, "task": "", "deadline": None, "priority": 0}


async def filter_commitments(commitments: List[Commitment]) -> List[Commitment]:
    """Filter out noise, keep what matters"""
    if not commitments:
        return []
    
    # Without LLM, return all
    if not HAS_LITELLM or not settings.openrouter_api_key:
        return commitments
    
    # Batch descriptions
    items = [
        f"- [{c.source.value}] {c.text[:100]}..."
        for c in commitments[:20]
    ]
    
    prompt = f"""You are filtering commitments for a busy person.

Here are {len(items)} items. Some are noise, some are real commitments.

For each item, determine:
- Is this a real commitment or just noise?
- Should this be kept or can it be safely ignored?

Items:
{chr(10).join(items)}

Return JSON array with indices to KEEP:
{{"keep": [0, 1, 3, ...]}}"""
    
    from litellm import acompletion
    response = await acompletion(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        keep_indices = set(result.get("keep", []))
        return [c for i, c in enumerate(commitments) if i in keep_indices]
    except:
        return commitments


async def prioritize_commitments(commitments: List[Commitment]) -> List[Commitment]:
    """Prioritize commitments by importance and urgency"""
    if not commitments:
        return []
    
    # Sort by existing priority first
    sorted_commits = sorted(commitments, key=lambda c: c.priority, reverse=True)
    
    # If deadlines exist, boost those
    with_deadlines = [c for c in sorted_commits if c.deadline]
    without_deadlines = [c for c in sorted_commits if not c.deadline]
    
    # Sort by deadline
    with_deadlines.sort(key=lambda c: c.deadline or datetime.max)
    
    return with_deadlines + without_deadlines


async def pick_one_thing(commitments: List[Commitment]) -> Commitment | None:
    """Pick the ONE thing to focus on"""
    if not commitments:
        return None
    
    if len(commitments) == 1:
        return commitments[0]
    
    # Without LLM, pick highest priority
    if not HAS_LITELLM or not settings.openrouter_api_key:
        # Sort by priority, then deadline
        sorted_commits = sorted(commitments, key=lambda c: (c.priority, c.deadline or datetime.max), reverse=True)
        return sorted_commits[0]
    
    # Describe top candidates
    candidates = commitments[:10]
    items = [
        f"- {c.extracted_task} (priority: {c.priority}, deadline: {c.deadline or 'none'})"
        for c in candidates
    ]
    
    prompt = f"""You are helping someone pick ONE thing to focus on today.

They have {len(commitments)} commitments. Here are the top {len(items)}:
{chr(10).join(items)}

Pick the ONE most important and urgent item.
Consider:
- Priority (higher = more important)
- Deadlines (sooner = more urgent)
- Impact (what would have the most benefit)

Return JSON with the index (0-based):
{{"pick": 0}}"""
    
    from litellm import acompletion
    response = await acompletion(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        idx = result.get("pick", 0)
        return candidates[idx] if idx < len(candidates) else candidates[0]
    except:
        return candidates[0]


async def explain_why(commitment: Commitment) -> str:
    """Explain why this commitment was chosen"""
    if not HAS_LITELLM or not settings.openrouter_api_key:
        return f"Priority: {commitment.priority}, Source: {commitment.source.value}"
    
    prompt = f"""Explain briefly why this commitment is a good focus for today:

Task: {commitment.extracted_task}
Source: {commitment.source.value}
Priority: {commitment.priority}
Deadline: {commitment.deadline or 'none'}

One sentence explanation:"""
    
    from litellm import acompletion
    response = await acompletion(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    
    return response.choices[0].message.content.strip()
