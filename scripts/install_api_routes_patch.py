"""
Safe installer for adaptive API routes.

This script patches app.py without requiring a manual merge.
It inserts:
    from api_routes import register_adaptive_api_routes
and:
    register_adaptive_api_routes(app)

Only inserts if missing.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_PATH = BASE_DIR / "app.py"

IMPORT_LINE = "from api_routes import register_adaptive_api_routes"
REGISTER_LINE = "register_adaptive_api_routes(app)"


def main():
    if not APP_PATH.exists():
        print({"ok": False, "error": "app.py not found"})
        return

    text = APP_PATH.read_text(encoding="utf-8")
    updated = text
    changed = False

    if IMPORT_LINE not in updated:
        marker = "app = Flask(__name__)"
        if marker in updated:
            updated = updated.replace(marker, f"{IMPORT_LINE}\n\n{marker}")
            changed = True

    if REGISTER_LINE not in updated:
        marker = "if __name__ == \"__main__\":"
        if marker in updated:
            updated = updated.replace(marker, f"\n\n{REGISTER_LINE}\n\n{marker}")
            changed = True

    if changed:
        APP_PATH.write_text(updated, encoding="utf-8")

    print({
        "ok": True,
        "changed": changed,
        "import_present": IMPORT_LINE in updated,
        "register_present": REGISTER_LINE in updated,
        "app_path": str(APP_PATH),
    })


if __name__ == "__main__":
    main()
