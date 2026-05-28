# release-validation-pipeline

Automated release validation pipeline that replaced 47 manual pre-release
health checks consuming 4 hours per release cycle. All checks now run in
under 12 minutes as a mandatory Jenkins and GitHub Actions pipeline gate.

---

## Problem Statement

Pre-release validation required engineers to manually run 47 health checks
across the API, Redis, Kubernetes, and configuration before every deployment.
This took approximately 4 hours, was error-prone, and created inconsistent
release quality. A single missed check could allow a broken release to reach
production.

---

## Architecture

    Developer pushes to develop branch
            |
            v
    GitHub Actions / Jenkins triggered
            |
            v
    Stage 1: Security Scan (Trivy — CRITICAL CVEs block)
            |
            v
    Stage 2: Redis Health Checks (12 checks)
            |
            v
    Stage 3: API Health Checks (15 checks)
            |
            v
    Stage 4: Kubernetes Health Checks (10 checks)
            |
            v
    Stage 5: Config Parity Checks (10 checks)
            |
            v
    Stage 6: Audit Log (structured JSON — append-only)
            |
            v
    Stage 7: Deploy Gate (PASS / FAIL)

---

## How To Run

Prerequisites: Python 3.12, Redis running on localhost:6379, trade-signal-api running on localhost:8000

    git clone https://github.com/thejas-sre/release-validation-pipeline.git
    cd release-validation-pipeline
    pip install redis requests fastapi uvicorn prometheus-client pydantic

Run all 47 checks:

    python3 validation/health_checks.py

Run individual check groups:

    python3 -c "from validation.check_redis import run_redis_checks; import json; print(json.dumps(run_redis_checks(), indent=2))"
    python3 -c "from validation.check_api import run_api_checks; import json; print(json.dumps(run_api_checks(), indent=2))"

Run security scan (requires Docker and Trivy):

    bash security/trivy_scan.sh thejas-sre/trade-signal-api:latest

---

## Pipeline Stages

| Stage | Checks | Gate Condition |
|---|---|---|
| Security Scan | Trivy CVE scan | CRITICAL severity blocks pipeline |
| Redis Health | 12 checks | Any failure blocks pipeline |
| API Health | 15 checks | Any failure blocks pipeline |
| Kubernetes Health | 10 checks | Failures block (skipped if no kubectl) |
| Config Parity | 10 checks | Any failure blocks pipeline |
| Audit Log | All 47 results | Always runs |
| Deploy Gate | Final decision | All stages must pass |

---

## Before and After

| Metric | Before | After |
|---|---|---|
| Validation time | approximately 4 hours | approximately 12 minutes |
| Check execution | Manual | Fully automated |
| Human error risk | Present | Eliminated |
| Security gate | None | Trivy CVE scan |
| Audit trail | None | Structured JSON per run |

---

## What This Project Demonstrates

- Jenkins declarative pipeline with stage gating
- GitHub Actions equivalent workflow triggered on develop branch push
- 47 automated checks across API, Redis, Kubernetes, and configuration
- Trivy container image security scanning — CRITICAL CVEs block release
- Structured JSON audit logging of every validation run
- Check catalogue documenting all 47 checks with purpose and threshold

---

## Compliance Considerations

- audit_logger.py writes append-only structured JSON logs of every run
- docs/check_catalogue.md documents every check — this is the change-control audit trail
- Security gate via Trivy prevents images with CRITICAL CVEs from reaching production
- All check results include timestamps for regulatory record-keeping

---

## Related Projects

| Project | Connection |
|---|---|
| trade-signal-api | The service this pipeline validates before every release |
| observability-stack | Monitors the service after each validated release |
| kubernetes-ops-runbook | Documents the Kubernetes environment this pipeline validates |
