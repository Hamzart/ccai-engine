"""
PropertyValue module for the Knowledge Graph.

This module defines the PropertyValue class, which represents a property value
with uncertainty in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from copy import deepcopy


@dataclass(frozen=True)
class PropertyValue:
    """
    A property value with uncertainty.
    
    The PropertyValue class represents a property value with uncertainty,
    including a confidence score, sources, and a timestamp.
    
    Attributes:
        value: The value of the property.
        confidence: A confidence score for the value (0.0 to 1.0).
        sources: A list of sources that provided the value.
        last_updated: A timestamp indicating when the value was last updated.
    """
    
    value: str
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update(self, value: str, confidence: float, source: str) -> 'PropertyValue':
        """
        Update the property value.
        
        Args:
            value: The new value.
            confidence: The new confidence score.
            source: The source of the update.
            
        Returns:
            A new PropertyValue instance with the updated values.
        """
        new_sources = deepcopy(self.sources)
        
        if source not in new_sources:
            new_sources.append(source)
        
        return PropertyValue(
            value=value,
            confidence=confidence,
            sources=new_sources,
            last_updated=datetime.now()
        )
    
    def get_value(self) -> str:
        """
        Get the value.
        
        Returns:
            The value of the property.
        """
        return self.value
    
    def get_confidence(self) -> float:
        """
        Get the confidence score.
        
        Returns:
            The confidence score for the value.
        """
        return self.confidence
    
    def get_sources(self) -> List[str]:
        """
        Get the sources.
        
        Returns:
            A list of sources that provided the value.
        """
        return self.sources.copy()
    
    def get_last_updated(self) -> datetime:
        """
        Get the last updated timestamp.
        
        Returns:
            A timestamp indicating when the value was last updated.
        """
        return self.last_updated
    
    def add_source(self, source: str) -> 'PropertyValue':
        """
        Add a source.
        
        Args:
            source: The source to add.
            
        Returns:
            A new PropertyValue instance with the added source.
        """
        if source in self.sources:
            return self
        
        new_sources = deepcopy(self.sources)
        new_sources.append(source)
        
        return PropertyValue(
            value=self.value,
            confidence=self.confidence,
            sources=new_sources,
            last_updated=self.last_updated
        )
    
    def merge(self, other: 'PropertyValue') -> 'PropertyValue':
        """
        Merge with another property value.
        
        This method merges this property value with another one,
        taking the value with the higher confidence score and
        combining the sources.
        
        Args:
            other: The other property value to merge with.
            
        Returns:
            A new PropertyValue instance with the merged values.
        """
        # Use the value with the higher confidence score
        if self.confidence >= other.confidence:
            value = self.value
            confidence = self.confidence
        else:
            value = other.value
            confidence = other.confidence
        
        # Combine the sources
        new_sources = list(set(self.sources + other.sources))
        
        # Use the more recent timestamp
        last_updated = max(self.last_updated, other.last_updated)
        
        return PropertyValue(
            value=value,
            confidence=confidence,
            sources=new_sources,
            last_updated=last_updated
        )
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the property value.
        """
        return {
            "value": self.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PropertyValue':
        """
        Create a PropertyValue instance from a dictionary.
        
        Args:
            data: A dictionary representation of a property value.
            
        Returns:
            A new PropertyValue instance.
        """
        return cls(
            value=data["value"],
            confidence=data["confidence"],
            sources=data["sources"],
            last_updated=datetime.fromisoformat(data["last_updated"])
        )