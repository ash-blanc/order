"""Base gatherer abstract class"""
from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..core.models import Commitment, GatherResult


class BaseGatherer(ABC):
    """Abstract base class for all gatherers"""
    
    @abstractmethod
    async def gather(self) -> AsyncIterator[Commitment]:
        """Yield commitments from source"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if source is accessible"""
        pass
    
    async def run(self) -> GatherResult:
        """Run gatherer and return result"""
        commitments = []
        error = None
        try:
            async for commitment in self.gather():
                commitments.append(commitment)
        except Exception as e:
            error = str(e)
        
        return GatherResult(
            source=self.source,
            total_found=len(commitments),
            commitments=commitments,
            error=error
        )
    
    @property
    @abstractmethod
    def source(self):
        """Return the Source enum value"""
        pass