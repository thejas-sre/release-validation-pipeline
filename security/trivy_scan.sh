#!/bin/bash
# Trivy Container Image Security Scan
# Scans the trade-signal-api Docker image for CVEs.
# CRITICAL severity vulnerabilities block the release pipeline.
# HIGH severity vulnerabilities generate a warning.

set -e

IMAGE="${1:-thejas-sre/trade-signal-api:latest}"
REPORT_FILE="reports/trivy_scan_$(date +%Y%m%d_%H%M%S).json"

echo "Scanning image: $IMAGE"

# Check if trivy is installed
if ! command -v trivy &> /dev/null; then
    echo "Trivy not installed. Installing..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
fi

mkdir -p reports

# Run scan — exit code 1 if CRITICAL vulnerabilities found
trivy image \
    --format json \
    --output "$REPORT_FILE" \
    --severity CRITICAL,HIGH \
    --exit-code 1 \
    "$IMAGE"

SCAN_EXIT=$?

if [ $SCAN_EXIT -eq 0 ]; then
    echo "PASS: No CRITICAL vulnerabilities found"
else
    echo "FAIL: CRITICAL vulnerabilities detected — release blocked"
    echo "Full report: $REPORT_FILE"
fi

exit $SCAN_EXIT
