"""
Intent classification for user messages.

This module provides functionality for classifying user messages into different
intent types, such as questions, statements, commands, etc.
"""

import re
from enum import Enum
from typing import Dict, List, Tuple, Optional


class IntentType(Enum):
    """Enumeration of possible user intent types."""
    QUESTION = "QUESTION"
    STATEMENT = "STATEMENT"
    COMMAND = "COMMAND"
    GREETING = "GREETING"
    FAREWELL = "FAREWELL"
    THANKS = "THANKS"
    UNKNOWN = "UNKNOWN"


class IntentClassifier:
    """
    Classifies user messages into different intent types.
    
    This class uses a combination of rule-based patterns and keyword matching
    to determine the intent of a user message.
    """
    
    def __init__(self):
        """Initialize the intent classifier with patterns for each intent type."""
        self.patterns: Dict[IntentType, List[re.Pattern]] = {
            IntentType.QUESTION: [
                re.compile(r'^(what|who|where|when|why|how|is|are|can|could|would|will|do|does|did|has|have|had)\b', re.IGNORECASE),
                re.compile(r'\?$')
            ],
            IntentType.COMMAND: [
                re.compile(r'^(please|kindly|can you|could you|would you|tell me|show me|find|search|look up|give me)\b', re.IGNORECASE)
            ],
            IntentType.GREETING: [
                re.compile(r'^(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b', re.IGNORECASE)
            ],
            IntentType.FAREWELL: [
                re.compile(r'^(bye|goodbye|see you|farewell|exit|quit)\b', re.IGNORECASE)
            ],
            IntentType.THANKS: [
                re.compile(r'^(thanks|thank you|appreciate it|grateful)\b', re.IGNORECASE)
            ]
        }
        
        # Keywords that strongly indicate a particular intent
        self.keywords: Dict[IntentType, List[str]] = {
            IntentType.QUESTION: [
                "what", "who", "where", "when", "why", "how", 
                "explain", "describe", "tell me about", "define"
            ],
            IntentType.COMMAND: [
                "find", "search", "look up", "show", "display", 
                "calculate", "compute", "create", "make", "add"
            ],
            IntentType.GREETING: [
                "hi", "hello", "hey", "greetings", "good morning", 
                "good afternoon", "good evening", "nice to meet you"
            ],
            IntentType.FAREWELL: [
                "bye", "goodbye", "see you", "farewell", "exit", "quit"
            ],
            IntentType.THANKS: [
                "thanks", "thank you", "appreciate it", "grateful", "thankful"
            ]
        }
    
    def classify(self, text: str) -> IntentType:
        """
        Classify the intent of a user message.
        
        Args:
            text: The user message to classify
            
        Returns:
            The classified intent type
        """
        # Check for pattern matches
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return intent_type
        
        # If no pattern match, check for keywords
        text_lower = text.lower()
        for intent_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return intent_type
        
        # If the text contains a verb and appears to be a statement
        # This is a simple heuristic and could be improved with proper NLP parsing
        words = text.split()
        if len(words) > 2:
            return IntentType.STATEMENT
        
        # Default to unknown if no other classification applies
        return IntentType.UNKNOWN
    
    def get_confidence_scores(self, text: str) -> Dict[IntentType, float]:
        """
        Get confidence scores for each possible intent type.
        
        Args:
            text: The user message to classify
            
        Returns:
            Dictionary mapping intent types to confidence scores (0-1)
        """
        scores: Dict[IntentType, float] = {intent: 0.0 for intent in IntentType}
        
        # Check for pattern matches
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    scores[intent_type] += 0.5  # Add 0.5 for each pattern match
        
        # Check for keywords
        text_lower = text.lower()
        for intent_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    scores[intent_type] += 0.3  # Add 0.3 for each keyword match
        
        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        if total > 0:
            for intent in scores:
                scores[intent] /= total
        else:
            # If no scores, set UNKNOWN to 1.0
            scores[IntentType.UNKNOWN] = 1.0
        
        return scores
    
    def get_top_intent(self, text: str) -> Tuple[IntentType, float]:
        """
        Get the most likely intent type and its confidence score.
        
        Args:
            text: The user message to classify
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        scores = self.get_confidence_scores(text)
        top_intent = max(scores.items(), key=lambda x: x[1])
        return top_intent