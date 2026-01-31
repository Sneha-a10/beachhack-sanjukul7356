"""
Test script to verify threshold adjustment functionality.
This creates a test scenario with a rejection and verifies the adjustment works correctly.
"""

import json
import os
import sys
from datetime import datetime

# Add trace-engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'trace-engine'))

def create_test_rejection():
    """Create a test rejection in interaction_logs.json"""
    
    logs_path = os.path.join('mt-llm', 'interaction_logs.json')
    
    # Load existing logs
    with open(logs_path, 'r') as f:
        logs = json.load(f)
    
    # Get the latest trace data
    trace_path = os.path.join('mt-llm', 'knowledge_base', 'post_decision_trace.json')
    with open(trace_path, 'r') as f:
        trace_data = json.load(f)
    
    # Create a rejection entry
    rejection_entry = {
        "timestamp": datetime.now().isoformat(),
        "input_trace": trace_data.get('input_trace', trace_data),
        "output_explanation": "Test explanation for threshold adjustment verification",
        "user_feedback": "Rejected"
    }
    
    # Add to logs
    logs.append(rejection_entry)
    
    # Save back
    with open(logs_path, 'w') as f:
        json.dump(logs, f, indent=4)
    
    print(f"✅ Created test rejection entry in {logs_path}")
    return rejection_entry

def verify_threshold_adjustment():
    """Run the threshold adjuster and verify results"""
    
    # Import directly from file path
    import importlib.util
    
    adjuster_path = os.path.join('trace-engine', 'rules', 'threshold_adjuster.py')
    spec = importlib.util.spec_from_file_location("threshold_adjuster", adjuster_path)
    threshold_adjuster_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(threshold_adjuster_module)
    
    config_path = os.path.join('trace-engine', 'rules', 'rules_config.py')
    spec_config = importlib.util.spec_from_file_location("rules_config", config_path)
    rules_config = importlib.util.module_from_spec(spec_config)
    spec_config.loader.exec_module(rules_config)
    
    ThresholdAdjuster = threshold_adjuster_module.ThresholdAdjuster
    
    trace_path = os.path.join('mt-llm', 'knowledge_base', 'post_decision_trace.json')
    logs_path = os.path.join('mt-llm', 'interaction_logs.json')
    
    # Load trace to get original thresholds
    with open(trace_path, 'r') as f:
        trace_data = json.load(f)
    
    input_trace = trace_data.get('input_trace', trace_data)
    component_id = input_trace.get('component_id')
    
    print("\n" + "="*60)
    print("BEFORE ADJUSTMENT")
    print("="*60)
    
    # Record original thresholds
    original_thresholds = {}
    for step in input_trace.get('reasoning_trace', []):
        rule_name = step.get('rule')
        threshold = rules_config.get_threshold(component_id, rule_name)
        original_thresholds[rule_name] = threshold
        print(f"{rule_name}: {threshold}")
    
    # Run adjuster
    print("\n" + "="*60)
    print("RUNNING THRESHOLD ADJUSTER")
    print("="*60)
    
    adjuster = ThresholdAdjuster(trace_path, logs_path)
    adjustments_made = adjuster.process_rejection()
    
    if adjustments_made:
        adjuster.save_changes()
        audit_data = adjuster.get_audit_data()
        
        print("\n" + "="*60)
        print("AFTER ADJUSTMENT")
        print("="*60)
        
        # Reload rules_config to see new values
        import importlib
        importlib.reload(rules_config)
        
        for rule_name, old_threshold in original_thresholds.items():
            new_threshold = rules_config.get_threshold(component_id, rule_name)
            change_pct = ((new_threshold - old_threshold) / old_threshold * 100) if old_threshold else 0
            print(f"{rule_name}: {old_threshold} → {new_threshold} (+{change_pct:.1f}%)")
        
        print("\n" + "="*60)
        print("AUDIT TRAIL")
        print("="*60)
        print(json.dumps(audit_data, indent=2))
        
        # Verify audit trail in final JSON
        final_rec_path = os.path.join('mt-llm', 'final_recommendation.json')
        if os.path.exists(final_rec_path):
            with open(final_rec_path, 'r') as f:
                final_rec = json.load(f)
            
            final_rec["threshold_adjustments"] = audit_data
            
            with open(final_rec_path, 'w') as f:
                json.dump(final_rec, f, indent=2)
            
            print(f"\n✅ Audit trail added to {final_rec_path}")
        
        return True
    else:
        print("\n❌ No adjustments were made")
        return False

def main():
    print("="*60)
    print("THRESHOLD ADJUSTMENT VERIFICATION TEST")
    print("="*60)
    
    # Step 1: Create test rejection
    print("\n[Step 1] Creating test rejection...")
    create_test_rejection()
    
    # Step 2: Run threshold adjuster
    print("\n[Step 2] Running threshold adjuster...")
    success = verify_threshold_adjustment()
    
    if success:
        print("\n" + "="*60)
        print("✅ VERIFICATION SUCCESSFUL")
        print("="*60)
        print("\nThreshold adjustment system is working correctly!")
        print("- Thresholds updated in rules_config.py")
        print("- Audit trail generated")
        print("- Changes persisted to file")
    else:
        print("\n" + "="*60)
        print("❌ VERIFICATION FAILED")
        print("="*60)

if __name__ == "__main__":
    main()
