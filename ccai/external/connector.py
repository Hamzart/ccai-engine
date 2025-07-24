"""
Base connector interface for external knowledge sources.

This module defines the base interface for all external knowledge connectors
and provides common functionality for retrieving and processing external data.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)


class KnowledgeConnector(ABC):
    """
    Abstract base class for external knowledge connectors.
    
    All external knowledge connectors should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, name: str):
        """
        Initialize the knowledge connector.
        
        Args:
            name: The name of the connector
        """
        self.name = name
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for information related to the query.
        
        Args:
            query: The search query
            **kwargs: Additional search parameters
            
        Returns:
            A list of search results as dictionaries
        """
        pass
    
    @abstractmethod
    def get_details(self, item_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific item.
        
        Args:
            item_id: The ID of the item to get details for
            **kwargs: Additional parameters
            
        Returns:
            A dictionary with detailed information or None if not found
        """
        pass
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: The search results to format
            
        Returns:
            A formatted string representation of the results
        """
        if not results:
            return "No results found."
        
        formatted = f"Results from {self.name}:\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "Untitled")
            snippet = result.get("snippet", "No description available.")
            url = result.get("url", "")
            
            formatted += f"{i}. {title}\n"
            formatted += f"   {snippet}\n"
            if url:
                formatted += f"   Source: {url}\n"
            formatted += "\n"
        
        return formatted
    
    def extract_concepts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract concepts from the retrieved data.
        
        This method can be overridden by subclasses to provide
        connector-specific concept extraction.
        
        Args:
            data: The data to extract concepts from
            
        Returns:
            A list of extracted concepts as dictionaries
        """
        # Default implementation returns an empty list
        return []


class KnowledgeConnectorRegistry:
    """
    Registry for knowledge connectors.
    
    This class maintains a registry of available knowledge connectors
    and provides methods for accessing them.
    """
    
    def __init__(self):
        """Initialize the connector registry."""
        self.connectors: Dict[str, KnowledgeConnector] = {}
    
    def register(self, connector: KnowledgeConnector) -> None:
        """
        Register a knowledge connector.
        
        Args:
            connector: The connector to register
        """
        self.connectors[connector.name] = connector
        logger.info(f"Registered knowledge connector: {connector.name}")
    
    def get_connector(self, name: str) -> Optional[KnowledgeConnector]:
        """
        Get a connector by name.
        
        Args:
            name: The name of the connector to get
            
        Returns:
            The connector or None if not found
        """
        return self.connectors.get(name)
    
    def list_connectors(self) -> List[str]:
        """
        Get a list of available connector names.
        
        Returns:
            A list of connector names
        """
        return list(self.connectors.keys())
    
    def search_all(self, query: str, **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all registered connectors.
        
        Args:
            query: The search query
            **kwargs: Additional search parameters
            
        Returns:
            A dictionary mapping connector names to their search results
        """
        results = {}
        
        for name, connector in self.connectors.items():
            try:
                connector_results = connector.search(query, **kwargs)
                results[name] = connector_results
            except Exception as e:
                logger.error(f"Error searching with connector {name}: {e}")
                results[name] = []
        
        return results


# Global registry instance
registry = KnowledgeConnectorRegistry()