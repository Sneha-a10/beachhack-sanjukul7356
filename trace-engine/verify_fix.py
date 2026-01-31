import sys
import os

# Add trace-engine to path explicitly
current_dir = os.path.dirname(os.path.abspath(__file__))
# trace-engine is the current dir if I put this script there?
# Actually run_live_simulation.py expects "trace_engine" to be importable.
# If I am in `trace-engine/`, and I have `integration` and `trace_engine` (Wait, is the package named `trace_engine`?)
# Structure:
# IOT-Trace/
#   trace-engine/
#      integration/
#      trace_engine/ (maybe? or is it flat?)
#      ui/

# Let's check listing of trace-engine folder first.
sys.path.append(current_dir)

try:
    from integration.run_live_simulation import run_live_simulation
    print("Running sim...")
    res = run_live_simulation()
    print(f"Success! Result count: {len(res)}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
