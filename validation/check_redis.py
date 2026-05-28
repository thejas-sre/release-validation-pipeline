"""
Redis Health Checks — 12 checks
Validates Redis connectivity, performance, and configuration
before every release.
"""

import redis
import time

REDIS_HOST = "localhost"
REDIS_PORT = 6379
LATENCY_THRESHOLD_MS = 10


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "status": "passed" if passed else "failed", "detail": detail}


def run_redis_checks() -> list:
    results = []
    client = None

    # Check 1 — Redis reachable
    try:
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        client.ping()
        results.append(check("redis_reachable", True))
    except Exception as e:
        results.append(check("redis_reachable", False, str(e)))
        return results

    # Check 2 — Ping latency under threshold
    try:
        start = time.perf_counter()
        client.ping()
        latency_ms = (time.perf_counter() - start) * 1000
        results.append(check(
            "redis_ping_latency_acceptable",
            latency_ms < LATENCY_THRESHOLD_MS,
            f"{latency_ms:.2f}ms"
        ))
    except Exception as e:
        results.append(check("redis_ping_latency_acceptable", False, str(e)))

    # Check 3 — SET operation works
    try:
        client.setex("healthcheck:test", 10, "ok")
        results.append(check("redis_set_operation_works", True))
    except Exception as e:
        results.append(check("redis_set_operation_works", False, str(e)))

    # Check 4 — GET operation works
    try:
        val = client.get("healthcheck:test")
        results.append(check("redis_get_operation_works", val == "ok"))
    except Exception as e:
        results.append(check("redis_get_operation_works", False, str(e)))

    # Check 5 — DEL operation works
    try:
        client.delete("healthcheck:test")
        val = client.get("healthcheck:test")
        results.append(check("redis_del_operation_works", val is None))
    except Exception as e:
        results.append(check("redis_del_operation_works", False, str(e)))

    # Check 6 — TTL is honoured
    try:
        client.setex("healthcheck:ttl", 2, "expires")
        ttl = client.ttl("healthcheck:ttl")
        results.append(check("redis_ttl_honoured", ttl > 0))
        client.delete("healthcheck:ttl")
    except Exception as e:
        results.append(check("redis_ttl_honoured", False, str(e)))

    # Check 7 — No slow queries in SLOWLOG
    try:
        slowlog = client.slowlog_get(10)
        results.append(check(
            "redis_slowlog_empty",
            len(slowlog) == 0,
            f"{len(slowlog)} slow queries found"
        ))
    except Exception as e:
        results.append(check("redis_slowlog_empty", False, str(e)))

    # Check 8 — Memory usage below threshold
    try:
        info = client.info("memory")
        used_mb = info["used_memory"] / (1024 * 1024)
        results.append(check(
            "redis_memory_below_threshold",
            used_mb < 200,
            f"{used_mb:.1f}MB used"
        ))
    except Exception as e:
        results.append(check("redis_memory_below_threshold", False, str(e)))

    # Check 9 — Connected clients within limit
    try:
        info = client.info("clients")
        connected = info["connected_clients"]
        results.append(check(
            "redis_connected_clients_within_limit",
            connected < 100,
            f"{connected} clients connected"
        ))
    except Exception as e:
        results.append(check("redis_connected_clients_within_limit", False, str(e)))

    # Check 10 — Replication role is master or standalone
    try:
        info = client.info("replication")
        role = info["role"]
        results.append(check(
            "redis_replication_role_valid",
            role in ["master", "standalone"],
            f"role: {role}"
        ))
    except Exception as e:
        results.append(check("redis_replication_role_valid", False, str(e)))

    # Check 11 — Persistence enabled
    try:
        info = client.info("persistence")
        results.append(check(
            "redis_persistence_enabled",
            info.get("aof_enabled", 0) == 1 or info.get("rdb_last_bgsave_status") == "ok"
        ))
    except Exception as e:
        results.append(check("redis_persistence_enabled", False, str(e)))

    # Check 12 — Pipeline operations work
    try:
        pipe = client.pipeline()
        for i in range(5):
            pipe.setex(f"healthcheck:pipeline:{i}", 10, str(i))
        pipe.execute()
        results.append(check("redis_pipeline_operations_work", True))
        for i in range(5):
            client.delete(f"healthcheck:pipeline:{i}")
    except Exception as e:
        results.append(check("redis_pipeline_operations_work", False, str(e)))

    return results
