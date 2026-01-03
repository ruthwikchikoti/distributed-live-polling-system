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
        # Task 2:
        redis_client = await self.redis_manager.get_client(poll_id)
        
        await redis_client.hincrby(f"poll:{poll_id}", option_id, 1)
        

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

        if poll_id in self.__cache:
            cached_data = self.__cache[poll_id]
            age = current_time -cached_data["timestamp"]

            if age < 5:
               return cached_data["results"],"app_cache"
            else:
                del self.__cache[poll_id]
      

        results = await redis_client.hgetall(f"poll:{poll_id}")
        
        vote_counts = {}
        for option, count in results.items():
            vote_counts[option] = int(count)
        
        self.__cache[poll_id] ={
            "results": vote_counts,
            "timestamp": current_time
        }
        return vote_counts,"redis"

    async def flush_batch(self):
        """
        Task 4: Background process to flush memory buffer to Redis.
        """
        # TODO: Implement the batch flushing loop
        # 1. Loop forever (while True)
        # 2. Wait for BATCH_INTERVAL_SECONDS
        # 3. Flush _memory_storage to Redis
        raise NotImplemented
