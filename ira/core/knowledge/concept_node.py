"""
ConceptNode module for the Knowledge Graph.

This module defines the ConceptNode class, which represents a concept
in the knowledge graph of the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from copy import deepcopy
from .property_value import PropertyValue
from .relation import Relation


@dataclass(frozen=True)
class ConceptNode:
    """
    A concept in the knowledge graph.
    
    The ConceptNode class represents a concept in the knowledge graph,
    with properties and relations to other concepts.
    
    Attributes:
        id: A unique identifier for the concept.
        name: A human-readable name for the concept.
        properties: A dictionary mapping property names to PropertyValue instances.
        relations: A dictionary mapping relation types to lists of Relation instances.
        aliases: A list of alternative names for the concept.
        categories: A list of categories the concept belongs to.
    """
    
    id: str
    name: str
    properties: Dict[str, PropertyValue] = field(default_factory=dict)
    relations: Dict[str, List[Relation]] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    def get_id(self) -> str:
        """
        Get the ID.
        
        Returns:
            The unique identifier for the concept.
        """
        return self.id
    
    def get_name(self) -> str:
        """
        Get the name.
        
        Returns:
            The human-readable name for the concept.
        """
        return self.name
    
    def get_property(self, name: str) -> Optional[PropertyValue]:
        """
        Get a property value.
        
        Args:
            name: The name of the property.
            
        Returns:
            The PropertyValue instance for the property, or None if the property doesn't exist.
        """
        return self.properties.get(name)
    
    def has_property(self, name: str) -> bool:
        """
        Check if the concept has a property.
        
        Args:
            name: The name of the property.
            
        Returns:
            True if the concept has the property, False otherwise.
        """
        return name in self.properties
    
    def get_property_value(self, name: str) -> Optional[str]:
        """
        Get the value of a property.
        
        Args:
            name: The name of the property.
            
        Returns:
            The value of the property, or None if the property doesn't exist.
        """
        property_value = self.get_property(name)
        return property_value.get_value() if property_value else None
    
    def get_property_confidence(self, name: str) -> float:
        """
        Get the confidence score of a property.
        
        Args:
            name: The name of the property.
            
        Returns:
            The confidence score for the property, or 0.0 if the property doesn't exist.
        """
        property_value = self.get_property(name)
        return property_value.get_confidence() if property_value else 0.0
    
    def get_properties(self) -> Dict[str, PropertyValue]:
        """
        Get all properties.
        
        Returns:
            A dictionary mapping property names to PropertyValue instances.
        """
        return deepcopy(self.properties)
    
    def set_property(self, name: str, value: PropertyValue) -> 'ConceptNode':
        """
        Set a property value.
        
        Args:
            name: The name of the property.
            value: The PropertyValue instance for the property.
            
        Returns:
            A new ConceptNode instance with the updated property.
        """
        new_properties = deepcopy(self.properties)
        new_properties[name] = value
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=new_properties,
            relations=deepcopy(self.relations),
            aliases=self.aliases.copy(),
            categories=self.categories.copy()
        )
    
    def remove_property(self, name: str) -> 'ConceptNode':
        """
        Remove a property.
        
        Args:
            name: The name of the property to remove.
            
        Returns:
            A new ConceptNode instance with the property removed.
        """
        if name not in self.properties:
            return self
        
        new_properties = deepcopy(self.properties)
        del new_properties[name]
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=new_properties,
            relations=deepcopy(self.relations),
            aliases=self.aliases.copy(),
            categories=self.categories.copy()
        )
    
    def get_relations(self, type: str) -> List[Relation]:
        """
        Get relations of a specific type.
        
        Args:
            type: The type of relations to get.
            
        Returns:
            A list of Relation instances of the specified type.
        """
        return self.relations.get(type, []).copy()
    
    def get_all_relations(self) -> List[Relation]:
        """
        Get all relations.
        
        Returns:
            A list of all Relation instances.
        """
        all_relations = []
        for relations in self.relations.values():
            all_relations.extend(relations)
        return all_relations
    
    def get_relation_types(self) -> List[str]:
        """
        Get all relation types.
        
        Returns:
            A list of all relation types.
        """
        return list(self.relations.keys())
    
    def add_relation(self, relation: Relation) -> 'ConceptNode':
        """
        Add a relation.
        
        Args:
            relation: The Relation instance to add.
            
        Returns:
            A new ConceptNode instance with the added relation.
        """
        new_relations = deepcopy(self.relations)
        
        if relation.type not in new_relations:
            new_relations[relation.type] = []
        
        # Check if a relation with the same ID already exists
        for i, existing_relation in enumerate(new_relations[relation.type]):
            if existing_relation.id == relation.id:
                # Replace the existing relation
                new_relations[relation.type][i] = relation
                break
        else:
            # Add the new relation
            new_relations[relation.type].append(relation)
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=deepcopy(self.properties),
            relations=new_relations,
            aliases=self.aliases.copy(),
            categories=self.categories.copy()
        )
    
    def remove_relation(self, relation_id: str) -> 'ConceptNode':
        """
        Remove a relation.
        
        Args:
            relation_id: The ID of the relation to remove.
            
        Returns:
            A new ConceptNode instance with the relation removed.
        """
        new_relations = deepcopy(self.relations)
        
        for type, relations in new_relations.items():
            new_relations[type] = [r for r in relations if r.id != relation_id]
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=deepcopy(self.properties),
            relations=new_relations,
            aliases=self.aliases.copy(),
            categories=self.categories.copy()
        )
    
    def get_related_concept_ids(self, type: Optional[str] = None) -> Set[str]:
        """
        Get the IDs of related concepts.
        
        Args:
            type: The type of relations to consider, or None to consider all types.
            
        Returns:
            A set of concept IDs related to this concept.
        """
        related_ids = set()
        
        if type is None:
            # Consider all relation types
            for relations in self.relations.values():
                for relation in relations:
                    if relation.source_concept_id == self.id:
                        related_ids.add(relation.target_concept_id)
                    else:
                        related_ids.add(relation.source_concept_id)
        else:
            # Consider only the specified relation type
            for relation in self.relations.get(type, []):
                if relation.source_concept_id == self.id:
                    related_ids.add(relation.target_concept_id)
                else:
                    related_ids.add(relation.source_concept_id)
        
        return related_ids
    
    def add_alias(self, alias: str) -> 'ConceptNode':
        """
        Add an alias.
        
        Args:
            alias: The alias to add.
            
        Returns:
            A new ConceptNode instance with the added alias.
        """
        if alias in self.aliases:
            return self
        
        new_aliases = self.aliases.copy()
        new_aliases.append(alias)
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=deepcopy(self.properties),
            relations=deepcopy(self.relations),
            aliases=new_aliases,
            categories=self.categories.copy()
        )
    
    def remove_alias(self, alias: str) -> 'ConceptNode':
        """
        Remove an alias.
        
        Args:
            alias: The alias to remove.
            
        Returns:
            A new ConceptNode instance with the alias removed.
        """
        if alias not in self.aliases:
            return self
        
        new_aliases = self.aliases.copy()
        new_aliases.remove(alias)
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=deepcopy(self.properties),
            relations=deepcopy(self.relations),
            aliases=new_aliases,
            categories=self.categories.copy()
        )
    
    def get_aliases(self) -> List[str]:
        """
        Get all aliases.
        
        Returns:
            A list of all aliases for the concept.
        """
        return self.aliases.copy()
    
    def add_category(self, category: str) -> 'ConceptNode':
        """
        Add a category.
        
        Args:
            category: The category to add.
            
        Returns:
            A new ConceptNode instance with the added category.
        """
        if category in self.categories:
            return self
        
        new_categories = self.categories.copy()
        new_categories.append(category)
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=deepcopy(self.properties),
            relations=deepcopy(self.relations),
            aliases=self.aliases.copy(),
            categories=new_categories
        )
    
    def remove_category(self, category: str) -> 'ConceptNode':
        """
        Remove a category.
        
        Args:
            category: The category to remove.
            
        Returns:
            A new ConceptNode instance with the category removed.
        """
        if category not in self.categories:
            return self
        
        new_categories = self.categories.copy()
        new_categories.remove(category)
        
        return ConceptNode(
            id=self.id,
            name=self.name,
            properties=deepcopy(self.properties),
            relations=deepcopy(self.relations),
            aliases=self.aliases.copy(),
            categories=new_categories
        )
    
    def get_categories(self) -> List[str]:
        """
        Get all categories.
        
        Returns:
            A list of all categories for the concept.
        """
        return self.categories.copy()
    
    def merge(self, other: 'ConceptNode') -> 'ConceptNode':
        """
        Merge with another concept.
        
        This method merges this concept with another one,
        combining properties, relations, aliases, and categories.
        
        Args:
            other: The other concept to merge with.
            
        Returns:
            A new ConceptNode instance with the merged values.
        """
        # Merge properties
        new_properties = deepcopy(self.properties)
        for name, value in other.properties.items():
            if name in new_properties:
                new_properties[name] = new_properties[name].merge(value)
            else:
                new_properties[name] = value
        
        # Merge relations
        new_relations = deepcopy(self.relations)
        for type, relations in other.relations.items():
            if type not in new_relations:
                new_relations[type] = []
            
            for relation in relations:
                # Check if a relation with the same ID already exists
                for i, existing_relation in enumerate(new_relations[type]):
                    if existing_relation.id == relation.id:
                        # Merge the relations
                        new_relations[type][i] = existing_relation.merge(relation)
                        break
                else:
                    # Add the new relation
                    new_relations[type].append(relation)
        
        # Merge aliases
        new_aliases = list(set(self.aliases + other.aliases))
        
        # Merge categories
        new_categories = list(set(self.categories + other.categories))
        
        return ConceptNode(
            id=self.id,  # Keep the ID of this concept
            name=self.name,  # Keep the name of this concept
            properties=new_properties,
            relations=new_relations,
            aliases=new_aliases,
            categories=new_categories
        )
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the concept.
        """
        return {
            "id": self.id,
            "name": self.name,
            "properties": {name: value.to_dict() for name, value in self.properties.items()},
            "relations": {type: [relation.to_dict() for relation in relations]
                         for type, relations in self.relations.items()},
            "aliases": self.aliases,
            "categories": self.categories
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConceptNode':
        """
        Create a ConceptNode instance from a dictionary.
        
        Args:
            data: A dictionary representation of a concept.
            
        Returns:
            A new ConceptNode instance.
        """
        properties = {}
        for name, value_data in data.get("properties", {}).items():
            properties[name] = PropertyValue.from_dict(value_data)
        
        relations = {}
        for type, relations_data in data.get("relations", {}).items():
            relations[type] = [Relation.from_dict(relation_data) for relation_data in relations_data]
        
        return cls(
            id=data["id"],
            name=data["name"],
            properties=properties,
            relations=relations,
            aliases=data.get("aliases", []),
            categories=data.get("categories", [])
        )