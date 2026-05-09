from pprint import pprint

from bridge_engine.runtime.task_runtime import UniversalTaskRuntime


runtime_engine = UniversalTaskRuntime()

runtime, plan = runtime_engine.create_lane(
    goal="I need to write a psychology paper but I keep avoiding it",
    interest_frame="film",
    cognitive_mode="adhd_mode",
)

print("\n=== CREATED RUNTIME ===")
pprint(runtime.__dict__)

print("\n=== PLAN ===")
pprint(plan)

runtime = runtime_engine.submit_feedback(runtime, "too_much")

print("\n=== ADAPTED RUNTIME ===")
pprint(runtime.__dict__)

exports = runtime_engine.export(runtime, plan)

print("\n=== EXPORTS ===")
pprint(exports)
