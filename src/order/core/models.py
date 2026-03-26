"""Core data models"""
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4


class Source(str, Enum):
    DISCORD = "discord"
    GITHUB = "github"
    X_DM = "x_dm"
    X_BOOKMARK = "x_bookmark"
    GMAIL = "gmail"


class CommitmentStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    IGNORED = "ignored"
    EXPIRED = "expired"
    IN_PROGRESS = "in_progress"


class Priority(int, Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3


class Commitment(BaseModel):
    """A commitment extracted from user's scattered digital life"""
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    source: Source
    text: str  # Original text
    extracted_task: str  # AI-extracted task
    platform_id: str  # Message ID / Issue ID
    platform_url: str  # Link to original
    created_at: datetime  # When the commitment was made
    discovered_at: datetime = Field(default_factory=datetime.now)
    deadline: datetime | None = None
    priority: int = Field(default=0, ge=0, le=3)
    status: CommitmentStatus = CommitmentStatus.PENDING
    raw_data: dict = Field(default_factory=dict)
    
    def is_expired(self, hours: int = 72) -> bool:
        """Check if commitment has expired"""
        age = (datetime.now() - self.discovered_at).total_seconds() / 3600
        return age > hours


class GatherResult(BaseModel):
    """Result from a gatherer run"""
    source: Source
    total_found: int
    commitments: list[Commitment]
    error: str | None = None
    ran_at: datetime = Field(default_factory=datetime.now)


class ReduceResult(BaseModel):
    """Result from reduce/filter operation"""
    total_before: int
    total_after: int
    ignored: list[Commitment]
    kept: list[Commitment]
    ran_at: datetime = Field(default_factory=datetime.now)