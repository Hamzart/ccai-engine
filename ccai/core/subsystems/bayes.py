"""Subsystem performing simple Bayesian confidence updates."""

from typing import List, Tuple

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem


class BayesianUpdater(Subsystem):
    """Updates signal confidence using stored priors on nodes."""

    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        if signal.purpose != "OBSERVE":
            return 0.0, []

        key = signal.payload.get("relation")
        if not key:
            return 0.0, []

        likelihood = node.priors.get(key, 0.5)
        prior = signal.confidence
        posterior = likelihood * prior
        delta = posterior - prior
        signal.confidence = posterior
        return delta, []
