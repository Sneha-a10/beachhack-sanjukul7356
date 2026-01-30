import sys
import os

# Add parent directory to path so we can import trace_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trace_engine.trace_context import start_trace, end_trace, get_active_trace
from trace_engine.trace_step import trace_step
from trace_engine.trace_persistence import save_trace, load_trace

def run_test():
    print("1. Starting trace...")
    trace = start_trace(component_id="TEST_COMPONENT_1")
    print(f"   Trace started with Alert ID: {trace['alert_id']}")
    
    print("2. Adding steps...")
    trace_step({
        "step_id": 1,
        "rule": "TEMP_CHECK",
        "feature": "temp",
        "value": 105,
        "threshold": 100,
        "outcome": "FAIL"
    })
    trace_step({
        "step_id": 2,
        "rule": "VIBRATION_CHECK",
        "feature": "vibration",
        "value": 2.5,
        "threshold": 5.0,
        "outcome": "PASS"
    })
    
    print("3. Ending trace...")
    completed_trace = end_trace(
        decision="ESCALATE",
        final_confidence=0.85,
        expected_behavior="NORMAL",
        observed_behavior="ABNORMAL"
    )
    
    print("4. Saving trace...")
    file_path = save_trace(completed_trace)
    print(f"   Saved to: {file_path}")
    
    print("5. Loading trace...")
    loaded_trace = load_trace(completed_trace["alert_id"])
    
    print("6. Verifying content...")
    assert loaded_trace["alert_id"] == completed_trace["alert_id"]
    assert len(loaded_trace["rules_triggered"]) == 2 # TEMP_CHECK and VIBRATION_CHECK
    assert "TEMP_CHECK" in loaded_trace["rules_triggered"]
    assert "VIBRATION_CHECK" in loaded_trace["rules_triggered"]
    assert loaded_trace["decision"] == "ESCALATE"
    
    print("SUCCESS: Trace engine end-to-end test passed!")

if __name__ == "__main__":
    run_test()