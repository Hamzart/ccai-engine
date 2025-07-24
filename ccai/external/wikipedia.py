"""
Wikipedia connector for external knowledge retrieval.

This module provides a connector for retrieving information from Wikipedia
and integrating it into the CCAI knowledge graph.
"""

import logging
import re
from typing import Dict, Any, List, Optional
import requests

from ccai.external.connector import KnowledgeConnector, registry
from ccai.core.models import ConceptNode, PropertySpec

# Set up logging
logger = logging.getLogger(__name__)


class WikipediaConnector(KnowledgeConnector):
    """
    Connector for retrieving information from Wikipedia.
    
    This connector uses the Wikipedia API to search for articles
    and retrieve their content.
    """
    
    def __init__(self, language: str = "en"):
        """
        Initialize the Wikipedia connector.
        
        Args:
            language: The Wikipedia language code (default: "en" for English)
        """
        super().__init__(name=f"wikipedia-{language}")
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"
        self.user_agent = "CCAI-WikipediaConnector/0.1"
    
    def search(self, query: str, limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for Wikipedia articles matching the query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            A list of search results as dictionaries
        """
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet",
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers={"User-Agent": self.user_agent}
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", []):
                # Clean up the snippet by removing HTML tags
                snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                
                result = {
                    "title": item.get("title", ""),
                    "pageid": item.get("pageid", 0),
                    "snippet": snippet,
                    "url": f"https://{self.language}.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                }
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return []
    
    def get_details(self, item_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a Wikipedia article.
        
        Args:
            item_id: The page ID or title of the article
            **kwargs: Additional parameters
            
        Returns:
            A dictionary with detailed information or None if not found
        """
        # Determine if item_id is a page ID or title
        # Convert item_id to string to handle cases where an integer is passed
        item_id_str = str(item_id)
        if item_id_str.isdigit():
            id_param = {"pageids": item_id_str}
        else:
            id_param = {"titles": item_id_str}
        
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|categories|links|info",
            "exintro": 1,  # Only get the introduction
            "explaintext": 1,  # Get plain text, not HTML
            "inprop": "url",
            **id_param
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers={"User-Agent": self.user_agent}
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract the page data
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return None
            
            # Get the first (and only) page
            page_id = next(iter(pages))
            page = pages[page_id]
            
            if "missing" in page:
                return None
            
            result = {
                "title": page.get("title", ""),
                "pageid": page.get("pageid", 0),
                "extract": page.get("extract", ""),
                "url": page.get("fullurl", ""),
                "categories": [cat.get("title", "") for cat in page.get("categories", [])],
                "links": [link.get("title", "") for link in page.get("links", [])],
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting Wikipedia article details: {e}")
            return None
    
    def extract_concepts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract concepts from Wikipedia article data.
        
        Args:
            data: The Wikipedia article data
            
        Returns:
            A list of extracted concepts as dictionaries
        """
        if not data:
            return []
        
        concepts = []
        
        # Create a concept for the main article
        main_concept = {
            "name": data.get("title", "").lower(),
            "ctype": "entity",
            "properties": {
                "description": [{"value": data.get("extract", "")[:200], "score": 1.0}]
            },
            "relations": {
                "source": ["wikipedia"]
            }
        }
        
        # Add categories as is_a relations
        is_a_relations = []
        for category in data.get("categories", []):
            # Clean up category name (remove "Category:" prefix)
            category_name = category.replace("Category:", "").lower()
            is_a_relations.append(category_name)
        
        if is_a_relations:
            main_concept["relations"]["is_a"] = is_a_relations
        
        # Add links as related_to relations
        related_to = []
        for link in data.get("links", [])[:10]:  # Limit to 10 links
            related_to.append(link.lower())
        
        if related_to:
            main_concept["relations"]["related_to"] = related_to
        
        concepts.append(main_concept)
        
        # Create concepts for categories
        for category in data.get("categories", [])[:5]:  # Limit to 5 categories
            category_name = category.replace("Category:", "").lower()
            category_concept = {
                "name": category_name,
                "ctype": "category",
                "relations": {
                    "source": ["wikipedia"]
                }
            }
            concepts.append(category_concept)
        
        return concepts
    
    def create_concept_nodes(self, data: Dict[str, Any]) -> List[ConceptNode]:
        """
        Create ConceptNode objects from Wikipedia article data.
        
        Args:
            data: The Wikipedia article data
            
        Returns:
            A list of ConceptNode objects
        """
        concept_dicts = self.extract_concepts(data)
        nodes = []
        
        for concept_dict in concept_dicts:
            # Create a new ConceptNode
            node = ConceptNode(
                name=concept_dict["name"],
                ctype=concept_dict.get("ctype", "entity")
            )
            
            # Add properties
            for prop_name, prop_values in concept_dict.get("properties", {}).items():
                node.properties[prop_name] = [
                    PropertySpec(value=pv["value"], score=pv["score"])
                    for pv in prop_values
                ]
            
            # Add relations
            for rel_type, targets in concept_dict.get("relations", {}).items():
                node.relations[rel_type] = targets
            
            nodes.append(node)
        
        return nodes


# Register the connector
wikipedia_connector = WikipediaConnector()
registry.register(wikipedia_connector)