# Distributed Live Polling System

High-throughput voting backend using **FastAPI**, **two Redis nodes** (simulated shard), **consistent hashing**, **in-memory vote batching**, and a short **TTL application cache** for hot poll reads.  
Originally based on the HLD assignment starter; **all core TODOs are implemented** in this repository.

**Repository:** [github.com/ruthwikchikoti/distributed-live-polling-system](https://github.com/ruthwikchikoti/distributed-live-polling-system)

---

## What is implemented

| Area | Details |
|------|---------|
| **Consistent hashing** | MD5-based ring with configurable **virtual nodes** (`VIRTUAL_NODES`, default 100); each poll ID maps to one Redis URL. |
| **Redis sharding** | `RedisManager` maintains async clients per node and routes keys via `ConsistentHash.get_node()`. |
| **Vote ingestion** | Votes are accepted via HTTP and accumulated in an **in-memory buffer** (per poll, per option). |
| **Batch flush** | Background task (`flush_batch`) runs every `BATCH_INTERVAL_SECONDS` (default 10s) and **`HINCRBY`** counts into `poll:{poll_id}` hashes on the correct shard. |
| **Read path** | `GET /results/{poll_id}` loads base counts from the sharded Redis node (with optional **5s in-process cache**), then **merges pending buffer** so reads stay fresh between flushes. |
| **Observability** | Results response includes `served_via` (`app_cache`, `redis_7000`, or `redis_7001`) to see cache vs shard. |

---

## Architecture

```
                    ┌─────────────────┐
                    │   FastAPI app   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────────┐   batch flush    ┌────────────────┐
     │ In-memory      │ ───────────────► │ Redis node 1     │  :7000 (host)
     │ vote buffer    │   (HINCRBY)      │ (shard A)        │
     └────────────────┘                  └────────────────┘
              │                                  ▲
              │         ConsistentHash(poll_id)    │
              └──────────────────────────────────┼──► ┌────────────────┐
                                                   └──│ Redis node 2     │  :7001 (host)
                                                      │ (shard B)        │
                                                      └────────────────┘
```

---

## Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Python 3.11+** (if running locally without Docker)

---

## Quick start (Docker)

```bash
git clone https://github.com/ruthwikchikoti/distributed-live-polling-system.git
cd distributed-live-polling-system

docker compose up --build
```

- API: [http://localhost:8000](http://localhost:8000) → `{"status":"healthy"}`
- Redis (host ports): **7000** → node 1, **7001** → node 2 (mapped from containers’ 6379)

---

## API

Base path: `/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/vote/{poll_id}` | Body: `{"option_id": "A"}`. Accepts vote into memory buffer. |
| `GET` | `/results/{poll_id}` | Returns `poll_id`, `results` map, and `served_via`. |

### Examples

```bash
# Vote
curl -X POST http://localhost:8000/api/v1/vote/100 \
  -H "Content-Type: application/json" \
  -d '{"option_id": "A"}'

# Results (Redis + pending buffer + optional app cache)
curl -s http://localhost:8000/api/v1/results/100 | jq
```

---

## Configuration (environment)

| Variable | Default | Purpose |
|----------|---------|---------|
| `REDIS_NODES` | *(set in Compose)* | Comma-separated Redis URLs, e.g. `redis://redis-node-1:6379,redis://redis-node-2:6379` |
| `VIRTUAL_NODES` | `100` | Virtual nodes per physical Redis URL on the hash ring |
| `BATCH_INTERVAL_SECONDS` | `10.0` | Flush interval for buffer → Redis |
| `DEBUG` | `true` | Verbose logging flag (app) |
| `API_PREFIX` | `/api/v1` | API prefix |

---

## Project structure

```
.
├── app/
│   ├── api/v1/
│   │   ├── api.py
│   │   └── endpoints/polls.py      # Routes; starts background flush on startup
│   ├── core/
│   │   ├── config.py               # Pydantic settings / env
│   │   ├── consistent_hash.py      # Hash ring + get_node(key)
│   │   └── redis_manager.py        # Shard routing + async Redis clients
│   ├── services/
│   │   └── polling_service.py      # Buffer, cache, flush, get_results merge
│   ├── schemas/poll.py
│   └── main.py
├── docker-compose.yml              # App + 2× Redis (AOF), host ports 7000/7001
├── Dockerfile
├── requirements.txt
├── ASSIGNMENT.md                   # Original assignment spec (reference)
└── README.md
```

---

## Debugging

**Follow API / batch logs**

```bash
docker compose logs -f app
```

**Inspect keys per shard** (service names from Compose)

```bash
docker compose exec redis-node-1 redis-cli KEYS "*"
docker compose exec redis-node-2 redis-cli KEYS "*"
```

**Inspect hash for one poll** (after at least one flush)

```bash
docker compose exec redis-node-1 redis-cli HGETALL "poll:100"
```

---

## Local run (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export REDIS_NODES="redis://localhost:7000,redis://localhost:7001"
# Start two local Redis instances on those ports, then:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Attribution

Starter structure and assignment description trace to the original **Distributed Live Polling System** HLD exercise; this fork contains a **full implementation** of the hashing, sharding, batching, and caching behavior described above.
