import json
from datetime import datetime
from pathlib import Path

from bridge_engine.automation.autonomous_learning_cycle import AutonomousLearningCycle
from bridge_engine.discovery.data_source_cycle import DataSourceCycle
from bridge_engine.discovery.integration_scanner_cycle import IntegrationScannerCycle
from bridge_engine.discovery.module_discovery_cycle import ModuleDiscoveryCycle
from bridge_engine.discovery.path_recognition_cycle import PathRecognitionCycle
from bridge_engine.discovery.workflow_pattern_cycle import WorkflowPatternCycle
from bridge_engine.simulation.synthetic_runtime_simulator import SyntheticRuntimeSimulator


OUTPUT_PATH = Path("data/bridge_brain_daemon_latest.json")


class BridgeBrainDaemon:
    """Unified autonomous runner for Bridge Engine learning, discovery, and simulation cycles."""

    def run_once(self):
        results = {
            "updated_at": datetime.utcnow().isoformat(),
            "cycles": {},
        }

        results["cycles"]["autonomous_learning"] = AutonomousLearningCycle().run()
        results["cycles"]["module_discovery"] = ModuleDiscoveryCycle().run()
        results["cycles"]["data_source_discovery"] = DataSourceCycle().run()
        results["cycles"]["integration_scanner"] = IntegrationScannerCycle().run()
        results["cycles"]["path_recognition"] = PathRecognitionCycle().run()
        results["cycles"]["workflow_patterns"] = WorkflowPatternCycle().run()
        results["cycles"]["synthetic_runtime_simulation"] = SyntheticRuntimeSimulator().run()

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
            json.dump(results, outfile, indent=2)

        return {
            "status": "bridge_brain_complete",
            "output": str(OUTPUT_PATH),
            "cycle_count": len(results["cycles"]),
            "updated_at": results["updated_at"],
        }


if __name__ == "__main__":
    daemon = BridgeBrainDaemon()
    print(daemon.run_once())
