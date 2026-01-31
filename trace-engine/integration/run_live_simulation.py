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
    
    
    # Collect all candidates first
    candidates = {k: [] for k in requirements}
    
    for event in feature_events:
        comp = event.get("component")
        phase = event.get("failure_phase")
        
        if comp in requirements and phase == requirements[comp]:
            candidates[comp].append(event)
            
    
    # Select the "most representative" event for each phase
    # - Normal: Low vibration (median/middle is fine)
    # - Pre-Failure: High trend/delta
    # - Failure: High RMS/Temp
    
    for comp, events in candidates.items():
        if not events:
            print(f"⚠️ No events found for {comp} (Phase {requirements[comp]})")
            continue
            
        target_event = None
        
        if comp == "PUMP":
             # Normal: Just pick middle
             target_event = events[min(len(events)//2, len(events)-1)]
             
        elif comp == "CONVEYOR":
             # Pre-Failure: Look for event that satisfies rules
             # Rules: Trend > 1.5 (+0.25), Spike > 0.8 (+0.2), Temp > 80 (+0.3)
             # We want BORDERLINE (score >= 0.1)
             target_event = events[0]
             max_conveyor_score = -1
             
             for e in events:
                 f = e["features"]
                 score = 0
                 if f.get("vibration_trend", 0) > 1.5: score += 0.25
                 if f.get("vibration_delta", 0) > 0.8: score += 0.2
                 
                 if score > max_conveyor_score:
                     max_conveyor_score = score
                     target_event = e
             
        elif comp == "COMPRESSOR":
             # Turn on Failure: Need DANGER (score >= 0.7)
             # Rules: Vib > 5.5 (+0.5), Temp > 50 (+0.2), Load > 85 (+0.35)
             target_event = events[0]
             max_comp_score = -1
             
             for e in events:
                 f = e["features"]
                 score = 0
                 if f.get("vibration_rms", 0) > 5.5: score += 0.5
                 if f.get("temperature_c", 0) > 50.0: score += 0.2
                 if f.get("load_avg", 0) > 85.0: score += 0.35
                 if f.get("temperature_delta", 0) > 5.0: score += 0.2
                 
                 if score > max_comp_score:
                     max_comp_score = score
                     target_event = e
        
        else:
             target_event = events[0]
             
        selected_events.append(target_event)
        found[comp] = True
            
    # Fallback: if specific phases not found, just take one of each component
    if not all(found.values()):
        print(f"⚠️ Could not find all exact phases. Found: {found}")
        # Try to fill gaps using any available event for valid components
        available_components = set(e.get("component") for e in feature_events)
        for k in requirements:
             if not found[k] and k in available_components:
                 # Find ANY event for this component
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
