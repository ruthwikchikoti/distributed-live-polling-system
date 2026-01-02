from typing import Dict

import redis.asyncio as redis  # Using async redis for FastAPI

from .config import settings
from .consistent_hash import ConsistentHash


class RedisManager:
    def __init__(self):
        self.clients: Dict[str, redis.Redis] = {}

        # Parse nodes
        nodes = [n.strip() for n in settings.REDIS_NODES.split(",") if n.strip()]
        # TODO: uncomment and use consistent hashing for Sharding
        # self.consistent_hash = ConsistentHash(nodes, settings.VIRTUAL_NODES)

        # Initialize clients for each node
        for node in nodes:
            self.clients[node] = redis.from_url(node, decode_responses=True)

    async def get_client(self, key: str) -> redis.Redis:
        """Return the correct Redis client based on the Sharding Key (poll_id)"""
        return list(self.clients.values())[0]
