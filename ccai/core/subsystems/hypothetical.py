"""Subsystem implementing hypothetical reasoning."""

from typing import List, Tuple, Dict, Any, Optional
import logging
import copy

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem
from ccai.core.graph import ConceptGraph

# Set up logging
logger = logging.getLogger(__name__)


class HypotheticalReasoner(Subsystem):
    """
    Performs hypothetical reasoning for "what if" scenarios.
    
    This subsystem can:
    1. Create temporary modifications to the concept graph
    2. Reason about hypothetical scenarios
    3. Handle counterfactual reasoning
    """
    
    def __init__(self, graph: ConceptGraph):
        """
        Initialize the hypothetical reasoner.
        
        Args:
            graph: The concept graph to reason over
        """
        self.graph = graph
    
    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        """
        Evaluate a signal using hypothetical reasoning.
        
        Args:
            signal: The signal to evaluate
            node: The node corresponding to the signal's origin
            
        Returns:
            Tuple of (confidence_delta, new_signals)
        """
        new_signals = []
        confidence_delta = 0.0
        
        # Handle "what if" queries
        if signal.purpose == "QUERY" and signal.payload.get("query_type") == "what_if":
            # Extract the hypothetical condition
            condition = signal.payload.get("condition", {})
            if not condition:
                return 0.0, []
            
            # Create a temporary copy of the node for hypothetical reasoning
            temp_node = copy.deepcopy(node)
            
            # Apply the hypothetical condition
            self._apply_condition(temp_node, condition)
            
            # Perform reasoning on the modified node
            result = self._reason_with_modified_node(temp_node, signal.payload.get("question"))
            
            if result:
                hypothetical_signal = signal.model_copy(deep=True)
                hypothetical_signal.payload["final_answer"] = result
                new_signals.append(hypothetical_signal)
        
        # Handle counterfactual queries
        elif signal.purpose == "QUERY" and signal.payload.get("query_type") == "counterfactual":
            # Extract the counterfactual condition
            condition = signal.payload.get("condition", {})
            if not condition:
                return 0.0, []
            
            # Create a temporary copy of the node for counterfactual reasoning
            temp_node = copy.deepcopy(node)
            
            # Apply the counterfactual condition (opposite of reality)
            self._apply_counterfactual(temp_node, condition)
            
            # Perform reasoning on the modified node
            result = self._reason_with_modified_node(temp_node, signal.payload.get("question"))
            
            if result:
                counterfactual_signal = signal.model_copy(deep=True)
                counterfactual_signal.payload["final_answer"] = result
                new_signals.append(counterfactual_signal)
        
        return confidence_delta, new_signals
    
    def _apply_condition(self, node: ConceptNode, condition: Dict[str, Any]) -> None:
        """
        Apply a hypothetical condition to a node.
        
        Args:
            node: The node to modify
            condition: The condition to apply
        """
        # Handle property modifications
        if "property" in condition:
            prop_name = condition["property"]
            prop_value = condition["value"]
            
            # Create or update the property
            if prop_name not in node.property_stats:
                node.property_stats[prop_name] = {}
            
            node.property_stats[prop_name] = {prop_value: 1}
            
            # Update the property specs
            node.properties[prop_name] = [{
                "value": prop_value,
                "score": 1.0
            }]
        
        # Handle relation modifications
        elif "relation" in condition:
            rel_type = condition["relation"]
            rel_target = condition["target"]
            
            # Create or update the relation
            if rel_type not in node.relations:
                node.relations[rel_type] = []
            
            if rel_target not in node.relations[rel_type]:
                node.relations[rel_type].append(rel_target)
        
        # Handle category modifications
        elif "category" in condition:
            category = condition["category"]
            
            # Add to inherits_from
            if category not in node.inherits_from:
                node.inherits_from.append(category)
            
            # Add to is_a relation
            if "is_a" not in node.relations:
                node.relations["is_a"] = []
            
            if category not in node.relations["is_a"]:
                node.relations["is_a"].append(category)
    
    def _apply_counterfactual(self, node: ConceptNode, condition: Dict[str, Any]) -> None:
        """
        Apply a counterfactual condition to a node.
        
        Args:
            node: The node to modify
            condition: The counterfactual condition to apply
        """
        # Handle property counterfactuals
        if "property" in condition:
            prop_name = condition["property"]
            prop_value = condition["value"]
            
            # Remove the property if it matches the counterfactual
            if prop_name in node.properties:
                current_values = [spec.value for spec in node.properties[prop_name]]
                if prop_value in current_values:
                    # Remove this value
                    node.properties[prop_name] = [
                        spec for spec in node.properties[prop_name]
                        if spec.value != prop_value
                    ]
                    
                    # Update property stats
                    if prop_name in node.property_stats and prop_value in node.property_stats[prop_name]:
                        del node.property_stats[prop_name][prop_value]
                else:
                    # Add the counterfactual value
                    self._apply_condition(node, condition)
        
        # Handle relation counterfactuals
        elif "relation" in condition:
            rel_type = condition["relation"]
            rel_target = condition["target"]
            
            # Remove the relation if it exists
            if rel_type in node.relations and rel_target in node.relations[rel_type]:
                node.relations[rel_type].remove(rel_target)
            else:
                # Add the counterfactual relation
                self._apply_condition(node, condition)
        
        # Handle category counterfactuals
        elif "category" in condition:
            category = condition["category"]
            
            # Remove from inherits_from if present
            if category in node.inherits_from:
                node.inherits_from.remove(category)
            
            # Remove from is_a relation if present
            if "is_a" in node.relations and category in node.relations["is_a"]:
                node.relations["is_a"].remove(category)
            else:
                # Add the counterfactual category
                self._apply_condition(node, condition)
    
    def _reason_with_modified_node(
        self, node: ConceptNode, question: Optional[str]
    ) -> Optional[str]:
        """
        Perform reasoning with a modified node.
        
        Args:
            node: The modified node
            question: The specific question to answer
            
        Returns:
            A string with the reasoning result or None
        """
        if not question:
            # If no specific question, provide a general description of the modified node
            return self._describe_modified_node(node)
        
        # Handle specific question types
        if "property" in question:
            prop_name = question["property"]
            if prop_name in node.properties and node.properties[prop_name]:
                values = [spec.value for spec in node.properties[prop_name]]
                return f"If the condition were true, the {prop_name} would be: {', '.join(str(v) for v in values)}"
            else:
                return f"If the condition were true, I couldn't determine the {prop_name}."
        
        elif "relation" in question:
            rel_type = question["relation"]
            if rel_type in node.relations and node.relations[rel_type]:
                targets = node.relations[rel_type]
                return f"If the condition were true, the {rel_type} would be: {', '.join(targets)}"
            else:
                return f"If the condition were true, I couldn't determine the {rel_type}."
        
        elif "category" in question:
            categories = node.relations.get("is_a", []) + node.inherits_from
            if categories:
                return f"If the condition were true, the categories would be: {', '.join(categories)}"
            else:
                return "If the condition were true, I couldn't determine the categories."
        
        return None
    
    def _describe_modified_node(self, node: ConceptNode) -> str:
        """
        Generate a description of a modified node.
        
        Args:
            node: The modified node
            
        Returns:
            A string describing the node
        """
        description = f"If the condition were true, {node.name} would have these characteristics:\n"
        
        # Add categories
        categories = node.relations.get("is_a", []) + node.inherits_from
        if categories:
            description += f"\nCategories: {', '.join(categories)}\n"
        
        # Add properties
        if node.properties:
            description += "\nProperties:\n"
            for prop_name, specs in node.properties.items():
                values = [spec.value for spec in specs]
                description += f"- {prop_name}: {', '.join(str(v) for v in values)}\n"
        
        # Add relations
        if node.relations:
            description += "\nRelations:\n"
            for rel_type, targets in node.relations.items():
                if rel_type != "is_a":  # Already included in categories
                    description += f"- {rel_type}: {', '.join(targets)}\n"
        
        return description