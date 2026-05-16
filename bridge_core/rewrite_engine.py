class RewriteEngine:
    """Contextual rewrite helpers for adaptive support."""

    def make_easier(self, text):
        return f"Do only the first tiny part: {text}"

    def break_smaller(self, text):
        return [
            "Open the document/app.",
            "Write one ugly line.",
            "Save progress.",
            f"Return to: {text}",
        ]

    def explain_differently(self, text, frame="gaming"):
        if frame == "gaming":
            return f"Treat this like a quest objective: {text}"
        if frame == "fitness":
            return f"Treat this like one training rep: {text}"
        if frame == "investing":
            return f"Treat this like a thesis checkpoint: {text}"
        return f"Try this approach instead: {text}"

    def give_example(self, task_type="essay"):
        examples = {
            "essay": "Example thesis: Social pressure changes identity through fear and belonging.",
            "study": "Example flashcard: Q: What is photosynthesis? A: Converting light into chemical energy.",
            "coding": "Example scaffold: create app.py, routes.py, templates/index.html",
        }
        return examples.get(task_type, "Example: start with one rough visible output.")

    def do_first_line(self, task_type="general"):
        examples = {
            "essay_writing": "First line: My essay is about the way this topic changes how people think or act.",
            "language_learning": "First line: Hola, me llamo ___.",
            "conversation": "First line: I want to talk about something that felt hard for me.",
            "professional": "First line: Recommendation: we should choose ___ because ___.",
            "coding_project": "First line: The smallest working version is ___.",
        }
        return examples.get(task_type, "First line: The smallest real piece I can write is ___.")
