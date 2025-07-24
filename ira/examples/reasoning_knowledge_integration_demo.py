#!/usr/bin/env python3
"""
Demo of the enhanced integration between the Unified Reasoning Core and the Knowledge Graph.

This script demonstrates how to use the enhanced integration between the Unified Reasoning Core
and the Knowledge Graph, including the bug fixes and enhancements.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.knowledge.concept_node import ConceptNode
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.reasoning.temporal_context import TemporalContext
from ira.core.reasoning.signal_propagator import SignalPropagator
from ira.core.reasoning.text_processor import TextProcessor
from ira.core.reasoning.dynamic_response_generator import DynamicResponseGenerator
from ira.core.reasoning.learning_engine import LearningEngine, Feedback
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes
from ira.core.ira_system import IRASystem


def create_test_knowledge_graph():
    """
    Create a test Knowledge Graph with some concepts.
    
    Returns:
        A KnowledgeGraph instance with test concepts.
    """
    knowledge_graph = KnowledgeGraph()
    
    # Add some test concepts
    dog_concept = knowledge_graph.add_concept("dog")
    knowledge_graph.update_concept(
        dog_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "bark",
            "definition": "A domesticated carnivorous mammal that typically has a long snout, an acute sense of smell, and a barking, howling, or whining voice."
        }
    )
    
    cat_concept = knowledge_graph.add_concept("cat")
    knowledge_graph.update_concept(
        cat_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "meow",
            "definition": "A small domesticated carnivorous mammal with soft fur, a short snout, and retractile claws."
        }
    )
    
    # Add a more complex concept with relationships
    animal_concept = knowledge_graph.add_concept("animal")
    knowledge_graph.update_concept(
        animal_concept.id,
        properties={
            "type": "category",
            "definition": "A living organism that feeds on organic matter, typically having specialized sense organs and nervous system and able to respond rapidly to stimuli."
        }
    )
    
    # Create relationships
    knowledge_graph.update_relation(dog_concept, animal_concept, "is_a", bidirectional=False)
    knowledge_graph.update_relation(cat_concept, animal_concept, "is_a", bidirectional=False)
    
    # Add some more concepts
    bird_concept = knowledge_graph.add_concept("bird")
    knowledge_graph.update_concept(
        bird_concept.id,
        properties={
            "type": "animal",
            "legs": "two",
            "wings": "two",
            "sound": "chirp",
            "definition": "A warm-blooded egg-laying vertebrate animal distinguished by the possession of feathers, wings, a beak, and typically by being able to fly."
        }
    )
    
    knowledge_graph.update_relation(bird_concept, animal_concept, "is_a", bidirectional=False)
    
    # Add a multi-word concept
    golden_retriever_concept = knowledge_graph.add_concept("golden retriever")
    knowledge_graph.update_concept(
        golden_retriever_concept.id,
        properties={
            "type": "dog breed",
            "coat": "golden",
            "temperament": "friendly",
            "definition": "A medium-large gun dog that was bred to retrieve shot waterfowl, such as ducks and upland game birds, during hunting and shooting parties."
        }
    )
    
    knowledge_graph.update_relation(golden_retriever_concept, dog_concept, "is_a", bidirectional=False)
    
    return knowledge_graph


def create_enhanced_integration():
    """
    Create an enhanced integration between the Unified Reasoning Core and the Knowledge Graph.
    
    Returns:
        A tuple containing the IRASystem instance and the ReasoningKnowledgeIntegration instance.
    """
    # Create a Knowledge Graph
    knowledge_graph = create_test_knowledge_graph()
    
    # Create an Ideom Network
    ideom_network = IdeomNetwork()
    
    # Create a Temporal Context
    temporal_context = TemporalContext(max_history_size=5)
    
    # Create a Signal Propagator with temporal context
    signal_propagator = SignalPropagator(
        ideom_network=ideom_network,
        temporal_context=temporal_context
    )
    
    # Create a Unified Reasoning Core with enhanced components
    reasoning_core = UnifiedReasoningCore(
        ideom_network=ideom_network,
        signal_propagator=signal_propagator
    )
    
    # Create a Text Processor
    text_processor = TextProcessor(ideom_network=ideom_network)
    
    # Create a Dynamic Response Generator
    response_generator = DynamicResponseGenerator(ideom_network=ideom_network)
    
    # Create a Learning Engine
    learning_engine = LearningEngine(
        ideom_network=ideom_network,
        prefab_manager=reasoning_core.prefab_manager
    )
    
    # Create a Reasoning Knowledge Integration
    integration = ReasoningKnowledgeIntegration(
        knowledge_graph,
        reasoning_core
    )
    
    # Apply bug fixes
    apply_bug_fixes(integration)
    
    # Create an IRA System
    ira_system = IRASystem(
        knowledge_graph=knowledge_graph,
        ideom_network=ideom_network,
        reasoning_core=reasoning_core,
        reasoning_integration=integration
    )
    
    # Initialize the integration
    integration.create_ideoms_from_concepts()
    integration.create_prefabs_from_concepts()
    
    return ira_system, integration


def demonstrate_enhanced_integration():
    """
    Demonstrate the enhanced integration between the Unified Reasoning Core and the Knowledge Graph.
    """
    print("Creating enhanced integration...")
    ira_system, integration = create_enhanced_integration()
    
    print("\nDemonstrating enhanced integration...")
    
    # Example 1: Basic query
    print("\nExample 1: Basic query")
    query = "What is a dog?"
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    # Example 2: Multi-word concept handling
    print("\nExample 2: Multi-word concept handling")
    query = "What is a golden retriever?"
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    # Example 3: Semantic understanding
    print("\nExample 3: Semantic understanding")
    query = "What is a canine?"
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    # Example 4: Multi-turn conversation
    print("\nExample 4: Multi-turn conversation")
    query = "Tell me about animals."
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    query = "Which ones have four legs?"
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    # Example 5: Knowledge extraction
    print("\nExample 5: Knowledge extraction")
    query = "Dogs are loyal companions that protect their owners."
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    # Check if the knowledge was extracted
    query = "Are dogs loyal?"
    print(f"Query: {query}")
    response = ira_system.process_message(query)
    print(f"Response: {response}")
    
    # Example 6: Error handling
    print("\nExample 6: Error handling")
    query = ""
    print(f"Query: {query} (empty query)")
    result = integration.process_input_with_knowledge(query)
    print(f"Response: {result['reasoning_result']['primary_response']}")
    
    # Example 7: Learning from feedback
    print("\nExample 7: Learning from feedback")
    query = "What is a bird?"
    print(f"Query: {query}")
    result = integration.reasoning_core.process(query)
    print(f"Response: {result.get_primary_response()}")
    
    # Create feedback with a correct response
    feedback = Feedback(
        input_text=query,
        original_result=result.get_activation_pattern(),
        score=1.0,
        correct_response="A bird is a warm-blooded egg-laying vertebrate animal distinguished by the possession of feathers, wings, a beak, and typically by being able to fly. Birds are known for their ability to sing and build nests."
    )
    
    # Apply the feedback
    integration.reasoning_core.learning_engine.learn_from_feedback(feedback)
    
    # Check if the learning improved the response
    print(f"Query (after learning): {query}")
    response = ira_system.process_message(query)
    print(f"Response (after learning): {response}")
    
    print("\nDemonstration completed.")


if __name__ == "__main__":
    demonstrate_enhanced_integration()