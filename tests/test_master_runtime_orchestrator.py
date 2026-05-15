from bridge_core.master_runtime_orchestrator import MasterRuntimeOrchestrator


def build_workspace(category: str, task: str):
    return {
        "id": f"test-{category}",
        "category": category,
        "task": task,
        "artifact": {
            "final_output": "draft output"
        },
        "runtime_state": {},
    }


def test_spanish_music_runtime_contract():
    orchestrator = MasterRuntimeOrchestrator(
        profile={
            "interests": ["music", "gaming"],
            "learning_preferences": ["audio", "visual"],
        },
        context={
            "environment": "walking",
            "energy": "normal",
            "available_minutes": 15,
        },
    )

    contract = orchestrator.build_contract(
        build_workspace("language_learning", "Learn Spanish through music"),
        latest_output="I practiced greetings aloud.",
    )

    assert contract["verification"]
    assert contract["voice_runtime"]
    assert contract["pathways"]


def test_essay_gaming_runtime_contract():
    orchestrator = MasterRuntimeOrchestrator(
        profile={
            "interests": ["gaming"],
            "interaction_style": "student",
        }
    )

    contract = orchestrator.build_contract(
        build_workspace("essay_writing", "Write psychology essay"),
        latest_output="I finished my thesis outline.",
    )

    assert contract["interaction_runtime"]
    assert contract["challenge_chain"]


def test_coding_systems_runtime_contract():
    orchestrator = MasterRuntimeOrchestrator(
        profile={
            "interests": ["coding", "systems"],
            "interaction_style": "professional",
        }
    )

    contract = orchestrator.build_contract(
        build_workspace("coding_project", "Ship backend runtime"),
        latest_output="I built the orchestrator layer.",
    )

    assert contract["contextual_runtime"]
    assert contract["environmental_runtime"]
