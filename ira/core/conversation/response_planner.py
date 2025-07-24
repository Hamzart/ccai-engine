"""
ResponsePlanner module for the Conversation Manager.

This module defines the ResponsePlanner class, which plans a response
to a user message in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
from .conversation_context import ConversationContext, Message, MessageType
from .intent_recognizer import Intent, IntentType


class ResponseType(Enum):
    """
    Enum for response types.
    """
    ANSWER = auto()  # Answer to a question
    ACKNOWLEDGMENT = auto()  # Acknowledgment of a statement
    GREETING = auto()  # Greeting response
    FAREWELL = auto()  # Farewell response
    CLARIFICATION = auto()  # Request for clarification
    ERROR = auto()  # Error response
    UNKNOWN = auto()  # Unknown response type


@dataclass
class ResponsePlan:
    """
    A plan for a response to a user message.
    
    Attributes:
        type: The type of the response.
        content: The content of the response.
        confidence: The confidence score for the response (0.0 to 1.0).
        metadata: Additional metadata for the response.
    """
    
    type: ResponseType
    content: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponsePlanner:
    """
    Plans a response to a user message.
    
    The ResponsePlanner class analyzes a user message and plans a response
    based on the recognized intent and the conversation context.
    
    Attributes:
        knowledge_interface: An interface to the knowledge graph.
        reasoning_interface: An interface to the unified reasoning core.
        response_templates: A dictionary mapping intent types to response templates.
    """
    
    knowledge_interface: Optional[Any] = None
    reasoning_interface: Optional[Any] = None
    response_templates: Dict[IntentType, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the response templates."""
        # Initialize response templates
        self.response_templates = {
            IntentType.QUERY: [
                "Based on my knowledge, {answer}.",
                "I believe that {answer}.",
                "According to my information, {answer}.",
                "The answer is {answer}.",
                "{answer}."
            ],
            IntentType.COMMAND: [
                "I'll {command} right away.",
                "Sure, I'll {command}.",
                "I'm {command} now.",
                "Done! I've {command}.",
                "I've completed your request to {command}."
            ],
            IntentType.STATEMENT: [
                "I understand.",
                "I see.",
                "Got it.",
                "Thanks for letting me know.",
                "I appreciate the information."
            ],
            IntentType.GREETING: [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! How may I assist you?",
                "Hello! What would you like to know?",
                "Hi! How can I be of service?"
            ],
            IntentType.FAREWELL: [
                "Goodbye! Have a great day!",
                "Farewell! It was nice talking to you.",
                "See you later! Feel free to return if you have more questions.",
                "Goodbye! Don't hesitate to ask if you need anything else.",
                "Take care! I'm here if you need assistance in the future."
            ],
            IntentType.AFFIRMATION: [
                "Great!",
                "Excellent!",
                "Perfect!",
                "Wonderful!",
                "Sounds good!"
            ],
            IntentType.NEGATION: [
                "I understand.",
                "I see.",
                "Got it.",
                "I'll keep that in mind.",
                "Thanks for clarifying."
            ],
            IntentType.CLARIFICATION: [
                "I'm sorry for the confusion. Let me clarify: {clarification}",
                "To clarify, {clarification}",
                "Let me explain better: {clarification}",
                "I apologize for not being clear. {clarification}",
                "To be more specific, {clarification}"
            ],
            IntentType.UNKNOWN: [
                "I'm not sure I understand. Could you please rephrase that?",
                "I'm having trouble understanding your request. Could you try again?",
                "I'm sorry, but I don't quite follow. Could you explain differently?",
                "I'm not sure what you're asking for. Could you provide more details?",
                "I'm afraid I don't understand. Could you be more specific?"
            ]
        }
    
    def plan_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a message.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        if message.type != MessageType.USER:
            # Only user messages get responses
            return ResponsePlan(
                type=ResponseType.ERROR,
                content="Cannot respond to non-user messages",
                confidence=0.0
            )
        
        # Handle different intent types
        if intent.type == IntentType.GREETING:
            return self._plan_greeting_response(message, intent, context)
        
        elif intent.type == IntentType.FAREWELL:
            return self._plan_farewell_response(message, intent, context)
        
        elif intent.type == IntentType.QUERY:
            return self._plan_query_response(message, intent, context)
        
        elif intent.type == IntentType.COMMAND:
            return self._plan_command_response(message, intent, context)
        
        elif intent.type == IntentType.STATEMENT:
            return self._plan_statement_response(message, intent, context)
        
        elif intent.type == IntentType.AFFIRMATION:
            return self._plan_affirmation_response(message, intent, context)
        
        elif intent.type == IntentType.NEGATION:
            return self._plan_negation_response(message, intent, context)
        
        elif intent.type == IntentType.CLARIFICATION:
            return self._plan_clarification_response(message, intent, context)
        
        else:
            return self._plan_unknown_response(message, intent, context)
    
    def _plan_greeting_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a greeting response.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        templates = self.response_templates[IntentType.GREETING]
        content = random.choice(templates)
        
        return ResponsePlan(
            type=ResponseType.GREETING,
            content=content,
            confidence=0.9
        )
    
    def _plan_farewell_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a farewell response.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        templates = self.response_templates[IntentType.FAREWELL]
        content = random.choice(templates)
        
        return ResponsePlan(
            type=ResponseType.FAREWELL,
            content=content,
            confidence=0.9
        )
    
    def _plan_query_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a query.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        # If we have a knowledge interface, use it to get an answer
        if self.knowledge_interface is not None:
            # This is a placeholder for the actual knowledge interface integration
            # In a real implementation, we would use the knowledge interface to get an answer
            answer = "I don't have enough information to answer that question"
            confidence = 0.5
        else:
            # Fallback answer
            answer = "I don't have enough information to answer that question"
            confidence = 0.3
        
        templates = self.response_templates[IntentType.QUERY]
        content = random.choice(templates).format(answer=answer)
        
        return ResponsePlan(
            type=ResponseType.ANSWER,
            content=content,
            confidence=confidence
        )
    
    def _plan_command_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a command.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        command_verb = intent.entities.get("command_verb", "")
        command_object = intent.entities.get("command_object", "")
        
        if command_verb and command_object:
            command = f"{command_verb} {command_object}"
        else:
            command = "process your request"
        
        templates = self.response_templates[IntentType.COMMAND]
        content = random.choice(templates).format(command=command)
        
        return ResponsePlan(
            type=ResponseType.ACKNOWLEDGMENT,
            content=content,
            confidence=0.7
        )
    
    def _plan_statement_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a statement.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        templates = self.response_templates[IntentType.STATEMENT]
        content = random.choice(templates)
        
        return ResponsePlan(
            type=ResponseType.ACKNOWLEDGMENT,
            content=content,
            confidence=0.7
        )
    
    def _plan_affirmation_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to an affirmation.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        templates = self.response_templates[IntentType.AFFIRMATION]
        content = random.choice(templates)
        
        return ResponsePlan(
            type=ResponseType.ACKNOWLEDGMENT,
            content=content,
            confidence=0.8
        )
    
    def _plan_negation_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a negation.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        templates = self.response_templates[IntentType.NEGATION]
        content = random.choice(templates)
        
        return ResponsePlan(
            type=ResponseType.ACKNOWLEDGMENT,
            content=content,
            confidence=0.8
        )
    
    def _plan_clarification_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a request for clarification.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        # Get the last system message
        last_system_message = context.get_last_system_message()
        
        if last_system_message is not None:
            clarification = last_system_message.content
        else:
            clarification = "I don't have any additional information to provide at this time."
        
        templates = self.response_templates[IntentType.CLARIFICATION]
        content = random.choice(templates).format(clarification=clarification)
        
        return ResponsePlan(
            type=ResponseType.CLARIFICATION,
            content=content,
            confidence=0.7
        )
    
    def _plan_unknown_response(self, message: Message, intent: Intent, context: ConversationContext) -> ResponsePlan:
        """
        Plan a response to a message with an unknown intent.
        
        Args:
            message: The message to respond to.
            intent: The recognized intent of the message.
            context: The conversation context.
            
        Returns:
            A response plan.
        """
        import random
        
        templates = self.response_templates[IntentType.UNKNOWN]
        content = random.choice(templates)
        
        return ResponsePlan(
            type=ResponseType.UNKNOWN,
            content=content,
            confidence=0.5
        )
    
    def set_knowledge_interface(self, interface: Any) -> None:
        """
        Set the knowledge interface.
        
        Args:
            interface: The knowledge interface.
        """
        self.knowledge_interface = interface
    
    def set_reasoning_interface(self, interface: Any) -> None:
        """
        Set the reasoning interface.
        
        Args:
            interface: The reasoning interface.
        """
        self.reasoning_interface = interface