"""
Ideom module for the Unified Reasoning Core.

This module defines the Ideom class, which represents an atomic unit of cognition
in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from copy import deepcopy


@dataclass(frozen=True)
class Ideom:
    """
    An atomic unit of cognition in the IRA architecture.
    
    Ideoms are the fundamental building blocks of cognition in the IRA architecture.
    They can be activated and connected to other ideoms to form complex thoughts.
    
    Attributes:
        id: A unique identifier for the ideom.
        name: A human-readable name for the ideom.
        connections: A dictionary mapping ideom IDs to connection strengths.
        activation_level: The current activation level of the ideom.
        activation_threshold: The threshold at which the ideom becomes active.
        decay_rate: The rate at which the activation level decays over time.
    """
    
    id: str
    name: str
    connections: Dict[str, float] = field(default_factory=dict)
    activation_level: float = 0.0
    activation_threshold: float = 0.5
    decay_rate: float = 0.1
    
    def activate(self, strength: float) -> 'Ideom':
        """
        Activate the ideom with the given strength.
        
        Args:
            strength: The strength of the activation.
            
        Returns:
            A new Ideom instance with the updated activation level.
        """
        new_activation = min(1.0, self.activation_level + strength)
        return Ideom(
            id=self.id,
            name=self.name,
            connections=deepcopy(self.connections),
            activation_level=new_activation,
            activation_threshold=self.activation_threshold,
            decay_rate=self.decay_rate
        )
    
    def decay(self) -> 'Ideom':
        """
        Decay the activation level of the ideom.
        
        Returns:
            A new Ideom instance with the decayed activation level.
        """
        new_activation = max(0.0, self.activation_level - self.decay_rate)
        return Ideom(
            id=self.id,
            name=self.name,
            connections=deepcopy(self.connections),
            activation_level=new_activation,
            activation_threshold=self.activation_threshold,
            decay_rate=self.decay_rate
        )
    
    def is_active(self) -> bool:
        """
        Check if the ideom is active.
        
        Returns:
            True if the activation level is above the activation threshold, False otherwise.
        """
        return self.activation_level >= self.activation_threshold
    
    def add_connection(self, ideom_id: str, strength: float) -> 'Ideom':
        """
        Add a connection to another ideom.
        
        Args:
            ideom_id: The ID of the ideom to connect to.
            strength: The strength of the connection.
            
        Returns:
            A new Ideom instance with the added connection.
        """
        new_connections = deepcopy(self.connections)
        new_connections[ideom_id] = strength
        return Ideom(
            id=self.id,
            name=self.name,
            connections=new_connections,
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            decay_rate=self.decay_rate
        )
    
    def update_connection(self, ideom_id: str, strength: float) -> 'Ideom':
        """
        Update the strength of a connection to another ideom.
        
        Args:
            ideom_id: The ID of the ideom to update the connection to.
            strength: The new strength of the connection.
            
        Returns:
            A new Ideom instance with the updated connection.
        """
        if ideom_id not in self.connections:
            return self.add_connection(ideom_id, strength)
        
        new_connections = deepcopy(self.connections)
        new_connections[ideom_id] = strength
        return Ideom(
            id=self.id,
            name=self.name,
            connections=new_connections,
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            decay_rate=self.decay_rate
        )
    
    def remove_connection(self, ideom_id: str) -> 'Ideom':
        """
        Remove a connection to another ideom.
        
        Args:
            ideom_id: The ID of the ideom to remove the connection to.
            
        Returns:
            A new Ideom instance with the removed connection.
        """
        if ideom_id not in self.connections:
            return self
        
        new_connections = deepcopy(self.connections)
        del new_connections[ideom_id]
        return Ideom(
            id=self.id,
            name=self.name,
            connections=new_connections,
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            decay_rate=self.decay_rate
        )
    
    def get_connection_strength(self, ideom_id: str) -> float:
        """
        Get the strength of the connection to another ideom.
        
        Args:
            ideom_id: The ID of the ideom to get the connection strength to.
            
        Returns:
            The strength of the connection, or 0.0 if there is no connection.
        """
        return self.connections.get(ideom_id, 0.0)