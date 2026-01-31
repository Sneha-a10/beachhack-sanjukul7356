"""
Threshold Adjuster - Automatically adjust rule thresholds based on user feedback.

This script processes rejected alerts from interaction_logs.json and adjusts
the corresponding rule thresholds in rules_config.py to prevent future false positives.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path to import rules_config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from rules import rules_config

# Constants
SAFETY_MARGIN = 0.05  # 5% margin beyond rejected value
MAX_INCREASE_RATIO = 0.50  # Maximum 50% increase from original threshold

class ThresholdAdjuster:
    """Handles threshold adjustments based on rejected user feedback."""
    
    def __init__(self, trace_path: str, logs_path: str):
        """
        Initialize the threshold adjuster.
        
        Args:
            trace_path: Path to post_decision_trace.json
            logs_path: Path to interaction_logs.json
        """
        self.trace_path = trace_path
        self.logs_path = logs_path
        self.adjustments = []
    
    def load_json(self, filepath: str) -> Optional[Any]:
        """Load JSON file safely."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filepath}: {e}")
            return None
    
    def find_latest_rejection(self) -> Optional[Dict]:
        """
        Find the most recent rejected feedback in interaction logs.
        
        Returns:
            Dict containing the rejected interaction, or None if not found
        """
        logs = self.load_json(self.logs_path)
        if not logs or not isinstance(logs, list):
            return None
        
        # Search from most recent to oldest
        for entry in reversed(logs):
            if entry.get('user_feedback') == 'Rejected':
                return entry
        
        return None
    
    def get_alert_context(self) -> Optional[Dict]:
        """
        Load the alert context from post_decision_trace.json.
        
        Returns:
            Dict containing alert details including triggered rules and feature values
        """
        trace_data = self.load_json(self.trace_path)
        if not trace_data:
            return None
        
        # Handle nested structure
        if 'input_trace' in trace_data:
            return trace_data['input_trace']
        
        return trace_data
    
    def calculate_new_threshold(self, old_threshold: float, rejected_value: float) -> float:
        """
        Calculate new threshold based on rejected value with safety constraints.
        
        Args:
            old_threshold: Original threshold value
            rejected_value: The value that triggered the alert (now considered normal)
            
        Returns:
            float: New threshold value
        """
        # Add 5% safety margin beyond the rejected value
        new_threshold = rejected_value * (1 + SAFETY_MARGIN)
        
        # Apply maximum increase constraint (50% of original)
        max_allowed = old_threshold * (1 + MAX_INCREASE_RATIO)
        
        if new_threshold > max_allowed:
            print(f"  ⚠ Capping threshold increase at 50% of original value")
            new_threshold = max_allowed
        
        return round(new_threshold, 2)
    
    def process_rejection(self) -> bool:
        """
        Process the latest rejection and adjust thresholds accordingly.
        
        Returns:
            bool: True if adjustments were made, False otherwise
        """
        # Check for rejection
        rejection = self.find_latest_rejection()
        if not rejection:
            print("No rejected feedback found in interaction logs.")
            return False
        
        print(f"\n📋 Found rejection at: {rejection.get('timestamp')}")
        
        # Get alert context
        alert_context = self.get_alert_context()
        if not alert_context:
            print("Error: Could not load alert context.")
            return False
        
        component_id = alert_context.get('component_id')
        rules_triggered = alert_context.get('rules_triggered', [])
        reasoning_trace = alert_context.get('reasoning_trace', [])
        
        if not component_id or not rules_triggered:
            print("Error: Missing component_id or rules_triggered in alert context.")
            return False
        
        print(f"📊 Component: {component_id}")
        print(f"🔥 Rules triggered: {', '.join(rules_triggered)}")
        
        # Process each triggered rule
        adjustments_made = False
        for step in reasoning_trace:
            rule_name = step.get('rule')
            feature_value = step.get('feature_value')
            old_threshold = step.get('threshold')
            
            if not all([rule_name, feature_value is not None, old_threshold is not None]):
                continue
            
            # Calculate new threshold
            new_threshold = self.calculate_new_threshold(old_threshold, feature_value)
            
            print(f"\n🔧 Adjusting {rule_name}:")
            print(f"   Feature value (rejected): {feature_value}")
            print(f"   Old threshold: {old_threshold}")
            print(f"   New threshold: {new_threshold} (+{((new_threshold/old_threshold - 1) * 100):.1f}%)")
            
            # Update the threshold
            success = rules_config.update_threshold(component_id, rule_name, new_threshold)
            
            if success:
                # Record adjustment for audit trail
                self.adjustments.append({
                    "rule": rule_name,
                    "component": component_id,
                    "feature": step.get('feature'),
                    "old_threshold": old_threshold,
                    "new_threshold": new_threshold,
                    "rejected_value": feature_value,
                    "timestamp": datetime.now().isoformat(),
                    "reason": "User rejected alert - value now considered normal"
                })
                adjustments_made = True
                print(f"   ✅ Threshold updated successfully")
            else:
                print(f"   ❌ Failed to update threshold")
        
        return adjustments_made
    
    def save_changes(self) -> bool:
        """
        Save the updated thresholds back to rules_config.py.
        
        Returns:
            bool: True if save was successful
        """
        config_path = os.path.join(
            os.path.dirname(__file__),
            'rules_config.py'
        )
        
        print(f"\n💾 Saving changes to {config_path}...")
        success = rules_config.save_rules_to_file(config_path)
        
        if success:
            print("✅ Rules configuration updated successfully")
        else:
            print("❌ Failed to save rules configuration")
        
        return success
    
    def get_audit_data(self) -> List[Dict]:
        """
        Get the audit trail of all adjustments made.
        
        Returns:
            List of adjustment records for transparency
        """
        return self.adjustments


def main():
    """Main execution function."""
    # Determine paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    trace_path = os.path.join(project_root, '..', 'mt-llm', 'knowledge_base', 'post_decision_trace.json')
    logs_path = os.path.join(project_root, '..', 'mt-llm', 'interaction_logs.json')
    
    # Normalize paths
    trace_path = os.path.normpath(trace_path)
    logs_path = os.path.normpath(logs_path)
    
    print("=" * 60)
    print("THRESHOLD ADJUSTER - Processing User Feedback")
    print("=" * 60)
    
    # Initialize adjuster
    adjuster = ThresholdAdjuster(trace_path, logs_path)
    
    # Process rejection and adjust thresholds
    adjustments_made = adjuster.process_rejection()
    
    if adjustments_made:
        # Save changes to rules_config.py
        if adjuster.save_changes():
            # Output audit trail
            audit_data = adjuster.get_audit_data()
            print(f"\n📝 Audit Trail ({len(audit_data)} adjustments):")
            print(json.dumps(audit_data, indent=2))
            
            # Save audit trail to a file for reference
            audit_path = os.path.join(script_dir, 'threshold_adjustments.json')
            with open(audit_path, 'w') as f:
                json.dump(audit_data, f, indent=2)
            print(f"\n📄 Audit trail saved to: {audit_path}")
            
            return audit_data
        else:
            print("\n⚠ Adjustments calculated but not saved due to error.")
            return []
    else:
        print("\nℹ No threshold adjustments needed.")
        return []


if __name__ == "__main__":
    main()
