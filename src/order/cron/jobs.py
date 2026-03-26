"""Default cron jobs"""
from ..core.store import store
from ..core.config import settings
from ..gatherers import DiscordGatherer, GitHubGatherer, XGatherer
from ..synthesis.llm import filter_commitments, prioritize_commitments


async def gather_all():
    """Gather commitments from all sources"""
    commitments = []
    
    # Discord
    discord = DiscordGatherer()
    if await discord.test_connection():
        result = await discord.run()
        commitments.extend(result.commitments)
    
    # GitHub
    github = GitHubGatherer()
    if await github.test_connection():
        result = await github.run()
        commitments.extend(result.commitments)
    
    # X/Twitter
    x = XGatherer()
    if await x.test_connection():
        result = await x.run()
        commitments.extend(result.commitments)
    
    # Store
    if commitments:
        await store.add_many(commitments)
    
    return len(commitments)


async def reduce_all():
    """Filter and prioritize commitments"""
    pending = await store.get_pending()
    
    if not pending:
        return 0
    
    # Filter noise
    filtered = await filter_commitments(pending)
    
    # Prioritize
    prioritized = await prioritize_commitments(filtered)
    
    # Update store
    for commitment in prioritized:
        await store.update_status(commitment.id, commitment.status)
    
    return len(prioritized)


async def expire_old():
    """Expire old pending commitments"""
    expired = await store.expire_old(hours=settings.commitment_expire_hours)
    return expired