"""
IntentRecognizer module for the Conversation Manager.

This module defines the IntentRecognizer class, which recognizes the intent
of a user message in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum, auto
import re
from .conversation_context import ConversationContext, Message, MessageType


class IntentType(Enum):
    """
    Enum for intent types.
    """
    QUERY = auto()  # User is asking a question
    COMMAND = auto()  # User is giving a command
    STATEMENT = auto()  # User is making a statement
    GREETING = auto()  # User is greeting the system
    FAREWELL = auto()  # User is saying goodbye
    AFFIRMATION = auto()  # User is affirming something
    NEGATION = auto()  # User is negating something
    CLARIFICATION = auto()  # User is asking for clarification
    UNKNOWN = auto()  # Intent could not be determined
    THANKS = auto()  # User is expressing gratitude
    CAPABILITY = auto()  # User is asking about capabilities
    IDENTITY = auto()  # User is asking about identity
    OPINION = auto()  # User is asking for an opinion
    PERSONAL = auto()  # User is asking a personal question
    QUESTION = auto()  # User is asking a specific question
    DEFINITION = auto()  # User is asking for a definition
    VERIFICATION = auto()  # User is asking for verification
    RELATIONSHIP = auto()  # User is asking about relationships
    PROPERTY = auto()  # User is asking about properties
    CORRECTION = auto()  # User is correcting information


@dataclass
class Intent:
    """
    An intent recognized from a user message.
    
    Attributes:
        type: The type of the intent.
        confidence: The confidence score for the intent (0.0 to 1.0).
        entities: Entities extracted from the message.
        metadata: Additional metadata for the intent.
    """
    
    type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentRecognizer:
    """
    Recognizes the intent of a user message.
    
    The IntentRecognizer class analyzes a user message and determines the user's intent.
    
    Attributes:
        intent_patterns: A dictionary mapping intent types to lists of regex patterns.
        greeting_phrases: A set of greeting phrases.
        farewell_phrases: A set of farewell phrases.
        affirmation_phrases: A set of affirmation phrases.
        negation_phrases: A set of negation phrases.
    """
    
    intent_patterns: Dict[IntentType, List[re.Pattern]] = field(default_factory=dict)
    greeting_phrases: Set[str] = field(default_factory=set)
    farewell_phrases: Set[str] = field(default_factory=set)
    affirmation_phrases: Set[str] = field(default_factory=set)
    negation_phrases: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize the intent patterns and phrase sets."""
        # Initialize intent patterns
        self.intent_patterns = {
            IntentType.QUERY: [
                re.compile(r"^(?:what|who|where|when|why|how|is|are|can|could|would|will|do|does|did|has|have|had)\b.*\?$", re.IGNORECASE),
                re.compile(r"^(?:tell me|show me|explain|describe|define)\b.*$", re.IGNORECASE),
                re.compile(r".*\?$")
            ],
            IntentType.COMMAND: [
                re.compile(r"^(?:please|kindly|)?\s*(?:do|make|create|generate|find|search|look up|calculate|compute|analyze|summarize|translate|convert|transform)\b.*$", re.IGNORECASE)
            ],
            IntentType.STATEMENT: [
                re.compile(r"^(?:i|we|they|he|she|it|this|that|these|those)\b.*$", re.IGNORECASE),
                re.compile(r"^(?:yes|no|maybe|perhaps|possibly|certainly|definitely|absolutely|indeed)\b.*$", re.IGNORECASE)
            ]
        }
        
        # Initialize phrase sets
        self.greeting_phrases = {
            "hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening",
            "howdy", "what's up", "how are you", "how's it going", "nice to meet you", "pleasure to meet you"
        }
        
        self.farewell_phrases = {
            "goodbye", "bye", "see you", "farewell", "take care", "have a nice day", "have a good one",
            "until next time", "catch you later", "talk to you later", "later", "good night"
        }
        
        self.affirmation_phrases = {
            "yes", "yeah", "yep", "yup", "sure", "certainly", "definitely", "absolutely", "indeed",
            "correct", "right", "true", "ok", "okay", "alright", "fine", "agreed", "roger that"
        }
        
        self.negation_phrases = {
            "no", "nope", "nah", "not", "never", "negative", "disagree", "incorrect", "wrong", "false"
        }
    
    def recognize_intent(self, message, context: Optional[ConversationContext] = None) -> Intent:
        """
        Recognize the intent of a message.
        
        Args:
            message: The message to analyze. Can be a Message object or a string.
            context: The conversation context, or None if not available.
            
        Returns:
            The recognized intent.
        """
        # Handle both Message objects and strings
        if isinstance(message, Message):
            if message.type != MessageType.USER:
                # Only user messages have intents
                return Intent(type=IntentType.UNKNOWN, confidence=0.0)
            content = message.content.strip().lower()
        else:
            # Assume it's a string
            content = str(message).strip().lower()
        
        # Check for greeting
        if content in self.greeting_phrases or any(content.startswith(phrase) for phrase in self.greeting_phrases):
            return Intent(type=IntentType.GREETING, confidence=0.9)
        
        # Check for farewell
        if content in self.farewell_phrases or any(content.startswith(phrase) for phrase in self.farewell_phrases):
            return Intent(type=IntentType.FAREWELL, confidence=0.9)
        
        # Check for affirmation
        if content in self.affirmation_phrases or any(content.startswith(phrase) for phrase in self.affirmation_phrases):
            return Intent(type=IntentType.AFFIRMATION, confidence=0.9)
        
        # Check for negation
        if content in self.negation_phrases or any(content.startswith(phrase) for phrase in self.negation_phrases):
            return Intent(type=IntentType.NEGATION, confidence=0.9)
        
        # Check for clarification
        if "what do you mean" in content or "i don't understand" in content or "can you explain" in content:
            return Intent(type=IntentType.CLARIFICATION, confidence=0.8)
        
        # Check for other intent types
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.match(content):
                    return Intent(type=intent_type, confidence=0.7)
        
        # Default to unknown intent
        return Intent(type=IntentType.UNKNOWN, confidence=0.5)
    
    def extract_entities(self, message, intent: Intent) -> Dict[str, Any]:
        """
        Extract entities from a message based on the recognized intent.
        
        Args:
            message: The message to extract entities from. Can be a Message object or a string.
            intent: The recognized intent.
            
        Returns:
            A dictionary of extracted entities.
        """
        # Handle both Message objects and strings
        if isinstance(message, Message):
            content = message.content.strip()
        else:
            # Assume it's a string
            content = str(message).strip()
        entities = {}
        
        if intent.type == IntentType.QUERY:
            # Extract subject of the query
            match = re.search(r"(?:what|who|where|when|why|how) (?:is|are|was|were) (.*?)(?:\?|$)", content, re.IGNORECASE)
            if match:
                entities["subject"] = match.group(1).strip()
            
            # Extract query type
            if re.search(r"^what\b", content, re.IGNORECASE):
                entities["query_type"] = "what"
            elif re.search(r"^who\b", content, re.IGNORECASE):
                entities["query_type"] = "who"
            elif re.search(r"^where\b", content, re.IGNORECASE):
                entities["query_type"] = "where"
            elif re.search(r"^when\b", content, re.IGNORECASE):
                entities["query_type"] = "when"
            elif re.search(r"^why\b", content, re.IGNORECASE):
                entities["query_type"] = "why"
            elif re.search(r"^how\b", content, re.IGNORECASE):
                entities["query_type"] = "how"
        
        elif intent.type == IntentType.COMMAND:
            # Extract command verb
            match = re.search(r"^(?:please|kindly|)?\s*(do|make|create|generate|find|search|look up|calculate|compute|analyze|summarize|translate|convert|transform)\b", content, re.IGNORECASE)
            if match:
                entities["command_verb"] = match.group(1).strip().lower()
            
            # Extract command object
            match = re.search(r"^(?:please|kindly|)?\s*(?:do|make|create|generate|find|search|look up|calculate|compute|analyze|summarize|translate|convert|transform)\s+(.*?)(?:\.|\?|$)", content, re.IGNORECASE)
            if match:
                entities["command_object"] = match.group(1).strip()
        
        return entities
    
    def analyze_message(self, message: Message, context: Optional[ConversationContext] = None) -> Intent:
        """
        Analyze a message to recognize its intent and extract entities.
        
        Args:
            message: The message to analyze.
            context: The conversation context, or None if not available.
            
        Returns:
            The recognized intent with extracted entities.
        """
        intent = self.recognize_intent(message, context)
        entities = self.extract_entities(message, intent)
        intent.entities = entities
        return intent
    
    def get_intent_description(self, intent: Intent) -> str:
        """
        Get a human-readable description of an intent.
        
        Args:
            intent: The intent to describe.
            
        Returns:
            A human-readable description of the intent.
        """
        if intent.type == IntentType.QUERY:
            query_type = intent.entities.get("query_type", "")
            subject = intent.entities.get("subject", "")
            
            if query_type and subject:
                return f"User is asking a {query_type} question about {subject}"
            else:
                return "User is asking a question"
        
        elif intent.type == IntentType.COMMAND:
            command_verb = intent.entities.get("command_verb", "")
            command_object = intent.entities.get("command_object", "")
            
            if command_verb and command_object:
                return f"User is asking to {command_verb} {command_object}"
            else:
                return "User is giving a command"
        
        elif intent.type == IntentType.STATEMENT:
            return "User is making a statement"
        
        elif intent.type == IntentType.GREETING:
            return "User is greeting the system"
        
        elif intent.type == IntentType.FAREWELL:
            return "User is saying goodbye"
        
        elif intent.type == IntentType.AFFIRMATION:
            return "User is affirming something"
        
        elif intent.type == IntentType.NEGATION:
            return "User is negating something"
        
        elif intent.type == IntentType.CLARIFICATION:
            return "User is asking for clarification"
        
        else:
            return "User's intent is unknown"