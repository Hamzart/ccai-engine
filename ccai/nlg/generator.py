"""
Response generation for CCAI chatbot.

This module provides the main ResponseGenerator class that combines templates,
variations, and reasoning results to generate natural language responses.
"""

from typing import Dict, List, Any, Optional, Union
import logging

from ccai.core.models import Signal
from ccai.conversation.context import ContextTracker
from ccai.nlg.templates import TemplateEngine, VariationGenerator

# Set up logging
logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates natural language responses based on reasoning results.
    
    The ResponseGenerator is responsible for:
    - Converting reasoning results into natural language
    - Selecting appropriate response templates
    - Adding variations to make responses more natural
    - Handling different types of queries and results
    """
    
    def __init__(
        self,
        template_engine: Optional[TemplateEngine] = None,
        variation_generator: Optional[VariationGenerator] = None
    ):
        """
        Initialize the response generator.
        
        Args:
            template_engine: Optional template engine (created if None)
            variation_generator: Optional variation generator (created if None)
        """
        self.template_engine = template_engine or TemplateEngine()
        self.variation_generator = variation_generator or VariationGenerator()
    
    def generate_from_signals(
        self,
        signals: List[Signal],
        query_type: str,
        context: Optional[ContextTracker] = None
    ) -> str:
        """
        Generate a response from reasoning signals.
        
        Args:
            signals: List of Signal objects from the reasoning core
            query_type: The type of query (e.g., "definition", "property")
            context: Optional conversation context
            
        Returns:
            A natural language response
        """
        if not signals:
            return self._generate_fallback_response()
        
        # Extract answers from signals
        answers = []
        for signal in signals:
            if 'final_answer' in signal.payload:
                answers.append(signal.payload['final_answer'])
            elif 'answer' in signal.payload:
                answers.append(signal.payload['answer'])
        
        if not answers:
            return self._generate_fallback_response()
        
        # Generate response based on query type
        if query_type == "is_a":
            return self._generate_definition_response(signals[0].origin, answers)
        elif query_type == "has_property":
            return self._generate_property_response(signals[0].origin, answers)
        elif query_type == "can_do":
            return self._generate_capability_response(signals[0].origin, answers)
        elif query_type == "has_part":
            return self._generate_part_response(signals[0].origin, answers)
        elif query_type == "used_for":
            return self._generate_purpose_response(signals[0].origin, answers)
        else:
            # Generic response for other query types
            return self._generate_generic_response(signals[0].origin, answers)
    
    def generate_from_verification(
        self,
        entity: str,
        relation: str,
        target: str,
        is_confirmed: bool
    ) -> str:
        """
        Generate a response for a verification query.
        
        Args:
            entity: The entity being verified
            relation: The relation being verified
            target: The target of the relation
            is_confirmed: Whether the relation is confirmed
            
        Returns:
            A natural language response
        """
        if relation == "is_a":
            if is_confirmed:
                data = {"entity": entity, "category": target}
                template = self.template_engine.select_template("definition")
                response = self.template_engine.fill_template(template, data)
            else:
                response = f"No, {entity} is not a {target} based on my knowledge."
        
        elif relation == "can_do":
            if is_confirmed:
                data = {"entity": entity, "action": target}
                template = self.template_engine.select_template("capability")
                response = self.template_engine.fill_template(template, data)
            else:
                data = {"entity": entity, "action": target}
                template = self.template_engine.select_template("capability_negative")
                response = self.template_engine.fill_template(template, data)
        
        elif relation == "has_property":
            if is_confirmed:
                # This is simplified; in a real system we'd need to know the property name
                response = f"Yes, {entity} is {target}."
            else:
                response = f"No, {entity} is not {target} based on my knowledge."
        
        elif relation == "has_part":
            if is_confirmed:
                response = f"Yes, {entity} has {target}."
            else:
                response = f"No, {entity} does not have {target} based on my knowledge."
        
        elif relation == "used_for":
            if is_confirmed:
                response = f"Yes, {entity} is used for {target}."
            else:
                response = f"No, {entity} is not used for {target} based on my knowledge."
        
        else:
            if is_confirmed:
                response = f"Yes, that's correct."
            else:
                response = f"No, that's not correct based on my knowledge."
        
        return self.variation_generator.apply_variations(response)
    
    def generate_learning_confirmation(self, fact: str) -> str:
        """
        Generate a confirmation response after learning a new fact.
        
        Args:
            fact: The fact that was learned
            
        Returns:
            A confirmation response
        """
        data = {"fact": fact}
        template = self.template_engine.select_template("learning")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def generate_unknown_concept_response(self, entity: str) -> str:
        """
        Generate a response for an unknown concept.
        
        Args:
            entity: The unknown entity
            
        Returns:
            A response indicating the concept is unknown
        """
        data = {"entity": entity}
        template = self.template_engine.select_template("unknown_concept")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def _generate_definition_response(self, entity: str, answers: List[str]) -> str:
        """Generate a response for a definition query."""
        data = {"entity": entity, "category": answers[0]}
        template = self.template_engine.select_template("definition")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def _generate_property_response(self, entity: str, answers: List[str]) -> str:
        """Generate a response for a property query."""
        # This is simplified; in a real system we'd need to know the property name
        data = {"entity": entity, "property": "property", "value": answers[0]}
        template = self.template_engine.select_template("property")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def _generate_capability_response(self, entity: str, answers: List[str]) -> str:
        """Generate a response for a capability query."""
        data = {"entity": entity, "action": answers[0]}
        template = self.template_engine.select_template("capability")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def _generate_part_response(self, entity: str, answers: List[str]) -> str:
        """Generate a response for a part query."""
        parts = ", ".join(answers)
        data = {"entity": entity, "parts": parts}
        template = self.template_engine.select_template("part")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def _generate_purpose_response(self, entity: str, answers: List[str]) -> str:
        """Generate a response for a purpose query."""
        purposes = ", ".join(answers)
        data = {"entity": entity, "purposes": purposes}
        template = self.template_engine.select_template("purpose")
        response = self.template_engine.fill_template(template, data)
        return self.variation_generator.apply_variations(response)
    
    def _generate_generic_response(self, entity: str, answers: List[str]) -> str:
        """Generate a generic response for other query types."""
        answer_text = ", ".join(answers)
        return f"Regarding {entity}, I found: {answer_text}"
    
    def _generate_fallback_response(self) -> str:
        """Generate a fallback response when no answer is found."""
        template = self.template_engine.select_template("fallback")
        response = self.template_engine.fill_template(template, {})
        return self.variation_generator.apply_variations(response)