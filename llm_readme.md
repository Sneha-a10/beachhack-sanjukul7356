# Explainability Agent – FLAN-T5 Large
## Overview

This notebook implements the Explainability Agent for our Industrial IoT Predictive Maintenance system.

The agent uses google/flan-t5-large to convert a deterministic decision trace into a clear, human-readable explanation suitable for maintenance engineers.

## Important:
The language model does not make decisions and does not reason over sensor data.
It only verbalizes already-recorded decision traces.

## Purpose of This File

Translate internal system decisions into engineering-friendly explanations

Improve trust, transparency, and interpretability

Avoid black-box or hallucinated explanations

Demonstrate explainable AI with auditability

This notebook focuses only on explanation generation, not prediction or maintenance actions.

## Input

The agent consumes a decision trace produced by the reasoning engine.

Example input (decision_trace):

decision_trace = {
    "decision": "EARLY_BEARING_DEGRADATION",
    "confidence": 0.82,
    "rules_triggered": [
        "VIBRATION_TREND_RULE",
        "THERMAL_CONFIRMATION_RULE"
    ],
    "intermediate_states": {
        "risk_after_vibration": 0.61,
        "risk_after_temperature": 0.82
    }
}


This trace is not passed directly to the LLM.

## Humanization Layer

Before explanation, the decision trace is deterministically translated into a human-safe, quantified representation.

This step:

Removes system terms (rules, states, internal scores)

Converts scores into physically meaningful descriptions

Preserves numeric insight in an engineer-friendly form

Example output of the humanization step:

{
  "observations": [
    "Vibration indicators increased, reaching a moderate level (around 61%).",
    "Temperature indicators increased, reaching a high level (around 82%)."
  ],
  "assessment": "The combined sensor behavior indicates internal mechanical wear in rotating components.",
  "decision": "Internal mechanical wear detected.",
  "confidence": "High confidence (82%)."
}

## Explanation Generation

The FLAN-T5 Large model receives only the human-safe trace and generates a natural language explanation.

Key constraints:

Low temperature decoding (to prevent hallucination)

No access to raw sensor data

No access to system logic or rules

Explanation must reflect cause → effect → conclusion

## Output

Example generated explanation:

“The machine shows a sustained increase in vibration, reaching a moderate level while operating under a stable load, indicating growing mechanical instability. This is followed by a temperature rise to a higher level, suggesting increased internal friction rather than normal operating variation. Together, these signs are consistent with early-stage bearing wear, and preventive maintenance is recommended.”

## Why FLAN-T5 Large?

Instruction-tuned and stable

Strong at structured-to-text transformation

Low hallucination risk

Suitable for constrained explainability tasks

Works well in hackathon environments

What This File Does NOT Do

❌ Predict failures
❌ Analyze raw sensor data
❌ Decide maintenance actions
❌ Modify system logic

Those responsibilities belong to other system layers.
