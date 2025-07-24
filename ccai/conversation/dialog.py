"""
Dialog management for the CCAI chatbot.

This module provides the DialogManager class, which orchestrates the conversation
flow, processes user messages, and generates appropriate responses.
"""

from typing import Dict, Any, Optional, List
import logging
import random

from ccai.core.graph import ConceptGraph
from ccai.core.reasoning import ReasoningCore
from ccai.core.models import Signal
from ccai.nlp.parser import QueryParser
from ccai.nlp.extractor import InformationExtractor
from ccai.nlp.sentiment import SentimentAnalyzer
from ccai.conversation.context import ContextTracker
from ccai.conversation.intent import IntentClassifier, IntentType
from ccai.nlg.generator import ResponseGenerator
from ccai.user.profile import UserProfileManager
from ccai.user.personalization import PersonalizationAdapter, EntityExtractor
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)


class DialogManager:
    """
    Orchestrates the conversation flow between the user and the CCAI system.
    
    The DialogManager is responsible for:
    - Processing user messages
    - Determining the appropriate action based on intent
    - Generating responses using the reasoning core and NLG
    - Maintaining conversation context
    """
    
    def __init__(
        self,
        graph: ConceptGraph,
        reasoning_core: ReasoningCore,
        extractor: InformationExtractor,
        query_parser: QueryParser,
        response_generator: Optional[ResponseGenerator] = None,
        context_tracker: Optional[ContextTracker] = None,
        intent_classifier: Optional[IntentClassifier] = None,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None,
        profile_manager: Optional[UserProfileManager] = None,
        personalization_adapter: Optional[PersonalizationAdapter] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        current_user_id: str = "default_user"
    ):
        """
        Initialize the dialog manager with required components.
        
        Args:
            graph: The concept graph containing knowledge
            reasoning_core: The reasoning engine for answering questions
            extractor: The information extractor for learning from statements
            query_parser: The parser for converting questions to signals
            context_tracker: Optional context tracker (created if None)
            intent_classifier: Optional intent classifier (created if None)
        """
        self.graph = graph
        self.reasoning_core = reasoning_core
        self.extractor = extractor
        self.query_parser = query_parser
        self.context_tracker = context_tracker or ContextTracker()
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.response_generator = response_generator or ResponseGenerator()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
        
        # Initialize user profile components
        profiles_dir = Path("user_data")
        self.profile_manager = profile_manager or UserProfileManager(profiles_dir)
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.personalization_adapter = personalization_adapter or PersonalizationAdapter(self.profile_manager)
        self.current_user_id = current_user_id
        
        # Simple template responses for common intents (fallback if NLG fails)
        self.templates = {
            IntentType.GREETING: [
                "Hello! How can I help you today?",
                "Hi there! What would you like to know?",
                "Greetings! I'm here to assist you."
            ],
            IntentType.FAREWELL: [
                "Goodbye! Have a great day!",
                "Farewell! Feel free to chat again anytime.",
                "See you later! It was nice chatting with you."
            ],
            IntentType.THANKS: [
                "You're welcome! Is there anything else I can help with?",
                "Happy to help! Let me know if you have more questions.",
                "My pleasure! What else would you like to know?"
            ],
            IntentType.UNKNOWN: [
                "I'm not sure I understand. Could you rephrase that?",
                "I didn't quite catch that. Can you say it differently?",
                "I'm still learning. Could you try asking in another way?"
            ]
        }
    
    def process_message(self, message: str, user_id: Optional[str] = None) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user's message text
            
        Returns:
            The system's response text
        """
        # Use provided user_id or default
        user_id = user_id or self.current_user_id
        
        # Add message to context
        self.context_tracker.add_user_message(message)
        
        # Extract entities and topics
        entities = self.entity_extractor.extract_entities(message)
        topics = self.entity_extractor.extract_topics(message)
        
        # Analyze sentiment
        sentiment_result = self.sentiment_analyzer.analyze(message)
        logger.info(f"Sentiment analysis: {sentiment_result['dominant_emotion']} (score: {sentiment_result['sentiment_score']:.2f})")
        
        # Get response adjustments based on sentiment
        response_adjustments = self.sentiment_analyzer.get_response_adjustment(sentiment_result)
        
        # Classify intent
        intent, confidence = self.intent_classifier.get_top_intent(message)
        logger.info(f"Classified intent: {intent.value} (confidence: {confidence:.2f})")
        
        # Update user profile
        message_type = "question" if intent == IntentType.QUESTION else \
                      "command" if intent == IntentType.COMMAND else "statement"
        self.profile_manager.update_profile(
            user_id,
            message,
            message_type,
            sentiment_result["sentiment_score"],
            entities,
            topics
        )
        
        # Process based on intent
        if intent == IntentType.GREETING:
            response = self._handle_greeting()
        elif intent == IntentType.FAREWELL:
            response = self._handle_farewell()
        elif intent == IntentType.THANKS:
            response = self._handle_thanks()
        elif intent == IntentType.QUESTION:
            response = self._handle_question(message)
        elif intent == IntentType.STATEMENT:
            response = self._handle_statement(message)
        elif intent == IntentType.COMMAND:
            response = self._handle_command(message)
        else:  # UNKNOWN
            response = self._handle_unknown()
        
        # Adjust response based on sentiment
        sentiment_adjusted = self._adjust_response_for_sentiment(response, response_adjustments)
        
        # Personalize response based on user profile
        context = {
            "intent": intent.value,
            "entities": entities,
            "topics": topics,
            "topic": topics[0] if topics else None,
            "sentiment": sentiment_result
        }
        personalized_response = self.personalization_adapter.personalize_response(
            user_id, sentiment_adjusted, context
        )
        
        # Add response to context
        self.context_tracker.add_system_message(personalized_response)
        
        return personalized_response
        
    def _adjust_response_for_sentiment(self, response: str, adjustments: Dict[str, Any]) -> str:
        """
        Adjust the response based on sentiment analysis.
        
        Args:
            response: The original response
            adjustments: Sentiment-based adjustments
            
        Returns:
            The adjusted response
        """
        # Get adjustment parameters
        tone = adjustments.get("tone", "neutral")
        empathy_level = adjustments.get("empathy_level", "moderate")
        verbosity = adjustments.get("verbosity", "moderate")
        suggested_phrases = adjustments.get("suggested_phrases", [])
        
        # Apply adjustments
        adjusted = response
        
        # Add empathetic phrases if needed
        if empathy_level == "high" and suggested_phrases:
            # Add an empathetic phrase at the beginning
            adjusted = f"{suggested_phrases[0]} {adjusted}"
        
        # Adjust verbosity
        if verbosity == "concise" and len(response.split()) > 20:
            # Simplify long responses
            sentences = response.split(". ")
            if len(sentences) > 2:
                # Keep only the first and last sentences
                adjusted = f"{sentences[0]}. {sentences[-1]}"
        
        # Adjust tone (this would be more sophisticated in a real implementation)
        if tone == "very positive" and not any(phrase in response.lower() for phrase in ["don't know", "don't have", "not familiar", "not in my knowledge", "couldn't understand"]):
            # Add positive reinforcement only if the response was actually helpful
            adjusted += " I'm glad I could help!"
        elif tone == "very negative":
            # Add reassurance
            adjusted += " I'll do my best to help resolve this."
        
        return adjusted
    
    def _handle_greeting(self) -> str:
        """Handle greeting intents."""
        import random
        return random.choice(self.templates[IntentType.GREETING])
    
    def _handle_farewell(self) -> str:
        """Handle farewell intents."""
        import random
        return random.choice(self.templates[IntentType.FAREWELL])
    
    def _handle_thanks(self) -> str:
        """Handle thanks intents."""
        import random
        return random.choice(self.templates[IntentType.THANKS])
    
    def _handle_unknown(self) -> str:
        """Handle unknown intents."""
        import random
        return random.choice(self.templates[IntentType.UNKNOWN])
    
    def _handle_question(self, message: str) -> str:
        """
        Handle question intents by parsing the question and using the reasoning core.
        
        Args:
            message: The user's question
            
        Returns:
            The answer to the question
        """
        # Parse the question into a signal
        initial_signal = self.query_parser.parse_question(message)
        
        if not initial_signal:
            return "I couldn't understand the structure of your question. Could you rephrase it?"
        
        # Check if the concept exists in the graph
        if not self.graph.get_node(initial_signal.origin):
            return self.response_generator.generate_unknown_concept_response(initial_signal.origin)
        
        # Process the signal through the reasoning core
        results = self.reasoning_core.process_signal(initial_signal)
        
        # Format the results into a natural language response
        if initial_signal.purpose == 'VERIFY':
            is_confirmed = any(res.payload.get('confirmed') for res in results)
            relation = initial_signal.payload.get('relation', '')
            target = initial_signal.payload.get('target', '')
            
            return self.response_generator.generate_from_verification(
                initial_signal.origin, relation, target, is_confirmed
            )
        else:  # Handle QUERY
            query_type = initial_signal.payload.get('ask', '')
            if query_type.startswith('relation.'):
                query_type = query_type[9:]  # Remove 'relation.' prefix
            elif 'ask_relation' in initial_signal.payload:
                query_type = initial_signal.payload['ask_relation']
            
            return self.response_generator.generate_from_signals(
                results, query_type, self.context_tracker
            )
    
    def _handle_statement(self, message: str) -> str:
        """
        Handle statement intents by extracting information and updating the knowledge graph.
        
        Args:
            message: The user's statement
            
        Returns:
            Acknowledgment of the information
        """
        # Extract information from the statement
        self.extractor.ingest_text(message)
        
        # Save the updated graph
        self.graph.save_snapshot()
        
        return self.response_generator.generate_learning_confirmation(message)
    
    def _handle_command(self, message: str) -> str:
        """
        Handle command intents by performing the requested action.
        
        Args:
            message: The user's command
            
        Returns:
            Response indicating the result of the command
        """
        # This is a placeholder for command handling
        # In a full implementation, this would parse the command and perform the appropriate action
        return "I understand you want me to do something, but I'm still learning how to handle commands."