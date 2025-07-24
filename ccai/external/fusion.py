"""
Knowledge fusion module for integrating external knowledge.

This module provides functionality for integrating knowledge from external sources
into the CCAI concept graph, resolving conflicts, and maintaining source attribution.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
import time

from ccai.core.graph import ConceptGraph
from ccai.core.models import ConceptNode, PropertySpec, Signal
from ccai.core.subsystems.base import Subsystem
from ccai.external.connector import KnowledgeConnector, registry

# Set up logging
logger = logging.getLogger(__name__)


class KnowledgeFusion:
    """
    Integrates external knowledge into the concept graph.
    
    This class is responsible for:
    - Retrieving information from external sources
    - Converting external data to concept nodes
    - Integrating external knowledge with existing knowledge
    - Resolving conflicts between different sources
    """
    
    def __init__(self, graph: ConceptGraph):
        """
        Initialize the knowledge fusion module.
        
        Args:
            graph: The concept graph to integrate knowledge into
        """
        self.graph = graph
    
    def search_external_sources(
        self, query: str, sources: Optional[List[str]] = None, limit: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search external sources for information about a query.
        
        Args:
            query: The search query
            sources: Optional list of source names to search (default: all)
            limit: Maximum number of results per source
            
        Returns:
            Dictionary mapping source names to search results
        """
        if sources is None:
            # Use all registered connectors
            sources = registry.list_connectors()
        
        results = {}
        
        for source_name in sources:
            connector = registry.get_connector(source_name)
            if connector:
                try:
                    source_results = connector.search(query, limit=limit)
                    results[source_name] = source_results
                except Exception as e:
                    logger.error(f"Error searching {source_name}: {e}")
                    results[source_name] = []
            else:
                logger.warning(f"Connector not found: {source_name}")
        
        return results
    
    def get_external_details(
        self, source: str, item_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an item from an external source.
        
        Args:
            source: The name of the source
            item_id: The ID of the item
            
        Returns:
            Detailed information or None if not found
        """
        connector = registry.get_connector(source)
        if not connector:
            logger.warning(f"Connector not found: {source}")
            return None
        
        try:
            return connector.get_details(item_id)
        except Exception as e:
            logger.error(f"Error getting details from {source}: {e}")
            return None
    
    def integrate_external_knowledge(
        self, source: str, data: Dict[str, Any], confidence: float = 0.7
    ) -> List[str]:
        """
        Integrate knowledge from an external source into the concept graph.
        
        Args:
            source: The name of the source
            data: The data to integrate
            confidence: Confidence score for the external data (0-1)
            
        Returns:
            List of concept names that were added or updated
        """
        connector = registry.get_connector(source)
        if not connector:
            logger.warning(f"Connector not found: {source}")
            return []
        
        # Extract concepts from the data
        concepts = connector.extract_concepts(data)
        
        # Track which concepts were added or updated
        updated_concepts = []
        
        for concept in concepts:
            name = concept.get("name", "").lower()
            if not name:
                continue
            
            # Check if the concept already exists
            existing_node = self.graph.get_node(name)
            
            if existing_node:
                # Update existing node
                self._update_existing_node(existing_node, concept, source, confidence)
            else:
                # Create new node
                new_node = self._create_new_node(concept, source, confidence)
                self.graph.add_node(new_node)
            
            updated_concepts.append(name)
        
        # Save changes to the graph
        self.graph.save_snapshot()
        
        return updated_concepts
    
    def _create_new_node(
        self, concept: Dict[str, Any], source: str, confidence: float
    ) -> ConceptNode:
        """Create a new node from external concept data."""
        node = ConceptNode(
            name=concept["name"],
            ctype=concept.get("ctype", "entity")
        )
        
        # Add properties
        for prop_name, prop_values in concept.get("properties", {}).items():
            node.properties[prop_name] = []
            node.property_stats[prop_name] = {}
            
            for pv in prop_values:
                value = pv["value"]
                score = pv["score"] * confidence  # Adjust score by confidence
                
                node.properties[prop_name].append(PropertySpec(value=value, score=score))
                node.property_stats[prop_name][value] = int(score * 10)  # Convert to count
        
        # Add relations
        for rel_type, targets in concept.get("relations", {}).items():
            node.relations[rel_type] = targets
        
        # Add source metadata
        if "source" not in node.relations:
            node.relations["source"] = []
        if source not in node.relations["source"]:
            node.relations["source"].append(source)
        
        # Update metadata
        node.metadata["created"] = time.time()
        node.metadata["last_updated"] = time.time()
        node.metadata["external_source"] = True
        
        return node
    
    def _update_existing_node(
        self, node: ConceptNode, concept: Dict[str, Any], source: str, confidence: float
    ) -> None:
        """Update an existing node with external concept data."""
        # Add source to relations if not already present
        if "source" not in node.relations:
            node.relations["source"] = []
        if source not in node.relations["source"]:
            node.relations["source"].append(source)
        
        # Update properties
        for prop_name, prop_values in concept.get("properties", {}).items():
            if prop_name not in node.properties:
                node.properties[prop_name] = []
            if prop_name not in node.property_stats:
                node.property_stats[prop_name] = {}
            
            for pv in prop_values:
                value = pv["value"]
                score = pv["score"] * confidence  # Adjust score by confidence
                
                # Check if property value already exists
                existing_values = [spec.value for spec in node.properties[prop_name]]
                if value not in existing_values:
                    node.properties[prop_name].append(PropertySpec(value=value, score=score))
                    node.property_stats[prop_name][value] = int(score * 10)  # Convert to count
        
        # Update relations
        for rel_type, targets in concept.get("relations", {}).items():
            if rel_type not in node.relations:
                node.relations[rel_type] = []
            
            for target in targets:
                if target not in node.relations[rel_type]:
                    node.relations[rel_type].append(target)
        
        # Update metadata
        node.metadata["last_updated"] = time.time()
        node.metadata["external_source"] = True


class ExternalKnowledgeSubsystem(Subsystem):
    """
    Subsystem for integrating external knowledge during reasoning.
    
    This subsystem can:
    1. Detect when internal knowledge is insufficient
    2. Query external sources for additional information
    3. Integrate external knowledge into the reasoning process
    """
    
    def __init__(self, graph: ConceptGraph, fusion: KnowledgeFusion):
        """
        Initialize the external knowledge subsystem.
        
        Args:
            graph: The concept graph to reason over
            fusion: The knowledge fusion module
        """
        self.graph = graph
        self.fusion = fusion
        self.external_query_threshold = 0.3  # Confidence threshold for querying external sources
    
    def evaluate(self, signal: Signal, node: ConceptNode) -> Tuple[float, List[Signal]]:
        """
        Evaluate a signal using external knowledge if needed.
        
        Args:
            signal: The signal to evaluate
            node: The node corresponding to the signal's origin
            
        Returns:
            Tuple of (confidence_delta, new_signals)
        """
        new_signals = []
        confidence_delta = 0.0
        
        # Check if we should query external sources
        if signal.confidence < self.external_query_threshold:
            # This is a low-confidence signal, try to get external knowledge
            external_results = self._query_external_sources(signal, node)
            
            if external_results:
                # Create new signals based on external knowledge
                for result in external_results:
                    external_signal = signal.model_copy(deep=True)
                    external_signal.payload["external_source"] = True
                    external_signal.payload["source_name"] = result["source"]
                    
                    if "answer" in result:
                        external_signal.payload["answer"] = result["answer"]
                    if "final_answer" in result:
                        external_signal.payload["final_answer"] = result["final_answer"]
                    
                    external_signal.confidence = result.get("confidence", 0.7)
                    new_signals.append(external_signal)
                
                # Boost confidence if we found external information
                confidence_delta = 0.2
        
        return confidence_delta, new_signals
    
    def _query_external_sources(
        self, signal: Signal, node: ConceptNode
    ) -> List[Dict[str, Any]]:
        """
        Query external sources for information related to the signal.
        
        Args:
            signal: The signal to get external information for
            node: The node corresponding to the signal's origin
            
        Returns:
            List of results from external sources
        """
        results = []
        
        # Determine what to search for
        query = node.name
        if "property" in signal.payload:
            query += f" {signal.payload['property']}"
        
        # Search external sources
        search_results = self.fusion.search_external_sources(query)
        
        for source_name, source_results in search_results.items():
            if not source_results:
                continue
            
            # Get details for the top result
            top_result = source_results[0]
            item_id = top_result.get("pageid", top_result.get("url", ""))
            
            if not item_id:
                continue
            
            details = self.fusion.get_external_details(source_name, item_id)
            
            if not details:
                continue
            
            # Integrate the knowledge into the graph
            self.fusion.integrate_external_knowledge(source_name, details)
            
            # Create a result based on the external information
            if signal.purpose == "QUERY":
                if "property" in signal.payload:
                    prop = signal.payload["property"]
                    # Extract relevant information from the details
                    # This is a simplified implementation
                    if "extract" in details:
                        extract = details["extract"]
                        # Look for sentences containing the property
                        sentences = extract.split(". ")
                        for sentence in sentences:
                            if prop.lower() in sentence.lower():
                                results.append({
                                    "source": source_name,
                                    "answer": sentence,
                                    "confidence": 0.7
                                })
                                break
                else:
                    # General query about the concept
                    if "extract" in details:
                        results.append({
                            "source": source_name,
                            "final_answer": details["extract"][:200] + "...",
                            "confidence": 0.8
                        })
            elif signal.purpose == "VERIFY":
                # For verification queries, this is more complex
                # This is a simplified implementation
                relation = signal.payload.get("relation", "")
                target = signal.payload.get("target", "")
                
                if relation and target and "extract" in details:
                    extract = details["extract"].lower()
                    if target.lower() in extract:
                        results.append({
                            "source": source_name,
                            "final_answer": f"Yes, according to {source_name}, {node.name} {relation} {target}.",
                            "confidence": 0.7
                        })
        
        return results