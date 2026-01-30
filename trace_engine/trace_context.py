import uuid
from datetime import datetime

# ---- TRACE CREATION ----

def create_trace(component_id: str):
    return {
        "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
        "component_id": component_id,
        "timestamp": datetime.utcnow().isoformat(),

        "decision": None,
        "final_confidence": None,

        "rules_triggered": [],
        "reasoning_trace": [],

        "expected_behavior": None,
        "observed_behavior": None,
        "expectation_mismatch": None
    }


# ---- TRACE MUTATION ----

def add_trace_step(trace: dict, step_data: dict):
    trace["reasoning_trace"].append(step_data)

    rule_name = step_data.get("rule")
    if rule_name and rule_name not in trace["rules_triggered"]:
        trace["rules_triggered"].append(rule_name)


def finalize_trace(
    trace: dict,
    decision: str,
    final_confidence: float,
    expected_behavior: str,
    observed_behavior: str
):
    trace["decision"] = decision
    trace["final_confidence"] = final_confidence
    trace["expected_behavior"] = expected_behavior
    trace["observed_behavior"] = observed_behavior
    trace["expectation_mismatch"] = (expected_behavior != observed_behavior)


# ---- TRACE CONTEXT MANAGER ----

_active_trace = None


def start_trace(component_id: str):
    global _active_trace
    _active_trace = create_trace(component_id)
    return _active_trace


def get_active_trace():
    return _active_trace


def end_trace(
    decision: str,
    final_confidence: float,
    expected_behavior: str,
    observed_behavior: str
):
    global _active_trace

    if _active_trace is None:
        raise RuntimeError("No active trace to finalize")

    finalize_trace(
        _active_trace,
        decision,
        final_confidence,
        expected_behavior,
        observed_behavior
    )

    completed_trace = _active_trace
    _active_trace = None
    return completed_trace
