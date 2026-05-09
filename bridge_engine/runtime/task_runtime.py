from uuid import uuid4

from bridge_engine.runtime.runtime_state import RuntimeState
from bridge_engine.runtime.lane_store import LaneStore
from bridge_engine.runtime.feedback_router import FeedbackRouter
from bridge_engine.runtime.exporter import RuntimeExporter
from bridge_engine.services.task_classifier import TaskClassifier
from bridge_engine.services.semantic_planner import SemanticPlanner


class UniversalTaskRuntime:
    def __init__(self):
        self.store = LaneStore()
        self.feedback_router = FeedbackRouter()
        self.exporter = RuntimeExporter()
        self.classifier = TaskClassifier()
        self.planner = SemanticPlanner()

    def create_lane(self, goal, interest_frame, cognitive_mode):
        task_type = self.classifier.classify(goal)

        runtime = RuntimeState(
            lane_id=str(uuid4()),
            user_goal=goal,
            interest_frame=interest_frame,
            cognitive_mode=cognitive_mode,
            task_type=task_type,
        )

        runtime.update_status("understood")

        plan = self.planner.plan(task_type, goal)

        runtime.update_status("planned")
        runtime.next_best_action = plan["steps"][0]["title"]
        runtime.resume_point = runtime.next_best_action

        self.store.save_lane(runtime)

        return runtime, plan

    def submit_feedback(self, runtime, feedback):
        runtime = self.feedback_router.apply_feedback(runtime, feedback)
        runtime.update_status("continued")

        self.store.save_lane(runtime)

        return runtime

    def export(self, runtime, plan):
        runtime.update_status("completed/exported")

        markdown_path = self.exporter.export_markdown(runtime, plan)
        json_path = self.exporter.export_json(runtime, plan)

        self.store.save_lane(runtime)

        return {
            "markdown": markdown_path,
            "json": json_path,
        }
