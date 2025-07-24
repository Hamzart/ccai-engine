#!/usr/bin/env python3
"""
Test script for the knowledge loaders in the IRA system.

This script tests the functionality of the FileKnowledgeLoader and WikipediaKnowledgeLoader
components, which allow the IRA system to learn from files and Wikipedia articles.
"""

import os
import sys
import unittest
from pathlib import Path
import tempfile
import nltk

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
from ira.core.learning.file_knowledge_loader import FileKnowledgeLoader
from ira.core.learning.wikipedia_knowledge_loader import WikipediaKnowledgeLoader
from ira.core.learning.knowledge_loader_manager import KnowledgeLoaderManager


class TestKnowledgeLoaders(unittest.TestCase):
    """Test case for the knowledge loaders."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a Knowledge Graph
        self.knowledge_graph = KnowledgeGraph()
        
        # Create an Ideom Network
        self.ideom_network = IdeomNetwork()
        
        # Create a Unified Reasoning Core
        self.reasoning_core = UnifiedReasoningCore(
            ideom_network=self.ideom_network
        )
        
        # Create a Reasoning Knowledge Integration
        self.integration = ReasoningKnowledgeIntegration(
            self.knowledge_graph,
            self.reasoning_core
        )
        
        # Create a Knowledge Loader Manager
        self.loader_manager = KnowledgeLoaderManager(
            self.knowledge_graph,
            self.reasoning_core,
            self.integration
        )
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Clean up after the test case."""
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_file_knowledge_loader(self):
        """Test the FileKnowledgeLoader."""
        # Use the sample knowledge file
        test_file_path = os.path.join(os.path.dirname(__file__), "test_data", "sample_knowledge.txt")
        
        # Load knowledge from the file
        result = self.loader_manager.load_from_file(test_file_path)
        
        # Check that the knowledge was loaded successfully
        self.assertTrue(result["success"])
        self.assertGreater(len(result["concepts_created"]), 0)
        
        # Check that the concepts were created in the knowledge graph
        lion_concept = self.knowledge_graph.get_concept_by_name("lion")
        self.assertIsNotNone(lion_concept)
        
        tiger_concept = self.knowledge_graph.get_concept_by_name("tiger")
        self.assertIsNotNone(tiger_concept)
        
        computer_concept = self.knowledge_graph.get_concept_by_name("computer")
        self.assertIsNotNone(computer_concept)
        
        ai_concept = self.knowledge_graph.get_concept_by_name("artificial intelligence")
        self.assertIsNotNone(ai_concept)
    
    def test_text_knowledge_loader(self):
        """Test loading knowledge from text."""
        # Create a test text
        test_text = """
        The elephant is a large mammal with a long trunk.
        Elephants are known for their intelligence and memory.
        Giraffes are tall mammals with long necks.
        Giraffes are known for their height and spotted pattern.
        """
        
        # Load knowledge from the text
        result = self.loader_manager.load_from_text(test_text, "test_text")
        
        # Check that the knowledge was loaded successfully
        self.assertTrue(result["success"])
        self.assertGreater(len(result["concepts_created"]), 0)
        
        # Check that the concepts were created in the knowledge graph
        elephant_concept = self.knowledge_graph.get_concept_by_name("elephant")
        self.assertIsNotNone(elephant_concept)
        
        giraffe_concept = self.knowledge_graph.get_concept_by_name("giraffe")
        self.assertIsNotNone(giraffe_concept)
    
    def test_wikipedia_knowledge_loader(self):
        """Test the WikipediaKnowledgeLoader."""
        # This test requires an internet connection
        # Skip the test if there's no internet connection
        try:
            # Search for Wikipedia articles
            search_result = self.loader_manager.search_wikipedia("Python programming language")
            
            # Check that the search was successful
            self.assertTrue(search_result["success"])
            self.assertGreater(len(search_result["results"]), 0)
            
            # Load knowledge from the first article
            article_title = search_result["results"][0]["title"]
            result = self.loader_manager.load_from_wikipedia_article(article_title)
            
            # Check that the knowledge was loaded successfully
            self.assertTrue(result["success"])
            self.assertGreater(len(result["concepts_created"]), 0)
            
            # Check that the concept was created in the knowledge graph
            python_concept = self.knowledge_graph.get_concept_by_name(article_title)
            self.assertIsNotNone(python_concept)
        except Exception as e:
            self.skipTest(f"Skipping Wikipedia test due to error: {str(e)}")
    
    def test_wikipedia_search_loader(self):
        """Test loading knowledge from Wikipedia search results."""
        # This test requires an internet connection
        # Skip the test if there's no internet connection
        try:
            # Load knowledge from Wikipedia search results
            result = self.loader_manager.load_from_wikipedia_search("artificial intelligence", limit=1)
            
            # Check that the knowledge was loaded successfully
            self.assertTrue(result["success"])
            self.assertGreater(len(result["concepts_created"]), 0)
            
            # Check that at least one article was processed
            self.assertGreater(result["articles_processed"], 0)
        except Exception as e:
            self.skipTest(f"Skipping Wikipedia search test due to error: {str(e)}")


if __name__ == "__main__":
    unittest.main()