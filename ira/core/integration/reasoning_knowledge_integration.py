"""
Integration module for connecting the Unified Reasoning Core with the Knowledge Graph.

This module provides classes and functions for integrating the Unified Reasoning Core
with the Knowledge Graph, enabling knowledge-based reasoning.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import re
from datetime import datetime

from ..knowledge.knowledge_graph import KnowledgeGraph
from ..knowledge.concept_node import ConceptNode
from ..knowledge.relation import Relation
from ..knowledge.property_value import PropertyValue
from ..reasoning.unified_reasoning_core import UnifiedReasoningCore, ReasoningResult
from ..reasoning.ideom import Ideom
from ..reasoning.ideom_network import IdeomNetwork
from ..reasoning.activation_pattern import ActivationPattern
from ..reasoning.prefab import Prefab


class ReasoningKnowledgeIntegration:
    """
    Integrates the Unified Reasoning Core with the Knowledge Graph.
    
    This class provides methods for querying the Knowledge Graph based on reasoning results,
    updating the Knowledge Graph based on reasoning, and extracting knowledge from
    reasoning patterns.
    
    Attributes:
        knowledge_graph: The KnowledgeGraph instance to integrate with.
        reasoning_core: The UnifiedReasoningCore instance to integrate with.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph, reasoning_core: UnifiedReasoningCore):
        """
        Initialize the ReasoningKnowledgeIntegration.
        
        Args:
            knowledge_graph: The KnowledgeGraph instance to integrate with.
            reasoning_core: The UnifiedReasoningCore instance to integrate with.
        """
        self.knowledge_graph = knowledge_graph
        self.reasoning_core = reasoning_core
        
    def query_knowledge_graph(self, reasoning_result: ReasoningResult) -> Dict[str, Any]:
        """
        Query the Knowledge Graph based on a reasoning result.
        
        Args:
            reasoning_result: The reasoning result to use for the query.
            
        Returns:
            A dictionary containing the query results.
        """
        # Get the most active ideoms from the reasoning result
        activation_pattern = reasoning_result.get_activation_pattern()
        most_active_ideoms = activation_pattern.get_most_active_ideoms(5)
        
        # Convert ideom IDs to concept names
        concept_names = []
        for ideom_id in most_active_ideoms:
            ideom = self.reasoning_core.ideom_network.get_ideom(ideom_id)
            if ideom:
                concept_names.append(ideom.name)
        
        # Query the Knowledge Graph for each concept
        results = {}
        for concept_name in concept_names:
            concept = self.knowledge_graph.get_concept_by_name(concept_name)
            if concept:
                # Get properties and relations for the concept
                properties = concept.get_properties()
                # Get all relations for the concept
                relations = []
                for relation_type in concept.get_relation_types():
                    relations.extend(concept.get_relations(relation_type))
                
                # Add to results
                results[concept_name] = {
                    "properties": {name: prop.value for name, prop in properties.items()},
                    "relations": [
                        {
                            "type": rel.type,
                            "target": rel.target.name,
                            "bidirectional": rel.bidirectional
                        }
                        for rel in relations
                    ]
                }
        
        return {
            "success": True,
            "type": "knowledge_query",
            "results": results
        }
    
    def update_knowledge_graph(self, reasoning_result: ReasoningResult) -> Dict[str, Any]:
        """
        Update the Knowledge Graph based on a reasoning result.
        
        Args:
            reasoning_result: The reasoning result to use for the update.
            
        Returns:
            A dictionary containing the update results.
        """
        # Get the most active ideoms from the reasoning result
        activation_pattern = reasoning_result.get_activation_pattern()
        most_active_ideoms = activation_pattern.get_most_active_ideoms(5)
        
        # Convert ideom IDs to concept names and create concepts if they don't exist
        concepts = []
        for ideom_id in most_active_ideoms:
            ideom = self.reasoning_core.ideom_network.get_ideom(ideom_id)
            if ideom:
                concept = self.knowledge_graph.get_concept_by_name(ideom.name)
                if not concept:
                    concept = self.knowledge_graph.add_concept(ideom.name)
                concepts.append(concept)
        
        # Create relations between concepts based on ideom connections
        relations_created = []
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                ideom1 = self.reasoning_core.ideom_network.get_ideom(most_active_ideoms[i])
                ideom2 = self.reasoning_core.ideom_network.get_ideom(most_active_ideoms[j])
                
                if ideom1 and ideom2:
                    connection_strength = ideom1.get_connection_strength(ideom2.id)
                    if connection_strength > 0.5:
                        # Create a relation between the concepts
                        relation_type = "related_to"  # Default relation type
                        relation = self.knowledge_graph.update_relation(
                            concepts[i], concepts[j], relation_type, bidirectional=True
                        )
                        relations_created.append({
                            "source": concepts[i].name,
                            "target": concepts[j].name,
                            "type": relation_type
                        })
        
        return {
            "success": True,
            "type": "knowledge_update",
            "concepts_created": [concept.name for concept in concepts if concept.name not in [c.name for c in self.knowledge_graph.get_all_concepts()]],
            "relations_created": relations_created
        }
    
    def extract_knowledge_from_reasoning(self, reasoning_result: ReasoningResult) -> Dict[str, Any]:
        """
        Extract knowledge from a reasoning result.
        
        Args:
            reasoning_result: The reasoning result to extract knowledge from.
            
        Returns:
            A dictionary containing the extracted knowledge.
        """
        # Get the active prefabs from the reasoning result
        active_prefabs = reasoning_result.get_active_prefabs()
        
        # Extract knowledge from each active prefab
        extracted_knowledge = []
        for prefab_id in active_prefabs:
            prefab = self.reasoning_core.prefab_manager.get_prefab(prefab_id)
            if prefab and prefab.response_template:
                # Extract subject-predicate-object triples from the response template
                triples = self._extract_triples_from_text(prefab.response_template)
                extracted_knowledge.extend(triples)
        
        return {
            "success": True,
            "type": "knowledge_extraction",
            "extracted_knowledge": extracted_knowledge
        }
    
    def _extract_triples_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract subject-predicate-object triples from text.
        
        Args:
            text: The text to extract triples from.
            
        Returns:
            A list of dictionaries, where each dictionary contains the subject,
            predicate, and object of a triple.
        """
        triples = []
        
        # Define patterns for extracting triples
        patterns = [
            # "X is Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X are Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+are\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X has Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+has\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X have Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+have\s+(?P<object>\w+(?:\s+\w+)*)",
            # "X [predicate] Y" pattern
            r"(?P<subject>\w+(?:\s+\w+)*)\s+(?P<predicate>\w+)\s+(?P<object>\w+(?:\s+\w+)*)"
        ]
        
        # Extract triples using the patterns
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                triple = match.groupdict()
                if "predicate" not in triple:
                    if "is" in match.group():
                        triple["predicate"] = "is"
                    elif "are" in match.group():
                        triple["predicate"] = "are"
                    elif "has" in match.group():
                        triple["predicate"] = "has"
                    elif "have" in match.group():
                        triple["predicate"] = "have"
                triples.append(triple)
        
        return triples
    
    def create_ideoms_from_concepts(self) -> Dict[str, Any]:
        """
        Create ideoms in the Unified Reasoning Core based on concepts in the Knowledge Graph.
        
        Returns:
            A dictionary containing the creation results.
        """
        # Get all concepts from the Knowledge Graph
        concepts = self.knowledge_graph.get_all_concepts()
        
        # Create ideoms for each concept
        ideoms_created = []
        for concept in concepts:
            # Check if an ideom with this name already exists
            existing_ideoms = self.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
            if not existing_ideoms:
                # Create a new ideom
                ideom = self.reasoning_core.create_ideom(concept.name)
                ideoms_created.append(ideom.name)
        
        # Create connections between ideoms based on concept relations
        connections_created = []
        for concept in concepts:
            # Get all relations for the concept
            # Get all relations for the concept
            relations = []
            for relation_type in concept.get_relation_types():
                relations.extend(concept.get_relations(relation_type))
            
            for relation in relations:
                # Get the ideoms for the source and target concepts
                source_ideoms = self.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
                target_ideoms = self.reasoning_core.ideom_network.get_ideoms_by_name(relation.target.name)
                
                if source_ideoms and target_ideoms:
                    source_ideom = source_ideoms[0]
                    target_ideom = target_ideoms[0]
                    
                    # Create a connection between the ideoms
                    connection_strength = 0.7  # Default connection strength
                    self.reasoning_core.ideom_network.connect_ideoms(
                        source_ideom.id, target_ideom.id, connection_strength
                    )
                    connections_created.append({
                        "source": source_ideom.name,
                        "target": target_ideom.name,
                        "strength": connection_strength
                    })
        
        return {
            "success": True,
            "type": "ideom_creation",
            "ideoms_created": ideoms_created,
            "connections_created": connections_created
        }
    
    def create_prefabs_from_concepts(self) -> Dict[str, Any]:
        """
        Create prefabs in the Unified Reasoning Core based on concepts in the Knowledge Graph.
        
        Returns:
            A dictionary containing the creation results.
        """
        # Get all concepts from the Knowledge Graph
        concepts = self.knowledge_graph.get_all_concepts()
        
        # Create prefabs for each concept
        prefabs_created = []
        for concept in concepts:
            # Get the ideoms for the concept
            ideoms = self.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
            
            if ideoms:
                ideom = ideoms[0]
                
                # Get related ideoms
                related_ideoms = self.reasoning_core.ideom_network.get_connected_ideoms(ideom.id)
                
                # Create ideom weights for the prefab
                ideom_weights = {ideom.id: 1.0}  # The concept's ideom has the highest weight
                for related_ideom in related_ideoms:
                    ideom_weights[related_ideom.id] = ideom.get_connection_strength(related_ideom.id)
                
                # Create a response template based on the concept's properties and relations
                properties = concept.get_properties()
                # Get all relations for the concept
                relations = []
                for relation_type in concept.get_relation_types():
                    relations.extend(concept.get_relations(relation_type))
                
                response_template = f"{concept.name} is "
                
                # Add "is_a" relations to the template
                is_a_relations = [rel for rel in relations if rel.type == "is_a"]
                if is_a_relations:
                    is_a_concepts = [rel.target.name for rel in is_a_relations]
                    if len(is_a_concepts) == 1:
                        response_template += f"a {is_a_concepts[0]}"
                    else:
                        response_template += "a " + ", ".join(is_a_concepts[:-1]) + f" and {is_a_concepts[-1]}"
                    response_template += " that "
                
                # Add properties to the template
                property_strings = []
                for prop_name, prop_value in properties.items():
                    if prop_name != "definition" and prop_name != "name":
                        property_strings.append(f"{prop_name} {prop_value.value}")
                
                if property_strings:
                    if len(property_strings) == 1:
                        response_template += property_strings[0]
                    else:
                        response_template += ", ".join(property_strings[:-1]) + f" and {property_strings[-1]}"
                
                # Create the prefab
                prefab = self.reasoning_core.create_prefab(
                    name=concept.name,
                    ideom_weights=ideom_weights,
                    response_template=response_template,
                    tags=["concept"]
                )
                
                prefabs_created.append(prefab.name)
        
        return {
            "success": True,
            "type": "prefab_creation",
            "prefabs_created": prefabs_created
        }
    
    def process_input_with_knowledge(self, input_text: str) -> Dict[str, Any]:
        """
        Process an input text using both the Unified Reasoning Core and the Knowledge Graph.
        
        Args:
            input_text: The input text to process.
            
        Returns:
            A dictionary containing the processing results.
        """
        # Process the input with the Unified Reasoning Core
        reasoning_result = self.reasoning_core.process(input_text)
        
        # Query the Knowledge Graph based on the reasoning result
        knowledge_query_result = self.query_knowledge_graph(reasoning_result)
        
        # Extract knowledge from the reasoning result
        knowledge_extraction_result = self.extract_knowledge_from_reasoning(reasoning_result)
        
        # Update the Knowledge Graph based on the reasoning result
        knowledge_update_result = self.update_knowledge_graph(reasoning_result)
        
        # Combine the results
        return {
            "success": True,
            "type": "integrated_processing",
            "reasoning_result": {
                "primary_response": reasoning_result.get_primary_response(),
                "alternative_responses": reasoning_result.get_alternative_responses(),
                "confidence": reasoning_result.get_highest_confidence()
            },
            "knowledge_query_result": knowledge_query_result,
            "knowledge_extraction_result": knowledge_extraction_result,
            "knowledge_update_result": knowledge_update_result
        }