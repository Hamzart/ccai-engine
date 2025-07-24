#!/usr/bin/env python3
"""
Run script for the IRA system.

This script serves as the entry point for the IRA (Ideom Resolver AI) system,
allowing users to interact with it through a command-line interface.
"""

import sys
import os
import argparse

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ira.core.ira_system import IRASystem


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run the IRA system.")
    
    parser.add_argument(
        "--knowledge-file",
        type=str,
        help="Path to a knowledge file to load."
    )
    
    parser.add_argument(
        "--memory-file",
        type=str,
        help="Path to a memory file to load."
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode."
    )
    
    return parser.parse_args()


def main():
    """Run the IRA system."""
    # Parse command-line arguments
    args = parse_args()
    
    # Create the IRA system
    ira = IRASystem()
    
    # TODO: Load knowledge and memory files if specified
    
    # Enable debug mode if specified
    if args.debug:
        print("Debug mode enabled.")
        # TODO: Set up debug logging
    
    # Run the command-line interface
    try:
        ira.run_cli()
    except KeyboardInterrupt:
        print("\nExiting...")
    
    print("Goodbye!")


if __name__ == "__main__":
    main()