#!/usr/bin/env python3
"""
Test script for the knowledge loading functionality in the IRA system.

This script demonstrates how to use the FileKnowledgeLoader and WikipediaKnowledgeLoader
components to load knowledge into the IRA system from files and Wikipedia articles.
"""

import os
import sys
from pathlib import Path
import nltk
import colorama

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading punkt tokenizer...")
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading punkt_tab tokenizer...")
    # The punkt_tab resource is part of the 'all' package
    nltk.download('all')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading stopwords...")
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading wordnet...")
    nltk.download('wordnet')

from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.learning.knowledge_loader_manager import KnowledgeLoaderManager
from ira.core.ira_system import IRASystem


# Initialize colorama for colored output
colorama.init()


def create_ira_system():
    """
    Create an IRA system with the knowledge loaders.
    
    Returns:
        An IRASystem instance with the knowledge loaders.
    """
    # Create a Knowledge Graph
    knowledge_graph = KnowledgeGraph()
    
    # Create an Ideom Network
    ideom_network = IdeomNetwork()
    
    # Create a Unified Reasoning Core
    reasoning_core = UnifiedReasoningCore(
        ideom_network=ideom_network
    )
    
    # Create a Reasoning Knowledge Integration
    integration = ReasoningKnowledgeIntegration(
        knowledge_graph,
        reasoning_core
    )
    
    # Create an IRA System
    ira_system = IRASystem(
        knowledge_graph=knowledge_graph,
        ideom_network=ideom_network,
        reasoning_core=reasoning_core,
        reasoning_integration=integration
    )
    
    return ira_system


