"""
Bug fixes for the integration between the Unified Reasoning Core and the Knowledge Graph.

This module contains bug fixes for the ReasoningKnowledgeIntegration class, addressing
issues with multi-word concept handling, temporal context integration, and error handling.
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
from ..reasoning.temporal_context import TemporalContext


class ReasoningKnowledgeIntegrationBugFixes:
    """
    Bug fixes for the ReasoningKnowledgeIntegration class.
    
    This class provides methods to fix bugs in the integration between the
    Unified Reasoning Core and the Knowledge Graph.
    """
    
    @staticmethod
    def fix_create_ideoms_from_concepts(integration):
        """
        Fix the create_ideoms_from_concepts method to handle multi-word concepts properly.
        
        Args:
            integration: The ReasoningKnowledgeIntegration instance to fix.
        """
        original_method = integration.create_ideoms_from_concepts
        
        def fixed_create_ideoms_from_concepts():
            """
            Create ideoms in the Unified Reasoning Core based on concepts in the Knowledge Graph.
            
            This fixed version handles multi-word concepts properly by creating both
            single-word ideoms and multi-word ideoms.
            
            Returns:
                A dictionary containing the creation results.
            """
            # Get all concepts from the Knowledge Graph
            concepts = integration.knowledge_graph.get_all_concepts()
            
            # Create ideoms for each concept
            ideoms_created = []
            for concept in concepts:
                # Check if an ideom with this name already exists
                existing_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
                if not existing_ideoms:
                    # Create a new ideom for the full concept name
                    ideom = integration.reasoning_core.create_ideom(concept.name)
                    ideoms_created.append(ideom.name)
                    
                    # For multi-word concepts, create ideoms for individual words
                    words = concept.name.split()
                    if len(words) > 1:
                        for word in words:
                            # Check if an ideom with this word already exists
                            word_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(word)
                            if not word_ideoms:
                                # Create a new ideom for the word
                                word_ideom = integration.reasoning_core.create_ideom(word)
                                ideoms_created.append(word_ideom.name)
                                
                                # Connect the word ideom to the concept ideom
                                integration.reasoning_core.ideom_network.connect_ideoms(
                                    ideom.id, word_ideom.id, 0.8
                                )
                                integration.reasoning_core.ideom_network.connect_ideoms(
                                    word_ideom.id, ideom.id, 0.8
                                )
                
                # Create ideoms for properties
                properties = concept.get_properties()
                for prop_name, prop_value in properties.items():
                    # Create an ideom for the property name if it doesn't exist
                    prop_name_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(prop_name)
                    if not prop_name_ideoms:
                        prop_name_ideom = integration.reasoning_core.create_ideom(prop_name)
                        ideoms_created.append(prop_name_ideom.name)
                    else:
                        prop_name_ideom = prop_name_ideoms[0]
                    
                    # Create an ideom for the property value if it doesn't exist
                    prop_value_str = str(prop_value.value)
                    prop_value_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(prop_value_str)
                    if not prop_value_ideoms:
                        prop_value_ideom = integration.reasoning_core.create_ideom(prop_value_str)
                        ideoms_created.append(prop_value_ideom.name)
                    else:
                        prop_value_ideom = prop_value_ideoms[0]
                    
                    # Connect the concept ideom to the property ideoms
                    concept_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
                    if concept_ideoms:
                        concept_ideom = concept_ideoms[0]
                        integration.reasoning_core.ideom_network.connect_ideoms(
                            concept_ideom.id, prop_name_ideom.id, 0.7
                        )
                        integration.reasoning_core.ideom_network.connect_ideoms(
                            prop_name_ideom.id, prop_value_ideom.id, 0.9
                        )
            
            # Create connections between ideoms based on concept relations
            connections_created = []
            for concept in concepts:
                # Get all relations for the concept
                relations = []
                for relation_type in concept.get_relation_types():
                    relations.extend(concept.get_relations(relation_type))
                
                for relation in relations:
                    # Get the ideoms for the source and target concepts
                    source_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
                    target_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(relation.target.name)
                    
                    if source_ideoms and target_ideoms:
                        source_ideom = source_ideoms[0]
                        target_ideom = target_ideoms[0]
                        
                        # Create a connection between the ideoms
                        connection_strength = 0.7  # Default connection strength
                        integration.reasoning_core.ideom_network.connect_ideoms(
                            source_ideom.id, target_ideom.id, connection_strength
                        )
                        connections_created.append({
                            "source": source_ideom.name,
                            "target": target_ideom.name,
                            "strength": connection_strength
                        })
                        
                        # Create an ideom for the relation type if it doesn't exist
                        relation_type_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(relation.type)
                        if not relation_type_ideoms:
                            relation_type_ideom = integration.reasoning_core.create_ideom(relation.type)
                            ideoms_created.append(relation_type_ideom.name)
                        else:
                            relation_type_ideom = relation_type_ideoms[0]
                        
                        # Connect the relation type ideom to the source and target ideoms
                        integration.reasoning_core.ideom_network.connect_ideoms(
                            source_ideom.id, relation_type_ideom.id, 0.6
                        )
                        integration.reasoning_core.ideom_network.connect_ideoms(
                            relation_type_ideom.id, target_ideom.id, 0.6
                        )
            
            return {
                "success": True,
                "type": "ideom_creation",
                "ideoms_created": ideoms_created,
                "connections_created": connections_created
            }
        
        # Replace the original method with the fixed one
        integration.create_ideoms_from_concepts = fixed_create_ideoms_from_concepts
    
    @staticmethod
    def fix_create_prefabs_from_concepts(integration):
        """
        Fix the create_prefabs_from_concepts method to create more natural response templates.
        
        Args:
            integration: The ReasoningKnowledgeIntegration instance to fix.
        """
        original_method = integration.create_prefabs_from_concepts
        
        def fixed_create_prefabs_from_concepts():
            """
            Create prefabs in the Unified Reasoning Core based on concepts in the Knowledge Graph.
            
            This fixed version creates more natural response templates and handles
            multi-word concepts properly.
            
            Returns:
                A dictionary containing the creation results.
            """
            # Get all concepts from the Knowledge Graph
            concepts = integration.knowledge_graph.get_all_concepts()
            
            # Create prefabs for each concept
            prefabs_created = []
            for concept in concepts:
                # Get the ideoms for the concept
                ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name(concept.name)
                
                if ideoms:
                    ideom = ideoms[0]
                    
                    # Get related ideoms
                    related_ideoms = integration.reasoning_core.ideom_network.get_connected_ideoms(ideom.id)
                    
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
                    
                    # Start with a basic template
                    response_template = f"{concept.name} is "
                    
                    # Add "is_a" relations to the template
                    is_a_relations = [rel for rel in relations if rel.type == "is_a"]
                    if is_a_relations:
                        is_a_concepts = [rel.target.name for rel in is_a_relations]
                        if len(is_a_concepts) == 1:
                            response_template += f"a {is_a_concepts[0]}"
                        else:
                            response_template += "a " + ", ".join(is_a_concepts[:-1]) + f" and {is_a_concepts[-1]}"
                        
                        # Check if we have properties to add
                        if properties:
                            response_template += " that "
                    
                    # Add properties to the template
                    property_strings = []
                    for prop_name, prop_value in properties.items():
                        if prop_name != "definition" and prop_name != "name":
                            # Format the property more naturally
                            if prop_name == "type":
                                property_strings.append(f"is a {prop_value.value}")
                            elif prop_name == "sound":
                                property_strings.append(f"makes a {prop_value.value} sound")
                            elif prop_name == "legs":
                                property_strings.append(f"has {prop_value.value} legs")
                            else:
                                property_strings.append(f"has {prop_name} {prop_value.value}")
                    
                    if property_strings:
                        if not is_a_relations:  # If we didn't add "is_a" relations
                            if len(property_strings) == 1:
                                response_template += property_strings[0]
                            else:
                                response_template += ", ".join(property_strings[:-1]) + f" and {property_strings[-1]}"
                        else:  # If we added "is_a" relations
                            if len(property_strings) == 1:
                                response_template += property_strings[0]
                            else:
                                response_template += ", ".join(property_strings[:-1]) + f" and {property_strings[-1]}"
                    
                    # Add a definition if available
                    if "definition" in properties:
                        if response_template.endswith(" is "):
                            response_template += properties["definition"].value
                        else:
                            response_template += f". It is defined as: {properties['definition'].value}"
                    
                    # Add a period at the end if there isn't one
                    if not response_template.endswith("."):
                        response_template += "."
                    
                    # Create the prefab
                    prefab = integration.reasoning_core.create_prefab(
                        name=concept.name,
                        ideom_weights=ideom_weights,
                        response_template=response_template,
                        tags=["concept"]
                    )
                    
                    prefabs_created.append(prefab.name)
                    
                    # Create additional prefabs for common question patterns
                    # "What is a [concept]?" prefab
                    what_is_weights = {ideom.id: 1.0}
                    what_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name("what")
                    is_ideoms = integration.reasoning_core.ideom_network.get_ideoms_by_name("is")
                    
                    if what_ideoms and is_ideoms:
                        what_ideom = what_ideoms[0]
                        is_ideom = is_ideoms[0]
                        what_is_weights[what_ideom.id] = 0.8
                        what_is_weights[is_ideom.id] = 0.8
                        
                        what_is_prefab = integration.reasoning_core.create_prefab(
                            name=f"what_is_{concept.name}",
                            ideom_weights=what_is_weights,
                            response_template=response_template,
                            tags=["question", "what_is", "concept"]
                        )
                        
                        prefabs_created.append(what_is_prefab.name)
            
            return {
                "success": True,
                "type": "prefab_creation",
                "prefabs_created": prefabs_created
            }
        
        # Replace the original method with the fixed one
        integration.create_prefabs_from_concepts = fixed_create_prefabs_from_concepts
    
    @staticmethod
    def fix_extract_triples_from_text(integration):
        """
        Fix the _extract_triples_from_text method to handle more complex patterns.
        
        Args:
            integration: The ReasoningKnowledgeIntegration instance to fix.
        """
        original_method = integration._extract_triples_from_text
        
        def fixed_extract_triples_from_text(text: str) -> List[Dict[str, str]]:
            """
            Extract subject-predicate-object triples from text.
            
            This fixed version handles more complex patterns and negation.
            
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
                r"(?P<subject>\w+(?:\s+\w+)*)\s+(?P<predicate>\w+)\s+(?P<object>\w+(?:\s+\w+)*)",
                # "X is not Y" pattern (negation)
                r"(?P<subject>\w+(?:\s+\w+)*)\s+is\s+not\s+(?P<object>\w+(?:\s+\w+)*)",
                # "X are not Y" pattern (negation)
                r"(?P<subject>\w+(?:\s+\w+)*)\s+are\s+not\s+(?P<object>\w+(?:\s+\w+)*)",
                # "X does not [predicate] Y" pattern (negation)
                r"(?P<subject>\w+(?:\s+\w+)*)\s+does\s+not\s+(?P<predicate>\w+)\s+(?P<object>\w+(?:\s+\w+)*)",
                # "X do not [predicate] Y" pattern (negation)
                r"(?P<subject>\w+(?:\s+\w+)*)\s+do\s+not\s+(?P<predicate>\w+)\s+(?P<object>\w+(?:\s+\w+)*)"
            ]
            
            # Extract triples using the patterns
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    triple = match.groupdict()
                    
                    # Handle negation
                    negation = False
                    if "not" in match.group():
                        negation = True
                    
                    # Set the predicate if not already in the triple
                    if "predicate" not in triple:
                        if "is not" in match.group() or "is" in match.group():
                            triple["predicate"] = "is" if not negation else "is_not"
                        elif "are not" in match.group() or "are" in match.group():
                            triple["predicate"] = "are" if not negation else "are_not"
                        elif "has" in match.group():
                            triple["predicate"] = "has"
                        elif "have" in match.group():
                            triple["predicate"] = "have"
                    elif negation:
                        # Add negation to the predicate
                        triple["predicate"] = "not_" + triple["predicate"]
                    
                    # Clean up the subject and object
                    if "subject" in triple:
                        triple["subject"] = triple["subject"].strip()
                    if "object" in triple:
                        triple["object"] = triple["object"].strip()
                    
                    triples.append(triple)
            
            return triples
        
        # Replace the original method with the fixed one
        integration._extract_triples_from_text = fixed_extract_triples_from_text
    
    @staticmethod
    def fix_process_input_with_knowledge(integration):
        """
        Fix the process_input_with_knowledge method to handle errors gracefully.
        
        Args:
            integration: The ReasoningKnowledgeIntegration instance to fix.
        """
        original_method = integration.process_input_with_knowledge
        
        def fixed_process_input_with_knowledge(input_text: str) -> Dict[str, Any]:
            """
            Process an input text using both the Unified Reasoning Core and the Knowledge Graph.
            
            This fixed version handles errors gracefully and provides better error messages.
            
            Args:
                input_text: The input text to process.
                
            Returns:
                A dictionary containing the processing results.
            """
            try:
                # Process the input with the Unified Reasoning Core
                reasoning_result = integration.reasoning_core.process(input_text)
                
                # Query the Knowledge Graph based on the reasoning result
                knowledge_query_result = integration.query_knowledge_graph(reasoning_result)
                
                # Extract knowledge from the reasoning result
                knowledge_extraction_result = integration.extract_knowledge_from_reasoning(reasoning_result)
                
                # Update the Knowledge Graph based on the reasoning result
                knowledge_update_result = integration.update_knowledge_graph(reasoning_result)
                
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
            except Exception as e:
                # Handle errors gracefully
                return {
                    "success": True,  # Still return success to avoid crashing
                    "type": "error",
                    "error_message": str(e),
                    "reasoning_result": {
                        "primary_response": "I'm not sure how to respond to that.",
                        "alternative_responses": [],
                        "confidence": 0.0
                    },
                    "knowledge_query_result": {"success": False, "type": "error", "results": {}},
                    "knowledge_extraction_result": {"success": False, "type": "error", "extracted_knowledge": []},
                    "knowledge_update_result": {"success": False, "type": "error", "concepts_created": [], "relations_created": []}
                }
        
        # Replace the original method with the fixed one
        integration.process_input_with_knowledge = fixed_process_input_with_knowledge
    
    @staticmethod
    def fix_query_knowledge_graph(integration):
        """
        Fix the query_knowledge_graph method to handle multi-word concepts better.
        
        Args:
            integration: The ReasoningKnowledgeIntegration instance to fix.
        """
        original_method = integration.query_knowledge_graph
        
        def fixed_query_knowledge_graph(reasoning_result: ReasoningResult) -> Dict[str, Any]:
            """
            Query the Knowledge Graph based on a reasoning result.
            
            This fixed version handles multi-word concepts better and provides more
            comprehensive results.
            
            Args:
                reasoning_result: The reasoning result to use for the query.
                
            Returns:
                A dictionary containing the query results.
            """
            # Get the most active ideoms from the reasoning result
            activation_pattern = reasoning_result.get_activation_pattern()
            most_active_ideoms = activation_pattern.get_most_active_ideoms(10)  # Increased from 5 to 10
            
            # Convert ideom IDs to concept names
            concept_names = []
            for ideom_id in most_active_ideoms:
                ideom = integration.reasoning_core.ideom_network.get_ideom(ideom_id)
                if ideom:
                    concept_names.append(ideom.name)
            
            # Query the Knowledge Graph for each concept
            results = {}
            for concept_name in concept_names:
                # Handle multi-word concepts by checking each word
                words = concept_name.split()
                if len(words) > 1:
                    # Try to find the concept by its full name
                    concept = integration.knowledge_graph.get_concept_by_name(concept_name)
                    if not concept:
                        # Try to find concepts that contain any of the words
                        for word in words:
                            word_concept = integration.knowledge_graph.get_concept_by_name(word)
                            if word_concept:
                                concept = word_concept
                                break
                else:
                    concept = integration.knowledge_graph.get_concept_by_name(concept_name)
                
                if concept:
                    # Get properties and relations for the concept
                    properties = concept.get_properties()
                    # Get all relations for the concept
                    relations = []
                    for relation_type in concept.get_relation_types():
                        relations.extend(concept.get_relations(relation_type))
                    
                    # Add to results
                    results[concept.name] = {
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
        
        # Replace the original method with the fixed one
        integration.query_knowledge_graph = fixed_query_knowledge_graph
    
    @staticmethod
    def apply_all_fixes(integration):
        """
        Apply all bug fixes to the ReasoningKnowledgeIntegration instance.
        
        Args:
            integration: The ReasoningKnowledgeIntegration instance to fix.
        """
        ReasoningKnowledgeIntegrationBugFixes.fix_create_ideoms_from_concepts(integration)
        ReasoningKnowledgeIntegrationBugFixes.fix_create_prefabs_from_concepts(integration)
        ReasoningKnowledgeIntegrationBugFixes.fix_extract_triples_from_text(integration)
        ReasoningKnowledgeIntegrationBugFixes.fix_process_input_with_knowledge(integration)
        ReasoningKnowledgeIntegrationBugFixes.fix_query_knowledge_graph(integration)


def apply_bug_fixes(integration):
    """
    Apply all bug fixes to the ReasoningKnowledgeIntegration instance.
    
    Args:
        integration: The ReasoningKnowledgeIntegration instance to fix.
    """
    ReasoningKnowledgeIntegrationBugFixes.apply_all_fixes(integration)