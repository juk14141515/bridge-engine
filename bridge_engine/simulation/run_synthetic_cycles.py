import json
from pathlib import Path

from bridge_engine.simulation.synthetic_runtime_simulator import SyntheticRuntimeSimulator


OUTPUT_PATH = Path("data/synthetic_runtime_results.json")


def main():
    simulator = SyntheticRuntimeSimulator()
    results = simulator.run()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=2)

    print({
        "status": "simulation_complete",
        "output": str(OUTPUT_PATH),
        "count": results["simulation_count"],
    })


if __name__ == "__main__":
    main()
