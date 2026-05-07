"""
Bridge Engine Adaptive Backend Brain

Purpose:
- Fuse real usage, synthetic usage, complex simulations, reward loops, context intelligence,
  and path effectiveness into one continuously learning backend layer.
- Promote path structures that work.
- Suppress path structures that repeatedly fail.
- Generate per-user/per-interest/per-requirement strategy profiles.
- Create smart path rules that future UI/API routes can consume.

This is still a prototype. It does not train a model yet; it builds a transparent rule/scoring layer
from structured data so the product can adapt safely before real users arrive.

Run manually:
    python scripts/adaptive_backend_brain.py

Recommended cron:
    */10 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/bridge_brain.py >> /home/ubuntu/bridge-engine/data/bridge_brain.log 2>&1
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUTS = {
    "real_paths": os.path.join(DATA_DIR, "bridge_paths.json"),
    "retention": os.path.join(DATA_DIR, "retention_metrics_latest.json"),
    "reward": os.path.join(DATA_DIR, "reward_loop_latest.json"),
    "context": os.path.join(DATA_DIR, "context_intelligence_latest.json"),
    "path_effectiveness": os.path.join(DATA_DIR, "path_effectiveness_latest.json"),
    "smart_filter": os.path.join(DATA_DIR, "smart_path_filter_latest.json"),
    "complex_filter": os.path.join(DATA_DIR, "complex_path_filter_latest.json"),
    "synthetic_rankings": os.path.join(DATA_DIR, "smart_path_rankings_latest.json"),
}

OUTPUT_FILE = os.path.join(DATA_DIR, "adaptive_backend_brain_latest.json")
RULES_FILE = os.path.join(DATA_DIR, "adaptive_path_rules_latest.json")
PROMOTION_FILE = os.path.join(DATA_DIR, "path_promotion_suppression_latest.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")


def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def progress_percent(path):
    steps = path.get("steps", [])
    if not steps:
        return 0
    done = len([s for s in steps if s.get("status") == "done"])
    return int((done / len(steps)) * 100)


def summarize_real_paths(paths):
    summary = {
        "total_paths": len(paths),
        "by_goal": {},
        "global": {
            "completed": 0,
            "started": 0,
            "abandoned": 0,
            "avg_progress": 0,
        }
    }
    progress_values = []
    for path in paths:
        goal = path.get("learning_goal") or path.get("goal") or path.get("interest") or "unknown"
        pct = progress_percent(path)
        progress_values.append(pct)
        bucket = summary["by_goal"].setdefault(goal, {"total": 0, "completed": 0, "started": 0, "abandoned": 0, "progress": []})
        bucket["total"] += 1
        bucket["progress"].append(pct)
        if pct == 100:
            bucket["completed"] += 1
            summary["global"]["completed"] += 1
        elif pct > 0:
            bucket["started"] += 1
            summary["global"]["started"] += 1
        else:
            bucket["abandoned"] += 1
            summary["global"]["abandoned"] += 1

    for bucket in summary["by_goal"].values():
        bucket["avg_progress"] = int(sum(bucket["progress"]) / len(bucket["progress"])) if bucket["progress"] else 0
        del bucket["progress"]
    summary["global"]["avg_progress"] = int(sum(progress_values) / len(progress_values)) if progress_values else 0
    return summary


def merge_filters(smart_filter, complex_filter):
    merged = []
    for item in smart_filter.get("filters", []):
        merged.append({
            "source": "smart_path_filter",
            "user_type": item.get("user_id"),
            "goal_id": item.get("goal_id"),
            "domain": item.get("goal_id"),
            "action": item.get("action"),
            "features": item.get("required_features", []),
            "avoid": item.get("avoid_features", []),
            "best_modality": item.get("best_modality"),
            "best_difficulty": item.get("best_difficulty"),
            "completion_rate": item.get("completion_rate", 0),
            "start_rate": item.get("start_rate", 0),
        })
    for item in complex_filter.get("filters", []):
        merged.append({
            "source": "complex_path_filter",
            "user_type": item.get("user_id"),
            "goal_id": item.get("scenario_id"),
            "domain": item.get("domain"),
            "action": item.get("action"),
            "features": item.get("recommended_structures", []),
            "avoid": [],
            "best_modality": None,
            "best_difficulty": None,
            "completion_rate": item.get("avg_completion", 0),
            "start_rate": max(0, 100 - item.get("overwhelm_rate", 0)),
            "overwhelm_rate": item.get("overwhelm_rate", 0),
        })
    return merged


def score_rule(item):
    completion = item.get("completion_rate", 0)
    start = item.get("start_rate", 0)
    overwhelm = item.get("overwhelm_rate", 0)
    return int((completion * 0.55) + (start * 0.30) - (overwhelm * 0.15))


def build_promotion_suppression(merged_filters):
    promoted = []
    watch = []
    suppressed = []

    for item in merged_filters:
        score = score_rule(item)
        record = {**item, "score": score}
        if score >= 65:
            promoted.append(record)
        elif score <= 30 or item.get("action") in ["micro_recovery_first", "needs_recovery_first"]:
            watch.append(record)
        else:
            watch.append(record)

        if item.get("completion_rate", 0) < 20 and item.get("start_rate", 0) < 45:
            suppressed.append({
                **record,
                "reason": "Low start and completion rates. Do not default this structure until redesigned.",
            })

    return {
        "promoted": sorted(promoted, key=lambda x: x["score"], reverse=True)[:50],
        "watch": sorted(watch, key=lambda x: x["score"])[:50],
        "suppressed": sorted(suppressed, key=lambda x: x["score"])[:50],
    }


def build_adaptive_rules(merged_filters, reward, context, retention):
    rules = []
    reward_plan = reward.get("reward_plan", {})
    context_rec = context.get("recommendation", {})

    for item in merged_filters:
        score = score_rule(item)
        if score < 25:
            continue
        rules.append({
            "rule_id": f"{item.get('source')}::{item.get('user_type')}::{item.get('goal_id')}",
            "user_type": item.get("user_type"),
            "goal_id": item.get("goal_id"),
            "domain": item.get("domain"),
            "priority_score": score,
            "path_action": item.get("action"),
            "prefer_features": item.get("features", []),
            "avoid_features": item.get("avoid", []),
            "preferred_modality": item.get("best_modality") or context_rec.get("best_environment"),
            "preferred_difficulty": item.get("best_difficulty") or "adaptive",
            "recommended_task_size": reward_plan.get("task_size", "small"),
            "recommended_reward_frequency": reward_plan.get("reward_frequency", "steady"),
            "fallback_if_stuck": "Use recovery mode, lower task size, and create one visible artifact or one clear checkpoint.",
        })

    rules = sorted(rules, key=lambda x: x["priority_score"], reverse=True)

    global_rules = [
        {
            "rule_id": "global::low_completion_recovery",
            "condition": "completion_rate_below_30",
            "action": "default_to_micro_start_and_recovery_mode",
            "active": retention.get("completion_rate", 0) < 30,
        },
        {
            "rule_id": "global::high_momentum_scale",
            "condition": "high_start_rate_and_flow",
            "action": "offer_keep_going_or_challenge_mode_with_stop_checkpoint",
            "active": retention.get("start_rate", 0) >= 70 and retention.get("flow_events", 0) > 0,
        },
        {
            "rule_id": "global::avoid_shame",
            "condition": "abandoned_or_overdue_tasks",
            "action": "show_restart_path_not_failure_dashboard",
            "active": True,
        },
    ]

    return {"global_rules": global_rules, "path_rules": rules[:100]}


def build_next_path_strategy(rules, promotion):
    top_rules = rules.get("path_rules", [])[:10]
    return {
        "generated_at": now_stamp(),
        "strategy": "Generate new paths from promoted structures first, then personalize by context/reward/user type. Suppress structures with repeated low start+completion.",
        "best_default_features": collect_top_features(promotion.get("promoted", [])),
        "safe_recovery_defaults": ["micro_start", "clear_checkpoint", "recovery_mode", "low_text", "visible_artifact"],
        "top_path_rules": top_rules,
        "do_not_default": promotion.get("suppressed", [])[:10],
    }


def collect_top_features(promoted):
    counts = {}
    for item in promoted:
        for feature in item.get("features", []):
            counts[feature] = counts.get(feature, 0) + 1
    return [name for name, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]]


def add_notification(payload):
    notifications = load_json(NOTIFICATIONS_FILE, [])
    notifications.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": "adaptive_backend_brain",
        "title": "Adaptive backend brain updated",
        "message": f"Promoted {len(payload['promotion']['promoted'])} path structures; watching {len(payload['promotion']['watch'])}; suppressed {len(payload['promotion']['suppressed'])} weak structures.",
        "priority": "normal",
        "created_at": now_stamp(),
        "read": False,
    })
    save_json(NOTIFICATIONS_FILE, notifications[-100:])


def main():
    real_paths = load_json(INPUTS["real_paths"], [])
    retention = load_json(INPUTS["retention"], {})
    reward = load_json(INPUTS["reward"], {})
    context = load_json(INPUTS["context"], {})
    path_effectiveness = load_json(INPUTS["path_effectiveness"], {})
    smart_filter = load_json(INPUTS["smart_filter"], {})
    complex_filter = load_json(INPUTS["complex_filter"], {})
    synthetic_rankings = load_json(INPUTS["synthetic_rankings"], {})

    real_summary = summarize_real_paths(real_paths)
    merged = merge_filters(smart_filter, complex_filter)
    promotion = build_promotion_suppression(merged)
    rules = build_adaptive_rules(merged, reward, context, retention)
    next_strategy = build_next_path_strategy(rules, promotion)

    payload = {
        "generated_at": now_stamp(),
        "purpose": "Continuously fuse real/synthetic/context/reward data into adaptive path rules.",
        "real_summary": real_summary,
        "retention": retention,
        "reward_plan": reward.get("reward_plan", {}),
        "context_recommendation": context.get("recommendation", {}),
        "path_effectiveness_summary": path_effectiveness.get("recommendations", []),
        "synthetic_event_count": synthetic_rankings.get("total_events", 0),
        "merged_filter_count": len(merged),
        "promotion": promotion,
        "rules_summary": {
            "global_rules": len(rules["global_rules"]),
            "path_rules": len(rules["path_rules"]),
        },
        "next_path_strategy": next_strategy,
        "guardrails": [
            "Do not treat synthetic data as real traction.",
            "Promote structures transparently based on start/completion/friction signals.",
            "Suppress harmful or ineffective structures instead of pressuring users harder.",
            "Default to recovery and clarity when confidence is low.",
            "Optimize for sustainable progress, not addictive screen time."
        ]
    }

    save_json(OUTPUT_FILE, payload)
    save_json(RULES_FILE, rules)
    save_json(PROMOTION_FILE, promotion)
    add_notification(payload)

    print(json.dumps({
        "ok": True,
        "generated_at": payload["generated_at"],
        "merged_filter_count": payload["merged_filter_count"],
        "promoted": len(promotion["promoted"]),
        "watch": len(promotion["watch"]),
        "suppressed": len(promotion["suppressed"]),
        "path_rules": len(rules["path_rules"]),
        "best_default_features": next_strategy["best_default_features"],
    }, indent=2))


if __name__ == "__main__":
    main()
