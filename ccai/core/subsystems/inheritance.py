# ccai/core/subsystems/inheritance.py

import uuid
from typing import List, Tuple

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem

class InheritanceResolver(Subsystem):
    """
    A subsystem that resolves queries and verifies facts by traversing 
    'is_a' and 'inherits_from' relationships.
    """
    def evaluate(
        self, signal: Signal, node: ConceptNode
    ) -> Tuple[float, List[Signal]]:
        
        new_signals = []
        confidence_delta = 0.0
        parent_names = node.relations.get("is_a", []) + node.inherits_from

        # --- Handle QUERY signals (existing logic) ---
        if signal.purpose == "QUERY" and signal.payload.get("ask") == "relation.is_a":
            for parent_name in parent_names:
                new_signal = signal.model_copy(deep=True)
                new_signal.id = uuid.uuid4()
                new_signal.history.append((node.name, "found_parent", new_signal.confidence))
                new_signal.confidence *= 0.95
                new_signal.payload['answer'] = parent_name
                new_signals.append(new_signal)
        
        # --- Handle VERIFY signals (new logic) ---
        if signal.purpose == "VERIFY" and signal.payload.get("relation") == "is_a":
            # Check if the target is a direct parent of the current node
            if signal.payload.get("target") in parent_names:
                confirmation_signal = signal.model_copy()
                confirmation_signal.id = uuid.uuid4()
                confirmation_signal.payload['confirmed'] = True
                new_signals.append(confirmation_signal)
                return confidence_delta, new_signals

            # Track visited nodes to prevent infinite loops
            visited = set(signal.constraints.get("visited", []))
            visited.add(node.name)

            # Recurse up the hierarchy to verify against ancestors
            for parent_name in parent_names:
                if parent_name not in visited:
                    recursive_signal = signal.model_copy(deep=True)
                    recursive_signal.id = uuid.uuid4()
                    recursive_signal.origin = parent_name
                    recursive_signal.history.append((node.name, "verifying_parent", recursive_signal.confidence))
                    recursive_signal.constraints["visited"] = list(visited)
                    new_signals.append(recursive_signal)

        return confidence_delta, new_signals
