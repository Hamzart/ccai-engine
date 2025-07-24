#!/usr/bin/env python3
"""
Script to run the Knowledge Graph tests.

This script runs the tests for the Knowledge Graph component
and displays the results.
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tests.test_knowledge_graph import run_all_tests


def main():
    """Run the Knowledge Graph tests."""
    print("Running Knowledge Graph tests...")
    print("=" * 80)
    run_all_tests()
    print("=" * 80)
    print("Knowledge Graph tests completed.")


if __name__ == "__main__":
    main()