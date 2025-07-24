"""
Prefab module for the Unified Reasoning Core.

This module defines the Prefab class, which represents a pattern of ideom activations
that corresponds to a higher-level concept or response in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from copy import deepcopy
from .activation_pattern import ActivationPattern


@dataclass(frozen=True)
class Prefab:
    """
    A pattern of ideom activations that corresponds to a higher-level concept or response.
    
    Prefabs are activated when their corresponding pattern of ideom activations is detected
    in the network. They can represent complex concepts, responses, or behaviors.
    
    Attributes:
        id: A unique identifier for the prefab.
        name: A human-readable name for the prefab.
        ideom_weights: A dictionary mapping ideom IDs to weights.
        activation_level: The current activation level of the prefab.
        activation_threshold: The threshold at which the prefab becomes active.
        response_template: An optional template for generating responses.
        tags: A list of tags for categorizing the prefab.
    """
    
    id: str
    name: str
    ideom_weights: Dict[str, float] = field(default_factory=dict)
    activation_level: float = 0.0
    activation_threshold: float = 0.5
    response_template: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def activate(self, activation_pattern: ActivationPattern) -> float:
        """
        Activate the prefab based on the given activation pattern.
        
        Args:
            activation_pattern: The activation pattern to match against.
            
        Returns:
            The new activation level of the prefab.
        """
        # Calculate the weighted sum of ideom activations
        weighted_sum = 0.0
        total_weight = 0.0
        
        for ideom_id, weight in self.ideom_weights.items():
            activation = activation_pattern.get_activation_level(ideom_id)
            weighted_sum += activation * weight
            total_weight += weight
        
        # Normalize by the total weight
        if total_weight > 0:
            new_activation = weighted_sum / total_weight
        else:
            new_activation = 0.0
        
        # Create a new prefab with the updated activation level
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=deepcopy(self.ideom_weights),
            activation_level=new_activation,
            activation_threshold=self.activation_threshold,
            response_template=self.response_template,
            tags=self.tags.copy()
        )
    
    def is_active(self) -> bool:
        """
        Check if the prefab is active.
        
        Returns:
            True if the activation level is above the activation threshold, False otherwise.
        """
        return self.activation_level >= self.activation_threshold
    
    def get_ideom_weights(self) -> Dict[str, float]:
        """
        Get the ideom weights.
        
        Returns:
            A dictionary mapping ideom IDs to weights.
        """
        return self.ideom_weights.copy()
    
    def add_ideom_weight(self, ideom_id: str, weight: float) -> 'Prefab':
        """
        Add a weight for an ideom.
        
        Args:
            ideom_id: The ID of the ideom.
            weight: The weight for the ideom.
            
        Returns:
            A new Prefab instance with the added weight.
        """
        new_weights = deepcopy(self.ideom_weights)
        new_weights[ideom_id] = weight
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=new_weights,
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            response_template=self.response_template,
            tags=self.tags.copy()
        )
    
    def update_ideom_weight(self, ideom_id: str, weight: float) -> 'Prefab':
        """
        Update the weight for an ideom.
        
        Args:
            ideom_id: The ID of the ideom.
            weight: The new weight for the ideom.
            
        Returns:
            A new Prefab instance with the updated weight.
        """
        if ideom_id not in self.ideom_weights:
            return self.add_ideom_weight(ideom_id, weight)
        
        new_weights = deepcopy(self.ideom_weights)
        new_weights[ideom_id] = weight
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=new_weights,
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            response_template=self.response_template,
            tags=self.tags.copy()
        )
    
    def remove_ideom_weight(self, ideom_id: str) -> 'Prefab':
        """
        Remove the weight for an ideom.
        
        Args:
            ideom_id: The ID of the ideom.
            
        Returns:
            A new Prefab instance with the removed weight.
        """
        if ideom_id not in self.ideom_weights:
            return self
        
        new_weights = deepcopy(self.ideom_weights)
        del new_weights[ideom_id]
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=new_weights,
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            response_template=self.response_template,
            tags=self.tags.copy()
        )
    
    def set_response_template(self, template: str) -> 'Prefab':
        """
        Set the response template.
        
        Args:
            template: The response template.
            
        Returns:
            A new Prefab instance with the updated response template.
        """
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=deepcopy(self.ideom_weights),
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            response_template=template,
            tags=self.tags.copy()
        )
    
    def add_tag(self, tag: str) -> 'Prefab':
        """
        Add a tag to the prefab.
        
        Args:
            tag: The tag to add.
            
        Returns:
            A new Prefab instance with the added tag.
        """
        if tag in self.tags:
            return self
        
        new_tags = self.tags.copy()
        new_tags.append(tag)
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=deepcopy(self.ideom_weights),
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            response_template=self.response_template,
            tags=new_tags
        )
    
    def remove_tag(self, tag: str) -> 'Prefab':
        """
        Remove a tag from the prefab.
        
        Args:
            tag: The tag to remove.
            
        Returns:
            A new Prefab instance with the removed tag.
        """
        if tag not in self.tags:
            return self
        
        new_tags = self.tags.copy()
        new_tags.remove(tag)
        return Prefab(
            id=self.id,
            name=self.name,
            ideom_weights=deepcopy(self.ideom_weights),
            activation_level=self.activation_level,
            activation_threshold=self.activation_threshold,
            response_template=self.response_template,
            tags=new_tags
        )
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if the prefab has a specific tag.
        
        Args:
            tag: The tag to check for.
            
        Returns:
            True if the prefab has the tag, False otherwise.
        """
        return tag in self.tags
    
    def get_activation_score(self, activation_pattern: ActivationPattern) -> float:
        """
        Calculate the activation score for this prefab based on the given activation pattern.
        
        This method calculates how well the activation pattern matches the prefab's
        ideom weights, without updating the prefab's activation level.
        
        Args:
            activation_pattern: The activation pattern to match against.
            
        Returns:
            The activation score, between 0.0 and 1.0.
        """
        # Calculate the weighted sum of ideom activations
        weighted_sum = 0.0
        total_weight = 0.0
        
        for ideom_id, weight in self.ideom_weights.items():
            activation = activation_pattern.get_activation_level(ideom_id)
            weighted_sum += activation * weight
            total_weight += weight
        
        # Normalize by the total weight
        if total_weight > 0:
            return weighted_sum / total_weight
        else:
            return 0.0