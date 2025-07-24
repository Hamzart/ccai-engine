#!/usr/bin/env python3
"""
Script to apply all bug fixes and verify that they work correctly.

This script applies all the bug fixes to the ReasoningKnowledgeIntegration class,
runs the tests to verify that the bugs have been fixed, and demonstrates the fixes
with some examples.
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
from ira.core.reasoning.temporal_context import TemporalContext
from ira.core.reasoning.signal_propagator import SignalPropagator


def apply_fixes_and_run_tests():
    """
    Apply bug fixes to the ReasoningKnowledgeIntegration class and run tests.
    
    Returns:
        bool: True if all tests passed, False otherwise.
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


def verify_chat_interface():
    """
    Verify that the chat interface works correctly with the bug fixes.
    
    Returns:
        bool: True if the chat interface works correctly, False otherwise.
    """
    print("\nVerifying chat interface...")
    
    try:
        # Import the chat interface module
        import nltk
        
        # Check if the required NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
            print("  punkt tokenizer is available")
        except LookupError:
            print("  punkt tokenizer is not available, downloading...")
            nltk.download('punkt')
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
            print("  punkt_tab tokenizer is available")
        except LookupError:
            print("  punkt_tab tokenizer is not available, downloading...")
            # The punkt_tab resource is part of the 'all' package
            nltk.download('all')
        
        try:
            nltk.data.find('corpora/stopwords')
            print("  stopwords corpus is available")
        except LookupError:
            print("  stopwords corpus is not available, downloading...")
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
            print("  wordnet corpus is available")
        except LookupError:
            print("  wordnet corpus is not available, downloading...")
            nltk.download('wordnet')
        
        # Explicitly ensure punkt is downloaded and available
        if not nltk.download('punkt', quiet=True):
            print("  Warning: Failed to download punkt tokenizer. Some functionality may not work.")
        
        # Import the chat interface module
        from ira.chat_interface import create_enhanced_ira_system
        
        # Create an IRA system
        print("  Creating IRA system...")
        ira_system = create_enhanced_ira_system()
        
        # Test a simple query
        print("  Testing a simple query...")
        response = ira_system.process_message("What is a dog?")
        print(f"  Response: {response}")
        
        print("Chat interface verified successfully.")
        return True
    
    except Exception as e:
        print(f"Error verifying chat interface: {e}")
        return False


def run_simple_demo():
    """
    Run the simple integration demo.
    
    Returns:
        bool: True if the demo ran successfully, False otherwise.
    """
    print("\nRunning simple integration demo...")
    
    try:
        # Import the demo module
        from ira.examples.simple_integration_demo import main as demo_main
        
        # Run the demo
        demo_main()
        
        print("Simple integration demo ran successfully.")
        return True
    
    except Exception as e:
        print(f"Error running simple integration demo: {e}")
        return False


def main():
    """Run the script."""
    print("=" * 80)
    print("Applying all bug fixes and verifying that they work correctly")
    print("=" * 80)
    
    # Apply fixes and run tests
    tests_passed = apply_fixes_and_run_tests()
    
    if not tests_passed:
        print("\nSome tests failed. Please check the test results above.")
        return 1
    
    print("\nAll tests passed!")
    
    # Verify chat interface
    chat_interface_works = verify_chat_interface()
    
    if not chat_interface_works:
        print("\nChat interface verification failed. Please check the errors above.")
        return 1
    
    # Run simple demo
    demo_ran = run_simple_demo()
    
    if not demo_ran:
        print("\nSimple integration demo failed. Please check the errors above.")
        return 1
    
    print("\nAll verifications passed!")
    print("\nThe bug fixes have been applied successfully and all components work correctly.")
    print("\nYou can now use the IRA system with the enhanced integration between")
    print("the Unified Reasoning Core and the Knowledge Graph.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())