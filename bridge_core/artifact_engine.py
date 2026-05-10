from datetime import datetime


class ArtifactEngine:
    """Builds usable outputs from Bridge sessions."""

    def build_essay_outline(self, session):
        sections = session.get("artifact", {}).get("sections", {})

        return {
            "type": "essay_outline",
            "generated_at": datetime.utcnow().isoformat(),
            "title": session.get("task"),
            "outline": {
                "introduction": sections.get("thesis_seed", ""),
                "body_points": sections.get("support_points", ""),
                "draft_seed": sections.get("body_paragraph_seed", ""),
                "conclusion": "Restate thesis and explain why it matters.",
            },
        }

    def build_flashcards(self, topic, concepts):
        cards = []
        for concept in concepts:
            cards.append({
                "front": concept,
                "back": f"Definition/example for {concept}",
            })
        return {
            "topic": topic,
            "cards": cards,
        }

    def build_code_scaffold(self, project_name):
        return {
            "project": project_name,
            "files": [
                "app.py",
                "routes.py",
                "templates/index.html",
                "static/styles.css",
            ],
        }

    def export_markdown(self, title, content):
        return f"# {title}\n\n{content}\n"
