"""
TemporalContext module for the Unified Reasoning Core.

This module defines the TemporalContext class, which maintains a history of
activation patterns over time in the IRA (Ideom Resolver AI) architecture.
"""

from typing import List, Dict, Optional, Tuple
from collections import deque
from .activation_pattern import ActivationPattern


class TemporalContext:
    """
    A context for maintaining a history of activation patterns over time.
    
    The TemporalContext maintains a history of activation patterns, allowing
    the system to track changes in activation over time and identify temporal
    patterns.
    
    Attributes:
        max_history_size: The maximum number of activation patterns to keep in history.
        history: A deque of activation patterns, ordered from oldest to newest.
        decay_rate: The rate at which activation patterns decay over time.
        temporal_weights: Weights for different time periods in the history.
    """
    
    def __init__(
        self,
        max_history_size: int = 10,
        decay_rate: float = 0.1,
        temporal_weights: Optional[List[float]] = None
    ):
        """
        Initialize a temporal context.
        
        Args:
            max_history_size: The maximum number of activation patterns to keep in history.
            decay_rate: The rate at which activation patterns decay over time.
            temporal_weights: Weights for different time periods in the history.
                If None, weights will decrease linearly from newest to oldest.
        """
        self.max_history_size = max_history_size
        self.history: deque = deque(maxlen=max_history_size)
        self.decay_rate = decay_rate
        
        # Set temporal weights
        if temporal_weights is None:
            # Default: linear decay from newest to oldest
            self.temporal_weights = [
                1.0 - (i / max_history_size) for i in range(max_history_size)
            ]
        else:
            # Use provided weights, but ensure they match the history size
            if len(temporal_weights) != max_history_size:
                raise ValueError(
                    f"Length of temporal_weights ({len(temporal_weights)}) "
                    f"must match max_history_size ({max_history_size})"
                )
            self.temporal_weights = temporal_weights
    
    def add_activation_pattern(self, pattern: ActivationPattern) -> None:
        """
        Add an activation pattern to the history.
        
        Args:
            pattern: The activation pattern to add.
        """
        self.history.append(pattern)
    
    def get_temporal_activation_pattern(self) -> ActivationPattern:
        """
        Get a temporal activation pattern that combines the history.
        
        This method creates a new activation pattern that combines all the
        patterns in the history, weighted by their temporal weights.
        
        Returns:
            A new ActivationPattern instance representing the temporal pattern.
        """
        # Create a new activation pattern
        temporal_pattern = ActivationPattern()
        
        # If history is empty, return an empty pattern
        if not self.history:
            return temporal_pattern
        
        # Combine all patterns in the history, weighted by their temporal weights
        for i, pattern in enumerate(self.history):
            # Get the weight for this pattern based on its position in history
            weight = self.temporal_weights[i] if i < len(self.temporal_weights) else 0.0
            
            # Add all ideom activations from this pattern, weighted by the temporal weight
            for ideom_id, activation in pattern.get_ideom_activations().items():
                weighted_activation = activation * weight
                if weighted_activation > 0.0:
                    temporal_pattern.add_ideom_activation(ideom_id, weighted_activation)
            
            # Add all active prefabs from this pattern
            for prefab_id in pattern.get_active_prefabs():
                temporal_pattern.add_active_prefab(prefab_id)
        
        return temporal_pattern
    
    def get_activation_trend(self, ideom_id: str) -> List[float]:
        """
        Get the activation trend for a specific ideom.
        
        This method returns a list of activation levels for the specified ideom
        over time, from oldest to newest.
        
        Args:
            ideom_id: The ID of the ideom to get the trend for.
            
        Returns:
            A list of activation levels, from oldest to newest.
        """
        trend = []
        
        for pattern in self.history:
            trend.append(pattern.get_activation_level(ideom_id))
        
        return trend
    
    def get_increasing_activations(self, threshold: float = 0.1) -> List[str]:
        """
        Get ideoms with increasing activation levels.
        
        This method identifies ideoms whose activation levels have been
        increasing over time.
        
        Args:
            threshold: The minimum increase in activation level to consider.
            
        Returns:
            A list of ideom IDs with increasing activation levels.
        """
        increasing_ideoms = []
        
        # Need at least 2 patterns to detect a trend
        if len(self.history) < 2:
            return increasing_ideoms
        
        # Get the oldest and newest patterns
        oldest_pattern = self.history[0]
        newest_pattern = self.history[-1]
        
        # Check all ideoms in the newest pattern
        for ideom_id, activation in newest_pattern.get_ideom_activations().items():
            # Get the activation level in the oldest pattern
            old_activation = oldest_pattern.get_activation_level(ideom_id)
            
            # Check if the activation has increased significantly
            if activation - old_activation >= threshold:
                increasing_ideoms.append(ideom_id)
        
        return increasing_ideoms
    
    def get_decreasing_activations(self, threshold: float = 0.1) -> List[str]:
        """
        Get ideoms with decreasing activation levels.
        
        This method identifies ideoms whose activation levels have been
        decreasing over time.
        
        Args:
            threshold: The minimum decrease in activation level to consider.
            
        Returns:
            A list of ideom IDs with decreasing activation levels.
        """
        decreasing_ideoms = []
        
        # Need at least 2 patterns to detect a trend
        if len(self.history) < 2:
            return decreasing_ideoms
        
        # Get the oldest and newest patterns
        oldest_pattern = self.history[0]
        newest_pattern = self.history[-1]
        
        # Check all ideoms in the oldest pattern
        for ideom_id, activation in oldest_pattern.get_ideom_activations().items():
            # Get the activation level in the newest pattern
            new_activation = newest_pattern.get_activation_level(ideom_id)
            
            # Check if the activation has decreased significantly
            if activation - new_activation >= threshold:
                decreasing_ideoms.append(ideom_id)
        
        return decreasing_ideoms
    
    def get_persistent_activations(self, threshold: float = 0.5) -> List[str]:
        """
        Get ideoms with persistent activation levels.
        
        This method identifies ideoms whose activation levels have remained
        consistently high over time.
        
        Args:
            threshold: The minimum activation level to consider.
            
        Returns:
            A list of ideom IDs with persistent activation levels.
        """
        # Get all unique ideom IDs from all patterns
        all_ideom_ids = set()
        for pattern in self.history:
            all_ideom_ids.update(pattern.get_ideom_activations().keys())
        
        # Check which ideoms have consistently high activation
        persistent_ideoms = []
        for ideom_id in all_ideom_ids:
            # Check if the ideom is active in all patterns
            is_persistent = True
            for pattern in self.history:
                if pattern.get_activation_level(ideom_id) < threshold:
                    is_persistent = False
                    break
            
            if is_persistent:
                persistent_ideoms.append(ideom_id)
        
        return persistent_ideoms
    
    def clear_history(self) -> None:
        """
        Clear the activation pattern history.
        """
        self.history.clear()