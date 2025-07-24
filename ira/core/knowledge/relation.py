"""
Relation module for the Knowledge Graph.

This module defines the Relation class, which represents a relationship between
two concepts with uncertainty in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from copy import deepcopy


@dataclass(frozen=True)
class Relation:
    """
    A relationship between two concepts with uncertainty.
    
    The Relation class represents a relationship between two concepts with uncertainty,
    including a confidence score, sources, and a timestamp.
    
    Attributes:
        id: A unique identifier for the relation.
        type: The type of the relation.
        source_concept_id: The ID of the source concept.
        target_concept_id: The ID of the target concept.
        confidence: A confidence score for the relation (0.0 to 1.0).
        properties: Optional properties of the relation.
        sources: A list of sources that provided the relation.
        last_updated: A timestamp indicating when the relation was last updated.
        bidirectional: Whether the relation is bidirectional (applies in both directions).
    """
    
    id: str
    type: str
    source_concept_id: str
    target_concept_id: str
    confidence: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    bidirectional: bool = False
    
    def update(self, confidence: float, source: str) -> 'Relation':
        """
        Update the relation.
        
        Args:
            confidence: The new confidence score.
            source: The source of the update.
            
        Returns:
            A new Relation instance with the updated values.
        """
        new_sources = deepcopy(self.sources)
        
        if source not in new_sources:
            new_sources.append(source)
        
        return Relation(
            id=self.id,
            type=self.type,
            source_concept_id=self.source_concept_id,
            target_concept_id=self.target_concept_id,
            confidence=confidence,
            properties=deepcopy(self.properties),
            sources=new_sources,
            last_updated=datetime.now(),
            bidirectional=self.bidirectional
        )
    
    def get_id(self) -> str:
        """
        Get the ID.
        
        Returns:
            The unique identifier for the relation.
        """
        return self.id
    
    def get_type(self) -> str:
        """
        Get the type.
        
        Returns:
            The type of the relation.
        """
        return self.type
    
    def get_source_concept_id(self) -> str:
        """
        Get the source concept ID.
        
        Returns:
            The ID of the source concept.
        """
        return self.source_concept_id
    
    def get_target_concept_id(self) -> str:
        """
        Get the target concept ID.
        
        Returns:
            The ID of the target concept.
        """
        return self.target_concept_id
    
    def get_confidence(self) -> float:
        """
        Get the confidence score.
        
        Returns:
            The confidence score for the relation.
        """
        return self.confidence
    
    def get_properties(self) -> Dict[str, Any]:
        """
        Get the properties.
        
        Returns:
            The properties of the relation.
        """
        return deepcopy(self.properties)
    
    def get_property(self, name: str) -> Optional[Any]:
        """
        Get a property value.
        
        Args:
            name: The name of the property.
            
        Returns:
            The value of the property, or None if the property doesn't exist.
        """
        return self.properties.get(name)
    
    def set_property(self, name: str, value: Any) -> 'Relation':
        """
        Set a property value.
        
        Args:
            name: The name of the property.
            value: The value of the property.
            
        Returns:
            A new Relation instance with the updated property.
        """
        new_properties = deepcopy(self.properties)
        new_properties[name] = value
        
        return Relation(
            id=self.id,
            type=self.type,
            source_concept_id=self.source_concept_id,
            target_concept_id=self.target_concept_id,
            confidence=self.confidence,
            properties=new_properties,
            sources=self.sources,
            last_updated=self.last_updated,
            bidirectional=self.bidirectional
        )
    
    def remove_property(self, name: str) -> 'Relation':
        """
        Remove a property.
        
        Args:
            name: The name of the property to remove.
            
        Returns:
            A new Relation instance with the property removed.
        """
        if name not in self.properties:
            return self
        
        new_properties = deepcopy(self.properties)
        del new_properties[name]
        
        return Relation(
            id=self.id,
            type=self.type,
            source_concept_id=self.source_concept_id,
            target_concept_id=self.target_concept_id,
            confidence=self.confidence,
            properties=new_properties,
            sources=self.sources,
            last_updated=self.last_updated,
            bidirectional=self.bidirectional
        )
    
    def get_sources(self) -> List[str]:
        """
        Get the sources.
        
        Returns:
            A list of sources that provided the relation.
        """
        return self.sources.copy()
    
    def add_source(self, source: str) -> 'Relation':
        """
        Add a source.
        
        Args:
            source: The source to add.
            
        Returns:
            A new Relation instance with the added source.
        """
        if source in self.sources:
            return self
        
        new_sources = deepcopy(self.sources)
        new_sources.append(source)
        
        return Relation(
            id=self.id,
            type=self.type,
            source_concept_id=self.source_concept_id,
            target_concept_id=self.target_concept_id,
            confidence=self.confidence,
            properties=deepcopy(self.properties),
            sources=new_sources,
            last_updated=self.last_updated,
            bidirectional=self.bidirectional
        )
    
    def get_last_updated(self) -> datetime:
        """
        Get the last updated timestamp.
        
        Returns:
            A timestamp indicating when the relation was last updated.
        """
        return self.last_updated
    
    def is_bidirectional(self) -> bool:
        """
        Check if the relation is bidirectional.
        
        Returns:
            True if the relation is bidirectional, False otherwise.
        """
        return self.bidirectional
    
    def merge(self, other: 'Relation') -> 'Relation':
        """
        Merge with another relation.
        
        This method merges this relation with another one,
        taking the confidence score from the relation with the higher confidence
        and combining the sources and properties.
        
        Args:
            other: The other relation to merge with.
            
        Returns:
            A new Relation instance with the merged values.
        """
        # Ensure the relations are compatible
        if (self.type != other.type or
            self.source_concept_id != other.source_concept_id or
            self.target_concept_id != other.target_concept_id):
            raise ValueError("Cannot merge incompatible relations")
        
        # Use the confidence score from the relation with the higher confidence
        if self.confidence >= other.confidence:
            confidence = self.confidence
        else:
            confidence = other.confidence
        
        # Combine the sources
        new_sources = list(set(self.sources + other.sources))
        
        # Combine the properties
        new_properties = deepcopy(self.properties)
        for name, value in other.properties.items():
            if name not in new_properties:
                new_properties[name] = value
        
        # Use the more recent timestamp
        last_updated = max(self.last_updated, other.last_updated)
        
        return Relation(
            id=self.id,  # Keep the ID of this relation
            type=self.type,
            source_concept_id=self.source_concept_id,
            target_concept_id=self.target_concept_id,
            confidence=confidence,
            properties=new_properties,
            sources=new_sources,
            last_updated=last_updated,
            bidirectional=self.bidirectional or other.bidirectional  # If either is bidirectional, the merged relation is bidirectional
        )
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the relation.
        """
        return {
            "id": self.id,
            "type": self.type,
            "source_concept_id": self.source_concept_id,
            "target_concept_id": self.target_concept_id,
            "confidence": self.confidence,
            "properties": self.properties,
            "sources": self.sources,
            "last_updated": self.last_updated.isoformat(),
            "bidirectional": self.bidirectional
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Relation':
        """
        Create a Relation instance from a dictionary.
        
        Args:
            data: A dictionary representation of a relation.
            
        Returns:
            A new Relation instance.
        """
        return cls(
            id=data["id"],
            type=data["type"],
            source_concept_id=data["source_concept_id"],
            target_concept_id=data["target_concept_id"],
            confidence=data["confidence"],
            properties=data.get("properties", {}),
            sources=data.get("sources", []),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            bidirectional=data.get("bidirectional", False)
        )