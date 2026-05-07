"""
Bridge Brain

Central orchestration layer for Bridge Engine.
Coordinates adaptive systems and autonomous workers.

Future responsibilities:
- scheduler orchestration
- recommendation fusion
- daily coach reports
- adaptive path generation
- context intelligence
- reward systems
- learning personalization
- recovery mode activation
"""

import subprocess
from datetime import datetime

ENGINES = [
    "scripts/automation_runner.py",
    "scripts/reward_loop_engine.py",
    "scripts/context_intelligence_engine.py",
    "scripts/path_effectiveness_engine.py",
    "scripts/adaptive_learning_engine.py",
]


def run_engine(path):
    print(f"Running: {path}")
    subprocess.run(["python", path], check=False)


if __name__ == "__main__":
    print(f"Bridge Brain start: {datetime.now()}")
    for engine in ENGINES:
        run_engine(engine)
    print(f"Bridge Brain complete: {datetime.now()}")
