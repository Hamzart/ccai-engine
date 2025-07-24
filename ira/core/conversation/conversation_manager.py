"""
ConversationManager module for the IRA architecture.

This module defines the ConversationManager class, which is responsible for
managing conversations with users, including processing user messages,
generating responses, and maintaining conversation context.
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Callable
import re
import time
from datetime import datetime

from .conversation_context import ConversationContext, Message, MessageType, ConversationState
from .intent_recognizer import IntentRecognizer, Intent, IntentType
from .response_planner import ResponsePlanner
from .memory_manager import MemoryManager

# This will be imported when the Knowledge Graph is implemented
# from ..knowledge.knowledge_graph import KnowledgeGraph


class ConversationManager:
    """
    Manages conversations with users.
    
    The ConversationManager class is responsible for processing user messages,
    generating responses, and maintaining conversation context.
    
    Attributes:
        memory_manager: The MemoryManager instance for managing conversation memory.
        intent_recognizer: The IntentRecognizer instance for recognizing user intents.
        response_planner: The ResponsePlanner instance for planning responses.
        knowledge_graph: The KnowledgeGraph instance for accessing knowledge.
        command_handlers: A dictionary mapping command names to handler functions.
        special_intent_handlers: A dictionary mapping special intent types to handler functions.
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        intent_recognizer: Optional[IntentRecognizer] = None,
        response_planner: Optional[ResponsePlanner] = None,
        # knowledge_graph: Optional[KnowledgeGraph] = None
    ):
        """
        Initialize the ConversationManager.
        
        Args:
            memory_manager: The MemoryManager instance for managing conversation memory.
                If None, a new MemoryManager will be created.
            intent_recognizer: The IntentRecognizer instance for recognizing user intents.
                If None, a new IntentRecognizer will be created.
            response_planner: The ResponsePlanner instance for planning responses.
                If None, a new ResponsePlanner will be created.
            knowledge_graph: The KnowledgeGraph instance for accessing knowledge.
                If None, a new KnowledgeGraph will be created.
        """
        self.memory_manager = memory_manager or MemoryManager()
        self.intent_recognizer = intent_recognizer or IntentRecognizer()
        self.response_planner = response_planner or ResponsePlanner()
        # self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        
        # Initialize command handlers
        self.command_handlers = {
            "help": self._handle_help_command,
            "search": self._handle_search_command,
            "define": self._handle_define_command,
            "clear": self._handle_clear_command,
            "status": self._handle_status_command,
        }
        
        # Initialize special intent handlers
        self.special_intent_handlers = {
            IntentType.GREETING: self._handle_greeting_intent,
            IntentType.FAREWELL: self._handle_farewell_intent,
            IntentType.THANKS: self._handle_thanks_intent,
            IntentType.CAPABILITY: self._handle_capability_intent,
            IntentType.IDENTITY: self._handle_identity_intent,
            IntentType.CLARIFICATION: self._handle_clarification_intent,
            IntentType.OPINION: self._handle_opinion_intent,
            IntentType.PERSONAL: self._handle_personal_intent,
        }
        
        # Load memory if available
        self.memory_manager.load_memory()
    
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
        # Get or create the conversation context
        context = self._get_or_create_context(context_id)
        
        # Add the user message to the context
        context.add_message(Message.create_user_message(
            content=message
        ))
        
        # Check if the message is a command
        command_match = re.match(r"^@(\w+)(?:\s+(.*))?$", message)
        if command_match:
            command = command_match.group(1).lower()
            args = command_match.group(2) or ""
            
            # Handle the command
            if command in self.command_handlers:
                response = self.command_handlers[command](context, args)
            else:
                response = f"Unknown command: {command}. Type @help for a list of commands."
        else:
            # Recognize the intent of the message
            intent = self.intent_recognizer.recognize_intent(message, context)
            
            # Handle special intents
            if intent.type in self.special_intent_handlers:
                response = self.special_intent_handlers[intent.type](context, intent)
            else:
                # Generate a response based on the intent
                # Get the last user message to pass to the response planner
                last_user_message = context.get_last_user_message()
                response_plan = self.response_planner.plan_response(last_user_message, intent, context)
                # Extract the content from the ResponsePlan object
                response = response_plan.content
        
        # Add the response to the context
        context.add_message(Message.create_system_message(
            content=response
        ))
        
        # Update the context state
        context.state = ConversationState.ACTIVE
        
        # Save the memory
        self.memory_manager.save_memory()
        
        return response
    
    def _get_or_create_context(self, context_id: Optional[str] = None) -> ConversationContext:
        """
        Get or create a conversation context.
        
        Args:
            context_id: The ID of the conversation context to get.
                If None, the active context will be used, or a new one will be created.
                
        Returns:
            The conversation context.
        """
        if context_id is not None:
            # Get the specified context
            context = self.memory_manager.get_context(context_id)
            if context is None:
                # Create a new context if the specified one doesn't exist
                context = self.memory_manager.create_context()
            else:
                # Set the specified context as active
                self.memory_manager.set_active_context(context_id)
        else:
            # Get the active context
            context = self.memory_manager.get_active_context()
            if context is None:
                # Create a new context if there is no active context
                context = self.memory_manager.create_context()
        
        return context
    
    def _handle_help_command(self, context: ConversationContext, args: str) -> str:
        """
        Handle the @help command.
        
        Args:
            context: The conversation context.
            args: The command arguments.
            
        Returns:
            The response to the command.
        """
        commands = {
            "help": "Show this help message.",
            "search": "Search for information on a topic.",
            "define": "Get the definition of a term.",
            "clear": "Clear the conversation history.",
            "status": "Show the status of the conversation system."
        }
        
        if args:
            # Show help for a specific command
            command = args.lower()
            if command in commands:
                return f"@{command}: {commands[command]}"
            else:
                return f"Unknown command: {command}. Type @help for a list of commands."
        else:
            # Show help for all commands
            help_text = "Available commands:\n"
            for command, description in commands.items():
                help_text += f"@{command}: {description}\n"
            return help_text
    
    def _handle_search_command(self, context: ConversationContext, args: str) -> str:
        """
        Handle the @search command.
        
        Args:
            context: The conversation context.
            args: The command arguments.
            
        Returns:
            The response to the command.
        """
        if not args:
            return "Please specify a search query. Usage: @search <query>"
        
        # TODO: Implement search functionality using the Knowledge Graph
        # For now, return a placeholder response
        return f"Searching for '{args}'... (Not implemented yet)"
    
    def _handle_define_command(self, context: ConversationContext, args: str) -> str:
        """
        Handle the @define command.
        
        Args:
            context: The conversation context.
            args: The command arguments.
            
        Returns:
            The response to the command.
        """
        if not args:
            return "Please specify a term to define. Usage: @define <term>"
        
        # TODO: Implement definition functionality using the Knowledge Graph
        # For now, return a placeholder response
        return f"Definition of '{args}': (Not implemented yet)"
    
    def _handle_clear_command(self, context: ConversationContext, args: str) -> str:
        """
        Handle the @clear command.
        
        Args:
            context: The conversation context.
            args: The command arguments.
            
        Returns:
            The response to the command.
        """
        # Clear the conversation history
        context.messages = []
        
        return "Conversation history cleared."
    
    def _handle_status_command(self, context: ConversationContext, args: str) -> str:
        """
        Handle the @status command.
        
        Args:
            context: The conversation context.
            args: The command arguments.
            
        Returns:
            The response to the command.
        """
        # Get the status of the conversation system
        status = f"Conversation ID: {context.id}\n"
        status += f"State: {context.state.name}\n"
        status += f"Created: {context.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        status += f"Updated: {context.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        status += f"Messages: {len(context.messages)}\n"
        
        # Add information about the active context
        active_context = self.memory_manager.get_active_context()
        if active_context:
            status += f"Active context: {active_context.id}\n"
        else:
            status += "No active context.\n"
        
        # Add information about the number of contexts
        status += f"Total contexts: {len(self.memory_manager.contexts)}\n"
        
        return status
    
    def _handle_greeting_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle a greeting intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a greeting response based on the time of day
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Good morning!"
        elif 12 <= hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        
        # Add a personalized greeting if the user has a name
        user_name = context.metadata.get("user_name")
        if user_name:
            greeting += f" How can I help you today, {user_name}?"
        else:
            greeting += " How can I help you today?"
        
        return greeting
    
    def _handle_farewell_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle a farewell intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a farewell response
        farewells = [
            "Goodbye! Have a great day!",
            "Farewell! It was nice talking to you.",
            "See you later! Take care.",
            "Goodbye! Feel free to come back anytime."
        ]
        
        # Choose a random farewell
        import random
        farewell = random.choice(farewells)
        
        # Update the context state
        context.state = ConversationState.ENDED
        
        return farewell
    
    def _handle_thanks_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle a thanks intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a response to thanks
        responses = [
            "You're welcome!",
            "Happy to help!",
            "No problem at all!",
            "Anytime!",
            "Glad I could assist!"
        ]
        
        # Choose a random response
        import random
        response = random.choice(responses)
        
        return response
    
    def _handle_capability_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle a capability intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a response about capabilities
        capabilities = [
            "I can answer questions, provide definitions, and have conversations.",
            "I can help you find information, explain concepts, and assist with various tasks.",
            "I'm designed to be helpful, informative, and conversational."
        ]
        
        # Choose a random capability statement
        import random
        capability = random.choice(capabilities)
        
        # Add information about commands
        capability += " You can also use commands like @help, @search, and @define."
        
        return capability
    
    def _handle_identity_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle an identity intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a response about identity
        return "I am an Ideom Resolver AI (IRA), designed to understand and respond to your questions and requests using a flexible knowledge representation system."
    
    def _handle_clarification_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle a clarification intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Get the last system message
        last_system_message = None
        for message in reversed(context.messages):
            if message.type == MessageType.SYSTEM:
                last_system_message = message
                break
        
        if last_system_message:
            # Generate a clarification of the last system message
            return f"I apologize if I wasn't clear. Let me rephrase: {last_system_message.content}"
        else:
            # Generate a generic clarification response
            return "I apologize if I wasn't clear. Could you please specify what you'd like me to clarify?"
    
    def _handle_opinion_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle an opinion intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a response about opinions
        return "As an AI, I don't have personal opinions. I can provide information and analysis based on available knowledge, but I don't form subjective judgments."
    
    def _handle_personal_intent(self, context: ConversationContext, intent: Intent) -> str:
        """
        Handle a personal intent.
        
        Args:
            context: The conversation context.
            intent: The recognized intent.
            
        Returns:
            The response to the intent.
        """
        # Generate a response about personal questions
        return "I'm an AI assistant designed to be helpful, harmless, and honest. I don't have personal experiences or feelings, but I'm here to assist you with information and conversation."