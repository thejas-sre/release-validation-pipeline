# Check Catalogue — All 47 Release Validation Checks

This document lists every automated check with its purpose and pass threshold.
In a regulated environment this catalogue forms part of the change-control audit trail.

## API Checks (15 checks)

| # | Check | Purpose | Pass Condition |
|---|---|---|---|
| 1 | api_health_endpoint_reachable | Service is running | HTTP 200 |
| 2 | api_health_status_healthy | All dependencies healthy | status == healthy |
| 3 | api_redis_connected | Redis connectivity confirmed | redis_connected == true |
| 4 | api_metrics_endpoint_reachable | Prometheus scrape target available | HTTP 200 |
| 5 | api_metrics_contains_request_counter | Metrics contain expected counters | Counter present in response |
| 6 | api_post_signals_accepts_valid_payload | Signal ingestion working | HTTP 200 |
| 7 | api_post_signals_returns_signal_id | Signal ID generation working | signal_id in response |
| 8 | api_get_signal_by_id_returns_cached | Cache read working | HTTP 200 with data |
| 9 | api_get_unknown_signal_returns_404 | Error handling correct | HTTP 404 |
| 10 | api_post_signals_rejects_invalid_payload | Input validation working | HTTP 422 |
| 11 | api_health_response_under_200ms | Performance acceptable | Latency under 200ms |
| 12 | api_batch_lookup_reachable | Batch endpoint available | HTTP 200 or 404 |
| 13 | api_returns_json_content_type | Response format correct | Content-Type: application/json |
| 14 | api_health_returns_version | Version field present | version in response |
| 15 | api_handles_concurrent_requests | No race conditions under load | 10 concurrent requests succeed |

## Redis Checks (12 checks)

| # | Check | Purpose | Pass Condition |
|---|---|---|---|
| 16 | redis_reachable | Redis is up | PING succeeds |
| 17 | redis_ping_latency_acceptable | Latency within threshold | Under 10ms |
| 18 | redis_set_operation_works | Write path functional | SET succeeds |
| 19 | redis_get_operation_works | Read path functional | GET returns expected value |
| 20 | redis_del_operation_works | Delete path functional | DEL removes key |
| 21 | redis_ttl_honoured | TTL expiry working | TTL > 0 after setex |
| 22 | redis_slowlog_empty | No degraded queries | SLOWLOG empty |
| 23 | redis_memory_below_threshold | Memory within bounds | Under 200MB |
| 24 | redis_connected_clients_within_limit | Connection count safe | Under 100 clients |
| 25 | redis_replication_role_valid | Cluster state correct | master or standalone |
| 26 | redis_persistence_enabled | Data durability confirmed | AOF or RDB active |
| 27 | redis_pipeline_operations_work | Batch write path functional | Pipeline executes cleanly |

## Kubernetes Checks (10 checks)

| # | Check | Purpose | Pass Condition |
|---|---|---|---|
| 28 | k8s_kubectl_available | kubectl accessible | Exit code 0 |
| 29 | k8s_nodes_ready | Cluster nodes healthy | All nodes Ready |
| 30 | k8s_trade_signal_pods_running | Pods exist | At least 1 pod |
| 31 | k8s_trade_signal_pods_ready | Pods accepting traffic | All pods Ready |
| 32 | k8s_no_crashloopbackoff_pods | No crash loops | 0 CrashLoopBackOff pods |
| 33 | k8s_no_oomkilled_pods | No memory kills | 0 OOMKilled pods |
| 34 | k8s_resource_limits_set | Resource governance in place | Limits on all containers |
| 35 | k8s_liveness_probes_configured | Automatic restart on failure | Probes on all containers |
| 36 | k8s_configmap_exists | Config management in place | ConfigMap present |
| 37 | k8s_service_exists | Network routing configured | Service present |

## Configuration Parity Checks (10 checks)

| # | Check | Purpose | Pass Condition |
|---|---|---|---|
| 38 | config_redis_host_set | Redis host configured | REDIS_HOST set |
| 39 | config_redis_port_valid | Port in valid range | 1-65535 |
| 40 | config_redis_pool_size_reasonable | Pool size safe | 1-200 |
| 41 | config_signal_ttl_positive | TTL valid | TTL > 0 |
| 42 | config_no_plaintext_secrets_in_env | No exposed credentials | No sensitive env vars |
| 43 | config_python_version_acceptable | Runtime version safe | Python 3.10+ |
| 44 | config_required_packages_installed | Dependencies present | All packages importable |
| 45 | config_debug_mode_disabled | Production mode active | DEBUG not true |
| 46 | config_log_level_valid | Logging configured | Valid log level |
| 47 | config_redis_not_localhost | Production Redis configured | REDIS_HOST not localhost |
