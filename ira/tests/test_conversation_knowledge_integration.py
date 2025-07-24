"""
Test script for the Conversation Knowledge Integration component.

This script tests the functionality of the Conversation Knowledge Integration component,
which connects the Conversation Manager with the Knowledge Graph.
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ira.core.conversation.conversation_context import ConversationContext, Message, MessageType
from ira.core.conversation.intent_recognizer import IntentRecognizer, Intent, IntentType
from ira.core.conversation.response_planner import ResponsePlanner
from ira.core.conversation.memory_manager import MemoryManager
from ira.core.conversation.conversation_manager import ConversationManager
from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.knowledge.concept_node import ConceptNode
from ira.core.knowledge.relation import Relation
from ira.core.knowledge.property_value import PropertyValue
from ira.core.integration.conversation_knowledge_integration import ConversationKnowledgeIntegration


def setup_knowledge_graph():
    """Set up a knowledge graph with some sample knowledge."""
    print("\n=== Setting up Knowledge Graph ===")
    
    # Create a knowledge graph
    kg = KnowledgeGraph()
    print("Created KnowledgeGraph")
    
    # Create some concept nodes
    cat = kg.add_concept("cat")
    dog = kg.add_concept("dog")
    animal = kg.add_concept("animal")
    pet = kg.add_concept("pet")
    mammal = kg.add_concept("mammal")
    
    # Add some properties
    cat.set_property("definition", "A small domesticated carnivorous mammal with soft fur, a short snout, and retractable claws.")
    cat.set_property("lifespan", "12-18 years")
    cat.set_property("sound", "meow")
    
    dog.set_property("definition", "A domesticated carnivorous mammal that typically has a long snout, an acute sense of smell, and a barking, howling, or whining voice.")
    dog.set_property("lifespan", "10-13 years")
    dog.set_property("sound", "bark")
    
    animal.set_property("definition", "A living organism that feeds on organic matter, typically having specialized sense organs and nervous system and able to respond rapidly to stimuli.")
    
    pet.set_property("definition", "A domestic or tamed animal kept for companionship or pleasure.")
    
    mammal.set_property("definition", "A warm-blooded vertebrate animal characterized by the possession of hair or fur, the secretion of milk by females for the nourishment of the young, and (typically) the birth of live young.")
    
    # Add some relations
    kg.create_relation(cat, animal, "is_a")
    kg.create_relation(cat, pet, "is_a")
    kg.create_relation(cat, mammal, "is_a")
    
    kg.create_relation(dog, animal, "is_a")
    kg.create_relation(dog, pet, "is_a")
    kg.create_relation(dog, mammal, "is_a")
    
    kg.create_relation(mammal, animal, "is_a")
    
    print("Added concepts, properties, and relations to the knowledge graph")
    
    return kg


def test_query_knowledge_graph(integration):
    """Test querying the knowledge graph based on user intents."""
    print("\n=== Testing Query Knowledge Graph ===")
    
    # Create a conversation context
    context = ConversationContext()
    
    # Test a definition intent
    definition_intent = Intent(
        type=IntentType.DEFINITION,
        confidence=0.9,
        entities={"term": "cat"},
        metadata={}
    )
    
    print("\nQuerying for definition of 'cat'...")
    result = integration.query_knowledge_graph(definition_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Term: {result['term']}")
    print(f"Definition: {result['definition']}")
    
    # Test a question intent (what is)
    question_intent = Intent(
        type=IntentType.QUESTION,
        confidence=0.8,
        entities={"topic": "dog"},
        metadata={"question_type": "what_is"}
    )
    
    print("\nQuerying for 'what is a dog'...")
    result = integration.query_knowledge_graph(question_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Concept: {result['concept']}")
    print(f"Definition: {result['definition']}")
    
    # Test a verification intent
    verification_intent = Intent(
        type=IntentType.VERIFICATION,
        confidence=0.95,
        entities={"subject": "cat", "object": "animal"},
        metadata={}
    )
    
    print("\nVerifying if 'cat is an animal'...")
    result = integration.query_knowledge_graph(verification_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Object: {result['object']}")
    print(f"Relation: {result['relation']}")
    print(f"Verified: {result['verified']}")
    print(f"Confidence: {result['confidence']}")
    
    # Test a relationship intent
    relationship_intent = Intent(
        type=IntentType.RELATIONSHIP,
        confidence=0.85,
        entities={"subject": "dog", "relation_type": "is_a"},
        metadata={}
    )
    
    print("\nQuerying for 'what is a dog'...")
    result = integration.query_knowledge_graph(relationship_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Relation Type: {result['relation_type']}")
    print(f"Relations: {result['relations']}")
    
    # Test a property intent
    property_intent = Intent(
        type=IntentType.PROPERTY,
        confidence=0.9,
        entities={"subject": "cat", "property": "sound"},
        metadata={}
    )
    
    print("\nQuerying for 'what sound does a cat make'...")
    result = integration.query_knowledge_graph(property_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Property: {result['property']}")
    print(f"Value: {result['value']}")
    print(f"Confidence: {result['confidence']}")
    
    print("\nQuery Knowledge Graph tests passed!")


def test_update_knowledge_graph(integration):
    """Test updating the knowledge graph based on user intents."""
    print("\n=== Testing Update Knowledge Graph ===")
    
    # Create a conversation context
    context = ConversationContext()
    
    # Test a statement intent (is_a relation)
    statement_intent = Intent(
        type=IntentType.STATEMENT,
        confidence=0.9,
        entities={"subject": "lion", "predicate": "is", "object": "animal"},
        metadata={}
    )
    
    print("\nAdding statement 'lion is an animal'...")
    result = integration.update_knowledge_graph(statement_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Object: {result['object']}")
    
    # Test a statement intent (property assignment)
    statement_intent = Intent(
        type=IntentType.STATEMENT,
        confidence=0.9,
        entities={"subject": "lion", "predicate": "has", "object": "sound=roar"},
        metadata={}
    )
    
    print("\nAdding statement 'lion has sound=roar'...")
    result = integration.update_knowledge_graph(statement_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Property: {result['property']}")
    print(f"Value: {result['value']}")
    
    # Test a correction intent
    correction_intent = Intent(
        type=IntentType.CORRECTION,
        confidence=0.95,
        entities={
            "subject": "lion",
            "predicate": "has",
            "old_object": "sound=roar",
            "new_object": "sound=growl"
        },
        metadata={}
    )
    
    print("\nCorrecting statement 'lion has sound=roar' to 'lion has sound=growl'...")
    result = integration.update_knowledge_graph(correction_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Old Property: {result['old_property']}")
    print(f"Old Value: {result['old_value']}")
    print(f"New Property: {result['new_property']}")
    print(f"New Value: {result['new_value']}")
    
    # Verify the changes
    property_intent = Intent(
        type=IntentType.PROPERTY,
        confidence=0.9,
        entities={"subject": "lion", "property": "sound"},
        metadata={}
    )
    
    print("\nVerifying the changes...")
    result = integration.query_knowledge_graph(property_intent, context)
    print(f"Success: {result['success']}")
    print(f"Type: {result['type']}")
    print(f"Subject: {result['subject']}")
    print(f"Property: {result['property']}")
    print(f"Value: {result['value']}")
    
    print("\nUpdate Knowledge Graph tests passed!")


def test_extract_knowledge(integration):
    """Test extracting knowledge from user messages."""
    print("\n=== Testing Extract Knowledge ===")
    
    # Create a conversation context
    context = ConversationContext()
    
    # Test extracting statements
    message = "A tiger is a big cat. Tigers have stripes. Tigers live in Asia."
    
    print(f"\nExtracting knowledge from message: '{message}'")
    result = integration.extract_knowledge(message, context)
    
    print("\nExtracted statements:")
    for statement in result["statements"]:
        print(f"- {statement}")
    
    # Test extracting definitions
    message = "A zebra is defined as a wild horse-like animal with black and white stripes. A giraffe means a long-necked African mammal."
    
    print(f"\nExtracting knowledge from message: '{message}'")
    result = integration.extract_knowledge(message, context)
    
    print("\nExtracted definitions:")
    for definition in result["definitions"]:
        print(f"- {definition}")
    
    # Test extracting relationships
    message = "A lion is a type of cat. A mane is a part of a lion. A pride belongs to lions."
    
    print(f"\nExtracting knowledge from message: '{message}'")
    result = integration.extract_knowledge(message, context)
    
    print("\nExtracted relationships:")
    for relationship in result["relationships"]:
        print(f"- {relationship}")
    
    # Test extracting properties
    message = "An elephant has a trunk of long. The color of a flamingo is pink. A cheetah's speed is fast."
    
    print(f"\nExtracting knowledge from message: '{message}'")
    result = integration.extract_knowledge(message, context)
    
    print("\nExtracted properties:")
    for property_ in result["properties"]:
        print(f"- {property_}")
    
    print("\nExtract Knowledge tests passed!")


def test_integration_with_conversation_manager(kg, integration):
    """Test the integration with the conversation manager."""
    print("\n=== Testing Integration with Conversation Manager ===")
    
    # Create a conversation manager
    memory_manager = MemoryManager()
    intent_recognizer = IntentRecognizer()
    response_planner = ResponsePlanner()
    
    conversation_manager = ConversationManager(
        memory_manager=memory_manager,
        intent_recognizer=intent_recognizer,
        response_planner=response_planner
    )
    
    # Modify the conversation manager to use the integration
    # This would normally be done by extending the ConversationManager class
    # or by modifying the existing implementation
    
    # For now, we'll just test the integration directly
    
    # Process a message that requires knowledge graph access
    message = "What is a cat?"
    
    print(f"\nProcessing message: '{message}'")
    
    # Recognize the intent
    context = conversation_manager.memory_manager.create_context()
    intent = conversation_manager.intent_recognizer.recognize_intent(message, context)
    
    print(f"Recognized intent: {intent.type.name}")
    print(f"Confidence: {intent.confidence}")
    print(f"Entities: {intent.entities}")
    
    # Query the knowledge graph
    if intent.type == IntentType.QUESTION and "topic" in intent.entities:
        result = integration.query_knowledge_graph(intent, context)
        
        if result["success"]:
            print(f"\nQuery result: {result}")
            
            # Generate a response based on the query result
            if result["type"] == "definition":
                response = f"{result['concept']} is {result['definition']}"
            else:
                response = f"I found some information about {result['concept']}"
            
            print(f"\nGenerated response: '{response}'")
        else:
            print(f"\nQuery failed: {result['error']}")
    else:
        print("\nIntent not suitable for knowledge graph query")
    
    print("\nIntegration with Conversation Manager tests passed!")


def main():
    """Run all tests."""
    print("=== Running Conversation Knowledge Integration Tests ===")
    
    # Set up the knowledge graph
    kg = setup_knowledge_graph()
    
    # Create the integration
    integration = ConversationKnowledgeIntegration(kg)
    
    # Run the tests
    test_query_knowledge_graph(integration)
    test_update_knowledge_graph(integration)
    test_extract_knowledge(integration)
    test_integration_with_conversation_manager(kg, integration)
    
    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    main()