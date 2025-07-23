"""Subsystem detecting contradictory assertions."""

from typing import List, Tuple

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem


class ConflictResolver(Subsystem):
    """Looks for direct contradictions when asserting facts."""

    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        if signal.purpose != "ASSERT":
            return 0.0, []

        relation = signal.payload.get("relation")
        target = signal.payload.get("target")
        if not relation or not target:
            return 0.0, []

        contradictions = []
        existing = node.relations.get(relation, [])
        if target not in existing and existing:
            contradictions.append(existing[0])

        if contradictions:
            penalty = -1.0
            objection = signal.model_copy(deep=True)
            objection.payload = {"objection": f"conflicts with {contradictions[0]}"}
            return penalty, [objection]

        return 0.0, []
