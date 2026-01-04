import asyncio
from collections import defaultdict
import time
from typing import Dict, Tuple
from app.core.config import settings
from app.core.redis_manager import RedisManager


class PollingService:
    # In-memory storage for Task 1 & Task 4 (Batch buffer)
    _memory_storage = defaultdict(lambda: defaultdict(int))

    # Task 3: Cache
    __cache={}
    
    def __init__(self):
        self.redis_manager = RedisManager()

    async def vote(self, poll_id: str, option_id: str) -> None:
        """
        Registers a vote.
        Task 1: Store in memory.
        Task 2: Write to Redis immediately.
        Task 4: Buffer in memory (Batching).
        """
        # Task 4:
        self._memory_storage[poll_id][option_id] += 1
        return

    async def get_results(self, poll_id: str) -> Dict[str, int]:
        """
        Get results.
        Task 1: Read from memory.
        Task 2: Read from Redis.
        Task 3: Check App Cache -> Redis.
        Task 4: Redis + Memory Buffer.
        """
        # Task 2: 
        redis_client = await self.redis_manager.get_client(poll_id)

        # Task 3:
        current_time = time.time()

        # Get base results (from cache or Redis)
        served_via = "redis"
        if poll_id in self.__cache:
            cached_data = self.__cache[poll_id]
            age = current_time - cached_data["timestamp"]
            if age < 5:
                vote_counts = cached_data["results"].copy()
                served_via = "app_cache"
            else:
                del self.__cache[poll_id]
        
        if served_via == "redis":
            results = await redis_client.hgetall(f"poll:{poll_id}")
            vote_counts = {}
            for option, count in results.items():
                vote_counts[option] = int(count)
            self.__cache[poll_id] = {
                "results": vote_counts.copy(),
                "timestamp": current_time
            }
        
        # Task 4: Always add buffer values (once, at the end)
        pending = self._memory_storage.get(poll_id, {})
        for option, count in pending.items():
            vote_counts[option] = vote_counts.get(option, 0) + count
        
        return vote_counts, served_via

    async def flush_batch(self):
        """
        Task 4: Background process to flush memory buffer to Redis.
        """
        while True:
            await asyncio.sleep(settings.BATCH_INTERVAL_SECONDS)
            for poll_id, options in list(self._memory_storage.items()):
                redis_client = await self.redis_manager.get_client(poll_id)
                for option, count in options.items():
                    await redis_client.hincrby(f"poll:{poll_id}", option, count)
            self._memory_storage.clear()
        
