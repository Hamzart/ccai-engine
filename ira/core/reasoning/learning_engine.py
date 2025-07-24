"""
LearningEngine module for the Unified Reasoning Core.

This module defines the LearningEngine class, which is responsible for learning
from activation patterns and feedback in the IRA (Ideom Resolver AI) architecture.
"""

from typing import Dict, List, Optional, Set
from .ideom_network import IdeomNetwork
from .prefab_manager import PrefabManager
from .activation_pattern import ActivationPattern
from .prefab import Prefab


class Feedback:
    """
    Feedback on a reasoning result.
    
    The Feedback class represents feedback on a reasoning result, including
    the original input, the result, a score, and optionally a correct response.
    
    Attributes:
        input_text: The original input text.
        original_result: The original reasoning result.
        score: A score indicating the quality of the result (-1.0 to 1.0).
        correct_response: The correct response, if available.
        activated_ideoms: A list of ideom IDs that should have been activated.
        activated_prefabs: A list of prefab IDs that should have been activated.
    """
    
    def __init__(
        self,
        input_text: str,
        original_result: ActivationPattern,
        score: float,
        correct_response: Optional[str] = None,
        activated_ideoms: Optional[List[str]] = None,
        activated_prefabs: Optional[List[str]] = None
    ):
        """
        Initialize a feedback instance.
        
        Args:
            input_text: The original input text.
            original_result: The original reasoning result.
            score: A score indicating the quality of the result (-1.0 to 1.0).
            correct_response: The correct response, if available.
            activated_ideoms: A list of ideom IDs that should have been activated.
            activated_prefabs: A list of prefab IDs that should have been activated.
        """
        self.input_text = input_text
        self.original_result = original_result
        self.score = score
        self.correct_response = correct_response
        self.activated_ideoms = activated_ideoms or []
        self.activated_prefabs = activated_prefabs or []
    
    def get_input_text(self) -> str:
        """
        Get the original input text.
        
        Returns:
            The original input text.
        """
        return self.input_text
    
    def get_original_result(self) -> ActivationPattern:
        """
        Get the original reasoning result.
        
        Returns:
            The original reasoning result.
        """
        return self.original_result
    
    def get_score(self) -> float:
        """
        Get the feedback score.
        
        Returns:
            The feedback score.
        """
        return self.score
    
    def get_correct_response(self) -> Optional[str]:
        """
        Get the correct response.
        
        Returns:
            The correct response, or None if not available.
        """
        return self.correct_response
    
    def get_activated_ideoms(self) -> List[str]:
        """
        Get the ideoms that should have been activated.
        
        Returns:
            A list of ideom IDs that should have been activated.
        """
        return self.activated_ideoms
    
    def get_activated_prefabs(self) -> List[str]:
        """
        Get the prefabs that should have been activated.
        
        Returns:
            A list of prefab IDs that should have been activated.
        """
        return self.activated_prefabs


