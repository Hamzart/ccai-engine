"""
KnowledgeLoaderManager module for the IRA architecture.

This module provides a centralized manager for all knowledge loaders in the IRA system,
including file and Wikipedia knowledge loaders.
"""

from typing import Dict, Any, Optional, List
from ..knowledge.knowledge_graph import KnowledgeGraph
from ..reasoning.unified_reasoning_core import UnifiedReasoningCore
from ..integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from .file_knowledge_loader import FileKnowledgeLoader
from .wikipedia_knowledge_loader import WikipediaKnowledgeLoader


class KnowledgeLoaderManager:
    """
    A manager for all knowledge loaders in the IRA system.
    
    The KnowledgeLoaderManager provides a centralized interface for loading knowledge
    from various sources, such as files and Wikipedia articles.
    
    Attributes:
        knowledge_graph: The KnowledgeGraph instance to add knowledge to.
        reasoning_core: The UnifiedReasoningCore instance for processing text.
        integration: The ReasoningKnowledgeIntegration instance for knowledge extraction.
        file_loader: The FileKnowledgeLoader instance for loading knowledge from files.
        wikipedia_loader: The WikipediaKnowledgeLoader instance for loading knowledge from Wikipedia.
    """
    
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        reasoning_core: UnifiedReasoningCore,
        integration: Optional[ReasoningKnowledgeIntegration] = None
    ):
        """
        Initialize a knowledge loader manager.
        
        Args:
            knowledge_graph: The KnowledgeGraph instance to add knowledge to.
            reasoning_core: The UnifiedReasoningCore instance for processing text.
            integration: The ReasoningKnowledgeIntegration instance, or None to create a new one.
        """
        self.knowledge_graph = knowledge_graph
        self.reasoning_core = reasoning_core
        self.integration = integration or ReasoningKnowledgeIntegration(
            knowledge_graph, reasoning_core
        )
        
        # Initialize the knowledge loaders
        self.file_loader = FileKnowledgeLoader(
            knowledge_graph, reasoning_core, integration=self.integration
        )
        self.wikipedia_loader = WikipediaKnowledgeLoader(
            knowledge_graph, reasoning_core, integration=self.integration
        )
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load knowledge from a file.
        
        Args:
            file_path: The path to the file to load.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        return self.file_loader.load_from_file(file_path)
    
    def load_from_text(self, text: str, source_name: str = "text_input") -> Dict[str, Any]:
        """
        Load knowledge from a text string.
        
        Args:
            text: The text to load knowledge from.
            source_name: A name for the source of the text.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        return self.file_loader.load_from_text(text, source_name)
    
    def load_from_wikipedia_article(self, title: str) -> Dict[str, Any]:
        """
        Load knowledge from a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article to load.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        return self.wikipedia_loader.load_from_article(title)
    
    def load_from_wikipedia_search(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Load knowledge from Wikipedia articles matching a search query.
        
        Args:
            query: The search query.
            limit: The maximum number of articles to load.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        return self.wikipedia_loader.load_from_search(query, limit)
    
    def search_wikipedia(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for Wikipedia articles matching a query.
        
        Args:
            query: The search query.
            limit: The maximum number of results to return.
            
        Returns:
            A dictionary containing the search results.
        """
        return self.wikipedia_loader.search_articles(query, limit)