def test_file_knowledge_loading():
    """Test loading knowledge from a file."""
    print(colorama.Fore.CYAN + "=== Testing File Knowledge Loading ===" + colorama.Style.RESET_ALL)
    
    # Create an IRA system
    ira_system = create_ira_system()
    
    # Get the path to the sample knowledge file
    sample_file_path = os.path.join(os.path.dirname(__file__), "..", "tests", "test_data", "sample_knowledge.txt")
    
    # Load knowledge from the file
    print(colorama.Fore.YELLOW + f"Loading knowledge from file: {sample_file_path}" + colorama.Style.RESET_ALL)
    result = ira_system.learn_from_file(sample_file_path)
    
    # Print the result
    if result["success"]:
        print(colorama.Fore.GREEN + "Successfully loaded knowledge from file:" + colorama.Style.RESET_ALL)
        print(f"- Chunks processed: {result.get('chunks_processed', 0)}")
        print(f"- Concepts created: {len(result.get('concepts_created', []))}")
        print(f"- Relations created: {len(result.get('relations_created', []))}")
        
        # Print some of the concepts created
        print(colorama.Fore.CYAN + "Some concepts created:" + colorama.Style.RESET_ALL)
        for concept in result.get("concepts_created", [])[:5]:
            print(f"- {concept}")
    else:
        print(colorama.Fore.RED + f"Failed to load knowledge from file: {result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
    
    # Test querying the knowledge
    print(colorama.Fore.CYAN + "\nTesting knowledge queries:" + colorama.Style.RESET_ALL)
    
    # Query about lions
    print(colorama.Fore.YELLOW + "Query: What is a lion?" + colorama.Style.RESET_ALL)
    response = ira_system.process_message("What is a lion?")
    print(colorama.Fore.GREEN + f"Response: {response}" + colorama.Style.RESET_ALL)
    
    # Query about tigers
    print(colorama.Fore.YELLOW + "Query: What is a tiger?" + colorama.Style.RESET_ALL)
    response = ira_system.process_message("What is a tiger?")
    print(colorama.Fore.GREEN + f"Response: {response}" + colorama.Style.RESET_ALL)
    
    # Query about computers
    print(colorama.Fore.YELLOW + "Query: What is a computer?" + colorama.Style.RESET_ALL)
    response = ira_system.process_message("What is a computer?")
    print(colorama.Fore.GREEN + f"Response: {response}" + colorama.Style.RESET_ALL)
    
    # Query about artificial intelligence
    print(colorama.Fore.YELLOW + "Query: What is artificial intelligence?" + colorama.Style.RESET_ALL)
    response = ira_system.process_message("What is artificial intelligence?")
    print(colorama.Fore.GREEN + f"Response: {response}" + colorama.Style.RESET_ALL)


def test_wikipedia_knowledge_loading():
    """Test loading knowledge from Wikipedia."""
    print(colorama.Fore.CYAN + "\n=== Testing Wikipedia Knowledge Loading ===" + colorama.Style.RESET_ALL)
    
    # Create an IRA system
    ira_system = create_ira_system()
    
    # Search for Wikipedia articles
    search_query = "Python programming language"
    print(colorama.Fore.YELLOW + f"Searching Wikipedia for: {search_query}" + colorama.Style.RESET_ALL)
    
    try:
        search_result = ira_system.search_wikipedia(search_query)
        
        if search_result["success"]:
            print(colorama.Fore.GREEN + f"Search results for: {search_result.get('query', search_query)}" + colorama.Style.RESET_ALL)
            for i, article in enumerate(search_result.get("results", []), 1):
                print(f"{i}. {article.get('title', 'Unknown')}")
                print(f"   {article.get('snippet', 'No snippet available')}")
                print()
            
            # Load knowledge from the first article
            if search_result.get("results"):
                article_title = search_result["results"][0]["title"]
                print(colorama.Fore.YELLOW + f"Loading knowledge from Wikipedia article: {article_title}" + colorama.Style.RESET_ALL)
                result = ira_system.learn_from_wikipedia(article_title)
                
                if result["success"]:
                    print(colorama.Fore.GREEN + f"Successfully loaded knowledge from Wikipedia article: {result.get('title', article_title)}" + colorama.Style.RESET_ALL)
                    print(f"- Chunks processed: {result.get('chunks_processed', 0)}")
                    print(f"- Concepts created: {len(result.get('concepts_created', []))}")
                    print(f"- Relations created: {len(result.get('relations_created', []))}")
                    
                    # Print some of the concepts created
                    print(colorama.Fore.CYAN + "Some concepts created:" + colorama.Style.RESET_ALL)
                    for concept in result.get("concepts_created", [])[:5]:
                        print(f"- {concept}")
                    
                    # Test querying the knowledge
                    print(colorama.Fore.CYAN + "\nTesting knowledge queries:" + colorama.Style.RESET_ALL)
                    
                    # Query about the article
                    print(colorama.Fore.YELLOW + f"Query: What is {article_title}?" + colorama.Style.RESET_ALL)
                    response = ira_system.process_message(f"What is {article_title}?")
                    print(colorama.Fore.GREEN + f"Response: {response}" + colorama.Style.RESET_ALL)
                else:
                    print(colorama.Fore.RED + f"Failed to load knowledge from Wikipedia article: {result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.RED + f"Failed to search Wikipedia: {search_result.get('error', 'Unknown error')}" + colorama.Style.RESET_ALL)
    except Exception as e:
        print(colorama.Fore.RED + f"Error during Wikipedia knowledge loading: {str(e)}" + colorama.Style.RESET_ALL)


def main():
    """Run the knowledge loading tests."""
    print(colorama.Fore.CYAN + """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║             IRA System Knowledge Loading Tests               ║
    ║                                                              ║
    ║  This script demonstrates how to use the FileKnowledgeLoader ║
    ║  and WikipediaKnowledgeLoader components to load knowledge   ║
    ║  into the IRA system from files and Wikipedia articles.      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """ + colorama.Style.RESET_ALL)
    
    # Test file knowledge loading
    test_file_knowledge_loading()
    
    # Test Wikipedia knowledge loading
    test_wikipedia_knowledge_loading()


if __name__ == "__main__":
    main()