class LearningEngine:
    """
    A learning engine for the Unified Reasoning Core.
    
    The LearningEngine is responsible for learning from activation patterns and feedback,
    updating the ideom network and prefab manager based on experience.
    
    Attributes:
        ideom_network: The ideom network to learn from and update.
        prefab_manager: The prefab manager to learn from and update.
        learning_rate: The rate at which to learn from experiences.
        connection_strength_threshold: The minimum connection strength to maintain.
    """
    
    def __init__(
        self,
        ideom_network: IdeomNetwork,
        prefab_manager: PrefabManager,
        learning_rate: float = 0.1,
        connection_strength_threshold: float = 0.1
    ):
        """
        Initialize a learning engine.
        
        Args:
            ideom_network: The ideom network to learn from and update.
            prefab_manager: The prefab manager to learn from and update.
            learning_rate: The rate at which to learn from experiences.
            connection_strength_threshold: The minimum connection strength to maintain.
        """
        self.ideom_network = ideom_network
        self.prefab_manager = prefab_manager
        self.learning_rate = learning_rate
        self.connection_strength_threshold = connection_strength_threshold
    
    def learn_from_activation(self, activation_pattern: ActivationPattern) -> None:
        """
        Learn from an activation pattern.
        
        This method updates the ideom network and prefab manager based on the
        activation pattern, strengthening connections between co-activated ideoms.
        
        Args:
            activation_pattern: The activation pattern to learn from.
        """
        ideom_activations = activation_pattern.get_ideom_activations()
        active_ideom_ids = list(ideom_activations.keys())
        
        # Strengthen connections between co-activated ideoms
        for i in range(len(active_ideom_ids)):
            ideom1_id = active_ideom_ids[i]
            ideom1 = self.ideom_network.get_ideom(ideom1_id)
            
            if ideom1 is None:
                continue
            
            for j in range(i + 1, len(active_ideom_ids)):
                ideom2_id = active_ideom_ids[j]
                ideom2 = self.ideom_network.get_ideom(ideom2_id)
                
                if ideom2 is None:
                    continue
                
                # Calculate the connection strength increase based on the product of activations
                activation_product = ideom_activations[ideom1_id] * ideom_activations[ideom2_id]
                connection_strength = ideom1.get_connection_strength(ideom2_id)
                new_connection_strength = connection_strength + self.learning_rate * activation_product
                
                # Update the connection if it's strong enough
                if new_connection_strength > self.connection_strength_threshold:
                    self.ideom_network.connect_ideoms(ideom1_id, ideom2_id, new_connection_strength)
        
        # Update prefabs based on the activation pattern
        active_prefabs = self.prefab_manager.find_matching_prefabs(activation_pattern)
        
        for prefab in active_prefabs:
            # Strengthen weights for active ideoms in the prefab
            for ideom_id, activation in ideom_activations.items():
                if ideom_id in prefab.ideom_weights:
                    weight = prefab.ideom_weights[ideom_id]
                    new_weight = weight + self.learning_rate * activation
                    prefab = prefab.update_ideom_weight(ideom_id, new_weight)
                else:
                    # Add new ideoms to the prefab if they're strongly activated
                    if activation > 0.5:
                        prefab = prefab.add_ideom_weight(ideom_id, activation)
            
            # Update the prefab in the manager
            self.prefab_manager.update_prefab(prefab)
    
    def learn_from_feedback(self, feedback: Feedback) -> None:
        """
        Learn from feedback on a reasoning result.
        
        This method updates the ideom network and prefab manager based on the
        feedback, strengthening or weakening connections and weights as appropriate.
        
        Args:
            feedback: The feedback to learn from.
        """
        original_activation_pattern = feedback.get_original_result()
        score = feedback.get_score()
        
        if score > 0:
            # Positive feedback - strengthen connections and weights
            self.learn_from_activation(original_activation_pattern)
        else:
            # Negative feedback - weaken connections and weights
            ideom_activations = original_activation_pattern.get_ideom_activations()
            active_ideom_ids = list(ideom_activations.keys())
            
            # Weaken connections between co-activated ideoms
            for i in range(len(active_ideom_ids)):
                ideom1_id = active_ideom_ids[i]
                ideom1 = self.ideom_network.get_ideom(ideom1_id)
                
                if ideom1 is None:
                    continue
                
                for j in range(i + 1, len(active_ideom_ids)):
                    ideom2_id = active_ideom_ids[j]
                    ideom2 = self.ideom_network.get_ideom(ideom2_id)
                    
                    if ideom2 is None:
                        continue
                    
                    # Calculate the connection strength decrease based on the score
                    connection_strength = ideom1.get_connection_strength(ideom2_id)
                    new_connection_strength = connection_strength - self.learning_rate * abs(score)
                    
                    # Update the connection if it's still strong enough, otherwise remove it
                    if new_connection_strength > self.connection_strength_threshold:
                        self.ideom_network.connect_ideoms(ideom1_id, ideom2_id, new_connection_strength)
                    else:
                        # Remove the connection by setting it to 0
                        self.ideom_network.connect_ideoms(ideom1_id, ideom2_id, 0)
            
            # Update prefabs based on the feedback
            active_prefabs = self.prefab_manager.find_matching_prefabs(original_activation_pattern)
            
            for prefab in active_prefabs:
                # Weaken weights for active ideoms in the prefab
                for ideom_id, activation in ideom_activations.items():
                    if ideom_id in prefab.ideom_weights:
                        weight = prefab.ideom_weights[ideom_id]
                        new_weight = weight - self.learning_rate * abs(score)
                        if new_weight > 0:
                            prefab = prefab.update_ideom_weight(ideom_id, new_weight)
                        else:
                            prefab = prefab.remove_ideom_weight(ideom_id)
                
                # Update the prefab in the manager
                self.prefab_manager.update_prefab(prefab)
        
        # If a correct response is provided, create a new prefab from it
        if feedback.get_correct_response():
            correct_response = feedback.get_correct_response()
            input_text = feedback.get_input_text()
            
            # Process the input text to get ideom activations
            from ..reasoning.text_processor import TextProcessor
            text_processor = TextProcessor(self.ideom_network)
            input_ideom_activations = text_processor.process_text(input_text)
            
            # Create an activation pattern from the input
            input_pattern = ActivationPattern()
            for ideom_id, activation in input_ideom_activations:
                input_pattern.add_ideom_activation(ideom_id, activation)
            
            # Process the correct response to get ideom activations
            response_ideom_activations = text_processor.process_text(correct_response)
            
            # Create a prefab that maps from input to response
            prefab_name = f"Learned_{len(input_text.split())}_words_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create ideom weights based on input activations
            ideom_weights = {}
            for ideom_id, activation in input_ideom_activations:
                ideom_weights[ideom_id] = activation
            
            # Create a new prefab with the correct response as the template
            new_prefab = self.prefab_manager.create_prefab(
                name=prefab_name,
                ideom_weights=ideom_weights,
                activation_threshold=0.3,
                response_template=correct_response,
                tags=["learned", "feedback"]
            )
            
            # Also create connections between input ideoms and response ideoms
            for input_ideom_id, input_activation in input_ideom_activations:
                for response_ideom_id, response_activation in response_ideom_activations:
                    # Only connect if they're different ideoms
                    if input_ideom_id != response_ideom_id:
                        # Calculate connection strength based on activations
                        connection_strength = 0.5 * (input_activation + response_activation)
                        
                        # Get current connection strength
                        input_ideom = self.ideom_network.get_ideom(input_ideom_id)
                        current_strength = input_ideom.get_connection_strength(response_ideom_id)
                        
                        # Update connection with higher strength
                        new_strength = max(current_strength, connection_strength)
                        if new_strength > self.connection_strength_threshold:
                            self.ideom_network.connect_ideoms(input_ideom_id, response_ideom_id, new_strength)
        
        # If specific ideoms or prefabs are provided, strengthen them
        if feedback.get_activated_ideoms():
            # Create an activation pattern with the specified ideoms
            correct_pattern = ActivationPattern()
            for ideom_id in feedback.get_activated_ideoms():
                correct_pattern.add_ideom_activation(ideom_id, 1.0)
            
            # Learn from this pattern
            self.learn_from_activation(correct_pattern)
    
    def create_prefab_from_successful_pattern(
        self,
        activation_pattern: ActivationPattern,
        name: str,
        response_template: Optional[str] = None,
        tags: List[str] = None
    ) -> Prefab:
        """
        Create a new prefab from a successful activation pattern.
        
        Args:
            activation_pattern: The activation pattern to create the prefab from.
            name: The name for the new prefab.
            response_template: An optional response template for the prefab.
            tags: Optional tags for the prefab.
            
        Returns:
            The newly created Prefab instance.
        """
        return self.prefab_manager.create_prefab_from_pattern(
            activation_pattern=activation_pattern,
            name=name,
            threshold=0.3,
            response_template=response_template,
            tags=tags
        )
    
    def adjust_connection_strengths(self, feedback: Feedback) -> None:
        """
        Adjust connection strengths based on feedback.
        
        This method is a more targeted version of learn_from_feedback that
        specifically adjusts connection strengths.
        
        Args:
            feedback: The feedback to learn from.
        """
        original_activation_pattern = feedback.get_original_result()
        score = feedback.get_score()
        
        ideom_activations = original_activation_pattern.get_ideom_activations()
        active_ideom_ids = list(ideom_activations.keys())
        
        # Adjust connections between co-activated ideoms
        for i in range(len(active_ideom_ids)):
            ideom1_id = active_ideom_ids[i]
            ideom1 = self.ideom_network.get_ideom(ideom1_id)
            
            if ideom1 is None:
                continue
            
            for j in range(i + 1, len(active_ideom_ids)):
                ideom2_id = active_ideom_ids[j]
                ideom2 = self.ideom_network.get_ideom(ideom2_id)
                
                if ideom2 is None:
                    continue
                
                # Calculate the connection strength adjustment based on the score
                connection_strength = ideom1.get_connection_strength(ideom2_id)
                adjustment = self.learning_rate * score
                new_connection_strength = connection_strength + adjustment
                
                # Update the connection if it's still strong enough, otherwise remove it
                if new_connection_strength > self.connection_strength_threshold:
                    self.ideom_network.connect_ideoms(ideom1_id, ideom2_id, new_connection_strength)
                else:
                    # Remove the connection by setting it to 0
                    self.ideom_network.connect_ideoms(ideom1_id, ideom2_id, 0)
    
    def optimize_network(self) -> None:
        """
        Optimize the ideom network by removing weak connections and merging similar prefabs.
        """
        # Remove weak connections
        for ideom in self.ideom_network.get_all_ideoms():
            for connected_ideom_id, strength in list(ideom.connections.items()):
                if strength < self.connection_strength_threshold:
                    self.ideom_network.add_ideom(ideom.remove_connection(connected_ideom_id))
        
        # Merge similar prefabs
        self.prefab_manager.merge_similar_prefabs()