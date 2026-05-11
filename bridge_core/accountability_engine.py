from datetime import datetime


class AccountabilityEngine:
    """Optional accountability/social motivation layer.

    Designed to stay opt-in and low pressure.
    """

    def create_accountability_state(self, workspace_id, owner, enabled=False):
        return {
            "workspace_id": workspace_id,
            "enabled": enabled,
            "owner": owner,
            "partners": [],
            "shared_progress": [],
            "streak_visibility": False,
            "created_at": datetime.utcnow().isoformat(),
        }

    def add_partner(self, state, partner_name, role="friend"):
        state.setdefault("partners", []).append({
            "name": partner_name,
            "role": role,
            "joined_at": datetime.utcnow().isoformat(),
        })
        return state

    def share_progress(self, state, progress_payload):
        state.setdefault("shared_progress", []).append({
            "payload": progress_payload,
            "shared_at": datetime.utcnow().isoformat(),
        })
        return {
            "shared": True,
            "visibility": "optional",
            "message": "Progress shared with accountability partners.",
        }

    def generate_support_message(self, completion_rate):
        if completion_rate >= 100:
            return "Finished. Acknowledge the win and encourage consistency."
        if completion_rate >= 50:
            return "Momentum is building. Reinforce visible progress."
        if completion_rate > 0:
            return "Celebrate the fact that they started. Avoid pressure."
        return "Keep support low-pressure and focused on restarting gently."
