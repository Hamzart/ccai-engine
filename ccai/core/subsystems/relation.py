# ccai/core/subsystems/relation.py

import uuid
from typing import List, Tuple, TYPE_CHECKING

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem

# Avoid circular import for type hints
if TYPE_CHECKING:
    from ccai.core.graph import ConceptGraph


class RelationResolver(Subsystem):
    """
    A general-purpose subsystem that finds and verifies relationships
    (has_part, can_do, etc.) and properties, including inherited ones.
    """
    def __init__(self, graph: "ConceptGraph"):
        """Initializes the resolver with a reference to the main graph."""
        self.graph = graph

    def evaluate(
        self, signal: Signal, node: ConceptNode
    ) -> Tuple[float, List[Signal]]:
        
        # This subsystem is now fully recursive, so we don't need to return new signals.
        # We will build a list of final answers directly.
        final_answers = []
        confidence_delta = 0.0

        # --- Handle QUERY signals ---
        if signal.purpose == "QUERY" and signal.payload.get("ask_relation"):
            relation_to_find = signal.payload["ask_relation"]
            found_targets = self._find_relations_recursively(node, relation_to_find, set())
            for target in found_targets:
                final_answers.append(self._create_answer_signal(signal, node, target))

        # --- Handle VERIFY signals ---
        if signal.purpose == "VERIFY" and signal.payload.get("relation"):
            relation_to_verify = signal.payload["relation"]
            target_to_verify = signal.payload["target"]
            
            if self._verify_relation_recursively(node, relation_to_verify, target_to_verify, set()):
                confirmation_signal = signal.model_copy()
                confirmation_signal.id = uuid.uuid4()
                confirmation_signal.payload['confirmed'] = True
                final_answers.append(confirmation_signal)

        return confidence_delta, final_answers

    def _find_relations_recursively(self, node: ConceptNode, relation: str, visited: set) -> set:
        """Recursively finds all matching relations up the inheritance chain."""
        if node.name in visited:
            return set()
        visited.add(node.name)

        found = set()
        
        # 1. Find direct relations on the current node
        all_relations = {**node.relations, **node.structure, **node.functions}
        if relation in all_relations:
            found.update(all_relations[relation])
        
        if relation == "has_property":
            for prop_list in node.properties.values():
                for prop_spec in prop_list:
                    found.add(prop_spec.value)

        # 2. Recurse up the parent chain
        for parent_name in node.relations.get("is_a", []) + node.inherits_from:
            parent_node = self.graph.get_node(parent_name)
            if parent_node:
                found.update(self._find_relations_recursively(parent_node, relation, visited))
        
        return found

    def _verify_relation_recursively(self, node: ConceptNode, relation: str, target: str, visited: set) -> bool:
        """Recursively checks if a relation is true, searching up the inheritance chain."""
        if node.name in visited:
            return False
        visited.add(node.name)

        # 1. Check for direct relation on the current node
        all_relations = {**node.relations, **node.structure, **node.functions}
        if relation in all_relations and target in all_relations[relation]:
            return True
            
        if relation == "has_property":
            for prop_list in node.properties.values():
                if any(prop.value == target for prop in prop_list):
                    return True

        # 2. If not found, recurse up the parent chain
        for parent_name in node.relations.get("is_a", []) + node.inherits_from:
            parent_node = self.graph.get_node(parent_name)
            if parent_node:
                if self._verify_relation_recursively(parent_node, relation, target, visited):
                    return True
        
        return False

    def _create_answer_signal(self, original_signal: Signal, at_node: ConceptNode, answer: str) -> Signal:
        """Helper to create a final answer signal."""
        answer_signal = original_signal.model_copy(deep=True)
        answer_signal.id = uuid.uuid4()
        answer_signal.history.append((at_node.name, "found_relation", answer_signal.confidence))
        answer_signal.payload['final_answer'] = answer
        return answer_signal
