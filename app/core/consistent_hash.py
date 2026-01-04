import hashlib

class ConsistentHash:
    def __init__(self, nodes, virtual_nodes=100):
        self.ring = []
        for node in nodes:
            for i in range(virtual_nodes):
                hash_key = int(hashlib.md5(f"{node}:{i}".encode()).hexdigest(), 16)
                self.ring.append((hash_key, node))
        self.ring.sort()
    
    def get_node(self, key):
        hash_key = int(hashlib.md5(key.encode()).hexdigest(), 16)
        for ring_hash, node in self.ring:
            if hash_key <= ring_hash:
                return node
        return self.ring[0][1]
