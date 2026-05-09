from bridge_engine.adaptive.learning_cycle import AdaptiveLearningCycle
from bridge_engine.discovery.data_source_cycle import DataSourceCycle
from bridge_engine.discovery.integration_scanner_cycle import IntegrationScannerCycle
from bridge_engine.discovery.module_discovery_cycle import ModuleDiscoveryCycle
from bridge_engine.discovery.path_recognition_cycle import PathRecognitionCycle
from bridge_engine.discovery.workflow_pattern_cycle import WorkflowPatternCycle


def run_all():
    print("Running adaptive learning cycle...")
    AdaptiveLearningCycle().update_user(
        "system-demo",
        {
            "completion_speed": 2,
            "helped_count": 5,
            "too_much_count": 0,
            "continuation_count": 4,
        },
    )

    print("Running module discovery...")
    ModuleDiscoveryCycle().run()

    print("Running data source discovery...")
    DataSourceCycle().run()

    print("Running integration scanner...")
    IntegrationScannerCycle().run()

    print("Running path recognition...")
    PathRecognitionCycle().run()

    print("Running workflow pattern discovery...")
    WorkflowPatternCycle().run()

    print("All Bridge Engine discovery cycles complete.")


if __name__ == "__main__":
    run_all()
