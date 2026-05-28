"""
API Health Checks — 15 checks
Validates all trade-signal-api endpoints before release.
"""

import requests
import json
import time

API_URL = "http://localhost:8000"
TIMEOUT = 5


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "status": "passed" if passed else "failed", "detail": detail}


def run_api_checks() -> list:
    results = []

    # Check 1 — Health endpoint responds
    try:
        r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        results.append(check("api_health_endpoint_reachable", r.status_code == 200))
    except Exception as e:
        results.append(check("api_health_endpoint_reachable", False, str(e)))

    # Check 2 — Health returns healthy status
    try:
        r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        data = r.json()
        results.append(check("api_health_status_healthy", data.get("status") == "healthy"))
    except Exception as e:
        results.append(check("api_health_status_healthy", False, str(e)))

    # Check 3 — Redis connected via health endpoint
    try:
        r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        data = r.json()
        results.append(check("api_redis_connected", data.get("redis_connected") is True))
    except Exception as e:
        results.append(check("api_redis_connected", False, str(e)))

    # Check 4 — Metrics endpoint reachable
    try:
        r = requests.get(f"{API_URL}/metrics", timeout=TIMEOUT)
        results.append(check("api_metrics_endpoint_reachable", r.status_code == 200))
    except Exception as e:
        results.append(check("api_metrics_endpoint_reachable", False, str(e)))

    # Check 5 — Metrics contains expected counters
    try:
        r = requests.get(f"{API_URL}/metrics", timeout=TIMEOUT)
        results.append(check(
            "api_metrics_contains_request_counter",
            "trade_signal_requests_total" in r.text
        ))
    except Exception as e:
        results.append(check("api_metrics_contains_request_counter", False, str(e)))

    # Check 6 — POST /signals accepts valid payload
    try:
        payload = {
            "symbol": "AAPL",
            "action": "BUY",
            "confidence": 0.87,
            "timestamp": "2025-01-15T10:30:00Z"
        }
        r = requests.post(f"{API_URL}/signals", json=payload, timeout=TIMEOUT)
        results.append(check("api_post_signals_accepts_valid_payload", r.status_code == 200))
    except Exception as e:
        results.append(check("api_post_signals_accepts_valid_payload", False, str(e)))

    # Check 7 — POST /signals returns signal_id
    try:
        payload = {
            "symbol": "GOOGL",
            "action": "SELL",
            "confidence": 0.72,
            "timestamp": "2025-01-15T10:30:00Z"
        }
        r = requests.post(f"{API_URL}/signals", json=payload, timeout=TIMEOUT)
        data = r.json()
        results.append(check("api_post_signals_returns_signal_id", "signal_id" in data))
    except Exception as e:
        results.append(check("api_post_signals_returns_signal_id", False, str(e)))

    # Check 8 — GET /signals/{id} retrieves cached signal
    try:
        payload = {
            "symbol": "INFY",
            "action": "HOLD",
            "confidence": 0.65,
            "timestamp": "2025-01-15T10:30:00Z"
        }
        post_r = requests.post(f"{API_URL}/signals", json=payload, timeout=TIMEOUT)
        signal_id = post_r.json().get("signal_id")
        get_r = requests.get(f"{API_URL}/signals/{signal_id}", timeout=TIMEOUT)
        results.append(check("api_get_signal_by_id_returns_cached", get_r.status_code == 200))
    except Exception as e:
        results.append(check("api_get_signal_by_id_returns_cached", False, str(e)))

    # Check 9 — GET /signals/{id} returns 404 for unknown id
    try:
        r = requests.get(f"{API_URL}/signals/nonexistent-id-12345", timeout=TIMEOUT)
        results.append(check("api_get_unknown_signal_returns_404", r.status_code == 404))
    except Exception as e:
        results.append(check("api_get_unknown_signal_returns_404", False, str(e)))

    # Check 10 — POST /signals rejects invalid payload
    try:
        r = requests.post(f"{API_URL}/signals", json={"invalid": "payload"}, timeout=TIMEOUT)
        results.append(check("api_post_signals_rejects_invalid_payload", r.status_code == 422))
    except Exception as e:
        results.append(check("api_post_signals_rejects_invalid_payload", False, str(e)))

    # Check 11 — Response time under 200ms
    try:
        start = time.perf_counter()
        requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        latency_ms = (time.perf_counter() - start) * 1000
        results.append(check(
            "api_health_response_under_200ms",
            latency_ms < 200,
            f"{latency_ms:.1f}ms"
        ))
    except Exception as e:
        results.append(check("api_health_response_under_200ms", False, str(e)))

    # Check 12 — Batch lookup endpoint reachable
    try:
        r = requests.get(f"{API_URL}/signals/batch/lookup?ids=id1,id2", timeout=TIMEOUT)
        results.append(check("api_batch_lookup_reachable", r.status_code in [200, 404]))
    except Exception as e:
        results.append(check("api_batch_lookup_reachable", False, str(e)))

    # Check 13 — Content-Type header is application/json
    try:
        r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        results.append(check(
            "api_returns_json_content_type",
            "application/json" in r.headers.get("content-type", "")
        ))
    except Exception as e:
        results.append(check("api_returns_json_content_type", False, str(e)))

    # Check 14 — Version field present in health response
    try:
        r = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        data = r.json()
        results.append(check("api_health_returns_version", "version" in data))
    except Exception as e:
        results.append(check("api_health_returns_version", False, str(e)))

    # Check 15 — API handles concurrent requests without error
    try:
        import threading
        errors = []
        def make_request():
            try:
                requests.get(f"{API_URL}/health", timeout=TIMEOUT)
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        results.append(check("api_handles_concurrent_requests", len(errors) == 0))
    except Exception as e:
        results.append(check("api_handles_concurrent_requests", False, str(e)))

    return results
