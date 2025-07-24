"""
Test module for the enhanced integration between the Unified Reasoning Core and the Knowledge Graph.

This module tests the enhanced components of the integration between the Unified Reasoning Core 
and the Knowledge Graph, including the enhanced TextProcessor, SignalPropagator with temporal 
context awareness, LearningEngine with true learning mechanism, and DynamicResponseGenerator.
"""

import unittest
from datetime import datetime
from ira.core.ira_system import IRASystem
from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.knowledge.concept_node import ConceptNode
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.text_processor import TextProcessor
from ira.core.reasoning.signal_propagator import SignalPropagator
from ira.core.reasoning.learning_engine import LearningEngine, Feedback
from ira.core.reasoning.dynamic_response_generator import DynamicResponseGenerator
from ira.core.reasoning.temporal_context import TemporalContext
from ira.core.reasoning.activation_pattern import ActivationPattern
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration


class TestEnhancedReasoningKnowledgeIntegration(unittest.TestCase):
    """Test case for the enhanced integration between the Unified Reasoning Core and the Knowledge Graph."""

    def setUp(self):
        """Set up the test case."""
        # Create a Knowledge Graph with some test concepts
        self.knowledge_graph = KnowledgeGraph()
        
        # Add some test concepts
        self.dog_concept = self.knowledge_graph.add_concept("dog")
        self.knowledge_graph.update_concept(
            self.dog_concept.id,
            properties={
                "type": "animal",
                "legs": "four",
                "sound": "bark"
            }
        )
        
        self.cat_concept = self.knowledge_graph.add_concept("cat")
        self.knowledge_graph.update_concept(
            self.cat_concept.id,
            properties={
                "type": "animal",
                "legs": "four",
                "sound": "meow"
            }
        )
        
        # Add a more complex concept with relationships
        self.animal_concept = self.knowledge_graph.add_concept("animal")
        self.knowledge_graph.update_concept(
            self.animal_concept.id,
            properties={
                "type": "category",
                "definition": "A living organism that feeds on organic matter"
            }
        )
        
        # Create relationships
        self.knowledge_graph.update_relation(self.dog_concept, self.animal_concept, "is_a", bidirectional=False)
        self.knowledge_graph.update_relation(self.cat_concept, self.animal_concept, "is_a", bidirectional=False)
        
        # Create an Ideom Network
        self.ideom_network = IdeomNetwork()
        
        # Create a Temporal Context
        self.temporal_context = TemporalContext(max_history_size=5)
        
        # Create a Signal Propagator with temporal context
        self.signal_propagator = SignalPropagator(
            ideom_network=self.ideom_network,
            temporal_context=self.temporal_context
        )
        
        # Create a Unified Reasoning Core with enhanced components
        self.reasoning_core = UnifiedReasoningCore(
            ideom_network=self.ideom_network,
            signal_propagator=self.signal_propagator
        )
        
        # Create a Text Processor
        self.text_processor = TextProcessor(ideom_network=self.ideom_network)
        
        # Create a Dynamic Response Generator
        self.response_generator = DynamicResponseGenerator(ideom_network=self.ideom_network)
        
        # Create a Learning Engine
        self.learning_engine = LearningEngine(
            ideom_network=self.ideom_network,
            prefab_manager=self.reasoning_core.prefab_manager
        )
        
        # Create a Reasoning Knowledge Integration
        self.reasoning_integration = ReasoningKnowledgeIntegration(
            self.knowledge_graph,
            self.reasoning_core
        )
        
        # Create an IRA System
        self.ira_system = IRASystem(
            knowledge_graph=self.knowledge_graph,
            ideom_network=self.ideom_network,
            reasoning_core=self.reasoning_core,
            reasoning_integration=self.reasoning_integration
        )
        
        # Initialize the integration
        self.reasoning_integration.create_ideoms_from_concepts()
        self.reasoning_integration.create_prefabs_from_concepts()

    def test_enhanced_text_processor(self):
        """Test the enhanced TextProcessor with improved semantic understanding."""
        # Process text with the enhanced TextProcessor
        activations = self.text_processor.process_text("What is a canine?")
        
        # Check if "dog" is activated due to semantic similarity
        dog_activated = False
        for ideom_id, activation in activations:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom and ideom.name == "dog":
                dog_activated = True
                break
        
        self.assertTrue(dog_activated, "The word 'canine' should activate the 'dog' ideom due to semantic similarity")
        
        # Test multi-word concept handling
        activations = self.text_processor.process_text("What is a domestic cat?")
        
        # Check if "cat" is activated
        cat_activated = False
        for ideom_id, activation in activations:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom and ideom.name == "cat":
                cat_activated = True
                break
        
        self.assertTrue(cat_activated, "The phrase 'domestic cat' should activate the 'cat' ideom")

    def test_temporal_context_awareness(self):
        """Test the SignalPropagator with temporal context awareness."""
        # Process a sequence of related inputs
        self.reasoning_core.process("What is a dog?")
        self.reasoning_core.process("Do dogs bark?")
        self.reasoning_core.process("What sound does a dog make?")
        
        # Check if the temporal context has recorded the activations
        self.assertEqual(len(self.temporal_context.history), 3, "Temporal context should have 3 activation patterns")
        
        # Check if "dog" has increasing activation
        increasing_ideoms = self.temporal_context.get_increasing_activations()
        dog_increasing = False
        for ideom_id in increasing_ideoms:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom and ideom.name == "dog":
                dog_increasing = True
                break
        
        self.assertTrue(dog_increasing, "The 'dog' ideom should have increasing activation")
        
        # Test pattern prediction
        result = self.signal_propagator.propagate_with_pattern_prediction(
            source_ideom_ids=[ideom.id for ideom in self.ideom_network.get_ideoms_by_name("dog")],
            initial_strength=1.0
        )
        
        # Check if "bark" is predicted to be activated
        bark_predicted = False
        for ideom_id, activation in result.get_ideom_activations().items():
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom and ideom.name == "bark":
                bark_predicted = True
                break
        
        self.assertTrue(bark_predicted, "The 'bark' ideom should be predicted to activate based on temporal patterns")

    def test_true_learning_mechanism(self):
        """Test the LearningEngine with true learning mechanism."""
        # Process an input
        result = self.reasoning_core.process("What is a dog?")
        
        # Create feedback with a correct response
        feedback = Feedback(
            input_text="What is a dog?",
            original_result=result.get_activation_pattern(),
            score=1.0,
            correct_response="A dog is a domesticated mammal of the family Canidae."
        )
        
        # Apply the feedback
        self.learning_engine.learn_from_feedback(feedback)
        
        # Check if a new prefab was created
        prefabs = self.reasoning_core.prefab_manager.get_all_prefabs()
        learned_prefabs = [p for p in prefabs if "learned" in p.tags]
        
        self.assertTrue(len(learned_prefabs) > 0, "A new prefab should be created from feedback")
        
        # Process the same input again
        new_result = self.reasoning_core.process("What is a dog?")
        
        # Check if the response has improved
        self.assertIn("domesticated", new_result.get_primary_response().lower(), 
                     "The response should incorporate the learned information")

    def test_dynamic_response_generation(self):
        """Test the DynamicResponseGenerator for template-free responses."""
        # Create an activation pattern
        pattern = ActivationPattern()
        
        # Add activations for dog-related ideoms
        for ideom in self.ideom_network.get_ideoms_by_name("dog"):
            pattern.add_ideom_activation(ideom.id, 1.0)
        
        for ideom in self.ideom_network.get_ideoms_by_name("animal"):
            pattern.add_ideom_activation(ideom.id, 0.8)
        
        for ideom in self.ideom_network.get_ideoms_by_name("bark"):
            pattern.add_ideom_activation(ideom.id, 0.7)
        
        # Generate a response
        response = self.response_generator.generate_response(pattern)
        
        # Check if the response contains relevant words
        self.assertTrue(any(word in response.lower() for word in ["dog", "animal", "bark"]), 
                       "The generated response should contain relevant words from the activation pattern")
        
        # Generate multiple responses
        responses = self.response_generator.generate_responses(pattern, count=3)
        
        # Check if we got multiple different responses
        self.assertEqual(len(responses), 3, "Should generate 3 different responses")
        self.assertTrue(len(set(responses)) > 1, "The responses should be different from each other")

    def test_knowledge_extraction_from_reasoning(self):
        """Test extracting knowledge from reasoning results."""
        # Process an input that should generate triples
        result = self.reasoning_core.process("Dogs are animals that bark.")
        
        # Extract knowledge from the reasoning result
        extraction_result = self.reasoning_integration.extract_knowledge_from_reasoning(result)
        
        # Check if knowledge was extracted
        self.assertTrue(extraction_result["success"], "Knowledge extraction should succeed")
        self.assertTrue(len(extraction_result["extracted_knowledge"]) > 0, 
                       "Knowledge should be extracted from the reasoning result")
        
        # Check if the extracted knowledge contains relevant triples
        triples = extraction_result["extracted_knowledge"]
        dog_is_animal_triple = False
        dog_bark_triple = False
        
        for triple in triples:
            if triple.get("subject") == "dog" and triple.get("predicate") == "is" and triple.get("object") == "animal":
                dog_is_animal_triple = True
            if triple.get("subject") == "dog" and triple.get("predicate") in ["bark", "barks"]:
                dog_bark_triple = True
        
        self.assertTrue(dog_is_animal_triple or dog_bark_triple, 
                       "The extracted knowledge should contain relevant triples about dogs")

    def test_update_knowledge_graph_from_reasoning(self):
        """Test updating the Knowledge Graph based on reasoning results."""
        # Process an input with new information
        result = self.reasoning_core.process("Cats like to chase mice.")
        
        # Update the Knowledge Graph based on the reasoning result
        update_result = self.reasoning_integration.update_knowledge_graph(result)
        
        # Check if the Knowledge Graph was updated
        self.assertTrue(update_result["success"], "Knowledge Graph update should succeed")
        
        # Check if new relations were created
        self.assertTrue(len(update_result["relations_created"]) > 0, 
                       "New relations should be created in the Knowledge Graph")
        
        # Check if the cat-mice relation was created
        cat_mice_relation = False
        for relation in update_result["relations_created"]:
            if relation["source"] == "cat" and relation["target"] == "mice":
                cat_mice_relation = True
                break
        
        # If the relation wasn't created automatically, we should at least have the concepts
        if not cat_mice_relation:
            # Check if "mice" concept was created
            mice_concept = self.knowledge_graph.get_concept_by_name("mice")
            self.assertIsNotNone(mice_concept, "A concept for 'mice' should be created")

    def test_error_handling(self):
        """Test error handling in the integration."""
        # Test with a non-existent concept
        result = self.reasoning_integration.process_input_with_knowledge("What is a unicorn?")
        
        # The system should handle this gracefully
        self.assertTrue(result["success"], "The system should handle non-existent concepts gracefully")
        
        # Test with malformed input
        result = self.reasoning_integration.process_input_with_knowledge("")
        
        # The system should handle this gracefully
        self.assertTrue(result["success"], "The system should handle empty input gracefully")
        
        # Test with very long input
        long_input = "dog " * 1000
        result = self.reasoning_integration.process_input_with_knowledge(long_input)
        
        # The system should handle this gracefully
        self.assertTrue(result["success"], "The system should handle very long input gracefully")

    def test_multi_turn_conversation(self):
        """Test the integration in a multi-turn conversation."""
        # First turn
        response1 = self.ira_system.process_message("What is a dog?")
        
        # Check if the response contains information about dogs
        self.assertIn("dog", response1.lower())
        
        # Second turn - follow-up question
        response2 = self.ira_system.process_message("What sound does it make?")
        
        # Check if the response contains information about barking
        self.assertIn("bark", response2.lower())
        
        # Third turn - correction
        response3 = self.ira_system.process_message("No, I meant what sound does a cat make?")
        
        # Check if the response contains information about meowing
        self.assertIn("meow", response3.lower())

    def test_integration_with_enhanced_components(self):
        """Test the integration of all enhanced components."""
        # Initialize the system with all enhanced components
        enhanced_system = IRASystem(
            knowledge_graph=self.knowledge_graph,
            ideom_network=self.ideom_network,
            reasoning_core=self.reasoning_core,
            reasoning_integration=self.reasoning_integration
        )
        
        # Process a complex query
        response = enhanced_system.process_message("Can you tell me about animals that make sounds?")
        
        # Check if the response contains information about dogs and cats
        self.assertTrue(any(animal in response.lower() for animal in ["dog", "cat"]), 
                       "The response should mention dogs or cats")
        self.assertTrue(any(sound in response.lower() for sound in ["bark", "meow"]), 
                       "The response should mention barking or meowing")
        
        # Process a follow-up query to test temporal context
        response = enhanced_system.process_message("Which one barks?")
        
        # Check if the response correctly identifies dogs
        self.assertIn("dog", response.lower())
        self.assertIn("bark", response.lower())
        
        # Add new information to test learning
        response = enhanced_system.process_message("Dogs are loyal pets that protect their owners.")
        
        # Query again to see if the system learned
        response = enhanced_system.process_message("What are dogs?")
        
        # Check if the response includes the new information
        self.assertTrue(any(word in response.lower() for word in ["loyal", "pet", "protect"]), 
                       "The response should include the newly learned information")


if __name__ == "__main__":
    unittest.main()