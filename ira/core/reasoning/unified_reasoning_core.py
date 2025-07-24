"""
UnifiedReasoningCore module for the IRA architecture.

This module defines the UnifiedReasoningCore class, which integrates all the components
of the reasoning core and provides the main interface for the reasoning functionality.
"""

import uuid
import json
import os
from typing import Dict, List, Optional, Set, Tuple, Any
from .ideom import Ideom
from .ideom_network import IdeomNetwork
from .activation_pattern import ActivationPattern
from .signal_propagator import SignalPropagator
from .prefab import Prefab
from .prefab_manager import PrefabManager
from .learning_engine import LearningEngine, Feedback
from .text_processor import TextProcessor
from .advanced_prefab_matcher import AdvancedPrefabMatcher
from .dynamic_response_generator import DynamicResponseGenerator


class ReasoningResult:
    """
    The result of a reasoning process.
    
    The ReasoningResult class represents the result of a reasoning process,
    including the activation pattern, active prefabs, confidence scores,
    and response options.
    
    Attributes:
        activation_pattern: The activation pattern resulting from the reasoning process.
        active_prefabs: A list of active prefab IDs.
        confidence_scores: A dictionary mapping response options to confidence scores.
        primary_response: The primary response.
        alternative_responses: A list of alternative responses.
    """
    
    def __init__(
        self,
        activation_pattern: ActivationPattern,
        active_prefabs: List[str],
        confidence_scores: Dict[str, float],
        primary_response: str,
        alternative_responses: List[str]
    ):
        """
        Initialize a reasoning result.
        
        Args:
            activation_pattern: The activation pattern resulting from the reasoning process.
            active_prefabs: A list of active prefab IDs.
            confidence_scores: A dictionary mapping response options to confidence scores.
            primary_response: The primary response.
            alternative_responses: A list of alternative responses.
        """
        self.activation_pattern = activation_pattern
        self.active_prefabs = active_prefabs
        self.confidence_scores = confidence_scores
        self.primary_response = primary_response
        self.alternative_responses = alternative_responses
    
    def get_activation_pattern(self) -> ActivationPattern:
        """
        Get the activation pattern.
        
        Returns:
            The activation pattern resulting from the reasoning process.
        """
        return self.activation_pattern
    
    def get_active_prefabs(self) -> List[str]:
        """
        Get the active prefabs.
        
        Returns:
            A list of active prefab IDs.
        """
        return self.active_prefabs.copy()
    
    def get_confidence_scores(self) -> Dict[str, float]:
        """
        Get the confidence scores.
        
        Returns:
            A dictionary mapping response options to confidence scores.
        """
        return self.confidence_scores.copy()
    
    def get_primary_response(self) -> str:
        """
        Get the primary response.
        
        Returns:
            The primary response.
        """
        return self.primary_response
    
    def get_alternative_responses(self) -> List[str]:
        """
        Get the alternative responses.
        
        Returns:
            A list of alternative responses.
        """
        return self.alternative_responses.copy()
    
    def get_highest_confidence(self) -> float:
        """
        Get the highest confidence score.
        
        Returns:
            The highest confidence score, or 0.0 if there are no confidence scores.
        """
        if not self.confidence_scores:
            return 0.0
        return max(self.confidence_scores.values())
    
    def get_average_confidence(self) -> float:
        """
        Get the average confidence score.
        
        Returns:
            The average confidence score, or 0.0 if there are no confidence scores.
        """
        if not self.confidence_scores:
            return 0.0
        return sum(self.confidence_scores.values()) / len(self.confidence_scores)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the reasoning result to a dictionary.
        
        Returns:
            A dictionary representation of the reasoning result.
        """
        return {
            "active_prefabs": self.active_prefabs,
            "confidence_scores": self.confidence_scores,
            "primary_response": self.primary_response,
            "alternative_responses": self.alternative_responses,
            "highest_confidence": self.get_highest_confidence(),
            "average_confidence": self.get_average_confidence()
        }


class UnifiedReasoningCore:
    """
    The unified reasoning core of the IRA architecture.
    
    The UnifiedReasoningCore integrates all the components of the reasoning core
    and provides the main interface for the reasoning functionality.
    
    Attributes:
        ideom_network: The ideom network.
        signal_propagator: The signal propagator.
        prefab_manager: The prefab manager.
        learning_engine: The learning engine.
    """
    
    def __init__(
        self,
        ideom_network: Optional[IdeomNetwork] = None,
        signal_propagator: Optional[SignalPropagator] = None,
        prefab_manager: Optional[PrefabManager] = None,
        learning_engine: Optional[LearningEngine] = None,
        text_processor: Optional[TextProcessor] = None,
        advanced_prefab_matcher: Optional[AdvancedPrefabMatcher] = None,
        dynamic_response_generator: Optional[DynamicResponseGenerator] = None
    ):
        """
        Initialize a unified reasoning core.
        
        Args:
            ideom_network: The ideom network, or None to create a new one.
            signal_propagator: The signal propagator, or None to create a new one.
            prefab_manager: The prefab manager, or None to create a new one.
            learning_engine: The learning engine, or None to create a new one.
            text_processor: The text processor, or None to create a new one.
            advanced_prefab_matcher: The advanced prefab matcher, or None to create a new one.
            dynamic_response_generator: The dynamic response generator, or None to create a new one.
        """
        self.ideom_network = ideom_network or IdeomNetwork()
        self.prefab_manager = prefab_manager or PrefabManager()
        self.signal_propagator = signal_propagator or SignalPropagator(self.ideom_network)
        self.learning_engine = learning_engine or LearningEngine(
            self.ideom_network, self.prefab_manager
        )
        self.text_processor = text_processor or TextProcessor(self.ideom_network)
        self.advanced_prefab_matcher = advanced_prefab_matcher or AdvancedPrefabMatcher(
            self.prefab_manager, self.ideom_network
        )
        self.dynamic_response_generator = dynamic_response_generator or DynamicResponseGenerator(
            self.ideom_network
        )
    
    def process(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None,
        use_temporal_context: bool = True,
        use_pattern_prediction: bool = True,
        use_dynamic_response: bool = False
    ) -> ReasoningResult:
        """
        Process an input text and generate a reasoning result.
        
        Args:
            input_text: The input text to process.
            context: Optional context information.
            use_temporal_context: Whether to use temporal context for propagation.
            use_pattern_prediction: Whether to use pattern prediction for propagation.
            use_dynamic_response: Whether to use dynamic response generation without templates.
            
        Returns:
            A ReasoningResult instance.
        """
        # Convert the input text to ideom activations
        source_ideom_ids = self._text_to_ideoms(input_text)
        
        # Get context ideoms if available
        context_ideom_ids = []
        if context and "context_ideoms" in context:
            context_ideom_ids = context["context_ideoms"]
        
        # Propagate activation signals with appropriate context
        if use_temporal_context:
            if use_pattern_prediction:
                # Use pattern prediction for the most sophisticated propagation
                activation_pattern = self.signal_propagator.propagate_with_pattern_prediction(
                    source_ideom_ids=source_ideom_ids,
                    initial_strength=1.0,
                    prediction_weight=0.3
                )
            else:
                # Use temporal context for more sophisticated propagation
                activation_pattern = self.signal_propagator.propagate_with_temporal_context(
                    source_ideom_ids=source_ideom_ids,
                    initial_strength=1.0,
                    temporal_influence=0.3,
                    trend_influence=0.2
                )
            
            # If we have explicit context ideoms, merge them in
            if context_ideom_ids:
                context_pattern = ActivationPattern()
                for ideom_id in context_ideom_ids:
                    context_pattern.add_ideom_activation(ideom_id, 0.5)
                activation_pattern = activation_pattern.merge(context_pattern)
        else:
            # Use simple context propagation
            activation_pattern = self.signal_propagator.propagate_with_context(
                source_ideom_ids=source_ideom_ids,
                context_ideom_ids=context_ideom_ids,
                initial_strength=1.0,
                context_strength=0.5
            )
        
        # Find matching prefabs using the advanced prefab matcher
        matching_prefabs = self.advanced_prefab_matcher.find_matching_prefabs(
            activation_pattern,
            include_partial_matches=True,
            include_combinations=True
        )
        
        # Also find semantic matches
        semantic_matches = self.advanced_prefab_matcher.get_semantic_matches(
            activation_pattern,
            semantic_threshold=0.6
        )
        
        # Combine all matches
        all_prefabs = matching_prefabs + semantic_matches
        
        # Remove duplicates (by prefab ID)
        unique_prefabs = {}
        for prefab in all_prefabs:
            if prefab.id not in unique_prefabs or prefab.activation_level > unique_prefabs[prefab.id].activation_level:
                unique_prefabs[prefab.id] = prefab
        
        # Sort by activation level in descending order
        sorted_prefabs = sorted(
            unique_prefabs.values(),
            key=lambda p: p.activation_level,
            reverse=True
        )
        
        # Get the active prefab IDs
        active_prefab_ids = [prefab.id for prefab in sorted_prefabs]
        
        # Generate responses based on the selected method
        if use_dynamic_response:
            # Use dynamic response generation without templates
            primary_response = self.dynamic_response_generator.generate_response(activation_pattern)
            alternative_responses = self.dynamic_response_generator.generate_responses(activation_pattern, 3)
            
            # Remove the primary response from alternatives if it's there
            if primary_response in alternative_responses:
                alternative_responses.remove(primary_response)
            
            # Limit to 2 alternative responses
            alternative_responses = alternative_responses[:2]
            
            # Create confidence scores (all equal for dynamic responses)
            confidence_scores = {}
            confidence_scores[primary_response] = 1.0
            for response in alternative_responses:
                confidence_scores[response] = 0.8  # Slightly lower confidence for alternatives
        else:
            # Use template-based response generation
            response_options = self._generate_response_options(matching_prefabs, activation_pattern)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(response_options, matching_prefabs)
            
            # Select the primary response
            primary_response, alternative_responses = self._select_responses(
                response_options, confidence_scores
            )
        
        # Create the reasoning result
        result = ReasoningResult(
            activation_pattern=activation_pattern,
            active_prefabs=active_prefab_ids,
            confidence_scores=confidence_scores,
            primary_response=primary_response,
            alternative_responses=alternative_responses
        )
        
        # Learn from the activation pattern
        self.learning_engine.learn_from_activation(activation_pattern)
        
        return result
    
    def learn(self, feedback: Feedback) -> None:
        """
        Learn from feedback on a reasoning result.
        
        Args:
            feedback: The feedback to learn from.
        """
        self.learning_engine.learn_from_feedback(feedback)
    
    def create_ideom(self, name: str) -> Ideom:
        """
        Create a new ideom.
        
        Args:
            name: The name for the new ideom.
            
        Returns:
            The newly created Ideom instance.
        """
        ideom_id = str(uuid.uuid4())
        ideom = Ideom(id=ideom_id, name=name)
        self.ideom_network.add_ideom(ideom)
        return ideom
    
    def create_prefab(
        self,
        name: str,
        ideom_weights: Dict[str, float],
        response_template: Optional[str] = None,
        tags: List[str] = None
    ) -> Prefab:
        """
        Create a new prefab.
        
        Args:
            name: The name for the new prefab.
            ideom_weights: A dictionary mapping ideom IDs to weights.
            response_template: An optional response template for the prefab.
            tags: Optional tags for the prefab.
            
        Returns:
            The newly created Prefab instance.
        """
        prefab_id = str(uuid.uuid4())
        prefab = Prefab(
            id=prefab_id,
            name=name,
            ideom_weights=ideom_weights,
            response_template=response_template,
            tags=tags or []
        )
        self.prefab_manager.add_prefab(prefab)
        return prefab
    
    def save(self, path: str) -> None:
        """
        Save the reasoning core to a directory.
        
        Args:
            path: The directory path to save to.
        """
        os.makedirs(path, exist_ok=True)
        
        # Save ideoms
        ideoms_data = {}
        for ideom in self.ideom_network.get_all_ideoms():
            ideoms_data[ideom.id] = {
                "name": ideom.name,
                "connections": ideom.connections,
                "activation_threshold": ideom.activation_threshold,
                "decay_rate": ideom.decay_rate
            }
        
        with open(os.path.join(path, "ideoms.json"), "w") as f:
            json.dump(ideoms_data, f, indent=2)
        
        # Save prefabs
        prefabs_data = {}
        for prefab in self.prefab_manager.get_all_prefabs():
            prefabs_data[prefab.id] = {
                "name": prefab.name,
                "ideom_weights": prefab.ideom_weights,
                "activation_threshold": prefab.activation_threshold,
                "response_template": prefab.response_template,
                "tags": prefab.tags
            }
        
        with open(os.path.join(path, "prefabs.json"), "w") as f:
            json.dump(prefabs_data, f, indent=2)
    
    def load(self, path: str) -> None:
        """
        Load the reasoning core from a directory.
        
        Args:
            path: The directory path to load from.
        """
        # Load ideoms
        with open(os.path.join(path, "ideoms.json"), "r") as f:
            ideoms_data = json.load(f)
        
        for ideom_id, ideom_data in ideoms_data.items():
            ideom = Ideom(
                id=ideom_id,
                name=ideom_data["name"],
                connections=ideom_data["connections"],
                activation_level=0.0,
                activation_threshold=ideom_data["activation_threshold"],
                decay_rate=ideom_data["decay_rate"]
            )
            self.ideom_network.add_ideom(ideom)
        
        # Load prefabs
        with open(os.path.join(path, "prefabs.json"), "r") as f:
            prefabs_data = json.load(f)
        
        for prefab_id, prefab_data in prefabs_data.items():
            prefab = Prefab(
                id=prefab_id,
                name=prefab_data["name"],
                ideom_weights=prefab_data["ideom_weights"],
                activation_level=0.0,
                activation_threshold=prefab_data["activation_threshold"],
                response_template=prefab_data["response_template"],
                tags=prefab_data["tags"]
            )
            self.prefab_manager.add_prefab(prefab)
    
    def _text_to_ideoms(self, text: str) -> List[str]:
        """
        Convert text to ideom activations using the TextProcessor.
        
        This method uses the TextProcessor to analyze text and convert it
        to ideom activations, handling multi-word concepts and semantic understanding.
        
        Args:
            text: The text to convert.
            
        Returns:
            A list of ideom IDs.
        """
        # Process the text using the TextProcessor
        ideom_activations = self.text_processor.process_text(text)
        
        # Extract the ideom IDs from the activations
        ideom_ids = [ideom_id for ideom_id, _ in ideom_activations]
        
        # Create an activation pattern for these ideoms
        activation_pattern = ActivationPattern()
        for ideom_id, activation in ideom_activations:
            activation_pattern.add_ideom_activation(ideom_id, activation)
        
        # Learn from this activation pattern
        self.learning_engine.learn_from_activation(activation_pattern)
        
        return ideom_ids
    
    def _generate_response_options(
        self,
        matching_prefabs: List[Prefab],
        activation_pattern: ActivationPattern
    ) -> List[str]:
        """
        Generate response options based on matching prefabs and the activation pattern.
        
        This method generates response options by filling template variables in the
        response templates of matching prefabs. It uses the activation pattern to
        determine which ideoms are active and uses their names to fill the variables.
        
        Args:
            matching_prefabs: The matching prefabs.
            activation_pattern: The activation pattern.
            
        Returns:
            A list of response options.
        """
        response_options = []
        
        # Get the most active ideoms for template variable filling
        most_active_ideoms = activation_pattern.get_most_active_ideoms(10)
        ideom_names = {}
        
        for ideom_id in most_active_ideoms:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom:
                ideom_names[ideom_id] = ideom.name
        
        # Use response templates from matching prefabs with template variable filling
        for prefab in matching_prefabs:
            if prefab.response_template:
                # Fill template variables with ideom names
                filled_template = self._fill_template_variables(
                    prefab.response_template,
                    ideom_names,
                    activation_pattern
                )
                response_options.append(filled_template)
        
        # If no response templates are available, generate a generic response
        if not response_options:
            response_options.append(self._generate_generic_response(activation_pattern))
        
        return response_options
        
    def _fill_template_variables(
        self,
        template: str,
        ideom_names: Dict[str, str],
        activation_pattern: ActivationPattern
    ) -> str:
        """
        Fill template variables with ideom names based on the activation pattern.
        
        This method replaces template variables in the format {variable_name} with
        appropriate values based on the activation pattern and ideom names.
        
        Args:
            template: The template string with variables in the format {variable_name}.
            ideom_names: A dictionary mapping ideom IDs to their names.
            activation_pattern: The activation pattern.
            
        Returns:
            The template with variables filled.
        """
        import re
        
        # Find all template variables in the format {variable_name}
        variables = re.findall(r'\{([^}]+)\}', template)
        
        filled_template = template
        
        for variable in variables:
            # Handle special variables
            if variable == "most_active_ideom":
                # Get the most active ideom
                most_active_ideoms = activation_pattern.get_most_active_ideoms(1)
                if most_active_ideoms:
                    replacement = ideom_names.get(most_active_ideoms[0], "that")
                else:
                    replacement = "that"
                filled_template = filled_template.replace(f"{{{variable}}}", replacement)
            
            elif variable.startswith("ideom_"):
                # Extract the index from the variable name (e.g., ideom_1 -> 1)
                try:
                    index = int(variable.split("_")[1]) - 1
                    most_active_ideoms = activation_pattern.get_most_active_ideoms(index + 1)
                    if index < len(most_active_ideoms):
                        replacement = ideom_names.get(most_active_ideoms[index], "that")
                    else:
                        replacement = "that"
                    filled_template = filled_template.replace(f"{{{variable}}}", replacement)
                except (ValueError, IndexError):
                    # If the index is invalid, leave the variable as is
                    pass
            
            elif variable == "random_active_ideom":
                # Get a random active ideom
                import random
                active_ideoms = activation_pattern.get_active_ideoms()
                if active_ideoms:
                    random_ideom_id = random.choice(list(active_ideoms))
                    replacement = ideom_names.get(random_ideom_id, "that")
                else:
                    replacement = "that"
                filled_template = filled_template.replace(f"{{{variable}}}", replacement)
            
            elif variable == "active_ideom_count":
                # Get the count of active ideoms
                active_ideoms = activation_pattern.get_active_ideoms()
                replacement = str(len(active_ideoms))
                filled_template = filled_template.replace(f"{{{variable}}}", replacement)
            
            elif variable == "active_ideoms_list":
                # Get a comma-separated list of active ideom names
                active_ideoms = activation_pattern.get_active_ideoms()
                active_ideom_names = [ideom_names.get(ideom_id, "that") for ideom_id in active_ideoms]
                if active_ideom_names:
                    if len(active_ideom_names) == 1:
                        replacement = active_ideom_names[0]
                    else:
                        replacement = ", ".join(active_ideom_names[:-1]) + " and " + active_ideom_names[-1]
                else:
                    replacement = "that"
                filled_template = filled_template.replace(f"{{{variable}}}", replacement)
        
        return filled_template
    
    def _generate_generic_response(self, activation_pattern: ActivationPattern) -> str:
        """
        Generate a generic response based on the activation pattern.
        
        Args:
            activation_pattern: The activation pattern.
            
        Returns:
            A generic response.
        """
        # Get the most active ideoms
        most_active_ideoms = activation_pattern.get_most_active_ideoms(5)
        ideom_names = []
        
        for ideom_id in most_active_ideoms:
            ideom = self.ideom_network.get_ideom(ideom_id)
            if ideom:
                ideom_names.append(ideom.name)
        
        # Generate a more helpful response based on the most active ideoms
        if ideom_names:
            # Check if it's likely a question
            question_indicators = ["what", "who", "how", "why", "when", "where", "is", "are", "can", "do", "does"]
            is_question = any(name.lower() in question_indicators for name in ideom_names)
            
            if is_question:
                return f"I don't have enough information to answer questions about {', '.join(ideom_names)}. You can teach me by making statements about these topics."
            else:
                return f"I understand you're talking about {', '.join(ideom_names)}, but I don't have enough knowledge to provide a detailed response. You can teach me more about these topics."
        else:
            return "I don't understand that yet. You can teach me by making simple statements or asking me about things I already know."
    
    def _calculate_confidence_scores(
        self,
        response_options: List[str],
        matching_prefabs: List[Prefab]
    ) -> Dict[str, float]:
        """
        Calculate confidence scores for response options.
        
        Args:
            response_options: The response options.
            matching_prefabs: The matching prefabs.
            
        Returns:
            A dictionary mapping response options to confidence scores.
        """
        confidence_scores = {}
        
        # If there are no matching prefabs, assign equal confidence to all options
        if not matching_prefabs:
            for option in response_options:
                confidence_scores[option] = 1.0 / len(response_options)
            return confidence_scores
        
        # Calculate confidence based on prefab activation levels
        prefab_confidence = {}
        for prefab in matching_prefabs:
            if prefab.response_template in response_options:
                prefab_confidence[prefab.response_template] = prefab.activation_level
        
        # Normalize confidence scores
        total_confidence = sum(prefab_confidence.values())
        if total_confidence > 0:
            for option, confidence in prefab_confidence.items():
                confidence_scores[option] = confidence / total_confidence
        
        # Assign a small confidence to options without a matching prefab
        for option in response_options:
            if option not in confidence_scores:
                confidence_scores[option] = 0.1
        
        # Normalize again
        total_confidence = sum(confidence_scores.values())
        if total_confidence > 0:
            for option in confidence_scores:
                confidence_scores[option] /= total_confidence
        
        return confidence_scores
    
    def _select_responses(
        self,
        response_options: List[str],
        confidence_scores: Dict[str, float]
    ) -> Tuple[str, List[str]]:
        """
        Select the primary response and alternative responses.
        
        Args:
            response_options: The response options.
            confidence_scores: The confidence scores for the response options.
            
        Returns:
            A tuple of (primary_response, alternative_responses).
        """
        # Sort response options by confidence score
        sorted_options = sorted(
            response_options,
            key=lambda option: confidence_scores.get(option, 0.0),
            reverse=True
        )
        
        # Select the primary response
        primary_response = sorted_options[0] if sorted_options else ""
        
        # Select alternative responses
        alternative_responses = sorted_options[1:] if len(sorted_options) > 1 else []
        
        return primary_response, alternative_responses