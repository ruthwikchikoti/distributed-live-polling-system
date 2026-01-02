import asyncio
from collections import defaultdict
from typing import Dict

from app.core.config import settings
from app.core.redis_manager import RedisManager


class PollingService:
    # In-memory storage for Task 1 & Task 4 (Batch buffer)
    _memory_storage = defaultdict(lambda: defaultdict(int))

    def __init__(self):
        self.redis_manager = RedisManager()

    async def vote(self, poll_id: str, option_id: str) -> None:
        """
        Registers a vote.
        Task 1: Store in memory.
        Task 2: Write to Redis immediately.
        Task 4: Buffer in memory (Batching).
        """
        self._memory_storage[poll_id][option_id] += 1
        
        # TODO: Implement vote logic based on the current task
        

    async def get_results(self, poll_id: str) -> Dict[str, int]:
        """
        Get results.
        Task 1: Read from memory.
        Task 2: Read from Redis.
        Task 3: Check App Cache -> Redis.
        Task 4: Redis + Memory Buffer.
        """
        return self._memory_storage[poll_id]
        # TODO: Implement result fetching logic
        # Should return a dictionary like {"OptionA": 5, "OptionB": 3}
      

    async def flush_batch(self):
        """
        Task 4: Background process to flush memory buffer to Redis.
        """
        # TODO: Implement the batch flushing loop
        # 1. Loop forever (while True)
        # 2. Wait for BATCH_INTERVAL_SECONDS
        # 3. Flush _memory_storage to Redis
        raise NotImplemented
