# ccai/core/reasoning.py

from typing import List

from ccai.core.graph import ConceptGraph
from ccai.core.models import Signal
from ccai.core.subsystems.base import Subsystem

class ReasoningCore:
    """
    Orchestrates the signal propagation process. It dispatches a signal
    to all subsystems and collects the results.
    """

    def __init__(self, graph: ConceptGraph, subsystems: List[Subsystem]):
        self.graph = graph
        self.subsystems = subsystems

    def process_signal(self, initial_signal: Signal) -> List[Signal]:
        """
        Processes an initial signal by sending it to all subsystems
        and returns a list of all resulting answer signals.
        """
        
        # The signal starts at its origin node.
        current_node = self.graph.get_node(initial_signal.origin)
        if not current_node:
            return []

        all_results = []
        
        # Dispatch the signal to all registered subsystems
        for subsystem in self.subsystems:
            # Subsystems are now responsible for their own logic, including recursion.
            confidence_delta, results = subsystem.evaluate(initial_signal, current_node)
            
            # We can apply the confidence delta if needed in the future
            # initial_signal.confidence += confidence_delta

            if results:
                all_results.extend(results)

        return all_results
