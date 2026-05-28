"""
Kubernetes Health Checks — 10 checks
Validates pod readiness, resource limits, and cluster health
before every release. Skipped gracefully if kubectl not available.
"""

import subprocess
import json


def check(name: str, passed: bool, detail: str = "", skipped: bool = False) -> dict:
    status = "skipped" if skipped else ("passed" if passed else "failed")
    return {"name": name, "status": status, "detail": detail}


def kubectl(args: list) -> tuple:
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True, text=True, timeout=10
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", "kubectl not found"
    except Exception as e:
        return -1, "", str(e)


def run_kubernetes_checks() -> list:
    results = []

    # Check if kubectl is available
    rc, _, err = kubectl(["version", "--client"])
    kubectl_available = rc == 0

    if not kubectl_available:
        for name in [
            "k8s_kubectl_available",
            "k8s_nodes_ready",
            "k8s_trade_signal_pods_running",
            "k8s_trade_signal_pods_ready",
            "k8s_no_crashloopbackoff_pods",
            "k8s_no_oomkilled_pods",
            "k8s_resource_limits_set",
            "k8s_liveness_probes_configured",
            "k8s_configmap_exists",
            "k8s_service_exists"
        ]:
            results.append(check(name, False, "kubectl not available", skipped=True))
        return results

    results.append(check("k8s_kubectl_available", True))

    # Check 2 — Nodes ready
    rc, out, _ = kubectl(["get", "nodes", "-o", "json"])
    if rc == 0:
        nodes = json.loads(out).get("items", [])
        all_ready = all(
            any(c["type"] == "Ready" and c["status"] == "True" for c in n["status"]["conditions"])
            for n in nodes
        )
        results.append(check("k8s_nodes_ready", all_ready, f"{len(nodes)} nodes"))
    else:
        results.append(check("k8s_nodes_ready", False, "could not get nodes"))

    # Check 3 — trade-signal-api pods running
    rc, out, _ = kubectl(["get", "pods", "-l", "app=trade-signal-api", "-o", "json"])
    pods = []
    if rc == 0:
        pods = json.loads(out).get("items", [])
        results.append(check("k8s_trade_signal_pods_running", len(pods) > 0, f"{len(pods)} pods"))
    else:
        results.append(check("k8s_trade_signal_pods_running", False, "skipped", skipped=True))

    # Check 4 — All pods ready
    if pods:
        all_ready = all(
            any(c["type"] == "Ready" and c["status"] == "True"
                for c in p["status"].get("conditions", []))
            for p in pods
        )
        results.append(check("k8s_trade_signal_pods_ready", all_ready))
    else:
        results.append(check("k8s_trade_signal_pods_ready", False, "no pods found", skipped=True))

    # Check 5 — No CrashLoopBackOff
    if pods:
        crash_pods = [
            p["metadata"]["name"] for p in pods
            if any(
                cs.get("state", {}).get("waiting", {}).get("reason") == "CrashLoopBackOff"
                for cs in p["status"].get("containerStatuses", [])
            )
        ]
        results.append(check(
            "k8s_no_crashloopbackoff_pods",
            len(crash_pods) == 0,
            f"CrashLoopBackOff: {crash_pods}" if crash_pods else ""
        ))
    else:
        results.append(check("k8s_no_crashloopbackoff_pods", False, "no pods", skipped=True))

    # Check 6 — No OOMKilled
    if pods:
        oom_pods = [
            p["metadata"]["name"] for p in pods
            if any(
                cs.get("lastState", {}).get("terminated", {}).get("reason") == "OOMKilled"
                for cs in p["status"].get("containerStatuses", [])
            )
        ]
        results.append(check(
            "k8s_no_oomkilled_pods",
            len(oom_pods) == 0,
            f"OOMKilled: {oom_pods}" if oom_pods else ""
        ))
    else:
        results.append(check("k8s_no_oomkilled_pods", False, "no pods", skipped=True))

    # Check 7 — Resource limits set
    if pods:
        limits_set = all(
            p["spec"]["containers"][0].get("resources", {}).get("limits")
            for p in pods
        )
        results.append(check("k8s_resource_limits_set", limits_set))
    else:
        results.append(check("k8s_resource_limits_set", False, "no pods", skipped=True))

    # Check 8 — Liveness probes configured
    if pods:
        probes_set = all(
            p["spec"]["containers"][0].get("livenessProbe")
            for p in pods
        )
        results.append(check("k8s_liveness_probes_configured", probes_set))
    else:
        results.append(check("k8s_liveness_probes_configured", False, "no pods", skipped=True))

    # Check 9 — ConfigMap exists
    rc, _, _ = kubectl(["get", "configmap", "trade-signal-api-config"])
    results.append(check("k8s_configmap_exists", rc == 0))

    # Check 10 — Service exists
    rc, _, _ = kubectl(["get", "service", "trade-signal-api-service"])
    results.append(check("k8s_service_exists", rc == 0))

    return results
