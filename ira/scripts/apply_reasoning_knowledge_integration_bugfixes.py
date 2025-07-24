#!/usr/bin/env python3
"""
Script to apply bug fixes to the ReasoningKnowledgeIntegration class and run tests.

This script applies the bug fixes from the ReasoningKnowledgeIntegrationBugFixes class
to the ReasoningKnowledgeIntegration class and runs the enhanced tests to verify that
the bugs have been fixed.
"""

import os
import sys
import unittest
import importlib
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes
from ira.core.ira_system import IRASystem
from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore


def apply_fixes_and_run_tests():
    """
    Apply bug fixes to the ReasoningKnowledgeIntegration class and run tests.
    """
    print("Applying bug fixes to ReasoningKnowledgeIntegration...")
    
    # Create a test instance of ReasoningKnowledgeIntegration
    knowledge_graph = KnowledgeGraph()
    ideom_network = IdeomNetwork()
    reasoning_core = UnifiedReasoningCore(ideom_network=ideom_network)
    integration = ReasoningKnowledgeIntegration(knowledge_graph, reasoning_core)
    
    # Apply bug fixes
    apply_bug_fixes(integration)
    
    print("Bug fixes applied successfully.")
    
    # Run the enhanced tests
    print("\nRunning enhanced tests...")
    
    # Import the test module
    test_module = importlib.import_module("ira.tests.test_enhanced_reasoning_knowledge_integration")
    
    # Create a test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Print the test results
    print("\nTest Results:")
    print(f"  Ran {test_result.testsRun} tests")
    print(f"  Failures: {len(test_result.failures)}")
    print(f"  Errors: {len(test_result.errors)}")
    print(f"  Skipped: {len(test_result.skipped)}")
    
    # Print detailed information about failures and errors
    if test_result.failures:
        print("\nFailures:")
        for test, traceback in test_result.failures:
            print(f"  {test}")
            print(f"  {traceback}")
    
    if test_result.errors:
        print("\nErrors:")
        for test, traceback in test_result.errors:
            print(f"  {test}")
            print(f"  {traceback}")
    
    # Return True if all tests passed, False otherwise
    return len(test_result.failures) == 0 and len(test_result.errors) == 0


def demonstrate_fixes():
    """
    Demonstrate the bug fixes by running some examples.
    """
    print("\nDemonstrating bug fixes with examples...")
    
    # Create a Knowledge Graph with some test concepts
    knowledge_graph = KnowledgeGraph()
    
    # Add some test concepts
    dog_concept = knowledge_graph.add_concept("dog")
    knowledge_graph.update_concept(
        dog_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "bark"
        }
    )
    
    cat_concept = knowledge_graph.add_concept("cat")
    knowledge_graph.update_concept(
        cat_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "meow"
        }
    )
    
    # Add a more complex concept with relationships
    animal_concept = knowledge_graph.add_concept("animal")
    knowledge_graph.update_concept(
        animal_concept.id,
        properties={
            "type": "category",
            "definition": "A living organism that feeds on organic matter"
        }
    )
    
    # Create relationships
    knowledge_graph.update_relation(dog_concept, animal_concept, "is_a", bidirectional=False)
    knowledge_graph.update_relation(cat_concept, animal_concept, "is_a", bidirectional=False)
    
    # Create an Ideom Network
    ideom_network = IdeomNetwork()
    
    # Create a Unified Reasoning Core
    reasoning_core = UnifiedReasoningCore(ideom_network=ideom_network)
    
    # Create a Reasoning Knowledge Integration
    integration = ReasoningKnowledgeIntegration(knowledge_graph, reasoning_core)
    
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
    
    # Example 1: Multi-word concept handling
    print("\nExample 1: Multi-word concept handling")
    result = integration.process_input_with_knowledge("What is a domestic dog?")
    print(f"Response: {result['reasoning_result']['primary_response']}")
    
    # Example 2: Error handling
    print("\nExample 2: Error handling")
    result = integration.process_input_with_knowledge("")
    print(f"Response: {result['reasoning_result']['primary_response']}")
    
    # Example 3: Knowledge extraction
    print("\nExample 3: Knowledge extraction")
    result = integration.process_input_with_knowledge("Dogs are loyal pets.")
    print(f"Extracted knowledge: {result['knowledge_extraction_result']['extracted_knowledge']}")
    
    # Example 4: Multi-turn conversation
    print("\nExample 4: Multi-turn conversation")
    response1 = ira_system.process_message("What is a dog?")
    print(f"Response 1: {response1}")
    response2 = ira_system.process_message("What sound does it make?")
    print(f"Response 2: {response2}")
    
    print("\nDemonstration completed.")


if __name__ == "__main__":
    # Apply fixes and run tests
    tests_passed = apply_fixes_and_run_tests()
    
    if tests_passed:
        print("\nAll tests passed!")
        
        # Demonstrate the fixes
        demonstrate_fixes()
    else:
        print("\nSome tests failed. Please check the test results above.")