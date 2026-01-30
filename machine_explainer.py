import json
import datetime
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Constants
MODEL_NAME = "google/flan-t5-large"
LOG_FILE = "interaction_logs.json"

SEVERITY_MAP = [
    (0.0, "low"),
    (0.4, "moderate"),
    (0.7, "high"),
    (0.9, "critical")
]

# Optional: Map technical codes to human-readable text if needed
DECISION_INTERPRETATIONS = {
    "EARLY_BEARING_DEGRADATION": "internal mechanical wear in rotating components",
    "OVERHEATING": "abnormal thermal behavior",
    "MISALIGNMENT": "shaft or coupling misalignment",
    "LUBRICATION_ISSUE": "insufficient or degraded lubrication"
}

class MachineExplainer:
    def __init__(self, model_name=MODEL_NAME):
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Model loaded on {self.device}.")

    def _score_to_level(self, score):
        for threshold, label in reversed(SEVERITY_MAP):
            if score >= threshold:
                return label
        return "low"

    def _score_to_percentage(self, score):
        return int(score * 100)

    def _humanize_decision_trace(self, trace):
        observations = []
        
        # Parse logic from the new 'reasoning_trace' list
        for step in trace.get("reasoning_trace", []):
            feature = step.get("feature", "Unknown Feature")
            val = step.get("feature_value", 0)
            
            # GENERALIZED LOGIC:
            # feature_value is the physical reading (e.g., 75 degrees, 0.61 mm/s)
            # confidence_after_step is the normalized risk score (0.0 - 1.0)
            
            risk_score = step.get("confidence_after_step", 0.0)
            threshold = step.get("threshold", 0)
            comparison = step.get("comparison", ">")
            
            # Use risk score for qualitative level (High/Low/Critical)
            level = self._score_to_level(risk_score)
            percentage = self._score_to_percentage(risk_score)
            
            # Infer ideal state for the explanation
            if comparison == ">":
                ideal = f"{threshold} or below"
            elif comparison == "<":
                ideal = f"{threshold} or above"
            else:
                ideal = f"{threshold}"
            
            # Construct a generalized observation
            observations.append(
                f"{feature.replace('_', ' ').capitalize()} reached {val} (ideal is {ideal}), indicating a {level} risk ({percentage}%)."
            )

        # Assessment based on behavior mismatch
        observed = trace.get("observed_behavior", "unknown behavior")
        expected = trace.get("expected_behavior", "normal behavior")
        
        if trace.get("expectation_mismatch", False):
            assessment = f"Observed {observed} instead of expected {expected}."
        else:
            assessment = f"Observed {observed}, matching expected {expected}."

        # Decision
        raw_decision = trace.get("decision", "Unknown Condition")
        decision_text = DECISION_INTERPRETATIONS.get(raw_decision, raw_decision.replace("_", " ").lower())
        
        # Confidence
        final_conf = trace.get("final_confidence", 0.0)
        confidence_str = f"{self._score_to_level(final_conf).capitalize()} confidence ({self._score_to_percentage(final_conf)}%)."

        return {
            "observations": observations,
            "assessment": assessment,
            "decision": f"{decision_text.capitalize()} detected.",
            "confidence": confidence_str
        }

    def generate_explanation(self, decision_trace):
        human_trace = self._humanize_decision_trace(decision_trace)
        
        obs_text = "\n".join([f"- {obs}" for obs in human_trace['observations']])

        prompt = f"""
Data:
- {human_trace['assessment']}
{obs_text}
- {human_trace['decision']}

Task: Write a detailed technical explanation of the machine status.
1. Start by mentioning the observed vs. expected behavior.
2. For each sensor, explicitly state what value was reached and contrast it with the ideal threshold (e.g., "Temperature reached X, but the ideal is Y").
3. Conclude with the detected condition.

Explanation:
"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_length=200,
            do_sample=True,
            temperature=0.2, 
            top_p=0.9,
            repetition_penalty=1.2,
            early_stopping=True
        )

        explanation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return explanation

    def log_interaction(self, input_trace, output_explanation):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "input_trace": input_trace,
            "output_explanation": output_explanation
        }

        # Append to existing log file or create new one
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
            except (json.JSONDecodeError, ValueError):
                logs = []
        else:
            logs = []

        logs.append(log_entry)

        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)
        
        print(f"Interaction logged to {LOG_FILE}")

def main():
    # New Schema Example Input
    decision_trace = {
        "alert_id": "ALT-1024",
        "sensor_id": "MTR-55",
        "timestamp": "2023-10-27T10:00:00Z",
        "decision": "EARLY_BEARING_DEGRADATION",
        "final_confidence": 0.82,
        "rules_triggered": [
            "VIBRATION_TREND_RULE",
            "THERMAL_CONFIRMATION_RULE"
        ],
        "reasoning_trace": [
            {
                "step_id": 1,
                "rule": "VIBRATION_TREND_RULE",
                "feature": "vibration_amplitude",
                "feature_value": 0.61,
                "threshold": 0.4,
                "comparison": ">",
                "rule_result": "FIRED",
                "confidence_after_step": 0.61,
                "timestamp": "2023-10-27T09:55:00Z"
            },
            {
                "step_id": 2,
                "rule": "THERMAL_CONFIRMATION_RULE",
                "feature": "bearing_temperature",
                "feature_value": 75.0,
                "threshold": 60.0,
                "comparison": ">",
                "rule_result": "FIRED",
                "confidence_after_step": 0.82,
                "timestamp": "2023-10-27T09:58:00Z"
            }
        ],
        "expected_behavior": "stable thermal profile under load",
        "observed_behavior": "rapid temperature spike",
        "expectation_mismatch": True
    }

    # Initialize Explainer
    explainer = MachineExplainer()

    # Generate Explanation
    print("\nGenerating explanation...")
    explanation = explainer.generate_explanation(decision_trace)
    
    # Print Result
    print("-" * 50)
    print("Generated Explanation:")
    print(explanation)
    print("-" * 50)

    # Log Interaction
    explainer.log_interaction(decision_trace, explanation)

if __name__ == "__main__":
    main()
