"""
WikipediaKnowledgeLoader module for the IRA architecture.

This module provides functionality to load knowledge from Wikipedia articles
and integrate it into the IRA system's knowledge graph.
"""

import requests
from typing import List, Dict, Any, Optional
from ..knowledge.knowledge_graph import KnowledgeGraph
from ..reasoning.unified_reasoning_core import UnifiedReasoningCore
from ..integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration

class WikipediaKnowledgeLoader:
    """
    A loader for importing knowledge from Wikipedia articles.
    
    The WikipediaKnowledgeLoader fetches Wikipedia articles and processes their content
    to extract knowledge and add it to the IRA system's knowledge graph.
    
    Attributes:
        knowledge_graph: The KnowledgeGraph instance to add knowledge to.
        reasoning_core: The UnifiedReasoningCore instance for processing text.
        integration: The ReasoningKnowledgeIntegration instance for knowledge extraction.
        api_url: The URL of the Wikipedia API.
    """
    
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        reasoning_core: UnifiedReasoningCore,
        integration: Optional[ReasoningKnowledgeIntegration] = None,
        api_url: str = "https://en.wikipedia.org/w/api.php"
    ):
        """
        Initialize a Wikipedia knowledge loader.
        
        Args:
            knowledge_graph: The KnowledgeGraph instance to add knowledge to.
            reasoning_core: The UnifiedReasoningCore instance for processing text.
            integration: The ReasoningKnowledgeIntegration instance, or None to create a new one.
            api_url: The URL of the Wikipedia API.
        """
        self.knowledge_graph = knowledge_graph
        self.reasoning_core = reasoning_core
        self.integration = integration or ReasoningKnowledgeIntegration(
            knowledge_graph, reasoning_core
        )
        self.api_url = api_url
    
    def fetch_article(self, title: str) -> Dict[str, Any]:
        """
        Fetch a Wikipedia article by title.
        
        Args:
            title: The title of the Wikipedia article to fetch.
            
        Returns:
            A dictionary containing the article content or an error message.
        """
        try:
            # Set up the API request parameters
            params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "exintro": 1,  # Get only the introduction
                "explaintext": 1,  # Get plain text content
                "redirects": 1  # Follow redirects
            }
            
            # Make the API request
            response = requests.get(self.api_url, params=params)
            data = response.json()
            
            # Extract the page content
            pages = data["query"]["pages"]
            page_id = next(iter(pages))
            
            if page_id == "-1":
                return {
                    "success": False,
                    "error": f"Article not found: {title}"
                }
            
            page = pages[page_id]
            content = page.get("extract", "")
            
            if not content:
                return {
                    "success": False,
                    "error": f"No content found for article: {title}"
                }
            
            return {
                "success": True,
                "title": page.get("title", title),
                "content": content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching Wikipedia article: {str(e)}"
            }
    
    def load_from_article(self, title: str) -> Dict[str, Any]:
        """
        Load knowledge from a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article to load.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        # Fetch the article
        article = self.fetch_article(title)
        
        if not article["success"]:
            return article
        
        try:
            content = article["content"]
            
            # Process the content in chunks to avoid overwhelming the system
            chunk_size = 1000  # characters
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            results = []
            for chunk in chunks:
                # Process the chunk using the integration
                result = self.integration.process_input_with_knowledge(chunk)
                results.append(result)
            
            # Extract statistics
            concepts_created = set()
            relations_created = set()
            knowledge_extracted = []
            
            for result in results:
                update_result = result.get("knowledge_update_result", {})
                extraction_result = result.get("knowledge_extraction_result", {})
                
                concepts_created.update(update_result.get("concepts_created", []))
                relations_created.update(update_result.get("relations_created", []))
                knowledge_extracted.extend(extraction_result.get("extracted_knowledge", []))
            
            # Create a concept for the article title if it doesn't exist
            title_concept = self.knowledge_graph.get_concept_by_name(article["title"])
            if not title_concept:
                title_concept = self.knowledge_graph.add_concept(article["title"])
                concepts_created.add(article["title"])
            
            # Add a property to the concept with the article content
            self.knowledge_graph.update_concept(
                title_concept.id,
                properties={
                    "wikipedia_article": [article["content"][:500]]  # Store a summary
                }
            )
            
            return {
                "success": True,
                "title": article["title"],
                "chunks_processed": len(chunks),
                "concepts_created": list(concepts_created),
                "relations_created": list(relations_created),
                "knowledge_extracted": knowledge_extracted
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading knowledge from Wikipedia article: {str(e)}"
            }
    
    def search_articles(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for Wikipedia articles matching a query.
        
        Args:
            query: The search query.
            limit: The maximum number of results to return.
            
        Returns:
            A dictionary containing the search results.
        """
        try:
            # Set up the API request parameters
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": limit
            }
            
            # Make the API request
            response = requests.get(self.api_url, params=params)
            data = response.json()
            
            # Extract the search results
            search_results = data["query"]["search"]
            
            if not search_results:
                return {
                    "success": False,
                    "error": f"No articles found for query: {query}"
                }
            
            results = []
            for result in search_results:
                results.append({
                    "title": result["title"],
                    "snippet": result.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                })
            
            return {
                "success": True,
                "query": query,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching Wikipedia: {str(e)}"
            }
    
    def load_from_search(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Load knowledge from Wikipedia articles matching a search query.
        
        Args:
            query: The search query.
            limit: The maximum number of articles to load.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        # Search for articles
        search_result = self.search_articles(query, limit)
        
        if not search_result["success"]:
            return search_result
        
        try:
            results = []
            for article in search_result["results"][:limit]:
                result = self.load_from_article(article["title"])
                results.append(result)
            
            # Extract statistics
            articles_processed = sum(1 for result in results if result.get("success", False))
            concepts_created = set()
            relations_created = set()
            knowledge_extracted = []
            
            for result in results:
                if result.get("success", False):
                    concepts_created.update(result.get("concepts_created", []))
                    relations_created.update(result.get("relations_created", []))
                    knowledge_extracted.extend(result.get("knowledge_extracted", []))
            
            return {
                "success": True,
                "query": query,
                "articles_processed": articles_processed,
                "total_articles": len(search_result["results"]),
                "concepts_created": list(concepts_created),
                "relations_created": list(relations_created),
                "knowledge_extracted": knowledge_extracted
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading knowledge from Wikipedia search: {str(e)}"
            }