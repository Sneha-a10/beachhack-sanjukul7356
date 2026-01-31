#!/bin/bash

curl -X POST http://dummy.local/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "EARLY_BEARING_DEGRADATION"
  }'
