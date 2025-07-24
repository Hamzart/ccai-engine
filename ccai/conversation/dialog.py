"""
Dialog management for the CCAI chatbot.

This module provides the DialogManager class, which orchestrates the conversation
flow, processes user messages, and generates appropriate responses.
"""

from typing import Dict, Any, Optional, List
import logging
import random
import json

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
from ccai.llm.interface import LLMInterface
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
        llm_interface: Optional[LLMInterface] = None,
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
        
        # Initialize LLM interface
        self.llm_interface = llm_interface or LLMInterface()
        
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
        
        # Use LLM to parse the query
        llm_parsed_query = self.llm_interface.parse_query(message)
        logger.info(f"LLM parsed query: {llm_parsed_query}")
        
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
        
        # Process based on intent and LLM parsing
        if intent == IntentType.GREETING:
            response = self._handle_greeting()
        elif intent == IntentType.FAREWELL:
            response = self._handle_farewell()
        elif intent == IntentType.THANKS:
            response = self._handle_thanks()
        elif intent == IntentType.QUESTION or llm_parsed_query.get("query_type") != "unknown":
            # Use LLM parsing for questions
            response = self._handle_question_with_llm(message, llm_parsed_query)
        elif intent == IntentType.STATEMENT:
            # Use LLM for knowledge extraction
            response = self._handle_statement_with_llm(message)
        elif intent == IntentType.COMMAND:
            response = self._handle_command(message)
        else:  # UNKNOWN
            response = self._handle_unknown()
        
        # Use LLM to improve response coherence
        response_data = {
            "original_response": response,
            "intent": intent.value,
            "query": message,
            "entities": entities,
            "sentiment": {
                "dominant_emotion": sentiment_result["dominant_emotion"],
                "score": sentiment_result["sentiment_score"]
            }
        }
        
        try:
            enhanced_response = self.llm_interface.generate_response(response_data)
            if enhanced_response and len(enhanced_response) > 10:  # Basic validation
                response = enhanced_response
        except Exception as e:
            logger.error(f"Error enhancing response with LLM: {e}")
            # Fall back to original response
        
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
    
    def _handle_question_with_llm(self, message: str, llm_parsed_query: Dict[str, Any]) -> str:
        """
        Handle question intents using LLM parsing and the reasoning core.
        
        Args:
            message: The user's question
            llm_parsed_query: The query parsed by the LLM
            
        Returns:
            The answer to the question
        """
        # Log the question for debugging
        logger.info(f"Processing question with LLM: {message}")
        
        # Extract entity from LLM parsing
        entity = llm_parsed_query.get("entity", "").strip().lower()
        query_type = llm_parsed_query.get("query_type", "unknown")
        
        # If LLM parsing failed, fall back to traditional parsing
        if not entity or query_type == "unknown":
            logger.info("LLM parsing failed, falling back to traditional parsing")
            initial_signal = self.query_parser.parse_question(message)
        else:
            # Convert LLM parsing to signal
            logger.info(f"Using LLM parsed entity: {entity}, query_type: {query_type}")
            
            if query_type == "definition":
                initial_signal = Signal(origin=entity, purpose="QUERY", payload={"ask": "relation.is_a"})
            elif query_type == "property":
                initial_signal = Signal(origin=entity, purpose="QUERY", payload={"ask_relation": "has_property"})
            elif query_type == "capability":
                initial_signal = Signal(origin=entity, purpose="QUERY", payload={"ask_relation": "can_do"})
            elif query_type == "part":
                initial_signal = Signal(origin=entity, purpose="QUERY", payload={"ask_relation": "has_part"})
            elif query_type == "purpose":
                initial_signal = Signal(origin=entity, purpose="QUERY", payload={"ask_relation": "used_for"})
            elif query_type == "verification":
                target = llm_parsed_query.get("attributes", {}).get("target", "")
                relation = llm_parsed_query.get("attributes", {}).get("relation", "is_a")
                initial_signal = Signal(origin=entity, purpose="VERIFY", payload={"relation": relation, "target": target})
            else:
                # Fall back to traditional parsing
                initial_signal = self.query_parser.parse_question(message)
        
        if not initial_signal:
            logger.warning(f"Failed to parse question: {message}")
            return "I couldn't understand your question. Could you rephrase it?"
        
        logger.info(f"Final parsed signal: {initial_signal.origin} ({initial_signal.purpose})")
        
        # Check if the concept exists in the graph
        if not self.graph.get_node(initial_signal.origin):
            logger.info(f"Unknown concept: {initial_signal.origin}")
            
            # Try to find similar concepts
            similar_concepts = self._find_similar_concepts(initial_signal.origin)
            if similar_concepts:
                logger.info(f"Found similar concepts: {similar_concepts}")
                # If we found similar concepts, suggest them
                concepts_str = ", ".join(similar_concepts[:3])
                return f"I don't have information about '{initial_signal.origin}' specifically. Did you mean {concepts_str}?"
            
            return self.response_generator.generate_unknown_concept_response(initial_signal.origin)
        
        # Process the signal through the reasoning core
        results = self.reasoning_core.process_signal(initial_signal)
        
        # Get activation explanation for debugging
        activation_explanation = self.reasoning_core.get_activation_explanation()
        logger.info(f"Activation explanation: {activation_explanation}")
        
        # Format the results into a natural language response
        if initial_signal.purpose == 'VERIFY':
            is_confirmed = any(res.payload.get('confirmed') for res in results)
            relation = initial_signal.payload.get('relation', '')
            target = initial_signal.payload.get('target', '')
            
            logger.info(f"Verification result: {is_confirmed} for {initial_signal.origin} {relation} {target}")
            
            # Prepare data for LLM response generation
            response_data = {
                "response_type": "verification",
                "entity": initial_signal.origin,
                "verified": is_confirmed,
                "relation": relation,
                "target": target
            }
            
            # Try to use LLM for response generation
            try:
                llm_response = self.llm_interface.generate_response(response_data)
                if llm_response and len(llm_response) > 10:  # Basic validation
                    return llm_response
            except Exception as e:
                logger.error(f"Error generating response with LLM: {e}")
            
            # Fall back to template-based response
            return self.response_generator.generate_from_verification(
                initial_signal.origin, relation, target, is_confirmed
            )
        else:  # Handle QUERY
            query_type = initial_signal.payload.get('ask', '')
            if query_type.startswith('relation.'):
                query_type = query_type[9:]  # Remove 'relation.' prefix
            elif 'ask_relation' in initial_signal.payload:
                query_type = initial_signal.payload['ask_relation']
            
            logger.info(f"Query type: {query_type}")
            
            # If we didn't get any results, try to find related information
            if not results:
                logger.info(f"No direct results found, looking for related information")
                related_info = self.reasoning_core.find_related_concepts(initial_signal.origin)
                
                if related_info and related_info.get("related_concepts"):
                    # Use related concepts to generate a response
                    logger.info(f"Found related concepts: {related_info}")
                    related_response = self._generate_related_concepts_response(
                        initial_signal.origin, related_info["related_concepts"]
                    )
                    if related_response:
                        return related_response
            
            # Extract answers from results
            answers = []
            for signal in results:
                if 'final_answer' in signal.payload:
                    answers.append(signal.payload['final_answer'])
                elif 'answer' in signal.payload:
                    answers.append(signal.payload['answer'])
            
            # Prepare data for LLM response generation
            response_data = {
                "response_type": query_type,
                "entity": initial_signal.origin,
                "answers": answers
            }
            
            # Try to use LLM for response generation
            try:
                llm_response = self.llm_interface.generate_response(response_data)
                if llm_response and len(llm_response) > 10:  # Basic validation
                    return llm_response
            except Exception as e:
                logger.error(f"Error generating response with LLM: {e}")
            
            # Fall back to template-based response
            return self.response_generator.generate_from_signals(
                results, query_type, self.context_tracker
            )
    
    def _find_similar_concepts(self, concept: str) -> List[str]:
        """Find concepts that are similar to the given concept."""
        similar = []
        
        # Simple string similarity (starts with)
        for node_name in self.graph._nodes.keys():
            # Check if the concept is a substring of the node name
            if concept in node_name or node_name in concept:
                similar.append(node_name)
                
        return similar
        
    def _generate_related_concepts_response(self, concept: str, related_concepts: List[Dict[str, Any]]) -> Optional[str]:
        """Generate a response based on related concepts."""
        if not related_concepts:
            return None
            
        # Try to use LLM for generating a more natural response
        try:
            response_data = {
                "response_type": "related_concepts",
                "concept": concept,
                "related_concepts": related_concepts
            }
            
            llm_response = self.llm_interface.generate_response(response_data)
            if llm_response and len(llm_response) > 20:  # Basic validation
                return llm_response
        except Exception as e:
            logger.error(f"Error generating related concepts response with LLM: {e}")
            # Fall back to template-based response
        
        # Group related concepts by relation type
        by_relation = {}
        for rc in related_concepts:
            relation = rc.get("relation", "related_to")
            # Handle second-order and semantic relations
            if relation.startswith("second_order."):
                relation = "second_order"
            elif relation == "semantic_similarity":
                relation = "semantic"
                
            if relation not in by_relation:
                by_relation[relation] = []
            
            # Add the concept with its metadata
            concept_info = {
                "name": rc["concept"],
                "distance": rc.get("distance", 1),
                "path": rc.get("path", []),
                "via": rc.get("via", None),
                "similarity": rc.get("similarity", None),
                "common_properties": rc.get("common_properties", [])
            }
            by_relation[relation].append(concept_info)
        
        # Generate response parts for each relation type
        response_parts = []
        
        # Direct relations first
        if "is_a" in by_relation:
            concepts = [c["name"] for c in by_relation["is_a"][:3]]  # Limit to 3
            response_parts.append(f"{concept} is a type of {', '.join(concepts)}.")
            
        if "has_part" in by_relation:
            concepts = [c["name"] for c in by_relation["has_part"][:3]]  # Limit to 3
            response_parts.append(f"{concept} has {', '.join(concepts)}.")
            
        if "can_do" in by_relation:
            concepts = [c["name"] for c in by_relation["can_do"][:3]]  # Limit to 3
            response_parts.append(f"{concept} can {', '.join(concepts)}.")
        
        # Second-order relations
        if "second_order" in by_relation:
            # Group by the intermediate concept
            by_via = {}
            for c in by_relation["second_order"]:
                via = c.get("via")
                if via:
                    if via not in by_via:
                        by_via[via] = []
                    by_via[via].append(c["name"])
            
            # Generate response for each intermediate concept
            for via, concepts in list(by_via.items())[:2]:  # Limit to 2 intermediate concepts
                concepts_str = ", ".join(concepts[:3])  # Limit to 3 concepts per intermediate
                response_parts.append(f"Through {via}, {concept} is connected to {concepts_str}.")
        
        # Semantic relations
        if "semantic" in by_relation:
            semantic_concepts = by_relation["semantic"]
            if semantic_concepts:
                # Sort by similarity
                semantic_concepts.sort(key=lambda x: x.get("similarity", 0), reverse=True)
                
                # Get top concepts
                top_concepts = semantic_concepts[:3]
                concepts_str = ", ".join(c["name"] for c in top_concepts)
                
                # If we have common properties, mention them
                if any("common_properties" in c and c["common_properties"] for c in top_concepts):
                    # Get the most common properties
                    all_properties = []
                    for c in top_concepts:
                        all_properties.extend(c.get("common_properties", []))
                    
                    # Count occurrences
                    property_counts = {}
                    for prop in all_properties:
                        property_counts[prop] = property_counts.get(prop, 0) + 1
                    
                    # Get top properties
                    top_properties = sorted(property_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    properties_str = ", ".join(p[0] for p in top_properties)
                    
                    response_parts.append(f"{concept} shares properties like {properties_str} with {concepts_str}.")
                else:
                    response_parts.append(f"{concept} has similarities with {concepts_str}.")
        
        # Add a generic part for other relations
        other_relations = set(by_relation.keys()) - {"is_a", "has_part", "can_do", "second_order", "semantic"}
        if other_relations:
            other_concepts = []
            for relation in other_relations:
                other_concepts.extend([c["name"] for c in by_relation[relation][:2]])  # Limit to 2 per relation
            
            if other_concepts:
                response_parts.append(f"{concept} is related to {', '.join(other_concepts)}.")
        
        if response_parts:
            return " ".join(response_parts)
        
        return None
    
    def _handle_statement_with_llm(self, message: str) -> str:
        """
        Handle statement intents using LLM for knowledge extraction.
        
        Args:
            message: The user's statement
            
        Returns:
            Acknowledgment of the information
        """
        # Log the statement for debugging
        logger.info(f"Processing statement with LLM: {message}")
        
        # Use LLM to extract knowledge triplets
        try:
            knowledge_triplets = self.llm_interface.extract_knowledge(message)
            logger.info(f"Extracted knowledge triplets: {knowledge_triplets}")
            
            if not knowledge_triplets:
                logger.warning("No knowledge triplets extracted by LLM")
                # Fall back to traditional extraction
                self.extractor.ingest_text(message)
            else:
                # Process each triplet
                for triplet in knowledge_triplets:
                    subject = triplet.get("subject", "").strip().lower()
                    relation = triplet.get("relation", "").strip().lower()
                    obj = triplet.get("object", "").strip().lower()
                    
                    if subject and relation and obj:
                        logger.info(f"Processing triplet: {subject} {relation} {obj}")
                        
                        # Create or get nodes
                        subject_node = self._get_or_create_node(subject)
                        object_node = self._get_or_create_node(obj)
                        
                        # Add the relationship
                        self.graph.add_edge(subject_node.name, relation, object_node.name)
            
            # Save the updated graph
            self.graph.save_snapshot()
            
            # Generate a confirmation response using LLM
            response_data = {
                "response_type": "learning",
                "statement": message,
                "triplets": knowledge_triplets
            }
            
            try:
                llm_response = self.llm_interface.generate_response(response_data)
                if llm_response and len(llm_response) > 10:  # Basic validation
                    return llm_response
            except Exception as e:
                logger.error(f"Error generating response with LLM: {e}")
            
            # Fall back to template-based response
            return self.response_generator.generate_learning_confirmation(message)
            
        except Exception as e:
            logger.error(f"Error processing statement with LLM: {e}")
            return "I had trouble understanding that statement. Could you try rephrasing it?"
    
    def _get_or_create_node(self, name: str) -> Any:
        """Helper to get or create a node in the graph."""
        node = self.graph.get_node(name)
        if not node:
            # Create a new node
            from ccai.core.models import ConceptNode
            node = ConceptNode(name=name, ctype="entity")
            self.graph.add_node(node)
        return node
    
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