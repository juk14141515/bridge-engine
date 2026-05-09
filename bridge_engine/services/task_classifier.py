class TaskClassifier:
    def classify(self, text: str):
        lowered = text.lower()

        mappings = {
            "essay": ["paper", "essay", "research"],
            "coding": ["python", "coding", "assignment", "bug"],
            "language": ["spanish", "language", "translate"],
            "relationship": ["girlfriend", "partner", "relationship"],
            "presentation": ["slides", "presentation", "pitch"],
            "study": ["study", "exam", "quiz"],
        }

        for task_type, keywords in mappings.items():
            if any(keyword in lowered for keyword in keywords):
                return task_type

        return "project"
