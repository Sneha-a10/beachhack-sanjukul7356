# Requestly Mock Rules for Maintenance Agent

To enable the maintenance agent to dynamically retrieve the correct knowledge based on the decision, you should set up a **Modify Response** rule in Requestly.

## Recommended Approach: Dynamic JavaScript Rule
This single rule handles *all* supported decisions by checking the request body.

1.  **Rule Type**: Modify Response
2.  **Request URL**: Contains `/retrieve` (e.g., `http://dummy.local/retrieve`)
3.  **Request Method**: `POST`
4.  **Response Body Generation**: Select **Function** (JavaScript)

### Paste this JavaScript Code:
```javascript
function modifyResponse(args) {
  const { method, url, body, headers } = args.request;
  
  // Parse the incoming JSON body
  let decision = "UNKNOWN";
  try {
      const parsedBody = JSON.parse(body);
      decision = parsedBody.decision;
  } catch (e) {
      // fallback if body isn't valid JSON
  }

  // Define the Knowledge Base map
   knowledgeBase = {
      "EARLY_BEARING_DEGRADATION": {
          "id": "chunk_01",
          "text": "Early bearing degradation requires inspection of bearing housing, lubrication check, alignment verification, and preventive maintenance within 5–10 operating days.",
          "urgency": "Medium",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "VIBRATION_ONLY": {
          "id": "chunk_02",
          "text": "Sustained vibration without temperature rise may indicate imbalance or loose mounting. Immediate shutdown is not required. Inspect mounting bolts, base, and verify shaft alignment.",
          "urgency": "Low",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "VIBRATION_AND_TEMPERATURE": {
          "id": "chunk_03",
          "text": "Combined vibration and temperature increase indicates confirmed mechanical degradation. Schedule maintenance during planned downtime. Prepare spare components if available.",
          "urgency": "Medium",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "TEMPERATURE_ONLY": {
          "id": "chunk_04",
          "text": "Gradual temperature rise without vibration may indicate lubrication degradation or cooling inefficiency. Inspect lubrication pathways, verify cooling airflow, and check temperature sensor calibration.",
          "urgency": "Medium",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "RECIP_COMPRESSOR_EARLY": {
          "id": "chunk_05",
          "text": "Irregular vibration and moderate temperature rise in reciprocating compressors requires inspection of piston and bearing assemblies, lubrication flow verification, and valve clearance inspection.",
          "urgency": "Medium",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "SENSOR_INCONSISTENCY": {
          "id": "chunk_06",
          "text": "Sudden step changes or conflicting signals suggests sensor error. Validate sensor readings and cross-check with secondary sensors. Do not escalate maintenance prematurely.",
          "urgency": "Low",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "CONFIRMED_PROGRESSION": {
          "id": "chunk_07",
          "text": "Confirmed progression of degradation requires component replacement. Immediate intervention may be necessary if trend accelerates.",
          "urgency": "High",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      },
      "GLOBAL_SAFETY": {
          "id": "chunk_08",
          "text": "Before any inspection or maintenance activity, ensure power isolation, lock-out/tag-out procedures, and appropriate PPE usage.",
          "urgency": "High",
          "source": "Predictive Maintenance Knowledge Base.pdf"
      }
  };

  const match = knowledgeBase[decision];

  if (match) {
      return {
          results: [match]
      };
  } else {
      return {
          results: [],
          error: "No knowledge found for decision: " + decision
      };
  }
}
```

## Alternative: Static Rules (Manual)
If you prefer creating individual static rules for testing specific scenarios.

**URL**: `http://dummy.local/retrieve`
**Method**: `POST`

### 1. Early Bearing Degradation
**Response Body**:
```json
{
  "results": [
    {
        "id": "chunk_01",
        "decision": "EARLY_BEARING_DEGRADATION",
        "text": "Early bearing degradation requires inspection of bearing housing, lubrication check, alignment verification, and preventive maintenance within 5–10 operating days.",
        "urgency": "Medium",
        "source": "Predictive Maintenance Knowledge Base.pdf"
    }
  ]
}
```

### 2. Vibration Only
**Response Body**:
```json
{
  "results": [
    {
        "id": "chunk_02",
        "decision": "VIBRATION_ONLY",
        "text": "Sustained vibration without temperature rise may indicate imbalance or loose mounting. Immediate shutdown is not required. Inspect mounting bolts, base, and verify shaft alignment.",
        "urgency": "Low",
        "source": "Predictive Maintenance Knowledge Base.pdf"
    }
  ]
}
```
