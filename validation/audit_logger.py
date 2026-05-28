"""
Audit Logger
Writes structured JSON audit logs of every validation run.
In a regulated environment, these logs form part of the
change-control audit trail. Logs are append-only.
"""

import json
import os
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")


def log_run(results: dict) -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"validation_run_{timestamp}.json"
    filepath = os.path.join(LOG_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)

    return filepath
