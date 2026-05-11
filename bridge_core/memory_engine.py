from datetime import datetime


class MemoryEngine:
    """Self-learning memory layer for Bridge Engine.

    Stores patterns about what helps the user start, continue, and finish.
    This is intentionally simple for SQLite/JSON now and can later move to
    Postgres + embeddings/vector search.
    """

    def summarize_session(self, session):
        steps = session.get("steps", [])
        completed = [s for s in steps if s.get("status") == "done"]
        supports = session.get("supports", [])

        return {
            "session_id": session.get("id"),
            "task": session.get("task"),
            "frame": session.get("frame"),
            "supports": supports,
            "completed_steps": len(completed),
            "total_steps": len(steps),
            "completion_rate": int((len(completed) / max(1, len(steps))) * 100),
            "finished": len(completed) == len(steps) and len(steps) > 0,
            "created_at": datetime.utcnow().isoformat(),
        }

    def infer_preferences(self, memories):
        if not memories:
            return {
                "preferred_frames": [],
                "preferred_supports": [],
                "best_completion_pattern": None,
                "risk_flags": [],
            }

        frame_scores = {}
        support_scores = {}
        risk_flags = []

        for memory in memories:
            rate = memory.get("completion_rate", 0)
            frame = memory.get("frame")
            if frame:
                frame_scores[frame] = frame_scores.get(frame, 0) + rate
            for support in memory.get("supports", []):
                support_scores[support] = support_scores.get(support, 0) + rate
            if rate == 0:
                risk_flags.append("started_but_no_progress")
            elif rate < 50:
                risk_flags.append("partial_completion")

        preferred_frames = sorted(frame_scores, key=frame_scores.get, reverse=True)
        preferred_supports = sorted(support_scores, key=support_scores.get, reverse=True)

        return {
            "preferred_frames": preferred_frames[:3],
            "preferred_supports": preferred_supports[:5],
            "best_completion_pattern": preferred_frames[0] if preferred_frames else None,
            "risk_flags": sorted(set(risk_flags)),
            "updated_at": datetime.utcnow().isoformat(),
        }

    def next_adaptation(self, session_summary):
        rate = session_summary.get("completion_rate", 0)
        if rate == 0:
            return {
                "mode": "reduce_friction",
                "recommendation": "Use fewer choices, a smaller first step, and an example-first prompt.",
            }
        if rate < 50:
            return {
                "mode": "support_continuation",
                "recommendation": "Keep the same frame but break the next step smaller.",
            }
        if rate >= 100:
            return {
                "mode": "increase_confidence",
                "recommendation": "Offer a slightly harder next quest or export the finished artifact.",
            }
        return {
            "mode": "preserve_momentum",
            "recommendation": "Continue with a similar step size and visible progress marker.",
        }
