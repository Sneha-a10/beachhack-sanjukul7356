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
        # GENERALIZED LOGIC:
        # Convert any input dictionary into a flat list of text observations.
        observations = []
        
        # 1. Handle Lists (like 'recommended_action')
        for key, value in trace.items():
            formatted_key = key.replace("_", " ").capitalize()
            
            if isinstance(value, list):
                if value:
                    items = ", ".join(str(v) for v in value)
                    observations.append(f"{formatted_key}: {items}")
            elif isinstance(value, (str, int, float, bool)):
                observations.append(f"{formatted_key}: {value}")
            elif isinstance(value, dict):
                 # Flatten nested dicts simply for now
                 observations.append(f"{formatted_key}: {str(value)}")

        return {
            "observations": observations
        }

    def generate_explanation(self, decision_trace):
        human_trace = self._humanize_decision_trace(decision_trace)
        
        data_text = "\n".join([f"- {obs}" for obs in human_trace['observations']])

        prompt = f"""
Data:
{data_text}

Task: Rewrite ALL the data below into a single, comprehensive imperative paragraph. 
- You MUST include every recommendation and safety note provided.
- Start directly with action verbs (e.g., "Inspect...", "Ensure...").
- List each specific action required.

Instructions:
"""
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_length=200,
            do_sample=True,
            temperature=0.3, 
            top_p=0.95,
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

INPUT_FILE = "input_data.json"

def load_last_input(file_path):
    """Reads the JSON file and returns the last entry if it's a list."""
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' not found.")
        return None
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            if not data:
                print("Error: Input list is empty.")
                return None
            print(f"Loaded input file with {len(data)} entries. Processing the last one.")
            return data[-1]
        elif isinstance(data, dict):
            print("Input file contains a single entry.")
            return data
        else:
            print("Error: Input file format not supported (must be list or dict).")
            return None
            
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def main():
    # Load Input from File
    decision_trace = load_last_input(INPUT_FILE)
    
    if not decision_trace:
        print("Aborting: No valid input data found.")
        return

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
