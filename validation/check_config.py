"""
Configuration Parity Checks — 10 checks
Validates environment configuration and detects drift between
expected and actual configuration state before release.
"""

import os
import json


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "status": "passed" if passed else "failed", "detail": detail}


def run_config_checks() -> list:
    results = []

    # Check 1 — REDIS_HOST configured
    redis_host = os.getenv("REDIS_HOST", "localhost")
    results.append(check("config_redis_host_set", bool(redis_host), redis_host))

    # Check 2 — REDIS_PORT is valid
    try:
        port = int(os.getenv("REDIS_PORT", "6379"))
        results.append(check("config_redis_port_valid", 1 <= port <= 65535, str(port)))
    except ValueError:
        results.append(check("config_redis_port_valid", False, "not a valid integer"))

    # Check 3 — REDIS_POOL_SIZE is reasonable
    try:
        pool_size = int(os.getenv("REDIS_POOL_SIZE", "20"))
        results.append(check(
            "config_redis_pool_size_reasonable",
            1 <= pool_size <= 200,
            str(pool_size)
        ))
    except ValueError:
        results.append(check("config_redis_pool_size_reasonable", False, "not valid"))

    # Check 4 — SIGNAL_TTL is positive
    try:
        ttl = int(os.getenv("SIGNAL_TTL", "60"))
        results.append(check("config_signal_ttl_positive", ttl > 0, str(ttl)))
    except ValueError:
        results.append(check("config_signal_ttl_positive", False, "not valid"))

    # Check 5 — No secrets in environment variable names (basic check)
    sensitive_patterns = ["PASSWORD", "SECRET", "TOKEN", "KEY", "CREDENTIAL"]
    env_keys = list(os.environ.keys())
    exposed = [k for k in env_keys if any(p in k.upper() for p in sensitive_patterns)]
    results.append(check(
        "config_no_plaintext_secrets_in_env",
        len(exposed) == 0,
        f"Potentially sensitive vars: {exposed}" if exposed else ""
    ))

    # Check 6 — Python version is 3.10 or higher
    import sys
    version = sys.version_info
    results.append(check(
        "config_python_version_acceptable",
        version >= (3, 10),
        f"{version.major}.{version.minor}.{version.micro}"
    ))

    # Check 7 — Required Python packages installed
    required = ["fastapi", "redis", "prometheus_client", "pydantic"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    results.append(check(
        "config_required_packages_installed",
        len(missing) == 0,
        f"Missing: {missing}" if missing else ""
    ))

    # Check 8 — No debug mode in production
    debug = os.getenv("DEBUG", "false").lower()
    results.append(check("config_debug_mode_disabled", debug not in ["true", "1", "yes"]))

    # Check 9 — LOG_LEVEL is valid
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    results.append(check(
        "config_log_level_valid",
        log_level in valid_levels,
        log_level
    ))

    # Check 10 — No localhost in production Redis host (warning only)
    redis_host = os.getenv("REDIS_HOST", "localhost")
    is_localhost = redis_host in ["localhost", "127.0.0.1"]
    results.append(check(
        "config_redis_not_localhost",
        not is_localhost,
        f"REDIS_HOST={redis_host} — acceptable for local/dev, not production"
    ))

    return results
