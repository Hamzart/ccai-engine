# ccai/core/subsystems/base.py

from abc import ABC, abstractmethod
from typing import List, Tuple

from ccai.core.models import Signal, ConceptNode

class Subsystem(ABC):
    """Abstract base class for all reasoning subsystems."""

    @abstractmethod
    def evaluate(
        self, signal: Signal, node: ConceptNode
    ) -> Tuple[float, List[Signal]]:
        """
        Processes a signal at a specific node.

        Args:
            signal: The signal currently being processed.
            node: The concept node the signal has arrived at.

        Returns:
            A tuple containing:
            - A float representing the change in confidence (delta).
            - A list of new signals to be spawned from this node.
        """
        pass