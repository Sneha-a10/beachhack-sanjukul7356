RULES = {
    "PUMP": [
        {
            "rule": "PUMP_VIBRATION_CRITICAL",
            "feature": "vibration_rms",
            "comparison": ">",
            "threshold": 4.0,
            "confidence_delta": 0.35
        },
        {
            "rule": "PUMP_TEMP_SPIKE",
            "feature": "temperature_delta",
            "comparison": ">",
            "threshold": 5.0,
            "confidence_delta": 0.3
        },
        {
            "rule": "PUMP_OVERHEAT",
            "feature": "temperature_c",
            "comparison": ">",
            "threshold": 95.0,
            "confidence_delta": 0.4
        },
        {
            "rule": "PUMP_HIGH_LOAD",
            "feature": "load_avg",
            "comparison": ">",
            "threshold": 85.0,
            "confidence_delta": 0.2
        }
    ],
    "CONVEYOR": [
        {
            "rule": "CONVEYOR_VIB_TRENDING",
            "feature": "vibration_trend",
            "comparison": ">",
            "threshold": 1.5,
            "confidence_delta": 0.25
        },
        {
            "rule": "CONVEYOR_MOTOR_HEAT",
            "feature": "temperature_c",
            "comparison": ">",
            "threshold": 80.0,
            "confidence_delta": 0.3
        },
        {
            "rule": "CONVEYOR_LOAD_PEAK",
            "feature": "load_avg",
            "comparison": ">",
            "threshold": 90.0,
            "confidence_delta": 0.2
        },
        {
            "rule": "CONVEYOR_VIB_SPIKE",
            "feature": "vibration_delta",
            "comparison": ">",
            "threshold": 0.8,
            "confidence_delta": 0.2
        }
    ],
    "COMPRESSOR": [
        {
            "rule": "COMP_DISCHARGE_TEMP",
            "feature": "temperature_c",
            "comparison": ">",
            "threshold": 50.0,
            "confidence_delta": 0.2
        },
        {
            "rule": "COMP_VIB_INSTABILITY",
            "feature": "vibration_rms",
            "comparison": ">",
            "threshold": 7.44,
            "confidence_delta": 0.5
        },
        {
            "rule": "COMP_RAPID_WARMING",
            "feature": "temperature_delta",
            "comparison": ">",
            "threshold": 5.57,
            "confidence_delta": 0.2
        },
        {
            "rule": "COMP_OVERLOAD",
            "feature": "load_avg",
            "comparison": ">",
            "threshold": 98.28,
            "confidence_delta": 0.35
        }
    ]
}



def update_threshold(component_id: str, rule_name: str, new_threshold: float) -> bool:
    """
    Update the threshold for a specific rule in the RULES configuration.
    
    Args:
        component_id: The component (e.g., 'PUMP', 'CONVEYOR', 'COMPRESSOR')
        rule_name: The rule identifier (e.g., 'PUMP_VIBRATION_CRITICAL')
        new_threshold: The new threshold value to set
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    if component_id not in RULES:
        return False
    
    for rule in RULES[component_id]:
        if rule["rule"] == rule_name:
            rule["threshold"] = new_threshold
            return True
    
    return False

def get_threshold(component_id: str, rule_name: str) -> float:
    """
    Get the current threshold for a specific rule.
    
    Args:
        component_id: The component (e.g., 'PUMP', 'CONVEYOR', 'COMPRESSOR')
        rule_name: The rule identifier (e.g., 'PUMP_VIBRATION_CRITICAL')
        
    Returns:
        float: Current threshold value, or None if not found
    """
    if component_id not in RULES:
        return None
    
    for rule in RULES[component_id]:
        if rule["rule"] == rule_name:
            return rule["threshold"]
    
    return None

def save_rules_to_file(filepath: str = None) -> bool:
    """
    Save the current RULES configuration back to the rules_config.py file.
    
    Args:
        filepath: Path to the rules_config.py file. If None, uses current file location.
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    import os
    
    if filepath is None:
        filepath = __file__
    
    try:
        # Read the current file to preserve imports and structure
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find where RULES starts
        rules_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('RULES = {'):
                rules_start = i
                break
        
        if rules_start is None:
            return False
        
        # Generate new RULES content
        import json
        rules_str = "RULES = " + json.dumps(RULES, indent=4)
        
        # Replace old RULES with new one
        # Find the end of RULES dictionary
        rules_end = None
        brace_count = 0
        for i in range(rules_start, len(lines)):
            for char in lines[i]:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        rules_end = i
                        break
            if rules_end is not None:
                break
        
        if rules_end is None:
            return False
        
        # Reconstruct file
        new_content = ''.join(lines[:rules_start]) + rules_str + '\n\n' + ''.join(lines[rules_end + 1:])
        
        # Write back to file
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error saving rules: {e}")
        return False
