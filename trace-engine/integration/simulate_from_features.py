"""
Simulation runner that connects feature extraction output
to the Trace Engine.

This script:
- Loads extracted_features.json (produced by notebooks)
- Feeds feature events to the Rule Engine
- Generates decision traces

This is intentionally event-based (not streaming)
for demo clarity and inspectability.
"""

import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trace_engine.rule_engine import RuleEngine


# -------- CONFIG --------

# Path to feature extraction output
FEATURE_FILE_PATH = "../data-n-sensor/extracted_features.json"

# Number of events to simulate in demo
MAX_EVENTS = 4


# -------- MAIN LOGIC --------

def run_simulation():
    if not os.path.exists(FEATURE_FILE_PATH):
        raise FileNotFoundError(
            f"Feature file not found at {FEATURE_FILE_PATH}. "
            "Run feature extraction notebook first."
        )

    with open(FEATURE_FILE_PATH, "r") as f:
        feature_events = json.load(f)

    if not isinstance(feature_events, list):
        raise ValueError("Expected extracted_features.json to be a list of records")

    engine = RuleEngine()

    print("\n=== TRACE ENGINE SIMULATION START ===\n")

    for idx, event in enumerate(feature_events[:MAX_EVENTS]):
        print(f"\n--- EVENT {idx + 1} ---")
        print(f"Component: {event.get('component')}")
        print("Features:")
        print(json.dumps(event.get("features", {}), indent=2))

        trace, trace_path = engine.evaluate(event)

        print("\nDecision:", trace["decision"])
        print("Confidence:", trace["final_confidence"])
        print("Trace saved at:", trace_path)

        if trace["reasoning_trace"]:
            print("\nReasoning Trace:")
            for step in trace["reasoning_trace"]:
                print(
                    f"  Step {step['step_id']}: {step['rule']} | "
                    f"{step['feature']} {step['comparison']} {step['threshold']} "
                    f"(value={step['feature_value']})"
                )
        else:
            print("\nReasoning Trace: <EMPTY – NORMAL OPERATION>")

    print("\n=== TRACE ENGINE SIMULATION END ===\n")


if __name__ == "__main__":
    run_simulation()
