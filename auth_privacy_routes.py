"""
Bridge Engine Auth + Privacy Routes

Alpha-ready account/auth layer for friends/family testing.
This is intentionally lightweight and file-backed so it can be added before
moving to SQLite/Postgres user tables.

Routes:
- POST /api/auth/register
- POST /api/auth/login
- GET  /api/auth/me
- POST /api/auth/logout
- GET  /api/privacy
- GET  /api/privacy/export
- DELETE /api/privacy/delete

Security notes:
- Uses PBKDF2 password hashing, not plaintext passwords.
- Uses signed bearer tokens with BRIDGE_AUTH_SECRET.
- Before public beta, migrate to database-backed sessions and rate limiting.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional

from flask import jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = DATA_DIR / "users.json"
EVENTS_JSONL = DATA_DIR / "events.jsonl"
FEEDBACK_JSONL = DATA_DIR / "feedback.jsonl"
COACH_JSONL = DATA_DIR / "coach_conversations.jsonl"
MEMORY_JSONL = DATA_DIR / "semantic_memory_events.jsonl"

TOKEN_TTL_SECONDS = int(os.getenv("BRIDGE_TOKEN_TTL_SECONDS", str(60 * 60 * 24 * 14)))
PBKDF2_ITERATIONS = 210_000


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _secret() -> str:
    # Fine for alpha fallback; set BRIDGE_AUTH_SECRET before testers.
    return os.getenv("BRIDGE_AUTH_SECRET") or os.getenv("SECRET_KEY") or "bridge-engine-alpha-change-me"


def _load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_jsonl(path: Path, user_id: Optional[str] = None, limit: int = 1000):
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if user_id is None or item.get("user_id") == user_id:
            items.append(item)
    return items[-limit:]


def _rewrite_jsonl_without_user(path: Path, user_id: str) -> int:
    if not path.exists():
        return 0
    kept = []
    removed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if item.get("user_id") == user_id:
                removed += 1
                continue
        except Exception:
            pass
        kept.append(line)
    path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    return removed


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PBKDF2_ITERATIONS,
    ).hex()
    return {
        "algorithm": "pbkdf2_sha256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt,
        "hash": digest,
    }


def _verify_password(password: str, stored: Dict[str, Any]) -> bool:
    try:
        candidate = _hash_password(password, stored.get("salt"))
        return hmac.compare_digest(candidate["hash"], stored.get("hash", ""))
    except Exception:
        return False


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _unb64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_token(user: Dict[str, Any]) -> str:
    payload = {
        "user_id": user["id"],
        "email": user["email"],
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    raw = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(_secret().encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        raw, sig = token.split(".", 1)
        expected = hmac.new(_secret().encode("utf-8"), raw.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_unb64(raw).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def get_user_from_bearer(req=None) -> Optional[Dict[str, Any]]:
    req = req or request
    header = req.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        return None
    token_payload = decode_token(header.split(" ", 1)[1].strip())
    if not token_payload:
        return None
    users = _load_json(USERS_FILE, {"users": []}).get("users", [])
    for user in users:
        if user.get("id") == token_payload.get("user_id"):
            return {
                "id": user.get("id"),
                "email": user.get("email"),
                "display_name": user.get("display_name"),
                "role": user.get("role", "tester"),
            }
    return None


def require_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_user_from_bearer(request)
        if not user:
            return jsonify({
                "ok": False,
                "error": "auth_required",
                "message": "Use Authorization: Bearer <token>."
            }), 401
        request.bridge_user = user
        return fn(*args, **kwargs)
    return wrapper


def _public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "display_name": user.get("display_name"),
        "role": user.get("role", "tester"),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
        "privacy_settings": user.get("privacy_settings", {}),
    }


def register_auth_privacy_routes(app):
    @app.post("/api/auth/register")
    def api_auth_register():
        body = request.get_json(silent=True) if request.is_json else {}
        email = _normalize_email(body.get("email", ""))
        password = str(body.get("password", ""))
        display_name = str(body.get("display_name", "")).strip() or email.split("@")[0]

        if "@" not in email or len(password) < 8:
            return jsonify({
                "ok": False,
                "error": "invalid_registration",
                "message": "Email is required and password must be at least 8 characters."
            }), 400

        store = _load_json(USERS_FILE, {"users": []})
        if any(u.get("email") == email for u in store.get("users", [])):
            return jsonify({"ok": False, "error": "email_already_registered"}), 409

        user = {
            "id": f"user_{uuid.uuid4().hex[:12]}",
            "email": email,
            "display_name": display_name,
            "password": _hash_password(password),
            "role": "tester",
            "created_at": _now_iso(),
            "last_login_at": _now_iso(),
            "privacy_settings": {
                "personalization_enabled": True,
                "allow_behavior_memory": True,
                "allow_synthetic_training_comparison": True,
                "notification_intensity": "calm",
            },
        }
        store.setdefault("users", []).append(user)
        _save_json(USERS_FILE, store)
        token = create_token(user)
        return jsonify({"ok": True, "user": _public_user(user), "token": token}), 201

    @app.post("/api/auth/login")
    def api_auth_login():
        body = request.get_json(silent=True) if request.is_json else {}
        email = _normalize_email(body.get("email", ""))
        password = str(body.get("password", ""))
        store = _load_json(USERS_FILE, {"users": []})
        for user in store.get("users", []):
            if user.get("email") == email and _verify_password(password, user.get("password", {})):
                user["last_login_at"] = _now_iso()
                _save_json(USERS_FILE, store)
                return jsonify({"ok": True, "user": _public_user(user), "token": create_token(user)})
        return jsonify({"ok": False, "error": "invalid_credentials"}), 401

    @app.get("/api/auth/me")
    @require_user
    def api_auth_me():
        return jsonify({"ok": True, "user": request.bridge_user})

    @app.post("/api/auth/logout")
    @require_user
    def api_auth_logout():
        return jsonify({
            "ok": True,
            "message": "Client should delete the bearer token. Server tokens are stateless in alpha."
        })

    @app.get("/api/privacy")
    def api_privacy():
        return jsonify({
            "ok": True,
            "product": "Bridge Engine",
            "stage": "alpha",
            "plain_language": [
                "Bridge Engine uses your actions to personalize learning and execution support.",
                "The app should avoid shame-based productivity patterns.",
                "Before public beta, user data should move from JSON files to isolated database tables.",
                "Bridge Engine is not medical care, therapy, or emergency support."
            ],
            "data_collected": [
                "account email/display name",
                "paths and steps",
                "completion and start events",
                "feedback on interventions",
                "coach conversation snippets",
                "adaptive memory cards"
            ],
            "controls": {
                "export": "/api/privacy/export",
                "delete": "/api/privacy/delete",
                "auth_required": True
            }
        })

    @app.get("/api/privacy/export")
    @require_user
    def api_privacy_export():
        user = request.bridge_user
        user_id = user["id"]
        return jsonify({
            "ok": True,
            "exported_at": _now_iso(),
            "user": user,
            "events": _read_jsonl(EVENTS_JSONL, user_id=user_id, limit=5000),
            "feedback": _read_jsonl(FEEDBACK_JSONL, user_id=user_id, limit=5000),
            "coach_conversations": _read_jsonl(COACH_JSONL, user_id=user_id, limit=5000),
            "memory_events": _read_jsonl(MEMORY_JSONL, user_id=user_id, limit=5000),
        })

    @app.delete("/api/privacy/delete")
    @require_user
    def api_privacy_delete():
        user = request.bridge_user
        user_id = user["id"]
        store = _load_json(USERS_FILE, {"users": []})
        before = len(store.get("users", []))
        store["users"] = [u for u in store.get("users", []) if u.get("id") != user_id]
        _save_json(USERS_FILE, store)
        removed = {
            "users": before - len(store.get("users", [])),
            "events": _rewrite_jsonl_without_user(EVENTS_JSONL, user_id),
            "feedback": _rewrite_jsonl_without_user(FEEDBACK_JSONL, user_id),
            "coach_conversations": _rewrite_jsonl_without_user(COACH_JSONL, user_id),
            "memory_events": _rewrite_jsonl_without_user(MEMORY_JSONL, user_id),
        }
        return jsonify({
            "ok": True,
            "deleted_at": _now_iso(),
            "user_id": user_id,
            "removed": removed,
            "note": "Alpha deletion removes account and JSONL user events. Future database storage should enforce full cascading deletion."
        })

    return app
