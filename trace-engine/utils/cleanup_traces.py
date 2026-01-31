"""
Utility script to clean local trace artifacts.

This deletes all files inside the `traces/` directory.
Intended for local use only.
Run manually when you want a clean slate.
"""

import os

TRACE_DIR = "traces"


def cleanup_traces():
    if not os.path.exists(TRACE_DIR):
        print(f"No '{TRACE_DIR}' directory found. Nothing to clean.")
        return

    files = os.listdir(TRACE_DIR)
    if not files:
        print(f"'{TRACE_DIR}' is already empty.")
        return

    deleted = 0
    for file in files:
        file_path = os.path.join(TRACE_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted += 1

    print(f"Cleanup complete. Deleted {deleted} trace file(s).")


if __name__ == "__main__":
    cleanup_traces()
