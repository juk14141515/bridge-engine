from abc import ABC, abstractmethod
from typing import Dict, List


class BaseExecutionModule(ABC):
    """Base class for adaptive execution modules."""

    module_name = "base"

    @abstractmethod
    def supports(self, interest: str, learning_goal: str) -> bool:
        pass

    @abstractmethod
    def generate_steps(self, interest: str, learning_goal: str) -> List[Dict]:
        pass

    def build_step(self, title: str, why: str, checkpoint: str):
        return {
            "title": title,
            "why": why,
            "checkpoint": checkpoint,
        }
