import json
import sys
import os

# Add parent directory to path so we can import trace_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trace_engine.rule_engine import RuleEngine

def run_test():
    engine = RuleEngine()

    with open("features/extracted_features.json", "r") as f:
        records = json.load(f)

    # Use only ONE record for demo clarity
    record = records[2]

    trace, path = engine.evaluate(record)

    print("Trace saved at:", path)
    print(json.dumps(trace, indent=2))

if __name__ == "__main__":
    run_test()
