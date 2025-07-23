# ccai/core/reasoning.py

from typing import List

from ccai.core.signal_hub import SignalHub

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

    def process_signal(self, initial_signal: Signal, threshold: float = 0.1) -> List[Signal]:
        """Processes a signal queue until exhausted or below confidence."""
        hub = SignalHub()
        hub.push(initial_signal)
        answers: List[Signal] = []

        while not hub.empty():
            signal = hub.pop()
            if not signal or signal.confidence < threshold:
                continue
            node = self.graph.get_node(signal.origin)
            if not node:
                continue

            for subsystem in self.subsystems:
                delta, new_sigs = subsystem.evaluate(signal, node)
                signal.confidence += delta
                for ns in new_sigs:
                    hub.push(ns)
                for ns in new_sigs:
                    if "final_answer" in ns.payload or ns.payload.get("confirmed"):
                        answers.append(ns)

        return answers
