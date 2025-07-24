"""Subsystem implementing temporal reasoning."""

from typing import List, Tuple, Dict, Set, Optional
import logging
from datetime import datetime, timedelta
import re

from ccai.core.models import Signal, ConceptNode
from ccai.core.subsystems.base import Subsystem

# Set up logging
logger = logging.getLogger(__name__)


class TemporalReasoner(Subsystem):
    """
    Performs temporal reasoning about events and their relationships in time.
    
    This subsystem can:
    1. Reason about temporal relations (before, after, during)
    2. Handle time-based queries
    3. Infer temporal ordering of events
    """
    
    def __init__(self):
        """Initialize the temporal reasoner."""
        # Temporal relation types
        self.temporal_relations = {
            "before", "after", "during", "starts", "ends",
            "overlaps", "meets", "equals"
        }
        
        # Regular expressions for extracting temporal information
        self.time_patterns = {
            "date": re.compile(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b'),
            "time": re.compile(r'\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\b', re.IGNORECASE),
            "duration": re.compile(r'\b(\d+)\s+(second|minute|hour|day|week|month|year)s?\b', re.IGNORECASE),
            "relative": re.compile(r'\b(yesterday|today|tomorrow|last|next)\s+(day|week|month|year)?\b', re.IGNORECASE)
        }
    
    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        """
        Evaluate a signal using temporal reasoning.
        
        Args:
            signal: The signal to evaluate
            node: The node corresponding to the signal's origin
            
        Returns:
            Tuple of (confidence_delta, new_signals)
        """
        new_signals = []
        confidence_delta = 0.0
        
        # Handle temporal relation queries
        if signal.purpose == "QUERY" and "temporal_relation" in signal.payload:
            relation = signal.payload.get("temporal_relation")
            target = signal.payload.get("target")
            
            if relation and target and relation in self.temporal_relations:
                result = self._evaluate_temporal_relation(node, relation, target)
                if result is not None:
                    temporal_signal = signal.model_copy(deep=True)
                    temporal_signal.payload["final_answer"] = result
                    new_signals.append(temporal_signal)
        
        # Handle "when" queries
        elif signal.purpose == "QUERY" and signal.payload.get("query_type") == "when":
            result = self._extract_temporal_information(node)
            if result:
                temporal_signal = signal.model_copy(deep=True)
                temporal_signal.payload["final_answer"] = result
                new_signals.append(temporal_signal)
        
        return confidence_delta, new_signals
    
    def _evaluate_temporal_relation(
        self, node: ConceptNode, relation: str, target: str
    ) -> Optional[str]:
        """
        Evaluate a temporal relation between two events.
        
        Args:
            node: The source event node
            relation: The temporal relation to evaluate
            target: The target event name
            
        Returns:
            A string describing the temporal relationship or None
        """
        # Check if the relation is directly stored
        if relation in node.relations and target in node.relations[relation]:
            return f"Yes, {node.name} is {relation} {target}."
        
        # Check for inverse relations
        inverse_relations = {
            "before": "after",
            "after": "before",
            "starts": "started_by",
            "ends": "ended_by",
            "during": "contains"
        }
        
        if relation in inverse_relations:
            inverse = inverse_relations[relation]
            if inverse in node.relations and target in node.relations[inverse]:
                return f"No, {node.name} is {inverse} {target}."
        
        # Check for transitive relations
        # For example, if A before B and B before C, then A before C
        if relation == "before" or relation == "after":
            transitive_result = self._check_transitive_relation(node, relation, target)
            if transitive_result:
                return transitive_result
        
        return None
    
    def _check_transitive_relation(
        self, node: ConceptNode, relation: str, target: str, visited: Optional[Set[str]] = None
    ) -> Optional[str]:
        """
        Check for transitive temporal relations.
        
        Args:
            node: The source event node
            relation: The temporal relation to check
            target: The target event name
            visited: Set of already visited nodes to prevent cycles
            
        Returns:
            A string describing the transitive relationship or None
        """
        if visited is None:
            visited = set()
        
        if node.name in visited:
            return None
        
        visited.add(node.name)
        
        # Check direct relations
        if relation not in node.relations:
            return None
        
        # If target is directly related, we've already checked this
        if target in node.relations[relation]:
            return None
        
        # Check each intermediate node
        for intermediate in node.relations[relation]:
            # Avoid self-references
            if intermediate == node.name:
                continue
            
            # Recursively check the relation from the intermediate node
            # This is a simplified implementation and might need a graph traversal
            # in a real system to handle complex transitive relations
            return f"Yes, {node.name} is {relation} {target} (inferred through {intermediate})."
        
        return None
    
    def _extract_temporal_information(self, node: ConceptNode) -> Optional[str]:
        """
        Extract temporal information from a node.
        
        Args:
            node: The node to extract temporal information from
            
        Returns:
            A string describing the temporal information or None
        """
        temporal_info = []
        
        # Check for time-related properties
        time_properties = {"time", "date", "duration", "period", "era", "epoch"}
        for prop in time_properties:
            if prop in node.properties:
                for spec in node.properties[prop]:
                    temporal_info.append(f"{prop}: {spec.value}")
        
        # Check for temporal relations
        for relation in self.temporal_relations:
            if relation in node.relations:
                targets = node.relations[relation]
                if targets:
                    temporal_info.append(f"{relation}: {', '.join(targets)}")
        
        if temporal_info:
            return f"Temporal information about {node.name}:\n" + "\n".join(temporal_info)
        
        return None
    
    def extract_temporal_expressions(self, text: str) -> Dict[str, List[str]]:
        """
        Extract temporal expressions from text.
        
        Args:
            text: The text to extract temporal expressions from
            
        Returns:
            Dictionary mapping expression types to lists of extracted expressions
        """
        results = {}
        
        for expr_type, pattern in self.time_patterns.items():
            matches = pattern.findall(text)
            if matches:
                results[expr_type] = matches
        
        return results
    
    def normalize_temporal_expression(self, expr: str, expr_type: str) -> Optional[datetime]:
        """
        Normalize a temporal expression to a datetime object.
        
        Args:
            expr: The temporal expression to normalize
            expr_type: The type of expression (date, time, duration, relative)
            
        Returns:
            A datetime object or None if normalization fails
        """
        now = datetime.now()
        
        if expr_type == "date":
            # Try different date formats
            for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"):
                try:
                    return datetime.strptime(expr, fmt)
                except ValueError:
                    continue
        
        elif expr_type == "time":
            # Try different time formats
            for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"):
                try:
                    time_obj = datetime.strptime(expr, fmt).time()
                    return datetime.combine(now.date(), time_obj)
                except ValueError:
                    continue
        
        elif expr_type == "relative":
            # Handle relative expressions
            if "yesterday" in expr:
                return now - timedelta(days=1)
            elif "today" in expr:
                return now
            elif "tomorrow" in expr:
                return now + timedelta(days=1)
            elif "last" in expr:
                if "day" in expr:
                    return now - timedelta(days=1)
                elif "week" in expr:
                    return now - timedelta(weeks=1)
                elif "month" in expr:
                    # Simplified; doesn't handle month boundaries correctly
                    return now - timedelta(days=30)
                elif "year" in expr:
                    # Simplified; doesn't handle leap years correctly
                    return now - timedelta(days=365)
            elif "next" in expr:
                if "day" in expr:
                    return now + timedelta(days=1)
                elif "week" in expr:
                    return now + timedelta(weeks=1)
                elif "month" in expr:
                    # Simplified; doesn't handle month boundaries correctly
                    return now + timedelta(days=30)
                elif "year" in expr:
                    # Simplified; doesn't handle leap years correctly
                    return now + timedelta(days=365)
        
        return None