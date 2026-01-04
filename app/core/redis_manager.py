import redis.asyncio as redis
from .config import settings
from .consistent_hash import ConsistentHash

class RedisManager:
    def __init__(self):
        nodes = [n.strip() for n in settings.REDIS_NODES.split(",") if n.strip()]
        self.hash = ConsistentHash(nodes, settings.VIRTUAL_NODES)
        self.clients = {n: redis.from_url(n, decode_responses=True) for n in nodes}
    
    async def get_client(self, key):
        return self.clients[self.hash.get_node(key)]
    
    def get_port(self, key):
        node = self.hash.get_node(key)
        return "7000" if "redis-node-1" in node else "7001"
