# Trace Engine — Decision Transparency Core

## What this component is

The **Trace Engine** is a deterministic decision recorder for industrial alerts.
It captures **how and why** an alert was triggered by recording every rule that fired, in order, with exact thresholds and confidence impact.

**This component is the source of truth for all alerts.**

---

## What problem it solves

In most predictive maintenance systems:
- Alerts are opaque.
- Engineers don’t know why something fired.
- Trust breaks down.

The Trace Engine fixes this by making every decision:
- **Inspectable**
- **Replayable**
- **Auditable**

**If an alert exists, a trace exists.**

---

## What the Trace Engine does

For each incoming feature record:

1.  **Receives** processed sensor features (not raw signals).
2.  **Applies** deterministic, human-defined rules.
3.  **For every rule that fires:**
    -   Records the feature value.
    -   Records the threshold.
    -   Records the comparison.
    -   Updates and records confidence.
4.  **Produces** a structured decision trace (JSON).

The trace shows **what happened**, **when it happened**, **why it happened**, and **how risk accumulated**.

### What it does NOT do

The Trace Engine does **not**:
- Run machine learning models.
- Generate natural language explanations.
- Suggest fixes.
- Infer causality.
- Learn or adapt rules.
- Modify data.

Explanation and remediation happen *after* the trace, using this output.

---

## Input contract

The Trace Engine expects a single feature record in this format:

```json
{
  "timestamp": "ISO-8601",
  "component": "PUMP | CONVEYOR | COMPRESSOR",
  "features": {
    "vibration_rms": float,
    "vibration_trend": float,
    "vibration_delta": float,
    "temperature_c": float,
    "temperature_delta": float,
    "load_avg": float
  }
}
```

*Feature extraction is handled upstream. The Trace Engine does not validate or correct features.*

---

## Output contract (decision trace)

Each alert produces exactly one decision trace:

```json
{
  "alert_id": "...",
  "component_id": "...",
  "timestamp": "...",
  "decision": "NORMAL | BORDERLINE | DANGER",
  "final_confidence": 0.0,
  "rules_triggered": [],
  "reasoning_trace": [
      {
          "step_id": 1,
          "rule": "RULE_NAME",
          "feature": "feature_name",
          "value": 0.0,
          "threshold": 0.0,
          "rule_result": "FIRED",
          "confidence_after_step": 0.0
      }
  ],
  "expected_behavior": "NORMAL",
  "observed_behavior": "DEGRADING",
  "expectation_mismatch": true
}
```

### Key fields
- **`reasoning_trace`**: Ordered list of fired rules with thresholds and confidence.
- **`final_confidence`**: Deterministic risk score (not probability).
- **`expectation_mismatch`**: Flags deviation from normal behavior.

---

## Confidence semantics

Confidence is a **deterministic risk score (0–1)**.
- Each fired rule adds a fixed amount.
- Confidence accumulates step-by-step.
- **It is not a probability.**

This makes risk progression visible and debuggable.

---

## Why this is not XAI

**Explainable AI (XAI)** tries to explain black-box models *after* a decision.

The **Trace Engine**:
- Records the decision *as it happens*.
- Does not guess explanations.
- Works even without ML.

**XAI explains models. The Trace Engine records decisions.**

---

## Why judges should care

With this component, a judge (or engineer) can:
1.  Point to an alert.
2.  Ask **“why?”**.
3.  See the exact reasoning path in seconds.
4.  Spot incorrect logic immediately.

**This builds real trust, not decorative explainability.**

---

## Demo notes

For the demo:
- Rules are **manually defined**.
- Thresholds are **static**.
- Data is **deterministic**.

This is intentional to maximize clarity and auditability.

---

## Summary

- If the Trace Engine is clear, the system is trustworthy.
- If the Trace Engine is vague, nothing else matters.

**This component makes system intelligence visible.**
