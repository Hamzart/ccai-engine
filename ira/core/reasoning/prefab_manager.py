"""
PrefabManager module for the Unified Reasoning Core.

This module defines the PrefabManager class, which manages a collection of prefabs
and provides methods for finding matching prefabs based on activation patterns.
"""

import uuid
from typing import Dict, List, Optional, Set
from .prefab import Prefab
from .activation_pattern import ActivationPattern


class PrefabManager:
    """
    A manager for prefabs in the Unified Reasoning Core.
    
    The PrefabManager manages a collection of prefabs and provides methods for
    finding matching prefabs based on activation patterns.
    
    Attributes:
        prefabs: A dictionary mapping prefab IDs to Prefab instances.
        activation_threshold: The threshold for considering a prefab activated.
    """
    
    def __init__(self, activation_threshold: float = 0.5):
        """
        Initialize a prefab manager.
        
        Args:
            activation_threshold: The threshold for considering a prefab activated.
        """
        self.prefabs: Dict[str, Prefab] = {}
        self.activation_threshold = activation_threshold
    
    def add_prefab(self, prefab: Prefab) -> None:
        """
        Add a prefab to the manager.
        
        Args:
            prefab: The Prefab instance to add.
        """
        self.prefabs[prefab.id] = prefab
    
    def remove_prefab(self, prefab_id: str) -> None:
        """
        Remove a prefab from the manager.
        
        Args:
            prefab_id: The ID of the prefab to remove.
        """
        if prefab_id in self.prefabs:
            del self.prefabs[prefab_id]
    
    def get_prefab(self, prefab_id: str) -> Optional[Prefab]:
        """
        Get a prefab by ID.
        
        Args:
            prefab_id: The ID of the prefab to retrieve.
            
        Returns:
            The Prefab instance with the given ID, or None if not found.
        """
        return self.prefabs.get(prefab_id)
    
    def get_all_prefabs(self) -> List[Prefab]:
        """
        Get all prefabs.
        
        Returns:
            A list of all Prefab instances.
        """
        return list(self.prefabs.values())
    
    def find_matching_prefabs(
        self,
        activation_pattern: ActivationPattern,
        threshold: Optional[float] = None
    ) -> List[Prefab]:
        """
        Find prefabs that match the given activation pattern.
        
        Args:
            activation_pattern: The activation pattern to match against.
            threshold: The activation threshold to use, or None to use the manager's threshold.
            
        Returns:
            A list of Prefab instances that match the activation pattern, sorted by activation level.
        """
        if threshold is None:
            threshold = self.activation_threshold
        
        matching_prefabs = []
        
        for prefab_id, prefab in self.prefabs.items():
            # Activate the prefab with the activation pattern
            activated_prefab = prefab.activate(activation_pattern)
            
            # Check if the prefab is active
            if activated_prefab.activation_level >= threshold:
                matching_prefabs.append(activated_prefab)
                activation_pattern.add_active_prefab(prefab_id)
        
        # Sort by activation level in descending order
        matching_prefabs.sort(key=lambda p: p.activation_level, reverse=True)
        
        return matching_prefabs
    
    def create_prefab_from_pattern(
        self,
        activation_pattern: ActivationPattern,
        name: str,
        threshold: float = 0.3,
        response_template: Optional[str] = None,
        tags: List[str] = None
    ) -> Prefab:
        """
        Create a new prefab from an activation pattern.
        
        Args:
            activation_pattern: The activation pattern to create the prefab from.
            name: The name for the new prefab.
            threshold: The minimum activation level for including an ideom in the prefab.
            response_template: An optional response template for the prefab.
            tags: Optional tags for the prefab.
            
        Returns:
            The newly created Prefab instance.
        """
        # Generate a unique ID for the prefab
        prefab_id = str(uuid.uuid4())
        
        # Extract ideom weights from the activation pattern
        ideom_weights = {}
        for ideom_id, activation in activation_pattern.get_ideom_activations().items():
            if activation >= threshold:
                ideom_weights[ideom_id] = activation
        
        # Create the prefab
        prefab = Prefab(
            id=prefab_id,
            name=name,
            ideom_weights=ideom_weights,
            activation_level=0.0,
            activation_threshold=self.activation_threshold,
            response_template=response_template,
            tags=tags or []
        )
        
        # Add the prefab to the manager
        self.add_prefab(prefab)
        
        return prefab
    
    def get_prefabs_by_tag(self, tag: str) -> List[Prefab]:
        """
        Get all prefabs with a specific tag.
        
        Args:
            tag: The tag to filter by.
            
        Returns:
            A list of Prefab instances with the given tag.
        """
        return [prefab for prefab in self.prefabs.values() if prefab.has_tag(tag)]
    
    def get_prefabs_by_name(self, name: str) -> List[Prefab]:
        """
        Get all prefabs with a specific name.
        
        Args:
            name: The name to filter by.
            
        Returns:
            A list of Prefab instances with the given name.
        """
        return [prefab for prefab in self.prefabs.values() if prefab.name == name]
    
    def update_prefab(self, prefab: Prefab) -> None:
        """
        Update a prefab in the manager.
        
        Args:
            prefab: The updated Prefab instance.
        """
        if prefab.id in self.prefabs:
            self.prefabs[prefab.id] = prefab
    
    def merge_similar_prefabs(self, similarity_threshold: float = 0.8) -> None:
        """
        Merge similar prefabs.
        
        This method identifies prefabs with similar ideom weights and merges them.
        
        Args:
            similarity_threshold: The threshold for considering prefabs similar.
        """
        prefabs = list(self.prefabs.values())
        merged_ids = set()
        
        for i in range(len(prefabs)):
            if prefabs[i].id in merged_ids:
                continue
            
            for j in range(i + 1, len(prefabs)):
                if prefabs[j].id in merged_ids:
                    continue
                
                similarity = self._calculate_prefab_similarity(prefabs[i], prefabs[j])
                
                if similarity >= similarity_threshold:
                    # Merge the prefabs
                    merged_prefab = self._merge_prefabs(prefabs[i], prefabs[j])
                    self.add_prefab(merged_prefab)
                    merged_ids.add(prefabs[i].id)
                    merged_ids.add(prefabs[j].id)
        
        # Remove the merged prefabs
        for prefab_id in merged_ids:
            self.remove_prefab(prefab_id)
    
    def _calculate_prefab_similarity(self, prefab1: Prefab, prefab2: Prefab) -> float:
        """
        Calculate the similarity between two prefabs.
        
        Args:
            prefab1: The first prefab.
            prefab2: The second prefab.
            
        Returns:
            The similarity score, between 0.0 and 1.0.
        """
        # Get the set of ideoms in each prefab
        ideoms1 = set(prefab1.ideom_weights.keys())
        ideoms2 = set(prefab2.ideom_weights.keys())
        
        # Calculate the Jaccard similarity
        intersection = len(ideoms1.intersection(ideoms2))
        union = len(ideoms1.union(ideoms2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _merge_prefabs(self, prefab1: Prefab, prefab2: Prefab) -> Prefab:
        """
        Merge two prefabs.
        
        Args:
            prefab1: The first prefab.
            prefab2: The second prefab.
            
        Returns:
            The merged Prefab instance.
        """
        # Generate a unique ID for the merged prefab
        prefab_id = str(uuid.uuid4())
        
        # Merge the ideom weights
        merged_weights = {}
        
        # Add weights from the first prefab
        for ideom_id, weight in prefab1.ideom_weights.items():
            merged_weights[ideom_id] = weight
        
        # Add or update weights from the second prefab
        for ideom_id, weight in prefab2.ideom_weights.items():
            if ideom_id in merged_weights:
                merged_weights[ideom_id] = (merged_weights[ideom_id] + weight) / 2
            else:
                merged_weights[ideom_id] = weight
        
        # Merge the tags
        merged_tags = list(set(prefab1.tags + prefab2.tags))
        
        # Use the response template from the prefab with the higher activation level
        response_template = None
        if prefab1.activation_level >= prefab2.activation_level:
            response_template = prefab1.response_template
        else:
            response_template = prefab2.response_template
        
        # Create the merged prefab
        return Prefab(
            id=prefab_id,
            name=f"Merged: {prefab1.name} + {prefab2.name}",
            ideom_weights=merged_weights,
            activation_level=0.0,
            activation_threshold=self.activation_threshold,
            response_template=response_template,
            tags=merged_tags
        )