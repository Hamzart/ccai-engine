"""
SignalPropagator module for the Unified Reasoning Core.

This module defines the SignalPropagator class, which is responsible for propagating
activation signals through the ideom network in the IRA (Ideom Resolver AI) architecture.
"""

from typing import List, Set, Optional, Dict, Tuple
from .ideom_network import IdeomNetwork
from .activation_pattern import ActivationPattern
from .ideom import Ideom
from .temporal_context import TemporalContext


class SignalPropagator:
    """
    A propagator for activation signals in the ideom network.
    
    The SignalPropagator is responsible for propagating activation signals through
    the ideom network, activating ideoms based on their connections.
    
    Attributes:
        ideom_network: The ideom network to propagate signals through.
        propagation_threshold: The minimum activation level for signal propagation.
        max_propagation_steps: The maximum number of propagation steps.
    """
    
    def __init__(
        self,
        ideom_network: IdeomNetwork,
        propagation_threshold: float = 0.1,
        max_propagation_steps: int = 10,
        temporal_context: Optional[TemporalContext] = None
    ):
        """
        Initialize a signal propagator.
        
        Args:
            ideom_network: The ideom network to propagate signals through.
            propagation_threshold: The minimum activation level for signal propagation.
            max_propagation_steps: The maximum number of propagation steps.
            temporal_context: The temporal context for tracking activation patterns over time.
                If None, a new TemporalContext will be created.
        """
        self.ideom_network = ideom_network
        self.propagation_threshold = propagation_threshold
        self.max_propagation_steps = max_propagation_steps
        self.temporal_context = temporal_context or TemporalContext()
    
    def propagate(
        self,
        source_ideom_ids: List[str],
        initial_strength: float
    ) -> ActivationPattern:
        """
        Propagate activation signals from the source ideoms.
        
        Args:
            source_ideom_ids: The IDs of the source ideoms to start propagation from.
            initial_strength: The initial activation strength.
            
        Returns:
            An ActivationPattern representing the resulting activation state.
        """
        activation_pattern = ActivationPattern()
        active_ideom_ids = set(source_ideom_ids)
        
        # Activate source ideoms
        for ideom_id in source_ideom_ids:
            ideom = self.ideom_network.get_ideom(ideom_id)
            
            if ideom is None:
                continue
            
            new_ideom = ideom.activate(initial_strength)
            self.ideom_network.add_ideom(new_ideom)
            activation_pattern.add_ideom_activation(ideom_id, new_ideom.activation_level)
        
        # Propagate activation
        for step in range(self.max_propagation_steps):
            new_active_ideom_ids = set()
            
            for ideom_id in active_ideom_ids:
                ideom = self.ideom_network.get_ideom(ideom_id)
                
                if ideom is None:
                    continue
                
                for connected_ideom in self.ideom_network.get_connected_ideoms(ideom_id):
                    activation_strength = ideom.activation_level * ideom.get_connection_strength(connected_ideom.id)
                    
                    if activation_strength > self.propagation_threshold:
                        new_ideom = connected_ideom.activate(activation_strength)
                        self.ideom_network.add_ideom(new_ideom)
                        activation_pattern.add_ideom_activation(connected_ideom.id, new_ideom.activation_level)
                        new_active_ideom_ids.add(connected_ideom.id)
            
            if not new_active_ideom_ids:
                break
            
            active_ideom_ids = new_active_ideom_ids
        
        return activation_pattern
    
    def inhibit(self, ideom_ids: List[str], inhibition_strength: float = 1.0) -> None:
        """
        Inhibit the activation of specific ideoms.
        
        Args:
            ideom_ids: The IDs of the ideoms to inhibit.
            inhibition_strength: The strength of the inhibition.
        """
        for ideom_id in ideom_ids:
            ideom = self.ideom_network.get_ideom(ideom_id)
            
            if ideom is None:
                continue
            
            # Set the activation level to 0
            new_ideom = Ideom(
                id=ideom.id,
                name=ideom.name,
                connections=ideom.connections,
                activation_level=0.0,
                activation_threshold=ideom.activation_threshold,
                decay_rate=ideom.decay_rate
            )
            
            self.ideom_network.add_ideom(new_ideom)
    
    def propagate_with_context(
        self,
        source_ideom_ids: List[str],
        context_ideom_ids: List[str],
        initial_strength: float,
        context_strength: float = 0.5
    ) -> ActivationPattern:
        """
        Propagate activation signals with context.
        
        This method propagates activation signals from the source ideoms,
        with additional activation from context ideoms.
        
        Args:
            source_ideom_ids: The IDs of the source ideoms to start propagation from.
            context_ideom_ids: The IDs of the context ideoms to provide additional activation.
            initial_strength: The initial activation strength for source ideoms.
            context_strength: The activation strength for context ideoms.
            
        Returns:
            An ActivationPattern representing the resulting activation state.
        """
        # Activate context ideoms
        context_pattern = ActivationPattern()
        
        for ideom_id in context_ideom_ids:
            ideom = self.ideom_network.get_ideom(ideom_id)
            
            if ideom is None:
                continue
            
            new_ideom = ideom.activate(context_strength)
            self.ideom_network.add_ideom(new_ideom)
            context_pattern.add_ideom_activation(ideom_id, new_ideom.activation_level)
        
        # Propagate from source ideoms
        source_pattern = self.propagate(source_ideom_ids, initial_strength)
        
        # Merge the patterns
        result_pattern = source_pattern.merge(context_pattern)
        
        # Add the result to the temporal context
        self.temporal_context.add_activation_pattern(result_pattern)
        
        return result_pattern
    
    def propagate_with_inhibition(
        self,
        source_ideom_ids: List[str],
        inhibited_ideom_ids: List[str],
        initial_strength: float
    ) -> ActivationPattern:
        """
        Propagate activation signals with inhibition.
        
        This method propagates activation signals from the source ideoms,
        while inhibiting specific ideoms.
        
        Args:
            source_ideom_ids: The IDs of the source ideoms to start propagation from.
            inhibited_ideom_ids: The IDs of the ideoms to inhibit.
            initial_strength: The initial activation strength.
            
        Returns:
            An ActivationPattern representing the resulting activation state.
        """
        # Inhibit specified ideoms
        self.inhibit(inhibited_ideom_ids)
        
        # Propagate from source ideoms
        result_pattern = self.propagate(source_ideom_ids, initial_strength)
        
        # Add the result to the temporal context
        self.temporal_context.add_activation_pattern(result_pattern)
        
        return result_pattern
        
    def propagate_with_temporal_context(
        self,
        source_ideom_ids: List[str],
        initial_strength: float,
        temporal_influence: float = 0.3,
        trend_influence: float = 0.2
    ) -> ActivationPattern:
        """
        Propagate activation signals with temporal context awareness.
        
        This method propagates activation signals from the source ideoms,
        influenced by the temporal context of previous activations. It considers
        persistent activations, increasing and decreasing trends, and the overall
        temporal pattern.
        
        Args:
            source_ideom_ids: The IDs of the source ideoms to start propagation from.
            initial_strength: The initial activation strength.
            temporal_influence: The influence of the temporal context (0.0 to 1.0).
            trend_influence: The influence of activation trends (0.0 to 1.0).
            
        Returns:
            An ActivationPattern representing the resulting activation state.
        """
        # Get the temporal context pattern
        temporal_pattern = self.temporal_context.get_temporal_activation_pattern()
        
        # Get persistent ideoms from the temporal context
        persistent_ideoms = self.temporal_context.get_persistent_activations()
        
        # Get ideoms with increasing activation
        increasing_ideoms = self.temporal_context.get_increasing_activations()
        
        # Get ideoms with decreasing activation
        decreasing_ideoms = self.temporal_context.get_decreasing_activations()
        
        # Create a boosted source ideoms list with adjusted activation strengths
        boosted_source_ideoms = []
        activation_adjustments = {}
        
        # Add original source ideoms
        for ideom_id in source_ideom_ids:
            boosted_source_ideoms.append(ideom_id)
            activation_adjustments[ideom_id] = initial_strength
        
        # Add persistent ideoms with boosted activation
        for ideom_id in persistent_ideoms:
            if ideom_id not in boosted_source_ideoms:
                boosted_source_ideoms.append(ideom_id)
                activation_adjustments[ideom_id] = initial_strength * 0.8  # Slightly lower than direct activation
            else:
                # Boost existing ideom
                activation_adjustments[ideom_id] *= 1.2  # 20% boost for persistent ideoms
        
        # Boost ideoms with increasing activation
        for ideom_id in increasing_ideoms:
            if ideom_id in boosted_source_ideoms:
                activation_adjustments[ideom_id] *= (1.0 + trend_influence)  # Boost based on trend influence
            else:
                boosted_source_ideoms.append(ideom_id)
                activation_adjustments[ideom_id] = initial_strength * trend_influence
        
        # Reduce ideoms with decreasing activation
        for ideom_id in decreasing_ideoms:
            if ideom_id in boosted_source_ideoms:
                activation_adjustments[ideom_id] *= (1.0 - trend_influence)  # Reduce based on trend influence
        
        # Propagate from each boosted source ideom with its adjusted activation
        source_pattern = ActivationPattern()
        
        for ideom_id in boosted_source_ideoms:
            # Get the adjusted activation strength
            adjusted_strength = activation_adjustments.get(ideom_id, initial_strength)
            
            # Create a temporary pattern for this ideom
            temp_pattern = self.propagate([ideom_id], adjusted_strength)
            
            # Merge into the source pattern
            for temp_ideom_id, activation in temp_pattern.get_ideom_activations().items():
                current_activation = source_pattern.get_activation_level(temp_ideom_id)
                # Use the maximum activation level
                source_pattern.add_ideom_activation(temp_ideom_id, max(current_activation, activation))
        
        # Merge with the temporal pattern, weighted by temporal influence
        for ideom_id, activation in temporal_pattern.get_ideom_activations().items():
            weighted_activation = activation * temporal_influence
            if weighted_activation > 0.0:
                current_activation = source_pattern.get_activation_level(ideom_id)
                # Use the maximum activation level
                source_pattern.add_ideom_activation(ideom_id, max(current_activation, weighted_activation))
        
        # Add active prefabs from the temporal pattern
        for prefab_id in temporal_pattern.get_active_prefabs():
            source_pattern.add_active_prefab(prefab_id)
        
        # Add the result to the temporal context
        self.temporal_context.add_activation_pattern(source_pattern)
        
        return source_pattern
        
    def detect_temporal_patterns(self, min_pattern_length: int = 3) -> Dict[str, List[float]]:
        """
        Detect temporal patterns in ideom activations.
        
        This method analyzes the temporal context to identify recurring patterns
        in ideom activations over time.
        
        Args:
            min_pattern_length: The minimum length of patterns to detect.
            
        Returns:
            A dictionary mapping ideom IDs to their activation patterns.
        """
        patterns = {}
        
        # Get all unique ideom IDs from the temporal context
        all_ideom_ids = set()
        for pattern in self.temporal_context.history:
            all_ideom_ids.update(pattern.get_ideom_activations().keys())
        
        # For each ideom, get its activation trend
        for ideom_id in all_ideom_ids:
            trend = self.temporal_context.get_activation_trend(ideom_id)
            
            # Only consider trends with sufficient length
            if len(trend) >= min_pattern_length:
                patterns[ideom_id] = trend
        
        return patterns
    
    def propagate_with_pattern_prediction(
        self,
        source_ideom_ids: List[str],
        initial_strength: float,
        prediction_weight: float = 0.3
    ) -> ActivationPattern:
        """
        Propagate activation signals with pattern prediction.
        
        This method propagates activation signals from the source ideoms,
        using pattern prediction to anticipate future activations based on
        temporal patterns.
        
        Args:
            source_ideom_ids: The IDs of the source ideoms to start propagation from.
            initial_strength: The initial activation strength.
            prediction_weight: The weight to give to predicted activations.
            
        Returns:
            An ActivationPattern representing the resulting activation state.
        """
        # First, propagate normally
        source_pattern = self.propagate(source_ideom_ids, initial_strength)
        
        # Detect temporal patterns
        temporal_patterns = self.detect_temporal_patterns()
        
        # If there are no patterns, return the source pattern
        if not temporal_patterns:
            return source_pattern
        
        # Predict future activations based on patterns
        predicted_activations = {}
        
        for ideom_id, pattern in temporal_patterns.items():
            # Simple prediction: if activation has been increasing, predict it will continue
            if len(pattern) >= 2 and pattern[-1] > pattern[-2]:
                # Predict a continued increase
                predicted_activation = pattern[-1] + (pattern[-1] - pattern[-2])
                predicted_activations[ideom_id] = min(1.0, predicted_activation)  # Cap at 1.0
        
        # Apply predicted activations to the source pattern
        for ideom_id, activation in predicted_activations.items():
            weighted_activation = activation * prediction_weight
            current_activation = source_pattern.get_activation_level(ideom_id)
            source_pattern.add_ideom_activation(ideom_id, max(current_activation, weighted_activation))
        
        return source_pattern
    
    def get_activation_spread(
        self,
        source_ideom_ids: List[str],
        initial_strength: float,
        threshold: float = 0.5
    ) -> Set[str]:
        """
        Get the set of ideoms that would be activated by propagation.
        
        Args:
            source_ideom_ids: The IDs of the source ideoms to start propagation from.
            initial_strength: The initial activation strength.
            threshold: The activation threshold for considering an ideom activated.
            
        Returns:
            A set of ideom IDs that would be activated.
        """
        activation_pattern = self.propagate(source_ideom_ids, initial_strength)
        return activation_pattern.get_active_ideoms(threshold)