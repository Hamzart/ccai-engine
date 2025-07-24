"""
IdeomNetwork module for the Unified Reasoning Core.

This module defines the IdeomNetwork class, which manages a collection of ideoms
and their connections in the IRA (Ideom Resolver AI) architecture.
"""

from typing import Dict, List, Optional, Set
from .ideom import Ideom


class IdeomNetwork:
    """
    A network of interconnected ideoms.
    
    The IdeomNetwork manages a collection of ideoms and their connections,
    providing methods for adding, retrieving, and connecting ideoms.
    
    Attributes:
        ideoms: A dictionary mapping ideom IDs to Ideom instances.
    """
    
    def __init__(self):
        """Initialize an empty ideom network."""
        self.ideoms: Dict[str, Ideom] = {}
    
    def get_ideom(self, ideom_id: str) -> Optional[Ideom]:
        """
        Get an ideom by ID.
        
        Args:
            ideom_id: The ID of the ideom to retrieve.
            
        Returns:
            The Ideom instance with the given ID, or None if not found.
        """
        return self.ideoms.get(ideom_id)
    
    def add_ideom(self, ideom: Ideom) -> None:
        """
        Add an ideom to the network.
        
        Args:
            ideom: The Ideom instance to add.
        """
        self.ideoms[ideom.id] = ideom
    
    def remove_ideom(self, ideom_id: str) -> None:
        """
        Remove an ideom from the network.
        
        Args:
            ideom_id: The ID of the ideom to remove.
        """
        if ideom_id in self.ideoms:
            # Remove connections to this ideom from all other ideoms
            for other_ideom_id, other_ideom in self.ideoms.items():
                if ideom_id in other_ideom.connections:
                    self.ideoms[other_ideom_id] = other_ideom.remove_connection(ideom_id)
            
            # Remove the ideom itself
            del self.ideoms[ideom_id]
    
    def connect_ideoms(self, ideom1_id: str, ideom2_id: str, strength: float) -> None:
        """
        Connect two ideoms with the given strength.
        
        Args:
            ideom1_id: The ID of the first ideom.
            ideom2_id: The ID of the second ideom.
            strength: The strength of the connection.
            
        Raises:
            ValueError: If either ideom is not found in the network.
        """
        ideom1 = self.get_ideom(ideom1_id)
        ideom2 = self.get_ideom(ideom2_id)
        
        if ideom1 is None or ideom2 is None:
            raise ValueError(f"Ideoms not found: {ideom1_id}, {ideom2_id}")
        
        self.ideoms[ideom1_id] = ideom1.update_connection(ideom2_id, strength)
        self.ideoms[ideom2_id] = ideom2.update_connection(ideom1_id, strength)
    
    def get_connected_ideoms(self, ideom_id: str) -> List[Ideom]:
        """
        Get all ideoms connected to the given ideom.
        
        Args:
            ideom_id: The ID of the ideom to get connected ideoms for.
            
        Returns:
            A list of Ideom instances connected to the given ideom.
        """
        ideom = self.get_ideom(ideom_id)
        
        if ideom is None:
            return []
        
        return [self.get_ideom(id) for id in ideom.connections.keys() 
                if self.get_ideom(id) is not None]
    
    def get_all_ideoms(self) -> List[Ideom]:
        """
        Get all ideoms in the network.
        
        Returns:
            A list of all Ideom instances in the network.
        """
        return list(self.ideoms.values())
    
    def get_active_ideoms(self) -> List[Ideom]:
        """
        Get all active ideoms in the network.
        
        Returns:
            A list of all active Ideom instances in the network.
        """
        return [ideom for ideom in self.ideoms.values() if ideom.is_active()]
    
    def decay_all_ideoms(self) -> None:
        """
        Decay the activation level of all ideoms in the network.
        """
        for ideom_id, ideom in self.ideoms.items():
            self.ideoms[ideom_id] = ideom.decay()
    
    def reset_activations(self) -> None:
        """
        Reset the activation level of all ideoms in the network to zero.
        """
        for ideom_id, ideom in self.ideoms.items():
            self.ideoms[ideom_id] = Ideom(
                id=ideom.id,
                name=ideom.name,
                connections=ideom.connections,
                activation_level=0.0,
                activation_threshold=ideom.activation_threshold,
                decay_rate=ideom.decay_rate
            )
    
    def get_ideoms_by_name(self, name: str) -> List[Ideom]:
        """
        Get all ideoms with the given name.
        
        Args:
            name: The name to search for.
            
        Returns:
            A list of Ideom instances with the given name.
        """
        return [ideom for ideom in self.ideoms.values() if ideom.name == name]
    
    def get_strongly_connected_ideoms(self, ideom_id: str, threshold: float = 0.5) -> List[Ideom]:
        """
        Get all ideoms strongly connected to the given ideom.
        
        Args:
            ideom_id: The ID of the ideom to get strongly connected ideoms for.
            threshold: The minimum connection strength to consider.
            
        Returns:
            A list of Ideom instances strongly connected to the given ideom.
        """
        ideom = self.get_ideom(ideom_id)
        
        if ideom is None:
            return []
        
        return [self.get_ideom(id) for id, strength in ideom.connections.items() 
                if strength >= threshold and self.get_ideom(id) is not None]
    
    def get_ideom_neighborhood(self, ideom_id: str, depth: int = 1) -> Set[Ideom]:
        """
        Get the neighborhood of the given ideom up to the specified depth.
        
        Args:
            ideom_id: The ID of the ideom to get the neighborhood for.
            depth: The maximum depth of the neighborhood.
            
        Returns:
            A set of Ideom instances in the neighborhood of the given ideom.
        """
        if depth <= 0:
            return set()
        
        ideom = self.get_ideom(ideom_id)
        
        if ideom is None:
            return set()
        
        neighborhood = {ideom}
        current_depth = 0
        current_frontier = {ideom}
        
        while current_depth < depth and current_frontier:
            next_frontier = set()
            
            for frontier_ideom in current_frontier:
                connected_ideoms = self.get_connected_ideoms(frontier_ideom.id)
                next_frontier.update(connected_ideoms)
            
            next_frontier -= neighborhood  # Remove ideoms already in the neighborhood
            neighborhood.update(next_frontier)
            current_frontier = next_frontier
            current_depth += 1
        
        return neighborhood