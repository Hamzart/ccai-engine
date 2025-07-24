# ccai/core/reasoning.py

import logging
from typing import List, Dict, Any, Set, Optional

from ccai.core.signal_hub import SignalHub
from ccai.core.graph import ConceptGraph
from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem

# Set up logging
logger = logging.getLogger(__name__)

class ReasoningCore:
    """
    Orchestrates the signal propagation process in alignment with the IRA philosophy.
    
    This core implements the Ideom Resolver AI approach, where:
    - Ideoms (atomic symbolic units) are represented as base concepts in the graph
    - Prefabs (conceptual templates) are composed of ideoms and form recognizable patterns
    - Signal propagation simulates the convergence of ideoms to activate prefab nodes
    """

    def __init__(self, graph: ConceptGraph, subsystems: List[Subsystem]):
        self.graph = graph
        self.subsystems = subsystems
        # Track activation patterns for debugging and explanation
        self.activation_patterns: Dict[str, Dict[str, float]] = {}

    def process_signal(self, initial_signal: Signal, threshold: float = 0.1) -> List[Signal]:
        """
        Processes a signal through the graph using the IRA signal propagation model.
        
        This simulates how ideoms (base concepts) converge to activate prefab nodes
        (higher-level concepts) through signal strength and pattern matching.
        """
        logger.info(f"Processing signal: {initial_signal.origin} ({initial_signal.purpose})")
        
        # Initialize the signal hub (manages signal propagation)
        hub = SignalHub()
        hub.push(initial_signal)
        answers: List[Signal] = []
        
        # Track visited nodes to prevent cycles
        visited_nodes: Set[str] = set()
        
        # Track activation patterns for this query
        self.activation_patterns = {}

        # Process signals until the hub is empty
        while not hub.empty():
            signal = hub.pop()
            
            # Skip signals below confidence threshold
            if not signal or signal.confidence < threshold:
                logger.debug(f"Signal below threshold: {signal.origin if signal else 'None'}")
                continue
                
            # If we already have an answer, add it to results
            if "confirmed" in signal.payload or "final_answer" in signal.payload:
                logger.info(f"Found answer: {signal.payload.get('final_answer', signal.payload.get('confirmed'))}")
                answers.append(signal)
                continue

            # Get the node from the graph
            node = self.graph.get_node(signal.origin)
            if not node:
                logger.debug(f"Node not found: {signal.origin}")
                continue
                
            # Skip if we've already processed this node for this signal path
            node_path_key = f"{signal.origin}:{signal.purpose}:{len(signal.history)}"
            if node_path_key in visited_nodes:
                logger.debug(f"Already visited: {node_path_key}")
                continue
                
            visited_nodes.add(node_path_key)
            
            # Track node activation for this concept
            self._track_activation(signal.origin, signal.confidence)
            
            # Process the signal through all subsystems
            logger.debug(f"Processing node: {node.name} with {len(self.subsystems)} subsystems")
            for subsystem in self.subsystems:
                delta, new_sigs = subsystem.evaluate(signal, node)
                
                # Update signal confidence based on subsystem evaluation
                signal.confidence += delta
                
                # Process new signals
                for ns in new_sigs:
                    if "final_answer" in ns.payload or ns.payload.get("confirmed"):
                        # If we have an answer, add it to results
                        logger.info(f"Subsystem found answer: {ns.payload.get('final_answer', ns.payload.get('confirmed'))}")
                        answers.append(ns)
                    else:
                        # Otherwise, continue propagation
                        hub.push(ns)
                        
        # If we have multiple answers, sort by confidence
        if len(answers) > 1:
            answers.sort(key=lambda x: x.confidence, reverse=True)
            
        logger.info(f"Found {len(answers)} answers")
        return answers
        
    def _track_activation(self, concept: str, strength: float) -> None:
        """Track concept activation for explanation and debugging."""
        if concept not in self.activation_patterns:
            self.activation_patterns[concept] = {"strength": 0.0, "count": 0}
            
        self.activation_patterns[concept]["strength"] += strength
        self.activation_patterns[concept]["count"] += 1
        
    def get_activation_explanation(self) -> Dict[str, Any]:
        """
        Get an explanation of the activation patterns for the last query.
        
        This helps explain how the system arrived at its answer, showing
        which concepts were activated and their relative strengths.
        """
        # Sort concepts by activation strength
        sorted_concepts = sorted(
            self.activation_patterns.items(),
            key=lambda x: x[1]["strength"],
            reverse=True
        )
        
        # Format the explanation
        explanation = {
            "activated_concepts": [
                {
                    "concept": concept,
                    "strength": data["strength"],
                    "activations": data["count"]
                }
                for concept, data in sorted_concepts[:10]  # Top 10 concepts
            ],
            "total_concepts_activated": len(self.activation_patterns)
        }
        
        return explanation
        
    def find_related_concepts(self, concept: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Find concepts related to the given concept through the graph.
        
        This implements the IRA prefab resolution approach, where related
        concepts are found through signal propagation and ideom matching.
        
        Enhanced to find connections between distant concepts through
        intermediate nodes and semantic similarity.
        """
        if not self.graph.get_node(concept):
            return {"related_concepts": [], "error": "Concept not found"}
            
        # Track visited nodes to prevent cycles
        visited: Set[str] = set()
        # Track related concepts and their relationship types
        related: Dict[str, Dict[str, Any]] = {}
        
        # Recursive function to explore the graph
        def explore(current: str, depth: int, path: List[str] = None) -> None:
            if depth > max_depth or current in visited:
                return
                
            if path is None:
                path = [current]
            else:
                path = path + [current]
                
            visited.add(current)
            node = self.graph.get_node(current)
            if not node:
                return
                
            # Add all directly related concepts
            for relation_type, targets in node.relations.items():
                for target in targets:
                    if target not in related and target != concept:
                        related[target] = {
                            "relation": relation_type,
                            "distance": depth,
                            "path": path + [target]
                        }
                        
                    # Continue exploration
                    if target not in visited:
                        explore(target, depth + 1, path)
            
            # Also check structure and functions
            for relation_type, targets in node.structure.items():
                for target in targets:
                    if target not in related and target != concept:
                        related[target] = {
                            "relation": f"structure.{relation_type}",
                            "distance": depth,
                            "path": path + [target]
                        }
                    
                    # Continue exploration
                    if target not in visited:
                        explore(target, depth + 1, path)
                        
            for relation_type, targets in node.functions.items():
                for target in targets:
                    if target not in related and target != concept:
                        related[target] = {
                            "relation": f"function.{relation_type}",
                            "distance": depth,
                            "path": path + [target]
                        }
                    
                    # Continue exploration
                    if target not in visited:
                        explore(target, depth + 1, path)
        
        # Start exploration from the given concept
        explore(concept, 1)
        
        # Find second-order connections (concepts related to related concepts)
        second_order = {}
        for related_concept in list(related.keys()):
            node = self.graph.get_node(related_concept)
            if not node:
                continue
                
            # Check all relations of this related concept
            for relation_type, targets in node.relations.items():
                for target in targets:
                    if target not in related and target != concept and target not in second_order:
                        # This is a second-order connection
                        second_order[target] = {
                            "relation": f"second_order.{relation_type}",
                            "distance": related[related_concept]["distance"] + 1,
                            "path": related[related_concept]["path"] + [target],
                            "via": related_concept
                        }
        
        # Add second-order connections to related concepts
        for concept_name, data in second_order.items():
            if data["distance"] <= max_depth:
                related[concept_name] = data
        
        # Find semantic connections (concepts that share properties)
        concept_node = self.graph.get_node(concept)
        if concept_node:
            # Get all properties of the concept
            concept_properties = set()
            for prop_list in concept_node.properties.values():
                for prop in prop_list:
                    concept_properties.add(prop.value)
            
            # Find nodes with similar properties
            if concept_properties:
                for node_name, node in self.graph._nodes.items():
                    if node_name == concept or node_name in related:
                        continue
                        
                    # Get properties of this node
                    node_properties = set()
                    for prop_list in node.properties.values():
                        for prop in prop_list:
                            node_properties.add(prop.value)
                    
                    # Check for property overlap
                    common_properties = concept_properties.intersection(node_properties)
                    if common_properties:
                        # Calculate similarity score
                        similarity = len(common_properties) / max(len(concept_properties), len(node_properties))
                        if similarity > 0.2:  # Threshold for similarity
                            related[node_name] = {
                                "relation": "semantic_similarity",
                                "distance": 2,  # Consider semantic connections as distance 2
                                "path": [concept, node_name],
                                "similarity": similarity,
                                "common_properties": list(common_properties)
                            }
        
        # Format the results
        result = {
            "concept": concept,
            "related_concepts": [
                {
                    "concept": related_concept,
                    "relation": data["relation"],
                    "distance": data["distance"],
                    "path": data["path"],
                    **({"via": data["via"]} if "via" in data else {}),
                    **({"similarity": data["similarity"], "common_properties": data["common_properties"]}
                       if "similarity" in data else {})
                }
                for related_concept, data in related.items()
            ]
        }
        
        # Sort by distance (closest first)
        result["related_concepts"].sort(key=lambda x: x["distance"])
        
        return result
