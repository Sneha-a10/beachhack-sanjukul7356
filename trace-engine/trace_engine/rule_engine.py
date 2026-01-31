from datetime import datetime

from rules.rules_config import RULES
from trace_engine.trace_context import start_trace, end_trace
from trace_engine.trace_step import trace_step
from trace_engine.trace_persistence import save_trace


class RuleEngine:
    def __init__(self):
        pass

    def _compare(self, value, comparison, threshold):
        if comparison == ">":
            return value > threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == "<=":
            return value <= threshold
        else:
            raise ValueError(f"Unsupported comparison operator: {comparison}")

    def _decision_from_confidence(self, confidence):
        if confidence >= 0.7:
            return "DANGER"
        elif confidence >= 0.1:
            return "BORDERLINE"
        else:
            return "NORMAL"

    def evaluate(self, record: dict):
        """
        record format:
        {
          "timestamp": "...",
          "component": "PUMP | CONVEYOR | COMPRESSOR",
          "features": { ... }
        }
        """

        component = record["component"]
        features = record["features"]

        rules = RULES.get(component, [])
        if not rules:
            raise ValueError(f"No rules defined for component: {component}")

        # ---- START TRACE ----
        start_trace(component_id=component)

        confidence = 0.0
        step_id = 1

        # ---- RULE EVALUATION ----
        for rule in rules:
            feature_name = rule["feature"]
            feature_value = features.get(feature_name)

            # If feature missing, skip rule safely
            if feature_value is None:
                continue

            fired = self._compare(
                feature_value,
                rule["comparison"],
                rule["threshold"]
            )

            if fired:
                confidence += rule["confidence_delta"]
                confidence = min(confidence, 1.0)

                trace_step({
                    "step_id": step_id,
                    "rule": rule["rule"],
                    "feature": feature_name,
                    "feature_value": feature_value,
                    "threshold": rule["threshold"],
                    "comparison": rule["comparison"],
                    "rule_result": "FIRED",
                    "confidence_after_step": round(confidence, 2),
                    "timestamp": datetime.utcnow().isoformat()
                })

                step_id += 1

        # ---- FINAL DECISION ----
        decision = self._decision_from_confidence(confidence)

        expected_behavior = "NORMAL"
        observed_behavior = "NORMAL" if decision == "NORMAL" else "DEGRADING"

        trace = end_trace(
            decision=decision,
            final_confidence=round(confidence, 2),
            expected_behavior=expected_behavior,
            observed_behavior=observed_behavior
        )

        path = save_trace(trace)
        return trace, path
