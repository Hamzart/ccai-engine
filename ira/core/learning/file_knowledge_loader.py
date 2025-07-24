"""
FileKnowledgeLoader module for the IRA architecture.

This module provides functionality to load knowledge from text files
and integrate it into the IRA system's knowledge graph.
"""

import os
from typing import List, Dict, Any, Optional
from ..knowledge.knowledge_graph import KnowledgeGraph
from ..reasoning.unified_reasoning_core import UnifiedReasoningCore
from ..integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration

class FileKnowledgeLoader:
    """
    A loader for importing knowledge from text files.
    
    The FileKnowledgeLoader reads text files and processes their content
    to extract knowledge and add it to the IRA system's knowledge graph.
    
    Attributes:
        knowledge_graph: The KnowledgeGraph instance to add knowledge to.
        reasoning_core: The UnifiedReasoningCore instance for processing text.
        integration: The ReasoningKnowledgeIntegration instance for knowledge extraction.
    """
    
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph,
        reasoning_core: UnifiedReasoningCore,
        integration: Optional[ReasoningKnowledgeIntegration] = None
    ):
        """
        Initialize a file knowledge loader.
        
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
    
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load knowledge from a text file.
        
        Args:
            file_path: The path to the text file to load.
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
            
            return {
                "success": True,
                "file_path": file_path,
                "chunks_processed": len(chunks),
                "concepts_created": list(concepts_created),
                "relations_created": list(relations_created),
                "knowledge_extracted": knowledge_extracted
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading knowledge from file: {str(e)}"
            }
    
    def load_from_directory(self, directory_path: str, file_extension: str = ".txt") -> Dict[str, Any]:
        """
        Load knowledge from all text files in a directory.
        
        Args:
            directory_path: The path to the directory containing text files.
            file_extension: The extension of files to load (default: ".txt").
            
        Returns:
            A dictionary containing the results of the knowledge loading process.
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }
        
        try:
            file_paths = [
                os.path.join(directory_path, filename)
                for filename in os.listdir(directory_path)
                if filename.endswith(file_extension)
            ]
            
            if not file_paths:
                return {
                    "success": False,
                    "error": f"No {file_extension} files found in {directory_path}"
                }
            
            results = []
            for file_path in file_paths:
                result = self.load_from_file(file_path)
                results.append(result)
            
            # Extract statistics
            files_processed = sum(1 for result in results if result.get("success", False))
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
                "directory_path": directory_path,
                "files_processed": files_processed,
                "total_files": len(file_paths),
                "concepts_created": list(concepts_created),
                "relations_created": list(relations_created),
                "knowledge_extracted": knowledge_extracted
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error loading knowledge from directory: {str(e)}"
            }