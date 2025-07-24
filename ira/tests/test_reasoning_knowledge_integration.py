"""
Test module for the integration between the Unified Reasoning Core and the Knowledge Graph.

This module tests the integration between the Unified Reasoning Core and the Knowledge Graph
to ensure that ideoms and prefabs are created correctly from concepts in the Knowledge Graph,
and that the processing of messages using the integrated components works correctly.
"""

import unittest
from ira.core.ira_system import IRASystem
from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.knowledge.concept_node import ConceptNode
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration


class TestReasoningKnowledgeIntegration(unittest.TestCase):
    """Test case for the integration between the Unified Reasoning Core and the Knowledge Graph."""

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
        
        # Create an Ideom Network
        self.ideom_network = IdeomNetwork()
        
        # Create a Unified Reasoning Core
        self.reasoning_core = UnifiedReasoningCore(ideom_network=self.ideom_network)
        
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

    def test_create_ideoms_from_concepts(self):
        """Test creating ideoms from concepts in the Knowledge Graph."""
        # Create ideoms from concepts
        self.reasoning_integration.create_ideoms_from_concepts()
        
        # Check if ideoms were created for the concepts
        dog_ideoms = self.ideom_network.get_ideoms_by_name("dog")
        cat_ideoms = self.ideom_network.get_ideoms_by_name("cat")
        self.assertTrue(len(dog_ideoms) > 0)
        self.assertTrue(len(cat_ideoms) > 0)
        
        # Check if ideoms were created for the properties
        animal_ideoms = self.ideom_network.get_ideoms_by_name("animal")
        four_ideoms = self.ideom_network.get_ideoms_by_name("four")
        bark_ideoms = self.ideom_network.get_ideoms_by_name("bark")
        meow_ideoms = self.ideom_network.get_ideoms_by_name("meow")
        
        self.assertTrue(len(animal_ideoms) > 0)
        self.assertTrue(len(four_ideoms) > 0)
        self.assertTrue(len(bark_ideoms) > 0)
        self.assertTrue(len(meow_ideoms) > 0)

    def test_create_prefabs_from_concepts(self):
        """Test creating prefabs from concepts in the Knowledge Graph."""
        # Create ideoms from concepts first
        self.reasoning_integration.create_ideoms_from_concepts()
        
        # Create prefabs from concepts
        self.reasoning_integration.create_prefabs_from_concepts()
        
        # Check if prefabs were created for the concepts
        prefabs = self.reasoning_core.prefab_manager.get_all_prefabs()
        
        # There should be at least 2 prefabs (one for each concept)
        self.assertGreaterEqual(len(prefabs), 2)
        
        # Check if there's a prefab for "dog"
        dog_prefabs = [p for p in prefabs if "dog" in p.name]
        self.assertGreaterEqual(len(dog_prefabs), 1)
        
        # Check if there's a prefab for "cat"
        cat_prefabs = [p for p in prefabs if "cat" in p.name]
        self.assertGreaterEqual(len(cat_prefabs), 1)

    def test_process_input_with_knowledge(self):
        """Test processing input with knowledge."""
        # Create ideoms and prefabs from concepts
        self.reasoning_integration.create_ideoms_from_concepts()
        self.reasoning_integration.create_prefabs_from_concepts()
        
        # Process input with knowledge
        result = self.reasoning_integration.process_input_with_knowledge("What is a dog?")
        
        # Check if the result contains information about dogs
        self.assertIsNotNone(result)
        self.assertIn("dog", str(result).lower())

    def test_ira_system_integration(self):
        """Test the integration in the IRA system."""
        # Process a message using the IRA system
        response = self.ira_system.process_message("What is a dog?")
        
        # Check if the response contains information about dogs
        self.assertIsNotNone(response)
        self.assertIn("dog", response.lower())
        
        # Process another message
        response = self.ira_system.process_message("What sound does a cat make?")
        
        # Check if the response contains information about cat sounds
        self.assertIsNotNone(response)
        self.assertIn("meow", response.lower())


if __name__ == "__main__":
    unittest.main()