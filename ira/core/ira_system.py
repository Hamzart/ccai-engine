"""
IRA System module for the IRA architecture.

This module provides the main integration point for the IRA (Ideom Resolver AI) system,
integrating all the components of the system, including the Knowledge Graph,
Conversation Manager, and the integration between them.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import os
import json
import time
from datetime import datetime

from .knowledge.knowledge_graph import KnowledgeGraph
from .conversation.conversation_context import ConversationContext, Message, MessageType
from .conversation.intent_recognizer import IntentRecognizer, Intent, IntentType
from .conversation.response_planner import ResponsePlanner
from .conversation.memory_manager import MemoryManager
from .conversation.conversation_manager import ConversationManager
from .integration.conversation_knowledge_integration import ConversationKnowledgeIntegration
from .integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from .reasoning.ideom import Ideom
from .reasoning.ideom_network import IdeomNetwork
from .reasoning.activation_pattern import ActivationPattern
from .reasoning.unified_reasoning_core import UnifiedReasoningCore
from .learning.knowledge_loader_manager import KnowledgeLoaderManager


class IRASystem:
    """
    Main class for the IRA (Ideom Resolver AI) system.
    
    This class integrates all the components of the IRA system, including the
    Knowledge Graph, Conversation Manager, and the integration between them.
    
    Attributes:
        knowledge_graph: The KnowledgeGraph instance.
        conversation_manager: The ConversationManager instance.
        conversation_integration: The ConversationKnowledgeIntegration instance.
        ideom_network: The IdeomNetwork instance.
        reasoning_core: The UnifiedReasoningCore instance.
        reasoning_integration: The ReasoningKnowledgeIntegration instance.
        knowledge_loader_manager: The KnowledgeLoaderManager instance.
    """
    
    def __init__(
        self,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        conversation_manager: Optional[ConversationManager] = None,
        conversation_integration: Optional[ConversationKnowledgeIntegration] = None,
        ideom_network: Optional[IdeomNetwork] = None,
        reasoning_core: Optional[UnifiedReasoningCore] = None,
        reasoning_integration: Optional[ReasoningKnowledgeIntegration] = None,
        knowledge_loader_manager: Optional[KnowledgeLoaderManager] = None
    ):
        """
        Initialize the IRA system.
        
        Args:
            knowledge_graph: The KnowledgeGraph instance.
                If None, a new KnowledgeGraph will be created.
            conversation_manager: The ConversationManager instance.
                If None, a new ConversationManager will be created.
            conversation_integration: The ConversationKnowledgeIntegration instance.
                If None, a new ConversationKnowledgeIntegration will be created.
            ideom_network: The IdeomNetwork instance.
                If None, a new IdeomNetwork will be created.
            reasoning_core: The UnifiedReasoningCore instance.
                If None, a new UnifiedReasoningCore will be created.
            reasoning_integration: The ReasoningKnowledgeIntegration instance.
                If None, a new ReasoningKnowledgeIntegration will be created.
            knowledge_loader_manager: The KnowledgeLoaderManager instance.
                If None, a new KnowledgeLoaderManager will be created.
        """
        # Initialize the Knowledge Graph
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        
        # Initialize the Conversation Manager
        self.conversation_manager = conversation_manager or ConversationManager()
        
        # Initialize the Ideom Network
        self.ideom_network = ideom_network or IdeomNetwork()
        
        # Initialize the Unified Reasoning Core
        self.reasoning_core = reasoning_core or UnifiedReasoningCore(
            ideom_network=self.ideom_network
        )
        
        # Initialize the Conversation Knowledge Integration
        self.conversation_integration = conversation_integration or ConversationKnowledgeIntegration(
            self.knowledge_graph
        )
        
        # Initialize the Reasoning Knowledge Integration
        self.reasoning_integration = reasoning_integration or ReasoningKnowledgeIntegration(
            self.knowledge_graph,
            self.reasoning_core
        )
        
        # Initialize the Knowledge Loader Manager
        self.knowledge_loader_manager = knowledge_loader_manager or KnowledgeLoaderManager(
            self.knowledge_graph,
            self.reasoning_core,
            self.reasoning_integration
        )
        
        # Extend the Conversation Manager to use the Conversation Integration
        self._extend_conversation_manager()
        
        # Initialize the knowledge-reasoning integration
        self._initialize_knowledge_reasoning_integration()
    
    def _extend_conversation_manager(self):
        """
        Extend the Conversation Manager to use the Conversation Integration.
        
        This method modifies the Conversation Manager to use the Conversation Integration
        for processing user messages that require knowledge graph access.
        """
        # Store the original process_message method
        original_process_message = self.conversation_manager.process_message
        
        # Define a new process_message method that uses the Conversation Integration
        def extended_process_message(message: str, context_id: Optional[str] = None) -> str:
            # Get or create the conversation context
            context = self.conversation_manager._get_or_create_context(context_id)
            
            # Add the user message to the context
            context.add_message(Message.create_user_message(
                content=message
            ))
            
            # Check if the message is a command
            if message.startswith("@"):
                # Use the original process_message method for commands
                return original_process_message(message, context.id)
            
            # Recognize the intent of the message
            intent = self.conversation_manager.intent_recognizer.recognize_intent(message, context)
            
            # Check if the intent requires knowledge graph access
            if intent.type in [IntentType.QUESTION, IntentType.DEFINITION, IntentType.VERIFICATION,
                               IntentType.RELATIONSHIP, IntentType.PROPERTY]:
                # Query the knowledge graph
                result = self.conversation_integration.query_knowledge_graph(intent, context)
                
                if result["success"]:
                    # Generate a response based on the query result
                    response = self._generate_response_from_query_result(result)
                else:
                    # Use the original process_message method if the query fails
                    return original_process_message(message, context.id)
            elif intent.type in [IntentType.STATEMENT, IntentType.CORRECTION]:
                # Update the knowledge graph
                result = self.conversation_integration.update_knowledge_graph(intent, context)
                
                if result["success"]:
                    # Generate a response based on the update result
                    response = self._generate_response_from_update_result(result)
                else:
                    # Use the original process_message method if the update fails
                    return original_process_message(message, context.id)
            else:
                # Use the original process_message method for other intents
                return original_process_message(message, context.id)
            
            # Add the response to the context
            context.add_message(Message.create_system_message(
                content=response
            ))
            
            # Update the context state
            context.state = ConversationContext.ConversationState.ACTIVE
            
            # Save the memory
            self.conversation_manager.memory_manager.save_memory()
            
            return response
        
        # Replace the process_message method
        self.conversation_manager.process_message = extended_process_message
    
    def _initialize_knowledge_reasoning_integration(self):
        """
        Initialize the integration between the Knowledge Graph and the Unified Reasoning Core.
        
        This method creates ideoms and prefabs in the Unified Reasoning Core based on
        concepts in the Knowledge Graph, and sets up the integration between them.
        """
        # Create ideoms in the Unified Reasoning Core based on concepts in the Knowledge Graph
        self.reasoning_integration.create_ideoms_from_concepts()
        
        # Create prefabs in the Unified Reasoning Core based on concepts in the Knowledge Graph
        self.reasoning_integration.create_prefabs_from_concepts()
    
    def _generate_response_from_query_result(self, result: Dict[str, Any]) -> str:
        """
        Generate a response from a knowledge graph query result.
        
        Args:
            result: The query result.
            
        Returns:
            The generated response.
        """
        if result["type"] == "definition":
            return f"{result['term']} is {result['definition']}"
        
        elif result["type"] == "generated_definition":
            return result["definition"]
        
        elif result["type"] == "simple_definition":
            return result["definition"]
        
        elif result["type"] == "how_to":
            return f"To {result['concept']}: {result['how_to']}"
        
        elif result["type"] == "steps":
            return f"Steps to {result['concept']}: {result['steps']}"
        
        elif result["type"] == "reason":
            return f"The reason for {result['concept']} is: {result['reason']}"
        
        elif result["type"] == "time":
            return f"{result['concept']} occurs at {result['time']}"
        
        elif result["type"] == "location":
            return f"{result['concept']} is located at {result['location']}"
        
        elif result["type"] == "person":
            return f"{result['concept']} is associated with {result['person']}"
        
        elif result["type"] == "general":
            # Generate a response based on the properties and relations
            response = f"Here's what I know about {result['concept']}:\n"
            
            # Add properties
            if result["properties"]:
                response += "Properties:\n"
                for name, value in result["properties"].items():
                    response += f"- {name}: {value}\n"
            
            # Add relations
            if result["relations"]:
                response += "Relations:\n"
                for relation in result["relations"]:
                    response += f"- {relation['type']} {relation['target']}\n"
            
            # If there are no properties or relations, provide a helpful message
            if not result["properties"] and not result["relations"]:
                response = f"I don't have any information about {result['concept']} yet. You can teach me about it by making statements like '{result['concept']} is a [type]' or '{result['concept']} has [property]'."
            
            return response
        
        elif result["type"] == "verification":
            if result["verified"]:
                return f"Yes, {result['subject']} {result['relation']} {result['object']} (confidence: {result['confidence']:.2f})"
            else:
                return f"No, {result['subject']} does not {result['relation']} {result['object']} (confidence: {result['confidence']:.2f})"
        
        elif result["type"] == "property_verification":
            return f"Yes, the {result['property']} of {result['subject']} is {result['value']} (confidence: {result['confidence']:.2f})"
        
        elif result["type"] == "specific_relation":
            if result["exists"]:
                return f"Yes, {result['subject']} {result['relation_type']} {result['object']} (confidence: {result['confidence']:.2f})"
            else:
                return f"No, {result['subject']} does not {result['relation_type']} {result['object']} (confidence: {result['confidence']:.2f})"
        
        elif result["type"] == "any_relation":
            if result["exists"]:
                return f"Yes, {result['subject']} {result['relation_type']} {result['object']} (confidence: {result['confidence']:.2f})"
            else:
                return f"No, there is no relation between {result['subject']} and {result['object']} (confidence: {result['confidence']:.2f})"
        
        elif result["type"] == "relations_by_type":
            if result["relations"]:
                response = f"{result['subject']} {result['relation_type']} the following:\n"
                for relation in result["relations"]:
                    response += f"- {relation['target']} (confidence: {relation['confidence']:.2f})\n"
                return response
            else:
                return f"{result['subject']} does not {result['relation_type']} anything"
        
        elif result["type"] == "all_relations":
            if result["relations"]:
                response = f"{result['subject']} has the following relations:\n"
                for relation in result["relations"]:
                    response += f"- {relation['type']} {relation['target']} (confidence: {relation['confidence']:.2f})\n"
                return response
            else:
                return f"{result['subject']} does not have any relations"
        
        elif result["type"] == "specific_property":
            if "exists" in result and not result["exists"]:
                return f"{result['subject']} does not have a {result['property']} property (confidence: {result['confidence']:.2f})"
            else:
                return f"The {result['property']} of {result['subject']} is {result['value']} (confidence: {result['confidence']:.2f})"
        
        elif result["type"] == "all_properties":
            if result["properties"]:
                response = f"{result['subject']} has the following properties:\n"
                for name, prop in result["properties"].items():
                    response += f"- {name}: {prop['value']} (confidence: {prop['confidence']:.2f})\n"
                return response
            else:
                return f"{result['subject']} does not have any properties"
        
        else:
            return f"I found some information about {result['type']}, but I'm not sure how to present it."
    
    def _generate_response_from_update_result(self, result: Dict[str, Any]) -> str:
        """
        Generate a response from a knowledge graph update result.
        
        Args:
            result: The update result.
            
        Returns:
            The generated response.
        """
        if result["type"] == "is_a_relation":
            return f"I've learned that {result['subject']} is a {result['object']}."
        
        elif result["type"] == "has_relation":
            return f"I've learned that {result['subject']} has a {result['object']}."
        
        elif result["type"] == "custom_relation":
            return f"I've learned that {result['subject']} {result['predicate']} {result['object']}."
        
        elif result["type"] == "property_assignment":
            return f"I've learned that the {result['property']} of {result['subject']} is {result['value']}."
        
        elif result["type"] == "is_a_relation_correction":
            return f"I've updated my knowledge: {result['subject']} is a {result['new_object']} (not a {result['old_object']})."
        
        elif result["type"] == "has_relation_correction":
            return f"I've updated my knowledge: {result['subject']} has a {result['new_object']} (not a {result['old_object']})."
        
        elif result["type"] == "custom_relation_correction":
            return f"I've updated my knowledge: {result['subject']} {result['predicate']} {result['new_object']} (not {result['old_object']})."
        
        elif result["type"] == "property_correction":
            return f"I've updated my knowledge: the {result['new_property']} of {result['subject']} is {result['new_value']} (not {result['old_value']})."
        
        elif result["type"] == "definition":
            return f"I've learned that {result['term']} is defined as: {result['definition']}."
        
        elif result["type"] == "relationship":
            return f"I've learned that {result['subject']} {result['relation_type']} {result['object']}."
        
        elif result["type"] == "property":
            return f"I've learned that the {result['property']} of {result['subject']} is {result['value']}."
        
        else:
            return f"I've updated my knowledge about {result['type']}, but I'm not sure how to describe it."
    
    def learn_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Learn knowledge from a file.
        
        Args:
            file_path: The path to the file to learn from.
            
        Returns:
            A dictionary containing the results of the learning process.
        """
        return self.knowledge_loader_manager.load_from_file(file_path)
    
    def learn_from_text(self, text: str, source_name: str = "text_input") -> Dict[str, Any]:
        """
        Learn knowledge from a text string.
        
        Args:
            text: The text to learn from.
            source_name: A name for the source of the text.
            
        Returns:
            A dictionary containing the results of the learning process.
        """
        return self.knowledge_loader_manager.load_from_text(text, source_name)
    
    def learn_from_wikipedia(self, title: str) -> Dict[str, Any]:
        """
        Learn knowledge from a Wikipedia article.
        
        Args:
            title: The title of the Wikipedia article to learn from.
            
        Returns:
            A dictionary containing the results of the learning process.
        """
        return self.knowledge_loader_manager.load_from_wikipedia_article(title)
    
    def learn_from_wikipedia_search(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Learn knowledge from Wikipedia articles matching a search query.
        
        Args:
            query: The search query.
            limit: The maximum number of articles to learn from.
            
        Returns:
            A dictionary containing the results of the learning process.
        """
        return self.knowledge_loader_manager.load_from_wikipedia_search(query, limit)
    
    def search_wikipedia(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search for Wikipedia articles matching a query.
        
        Args:
            query: The search query.
            limit: The maximum number of results to return.
            
        Returns:
            A dictionary containing the search results.
        """
        return self.knowledge_loader_manager.search_wikipedia(query, limit)
    
    def process_message(self, message: str, context_id: Optional[str] = None) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user message.
            context_id: The ID of the conversation context to use.
                If None, the active context will be used, or a new one will be created.
                
        Returns:
            The response to the user message.
        """
        # Extract knowledge from the message
        context = self.conversation_manager._get_or_create_context(context_id)
        knowledge = self.conversation_integration.extract_knowledge(message, context)
        
        # Check if the message is a question about a concept
        if message.lower().startswith("what is") or message.lower().startswith("who is") or message.lower().startswith("tell me about"):
            # Extract the concept name from the message
            concept_name = message.lower().replace("what is", "").replace("who is", "").replace("tell me about", "").strip()
            concept_name = concept_name.rstrip("?").strip()
            
            # Check if the concept exists in the knowledge graph
            concept = self.knowledge_graph.get_concept_by_name(concept_name)
            if concept:
                # Get the concept's properties and relations
                properties_dict = {}
                for name, prop_value in concept.get_properties().items():
                    properties_dict[name] = prop_value.get_value()
                
                relations_list = []
                for relation in concept.get_all_relations():
                    target_concept = self.knowledge_graph.get_concept_by_id(relation.target_concept_id)
                    if target_concept:
                        relations_list.append({
                            "type": relation.type,
                            "target": target_concept.name,
                            "confidence": 1.0
                        })
                
                # Create a query result
                result = {
                    "type": "general",
                    "concept": concept_name,
                    "properties": properties_dict,
                    "relations": relations_list,
                    "success": True
                }
                
                # Generate a response based on the query result
                return self._generate_response_from_query_result(result)
        
        # Process the message using the Unified Reasoning Core
        reasoning_result = self.reasoning_core.process(message)
        
        # Ensure new ideoms are added to the knowledge graph
        self._sync_ideoms_with_knowledge_graph(reasoning_result.get_activation_pattern())
        
        # Process the message using the Reasoning Knowledge Integration
        integrated_result = self.reasoning_integration.process_input_with_knowledge(message)
        
        # Try to use the conversation integration to query the knowledge graph
        intent = self.conversation_manager.intent_recognizer.recognize_intent(message, context)
        if intent.type in [IntentType.QUESTION, IntentType.DEFINITION, IntentType.VERIFICATION,
                          IntentType.RELATIONSHIP, IntentType.PROPERTY]:
            # Query the knowledge graph
            result = self.conversation_integration.query_knowledge_graph(intent, context)
            
            if result["success"]:
                # Generate a response based on the query result
                return self._generate_response_from_query_result(result)
        
        # Determine which response to use based on confidence scores
        conversation_response = self.conversation_manager.process_message(message, context_id)
        reasoning_response = reasoning_result.get_primary_response()
        
        # Use the reasoning response if it has high confidence, otherwise use the conversation response
        if reasoning_result.get_highest_confidence() > 0.7:
            response = reasoning_response
        else:
            response = conversation_response
        
        return response
        
    def _sync_ideoms_with_knowledge_graph(self, activation_pattern):
        """
        Ensure that ideoms in the activation pattern are also represented as concepts in the knowledge graph.
        
        Args:
            activation_pattern: The activation pattern containing ideoms.
        """
        # Get the active ideoms from the activation pattern
        active_ideom_ids = activation_pattern.get_active_ideoms()
        
        for ideom_id in active_ideom_ids:
            # Get the ideom from the ideom network
            ideom = self.reasoning_core.ideom_network.get_ideom(ideom_id)
            
            if ideom:
                # Check if a concept with the same name already exists in the knowledge graph
                concept = self.knowledge_graph.get_concept_by_name(ideom.name)
                
                if not concept:
                    # Create a new concept in the knowledge graph
                    self.knowledge_graph.add_concept(ideom.name)
    
    def run_cli(self):
        """
        Run a command-line interface for interacting with the IRA system.
        """
        print("=== IRA System CLI ===")
        print("Type 'exit' to quit.")
        print("Type '@help' for a list of commands.")
        print()
        
        while True:
            # Get user input
            user_input = input("User: ")
            
            # Check if the user wants to exit
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            # Process the user input
            response = self.process_message(user_input)
            
            # Print the response
            print(f"IRA: {response}")
            print()


def main():
    """Run the IRA system."""
    # Create the IRA system
    ira = IRASystem()
    
    # Run the command-line interface
    ira.run_cli()


if __name__ == "__main__":
    main()