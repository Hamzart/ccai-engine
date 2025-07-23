"""Subsystem implementing fuzzy property matching."""

from difflib import SequenceMatcher
from typing import List, Tuple

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem


class FuzzyMatch(Subsystem):
    """Adjusts signal confidence based on approximate property matches."""

    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        if signal.purpose != "VERIFY" or signal.payload.get("relation") != "has_property":
            return 0.0, []

        target = signal.payload.get("target")
        best = 0.0
        for prop_list in node.properties.values():
            for spec in prop_list:
                if isinstance(spec.value, str):
                    sim = SequenceMatcher(None, target, spec.value).ratio()
                    best = max(best, sim)
        penalty = - (1 - best)
        return penalty, []
