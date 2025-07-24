"""
ActivationPattern module for the Unified Reasoning Core.

This module defines the ActivationPattern class, which represents the current state
of activation in the ideom network in the IRA (Ideom Resolver AI) architecture.
"""

from typing import Dict, List, Set


class ActivationPattern:
    """
    A pattern of ideom activations in the ideom network.
    
    The ActivationPattern represents the current state of activation in the ideom network,
    tracking which ideoms are activated and to what degree, as well as which prefabs are active.
    
    Attributes:
        ideom_activations: A dictionary mapping ideom IDs to activation levels.
        active_prefabs: A list of active prefab IDs.
        total_activation: The total activation level across all ideoms.
    """
    
    def __init__(self):
        """Initialize an empty activation pattern."""
        self.ideom_activations: Dict[str, float] = {}
        self.active_prefabs: List[str] = []
        self.total_activation: float = 0.0
    
    def add_ideom_activation(self, ideom_id: str, activation: float) -> None:
        """
        Add or update an ideom activation.
        
        Args:
            ideom_id: The ID of the ideom.
            activation: The activation level of the ideom.
        """
        # If the ideom is already in the pattern, update its activation
        # to the higher value
        if ideom_id in self.ideom_activations:
            self.total_activation -= self.ideom_activations[ideom_id]
            self.ideom_activations[ideom_id] = max(self.ideom_activations[ideom_id], activation)
        else:
            self.ideom_activations[ideom_id] = activation
        
        self.total_activation += self.ideom_activations[ideom_id]
    
    def add_active_prefab(self, prefab_id: str) -> None:
        """
        Add an active prefab.
        
        Args:
            prefab_id: The ID of the active prefab.
        """
        if prefab_id not in self.active_prefabs:
            self.active_prefabs.append(prefab_id)
    
    def get_ideom_activations(self) -> Dict[str, float]:
        """
        Get the ideom activations.
        
        Returns:
            A dictionary mapping ideom IDs to activation levels.
        """
        return self.ideom_activations.copy()
    
    def get_active_prefabs(self) -> List[str]:
        """
        Get the active prefabs.
        
        Returns:
            A list of active prefab IDs.
        """
        return self.active_prefabs.copy()
    
    def get_total_activation(self) -> float:
        """
        Get the total activation level.
        
        Returns:
            The total activation level across all ideoms.
        """
        return self.total_activation
    
    def get_most_active_ideoms(self, n: int = 10) -> List[str]:
        """
        Get the most active ideoms.
        
        Args:
            n: The number of ideoms to return.
            
        Returns:
            A list of the n most active ideom IDs, sorted by activation level.
        """
        sorted_ideoms = sorted(
            self.ideom_activations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [ideom_id for ideom_id, _ in sorted_ideoms[:n]]
    
    def get_activation_level(self, ideom_id: str) -> float:
        """
        Get the activation level of an ideom.
        
        Args:
            ideom_id: The ID of the ideom.
            
        Returns:
            The activation level of the ideom, or 0.0 if the ideom is not in the pattern.
        """
        return self.ideom_activations.get(ideom_id, 0.0)
    
    def is_ideom_active(self, ideom_id: str, threshold: float = 0.5) -> bool:
        """
        Check if an ideom is active.
        
        Args:
            ideom_id: The ID of the ideom.
            threshold: The activation threshold.
            
        Returns:
            True if the ideom's activation level is above the threshold, False otherwise.
        """
        return self.get_activation_level(ideom_id) >= threshold
    
    def get_active_ideoms(self, threshold: float = 0.5) -> Set[str]:
        """
        Get all active ideoms.
        
        Args:
            threshold: The activation threshold.
            
        Returns:
            A set of ideom IDs with activation levels above the threshold.
        """
        return {ideom_id for ideom_id, activation in self.ideom_activations.items()
                if activation >= threshold}
    
    def merge(self, other: 'ActivationPattern') -> 'ActivationPattern':
        """
        Merge this activation pattern with another.
        
        Args:
            other: The other activation pattern to merge with.
            
        Returns:
            A new ActivationPattern instance with the merged activations.
        """
        result = ActivationPattern()
        
        # Merge ideom activations, taking the higher activation level for each ideom
        for ideom_id, activation in self.ideom_activations.items():
            result.add_ideom_activation(ideom_id, activation)
        
        for ideom_id, activation in other.ideom_activations.items():
            if ideom_id in result.ideom_activations:
                result.total_activation -= result.ideom_activations[ideom_id]
                result.ideom_activations[ideom_id] = max(result.ideom_activations[ideom_id], activation)
                result.total_activation += result.ideom_activations[ideom_id]
            else:
                result.ideom_activations[ideom_id] = activation
                result.total_activation += activation
        
        # Merge active prefabs
        for prefab_id in self.active_prefabs:
            result.add_active_prefab(prefab_id)
        
        for prefab_id in other.active_prefabs:
            if prefab_id not in result.active_prefabs:
                result.add_active_prefab(prefab_id)
        
        return result
    
    def __str__(self) -> str:
        """
        Get a string representation of the activation pattern.
        
        Returns:
            A string representation of the activation pattern.
        """
        active_ideoms = self.get_most_active_ideoms(5)
        active_ideoms_str = ", ".join([f"{ideom_id}: {self.ideom_activations[ideom_id]:.2f}" 
                                      for ideom_id in active_ideoms])
        
        return (f"ActivationPattern(total_activation={self.total_activation:.2f}, "
                f"active_ideoms=[{active_ideoms_str}], "
                f"active_prefabs={self.active_prefabs})")