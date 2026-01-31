"""
End-to-end live simulation orchestrator (Python-only).

Flow:
1. Run data_generated.py
2. Run feature_extraction.py
3. Load extracted_features.json
4. Select 2 feature events per component
5. Run Trace Engine
6. Return results for UI
"""

import json
import os
import subprocess
from trace_engine.rule_engine import RuleEngine


# -------------------------------------------------
# PATH CONFIG (data-n-sensor is a sibling folder)
# -------------------------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

DATA_SENSOR_DIR = os.path.join(BASE_DIR, "data-n-sensor")

DATA_GEN_SCRIPT = os.path.join(DATA_SENSOR_DIR, "data_generated.py")
FEATURE_SCRIPT = os.path.join(DATA_SENSOR_DIR, "feature_extraction.py")

FEATURE_JSON = os.path.join(DATA_SENSOR_DIR, "extracted_features.json")


# -------------------------------------------------
# MAIN ORCHESTRATION
# -------------------------------------------------

def run_live_simulation():
    import sys
    # 1️⃣ Run raw data generation
    subprocess.run(
        [sys.executable, DATA_GEN_SCRIPT],
        check=True,
        cwd=DATA_SENSOR_DIR  # Run inside data-n-sensor so files are saved there
    )

    # 2️⃣ Run feature extraction
    subprocess.run(
        [sys.executable, FEATURE_SCRIPT],
        check=True,
        cwd=DATA_SENSOR_DIR  # Run inside data-n-sensor so it finds the CSV and saves JSON there
    )

    # 3️⃣ Load extracted features
    if not os.path.exists(FEATURE_JSON):
        raise RuntimeError("extracted_features.json not found after feature extraction")

    with open(FEATURE_JSON, "r") as f:
        feature_events = json.load(f)

    if not isinstance(feature_events, list):
        raise ValueError("extracted_features.json must be a list")

    # 4️⃣ Select exactly 3 events: 1 Pump (Normal), 1 Conveyor (Pre-Failure), 1 Compressor (Failure)
    selected_events = []
    
    # Requirement:
    # - PUMP: Normal (Phase 0)
    # - CONVEYOR: Pre-Failure (Phase 2)
    # - COMPRESSOR: Failure Risk (Phase 3)
    
    requirements = {
        "PUMP": 0,
        "CONVEYOR": 2,
        "COMPRESSOR": 3
    }
    
    found = {k: False for k in requirements}
    
    # Shuffle or just find first match; finding first match is stable
    for event in feature_events:
        comp = event.get("component")
        phase = event.get("failure_phase")
        
        if comp in requirements and not found[comp]:
            if phase == requirements[comp]:
                selected_events.append(event)
                found[comp] = True
                
        if all(found.values()):
            break
            
    # Fallback: if specific phases not found, just take one of each component
    if not all(found.values()):
        print(f"⚠️ Could not find all exact phases. Found: {found}")
        # Try to fill gaps
        for k, v in found.items():
            if not v:
                # Find any event for this component
                for event in feature_events:
                    if event.get("component") == k:
                        selected_events.append(event)
                        break

    # 5️⃣ Run Trace Engine
    engine = RuleEngine()
    results = []

    for event in selected_events:
        trace, trace_path = engine.evaluate(event)
        results.append({
            "component": event["component"],
            "timestamp": event["timestamp"],
            "features": event["features"],
            "trace": trace,
            "trace_path": trace_path
        })

    return results
