"""
Bridge Brain Safe Runner

Central orchestration layer for Bridge Engine.
Uses sys.executable so cron runs each engine with the active virtualenv Python,
avoiding VPS errors where the `python` binary is missing.

Recommended cron:
*/10 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/bridge_brain_safe.py >> /home/ubuntu/bridge-engine/data/bridge_brain.log 2>&1
"""

import subprocess
import sys
from datetime import datetime

ENGINES = [
    "scripts/automation_runner.py",
    "scripts/reward_loop_engine.py",
    "scripts/context_intelligence_engine.py",
    "scripts/path_effectiveness_engine.py",
    "scripts/adaptive_learning_engine.py",
    "scripts/adaptive_backend_brain.py",
    "scripts/smart_path_simulation_engine.py",
    "scripts/complex_path_simulation_engine.py",
]


def run_engine(path):
    print(f"Running: {path}")
    result = subprocess.run([sys.executable, path], check=False)
    if result.returncode != 0:
        print(f"WARNING: {path} exited with code {result.returncode}")


if __name__ == "__main__":
    print(f"Bridge Brain Safe start: {datetime.now()}")
    print(f"Using Python interpreter: {sys.executable}")
    for engine in ENGINES:
        run_engine(engine)
    print(f"Bridge Brain Safe complete: {datetime.now()}")
