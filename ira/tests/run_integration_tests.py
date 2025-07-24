"""
Script to run the integration tests for the IRA system.

This script runs the tests for the integration between the Unified Reasoning Core
and the Knowledge Graph to ensure that the integration works correctly.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the test modules
from ira.tests.test_reasoning_knowledge_integration import TestReasoningKnowledgeIntegration


def run_tests():
    """Run the integration tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestReasoningKnowledgeIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result


if __name__ == "__main__":
    print("Running integration tests for the IRA system...")
    result = run_tests()
    
    # Print a summary of the results
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # Exit with a non-zero code if there were failures or errors
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)