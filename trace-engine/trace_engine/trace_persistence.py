import json
import os

TRACE_DIR = "traces"


def save_trace(trace: dict):
    os.makedirs(TRACE_DIR, exist_ok=True)

    alert_id = trace["alert_id"]
    file_path = os.path.join(TRACE_DIR, f"{alert_id}.json")

    with open(file_path, "w") as f:
        json.dump(trace, f, indent=2)

    return file_path


def load_trace(alert_id: str):
    file_path = os.path.join(TRACE_DIR, f"{alert_id}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No trace found for alert_id={alert_id}")

    with open(file_path, "r") as f:
        return json.load(f)
