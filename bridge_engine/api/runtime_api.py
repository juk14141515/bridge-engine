from flask import Blueprint, jsonify, request

from bridge_engine.services.path_builder import PathBuilderService
from bridge_engine.runtime.task_runtime import UniversalTaskRuntime
from bridge_engine.runtime.feedback_runtime_adapter import FeedbackRuntimeAdapter
from bridge_engine.storage.lane_store import LaneStore
from bridge_engine.simulation.demo_runtime_lanes import DEMO_RUNTIME_LANES


runtime_api = Blueprint('runtime_api', __name__)

builder = PathBuilderService()
runtime = UniversalTaskRuntime()
feedback_adapter = FeedbackRuntimeAdapter()
lane_store = LaneStore()


@runtime_api.route('/api/tasks', methods=['POST'])
def create_task():
    payload = request.json or {}

    interest = payload.get('interest', 'general')
    learning_goal = payload.get('goal', 'task completion')

    workflow = builder.build(interest, learning_goal)
    runtime_state = runtime.initialize(workflow)

    runtime_state['title'] = workflow['title']
    runtime_state['steps'] = workflow['steps']

    lane_store.upsert_lane(runtime_state)

    return jsonify(runtime_state)


@runtime_api.route('/api/lanes', methods=['GET'])
def get_lanes():
    saved = lane_store.load()

    if saved:
        return jsonify(saved)

    return jsonify(DEMO_RUNTIME_LANES)


@runtime_api.route('/api/runtime/feedback', methods=['POST'])
def runtime_feedback():
    payload = request.json or {}

    runtime_state = payload.get('runtime_state', {})
    feedback = payload.get('feedback', 'helpful')

    updated = feedback_adapter.apply_feedback(runtime_state, feedback)

    lane_store.upsert_lane(updated)

    return jsonify(updated)


@runtime_api.route('/api/runtime/next', methods=['GET'])
def runtime_next():
    lanes = lane_store.load()

    if not lanes:
        return jsonify({'message': 'No runtime lanes'})

    return jsonify(lanes[0])
