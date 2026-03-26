"""Hermes-style file-based cron scheduler"""
import asyncio
import fcntl
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Awaitable

from ..core.config import settings


class CronScheduler:
    """File-based cron scheduler with tick-based execution"""
    
    def __init__(
        self,
        tick_interval: int = 60,
        data_dir: str | None = None
    ):
        self.tick_interval = tick_interval
        self.data_dir = Path(data_dir or settings.data_dir)
        self.lock_file = self.data_dir / "cron" / ".tick.lock"
        self.state_file = self.data_dir / "cron" / "state.json"
        
        # Jobs registry
        self.jobs: dict[str, Callable[[], Awaitable]] = {}
        
        # Ensure directories exist
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    def register(self, name: str, job: Callable[[], Awaitable]):
        """Register a job"""
        self.jobs[name] = job
    
    async def tick(self):
        """Called every tick_interval seconds"""
        # File locking to prevent concurrent ticks
        try:
            with open(self.lock_file, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                try:
                    await self._run_jobs()
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except BlockingIOError:
            # Another process is running
            pass
    
    async def _run_jobs(self):
        """Run scheduled jobs"""
        state = self._load_state()
        now = datetime.now()
        
        # Gather job - every X minutes
        if self._should_run(state, "gather", minutes=settings.gather_interval_minutes):
            if "gather" in self.jobs:
                await self.jobs["gather"]()
            state["last_gather"] = now.isoformat()
        
        # Reduce job - every X minutes
        if self._should_run(state, "reduce", minutes=settings.reduce_interval_minutes):
            if "reduce" in self.jobs:
                await self.jobs["reduce"]()
            state["last_reduce"] = now.isoformat()
        
        # Expire job - every X hours
        if self._should_run(state, "expire", hours=settings.expire_interval_hours):
            if "expire" in self.jobs:
                await self.jobs["expire"]()
            state["last_expire"] = now.isoformat()
        
        self._save_state(state)
    
    def _should_run(
        self, 
        state: dict, 
        job_name: str, 
        minutes: int = 0, 
        hours: int = 0
    ) -> bool:
        """Check if job should run based on last run time"""
        key = f"last_{job_name}"
        last_run = state.get(key)
        
        if not last_run:
            return True
        
        try:
            last = datetime.fromisoformat(last_run)
            interval = timedelta(minutes=minutes, hours=hours)
            return datetime.now() - last >= interval
        except:
            return True
    
    def _load_state(self) -> dict:
        """Load scheduler state"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        return {}
    
    def _save_state(self, state: dict):
        """Save scheduler state"""
        self.state_file.write_text(json.dumps(state, indent=2))
    
    async def run_forever(self):
        """Run scheduler in a loop"""
        while True:
            await self.tick()
            await asyncio.sleep(self.tick_interval)
    
    def run_in_background(self):
        """Start scheduler in background"""
        asyncio.create_task(self.run_forever())