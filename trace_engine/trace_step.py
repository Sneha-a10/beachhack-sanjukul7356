from trace_engine.trace_context import get_active_trace, add_trace_step

def trace_step(step_data: dict):
    trace = get_active_trace()
    if trace is None:
        raise RuntimeError("No active trace. Did you forget to start_trace()?")

    add_trace_step(trace, step_data)
