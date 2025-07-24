"""Subsystem implementing analogical reasoning."""

from typing import List, Tuple, Dict, Set, Optional
import logging

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem
from ccai.core.graph import ConceptGraph

# Set up logging
logger = logging.getLogger(__name__)


class AnalogicalReasoner(Subsystem):
    """
    Performs analogical reasoning by finding similarities between concepts.
    
    This subsystem can:
    1. Find similar concepts based on shared properties and relations
    2. Transfer knowledge from one concept to another based on similarity
    3. Answer comparison questions by identifying similarities and differences
    """
    
    def __init__(self, graph: ConceptGraph, similarity_threshold: float = 0.3):
        """
        Initialize the analogical reasoner.
        
        Args:
            graph: The concept graph to reason over
            similarity_threshold: Minimum similarity score to consider concepts similar
        """
        self.graph = graph
        self.similarity_threshold = similarity_threshold
    
    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        """
        Evaluate a signal using analogical reasoning.
        
        Args:
            signal: The signal to evaluate
            node: The node corresponding to the signal's origin
            
        Returns:
            Tuple of (confidence_delta, new_signals)
        """
        new_signals = []
        confidence_delta = 0.0
        
        # Handle comparison queries
        if signal.purpose == "QUERY" and signal.payload.get("comparison_target"):
            target_name = signal.payload.get("comparison_target")
            target_node = self.graph.get_node(target_name)
            
            if not target_node:
                return 0.0, []
            
            # Find similarities and differences
            similarities, differences = self._compare_nodes(node, target_node)
            
            # Create a response signal with the comparison results
            comparison_signal = signal.model_copy(deep=True)
            comparison_signal.payload["final_answer"] = self._format_comparison(
                node.name, target_node.name, similarities, differences
            )
            new_signals.append(comparison_signal)
            
            return confidence_delta, new_signals
        
        # Handle property inference for unknown properties
        if signal.purpose == "QUERY" and "property" in signal.payload:
            property_name = signal.payload.get("property")
            
            # If the node doesn't have this property, try to infer it from similar concepts
            if property_name not in node.properties:
                similar_nodes = self._find_similar_nodes(node)
                
                for similar_name, similarity in similar_nodes:
                    similar_node = self.graph.get_node(similar_name)
                    if not similar_node:
                        continue
                    
                    # If the similar node has the property, infer it for the original node
                    if property_name in similar_node.properties:
                        property_specs = similar_node.properties[property_name]
                        if property_specs:
                            inference_signal = signal.model_copy(deep=True)
                            inference_signal.payload["inferred_answer"] = property_specs[0].value
                            inference_signal.payload["inference_source"] = similar_name
                            inference_signal.payload["inference_confidence"] = similarity
                            inference_signal.confidence = similarity
                            new_signals.append(inference_signal)
        
        return confidence_delta, new_signals
    
    def _find_similar_nodes(self, node: ConceptNode) -> List[Tuple[str, float]]:
        """
        Find nodes similar to the given node.
        
        Args:
            node: The node to find similar nodes for
            
        Returns:
            List of (node_name, similarity_score) tuples
        """
        similarities = []
        
        # Get all nodes from the graph
        for other_name, other_node in self.graph._nodes.items():
            if other_name == node.name:
                continue
            
            similarity = self._calculate_similarity(node, other_node)
            if similarity >= self.similarity_threshold:
                similarities.append((other_name, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities
    
    def _calculate_similarity(self, node1: ConceptNode, node2: ConceptNode) -> float:
        """
        Calculate similarity between two nodes based on shared properties and relations.
        
        Args:
            node1: First node
            node2: Second node
            
        Returns:
            Similarity score between 0 and 1
        """
        # Check for shared categories (is_a relations)
        category_similarity = self._calculate_category_similarity(node1, node2)
        
        # Check for shared properties
        property_similarity = self._calculate_property_similarity(node1, node2)
        
        # Check for shared relations
        relation_similarity = self._calculate_relation_similarity(node1, node2)
        
        # Weighted average of similarities
        weights = [0.4, 0.4, 0.2]  # Category, property, relation weights
        similarity = (
            weights[0] * category_similarity +
            weights[1] * property_similarity +
            weights[2] * relation_similarity
        )
        
        return similarity
    
    def _calculate_category_similarity(self, node1: ConceptNode, node2: ConceptNode) -> float:
        """Calculate similarity based on shared categories."""
        categories1 = set(node1.relations.get("is_a", []) + node1.inherits_from)
        categories2 = set(node2.relations.get("is_a", []) + node2.inherits_from)
        
        if not categories1 or not categories2:
            return 0.0
        
        # Jaccard similarity: intersection / union
        intersection = len(categories1.intersection(categories2))
        union = len(categories1.union(categories2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_property_similarity(self, node1: ConceptNode, node2: ConceptNode) -> float:
        """Calculate similarity based on shared properties."""
        properties1 = set(node1.properties.keys())
        properties2 = set(node2.properties.keys())
        
        if not properties1 or not properties2:
            return 0.0
        
        # Jaccard similarity for property keys
        key_intersection = len(properties1.intersection(properties2))
        key_union = len(properties1.union(properties2))
        key_similarity = key_intersection / key_union if key_union > 0 else 0.0
        
        # Check property values for shared keys
        value_similarity = 0.0
        shared_keys = properties1.intersection(properties2)
        
        if shared_keys:
            value_matches = 0
            for key in shared_keys:
                values1 = {spec.value for spec in node1.properties[key]}
                values2 = {spec.value for spec in node2.properties[key]}
                
                if values1.intersection(values2):
                    value_matches += 1
            
            value_similarity = value_matches / len(shared_keys)
        
        # Combine key and value similarity
        return 0.5 * key_similarity + 0.5 * value_similarity
    
    def _calculate_relation_similarity(self, node1: ConceptNode, node2: ConceptNode) -> float:
        """Calculate similarity based on shared relations."""
        relations1 = set(node1.relations.keys())
        relations2 = set(node2.relations.keys())
        
        if not relations1 or not relations2:
            return 0.0
        
        # Jaccard similarity for relation types
        type_intersection = len(relations1.intersection(relations2))
        type_union = len(relations1.union(relations2))
        type_similarity = type_intersection / type_union if type_union > 0 else 0.0
        
        # Check relation targets for shared types
        target_similarity = 0.0
        shared_types = relations1.intersection(relations2)
        
        if shared_types:
            target_matches = 0
            for rel_type in shared_types:
                targets1 = set(node1.relations[rel_type])
                targets2 = set(node2.relations[rel_type])
                
                if targets1.intersection(targets2):
                    target_matches += 1
            
            target_similarity = target_matches / len(shared_types)
        
        # Combine type and target similarity
        return 0.5 * type_similarity + 0.5 * target_similarity
    
    def _compare_nodes(
        self, node1: ConceptNode, node2: ConceptNode
    ) -> Tuple[Dict[str, List[str]], Dict[str, Tuple[Optional[str], Optional[str]]]]:
        """
        Compare two nodes to find similarities and differences.
        
        Args:
            node1: First node
            node2: Second node
            
        Returns:
            Tuple of (similarities, differences) where:
            - similarities is a dict mapping relation/property types to shared values
            - differences is a dict mapping relation/property types to (node1_value, node2_value)
        """
        similarities = {}
        differences = {}
        
        # Compare categories (is_a relations)
        categories1 = set(node1.relations.get("is_a", []) + node1.inherits_from)
        categories2 = set(node2.relations.get("is_a", []) + node2.inherits_from)
        
        shared_categories = categories1.intersection(categories2)
        if shared_categories:
            similarities["categories"] = list(shared_categories)
        
        diff_categories1 = categories1 - categories2
        diff_categories2 = categories2 - categories1
        if diff_categories1 or diff_categories2:
            cat1_str = ", ".join(diff_categories1) if diff_categories1 else None
            cat2_str = ", ".join(diff_categories2) if diff_categories2 else None
            differences["categories"] = (cat1_str, cat2_str)
        
        # Compare properties
        all_properties = set(node1.properties.keys()).union(node2.properties.keys())
        
        for prop in all_properties:
            values1 = {spec.value for spec in node1.properties.get(prop, [])}
            values2 = {spec.value for spec in node2.properties.get(prop, [])}
            
            shared_values = values1.intersection(values2)
            if shared_values:
                similarities[f"property:{prop}"] = list(shared_values)
            
            diff_values1 = values1 - values2
            diff_values2 = values2 - values1
            if diff_values1 or diff_values2:
                val1_str = ", ".join(str(v) for v in diff_values1) if diff_values1 else None
                val2_str = ", ".join(str(v) for v in diff_values2) if diff_values2 else None
                differences[f"property:{prop}"] = (val1_str, val2_str)
        
        # Compare relations (excluding is_a which was handled above)
        all_relations = set(node1.relations.keys()).union(node2.relations.keys())
        all_relations.discard("is_a")  # Already handled
        
        for rel in all_relations:
            targets1 = set(node1.relations.get(rel, []))
            targets2 = set(node2.relations.get(rel, []))
            
            shared_targets = targets1.intersection(targets2)
            if shared_targets:
                similarities[f"relation:{rel}"] = list(shared_targets)
            
            diff_targets1 = targets1 - targets2
            diff_targets2 = targets2 - targets1
            if diff_targets1 or diff_targets2:
                tgt1_str = ", ".join(diff_targets1) if diff_targets1 else None
                tgt2_str = ", ".join(diff_targets2) if diff_targets2 else None
                differences[f"relation:{rel}"] = (tgt1_str, tgt2_str)
        
        return similarities, differences
    
    def _format_comparison(
        self,
        name1: str,
        name2: str,
        similarities: Dict[str, List[str]],
        differences: Dict[str, Tuple[Optional[str], Optional[str]]]
    ) -> str:
        """
        Format comparison results into a readable string.
        
        Args:
            name1: Name of the first node
            name2: Name of the second node
            similarities: Dict of similarities
            differences: Dict of differences
            
        Returns:
            Formatted comparison string
        """
        result = f"Comparison between {name1} and {name2}:\n"
        
        # Add similarities
        if similarities:
            result += "\nSimilarities:\n"
            for key, values in similarities.items():
                if key == "categories":
                    result += f"- Both are types of: {', '.join(values)}\n"
                elif key.startswith("property:"):
                    prop = key[9:]  # Remove "property:" prefix
                    result += f"- Both have {prop}: {', '.join(str(v) for v in values)}\n"
                elif key.startswith("relation:"):
                    rel = key[9:]  # Remove "relation:" prefix
                    result += f"- Both {rel}: {', '.join(values)}\n"
        
        # Add differences
        if differences:
            result += "\nDifferences:\n"
            for key, (val1, val2) in differences.items():
                if key == "categories":
                    if val1:
                        result += f"- {name1} is a: {val1}\n"
                    if val2:
                        result += f"- {name2} is a: {val2}\n"
                elif key.startswith("property:"):
                    prop = key[9:]  # Remove "property:" prefix
                    if val1:
                        result += f"- {name1} has {prop}: {val1}\n"
                    if val2:
                        result += f"- {name2} has {prop}: {val2}\n"
                elif key.startswith("relation:"):
                    rel = key[9:]  # Remove "relation:" prefix
                    if val1:
                        result += f"- {name1} {rel}: {val1}\n"
                    if val2:
                        result += f"- {name2} {rel}: {val2}\n"
        
        return result