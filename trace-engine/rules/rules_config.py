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
            "threshold": 5.5,
            "confidence_delta": 0.5
        },
        {
            "rule": "COMP_RAPID_WARMING",
            "feature": "temperature_delta",
            "comparison": ">",
            "threshold": 5.0,
            "confidence_delta": 0.2
        },
        {
            "rule": "COMP_OVERLOAD",
            "feature": "load_avg",
            "comparison": ">",
            "threshold": 85.0,
            "confidence_delta": 0.35
        }
    ]
}
