"""
KnowledgeGraph module for the IRA architecture.

This module defines the KnowledgeGraph class, which is the main class for the
knowledge graph component of the IRA (Ideom Resolver AI) architecture.
"""

from typing import List, Dict, Tuple, Optional, Any, Set, Callable, Union
import uuid
import json
import os
from dataclasses import dataclass, field
from .concept_node import ConceptNode
from .property_value import PropertyValue
from .relation import Relation
from .uncertainty_handler import UncertaintyHandler
from .semantic_similarity import SemanticSimilarity
from .self_organizing_structure import SelfOrganizingStructure


@dataclass
class KnowledgeGraph:
    """
    The main class for the knowledge graph component.
    
    The KnowledgeGraph class integrates all the other classes in the knowledge graph
    component and provides a unified interface for interacting with the knowledge graph.
    
    Attributes:
        uncertainty_handler: The uncertainty handler.
        semantic_similarity: The semantic similarity calculator.
        self_organizing_structure: The self-organizing structure.
        concepts: A dictionary mapping concept IDs to ConceptNode instances.
        concept_name_to_id: A dictionary mapping concept names to concept IDs.
        alias_to_id: A dictionary mapping aliases to concept IDs.
        category_to_ids: A dictionary mapping categories to sets of concept IDs.
        relation_type_to_ids: A dictionary mapping relation types to sets of relation IDs.
        relation_ids: A set of all relation IDs.
    """
    
    uncertainty_handler: UncertaintyHandler = field(default_factory=UncertaintyHandler)
    semantic_similarity: SemanticSimilarity = field(default_factory=lambda: SemanticSimilarity())
    concepts: Dict[str, ConceptNode] = field(default_factory=dict)
    concept_name_to_id: Dict[str, str] = field(default_factory=dict)
    alias_to_id: Dict[str, str] = field(default_factory=dict)
    category_to_ids: Dict[str, Set[str]] = field(default_factory=dict)
    relation_type_to_ids: Dict[str, Set[str]] = field(default_factory=dict)
    relation_ids: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize the self-organizing structure after other attributes are set."""
        self.self_organizing_structure = SelfOrganizingStructure(semantic_similarity=self.semantic_similarity)
    
    def get_concept_by_id(self, concept_id: str) -> Optional[ConceptNode]:
        """
        Get a concept by its ID.
        
        Args:
            concept_id: The ID of the concept.
            
        Returns:
            The ConceptNode instance for the concept, or None if the concept doesn't exist.
        """
        return self.concepts.get(concept_id)
    
    def get_concept_by_name(self, name: str) -> Optional[ConceptNode]:
        """
        Get a concept by its name.
        
        Args:
            name: The name of the concept.
            
        Returns:
            The ConceptNode instance for the concept, or None if the concept doesn't exist.
        """
        concept_id = self.concept_name_to_id.get(name.lower())
        return self.get_concept_by_id(concept_id) if concept_id else None
    
    def get_concept_by_alias(self, alias: str) -> Optional[ConceptNode]:
        """
        Get a concept by one of its aliases.
        
        Args:
            alias: The alias of the concept.
            
        Returns:
            The ConceptNode instance for the concept, or None if no concept has the alias.
        """
        concept_id = self.alias_to_id.get(alias.lower())
        return self.get_concept_by_id(concept_id) if concept_id else None
    
    def get_concepts_by_category(self, category: str) -> List[ConceptNode]:
        """
        Get all concepts in a category.
        
        Args:
            category: The category to get concepts for.
            
        Returns:
            A list of ConceptNode instances for the concepts in the category.
        """
        concept_ids = self.category_to_ids.get(category.lower(), set())
        return [self.concepts[concept_id] for concept_id in concept_ids if concept_id in self.concepts]
    
    def get_relations_by_type(self, relation_type: str) -> List[Relation]:
        """
        Get all relations of a specific type.
        
        Args:
            relation_type: The type of relations to get.
            
        Returns:
            A list of Relation instances of the specified type.
        """
        relation_ids = self.relation_type_to_ids.get(relation_type.lower(), set())
        
        relations = []
        for concept in self.concepts.values():
            for relation in concept.get_relations(relation_type):
                if relation.id in relation_ids:
                    relations.append(relation)
        
        return relations
    
    def get_related_concepts(self, concept_id: str, relation_type: Optional[str] = None) -> List[ConceptNode]:
        """
        Get concepts related to a specific concept.
        
        Args:
            concept_id: The ID of the concept to get related concepts for.
            relation_type: The type of relations to consider, or None to consider all types.
            
        Returns:
            A list of ConceptNode instances related to the specified concept.
        """
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return []
        
        related_ids = concept.get_related_concept_ids(relation_type)
        return [self.concepts[related_id] for related_id in related_ids if related_id in self.concepts]
    
    def find_path_between_concepts(self, source_id: str, target_id: str, max_depth: int = 5) -> List[List[Tuple[str, Relation]]]:
        """
        Find paths between two concepts.
        
        Args:
            source_id: The ID of the source concept.
            target_id: The ID of the target concept.
            max_depth: The maximum path depth to consider.
            
        Returns:
            A list of paths, where each path is a list of tuples containing a relation type and a Relation instance.
        """
        if source_id == target_id:
            return [[]]
        
        if max_depth <= 0:
            return []
        
        source = self.get_concept_by_id(source_id)
        if not source:
            return []
        
        # Perform a breadth-first search
        visited = {source_id}
        queue = [(source_id, [])]
        paths = []
        
        while queue:
            current_id, path = queue.pop(0)
            current = self.get_concept_by_id(current_id)
            
            if not current:
                continue
            
            # Check all relations
            for relation_type in current.get_relation_types():
                for relation in current.get_relations(relation_type):
                    next_id = relation.target_concept_id if relation.source_concept_id == current_id else relation.source_concept_id
                    
                    if next_id == target_id:
                        # Found a path to the target
                        paths.append(path + [(relation_type, relation)])
                    elif next_id not in visited and len(path) < max_depth - 1:
                        # Continue the search
                        visited.add(next_id)
                        queue.append((next_id, path + [(relation_type, relation)]))
        
        return paths
    
    def add_concept(self, name: str, properties: Dict[str, Union[str, PropertyValue]] = None,
                   aliases: List[str] = None, categories: List[str] = None) -> ConceptNode:
        """
        Add a new concept to the knowledge graph.
        
        Args:
            name: The name of the concept.
            properties: A dictionary mapping property names to values or PropertyValue instances.
            aliases: A list of aliases for the concept.
            categories: A list of categories for the concept.
            
        Returns:
            The ConceptNode instance for the new concept.
        """
        # Check if a concept with the same name already exists
        existing = self.get_concept_by_name(name)
        if existing:
            return existing
        
        # Generate a unique ID for the concept
        concept_id = str(uuid.uuid4())
        
        # Convert property values to PropertyValue instances
        property_values = {}
        if properties:
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, PropertyValue):
                    property_values[prop_name] = prop_value
                else:
                    property_values[prop_name] = PropertyValue(value=str(prop_value))
        
        # Create the concept
        concept = ConceptNode(
            id=concept_id,
            name=name,
            properties=property_values,
            aliases=aliases or [],
            categories=categories or []
        )
        
        # Add the concept to the knowledge graph
        self.concepts[concept_id] = concept
        self.concept_name_to_id[name.lower()] = concept_id
        
        # Add aliases
        if aliases:
            for alias in aliases:
                self.alias_to_id[alias.lower()] = concept_id
        
        # Add categories
        if categories:
            for category in categories:
                category_lower = category.lower()
                if category_lower not in self.category_to_ids:
                    self.category_to_ids[category_lower] = set()
                self.category_to_ids[category_lower].add(concept_id)
        
        # Add the concept to the self-organizing structure
        self.self_organizing_structure.add_concept(concept, self.concepts)
        
        return concept
    
    def update_concept(self, concept_id: str, name: Optional[str] = None,
                      properties: Dict[str, Union[str, PropertyValue]] = None,
                      aliases: List[str] = None, categories: List[str] = None) -> Optional[ConceptNode]:
        """
        Update an existing concept in the knowledge graph.
        
        Args:
            concept_id: The ID of the concept to update.
            name: The new name for the concept, or None to keep the current name.
            properties: A dictionary mapping property names to values or PropertyValue instances.
            aliases: A list of aliases for the concept, or None to keep the current aliases.
            categories: A list of categories for the concept, or None to keep the current categories.
            
        Returns:
            The updated ConceptNode instance, or None if the concept doesn't exist.
        """
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return None
        
        # Update the name
        if name and name != concept.name:
            # Remove the old name from the mapping
            if concept.name.lower() in self.concept_name_to_id:
                del self.concept_name_to_id[concept.name.lower()]
            
            # Add the new name to the mapping
            self.concept_name_to_id[name.lower()] = concept_id
            
            # Create a new concept with the updated name
            concept = ConceptNode(
                id=concept.id,
                name=name,
                properties=concept.properties,
                relations=concept.relations,
                aliases=concept.aliases,
                categories=concept.categories
            )
        
        # Update properties
        if properties:
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, PropertyValue):
                    concept = concept.set_property(prop_name, prop_value)
                else:
                    concept = concept.set_property(prop_name, PropertyValue(value=str(prop_value)))
        
        # Update aliases
        if aliases is not None:
            # Remove old aliases
            for alias in concept.aliases:
                if alias.lower() in self.alias_to_id and self.alias_to_id[alias.lower()] == concept_id:
                    del self.alias_to_id[alias.lower()]
            
            # Add new aliases
            for alias in aliases:
                self.alias_to_id[alias.lower()] = concept_id
            
            # Create a new concept with the updated aliases
            concept = ConceptNode(
                id=concept.id,
                name=concept.name,
                properties=concept.properties,
                relations=concept.relations,
                aliases=aliases,
                categories=concept.categories
            )
        
        # Update categories
        if categories is not None:
            # Remove old categories
            for category in concept.categories:
                category_lower = category.lower()
                if category_lower in self.category_to_ids and concept_id in self.category_to_ids[category_lower]:
                    self.category_to_ids[category_lower].remove(concept_id)
            
            # Add new categories
            for category in categories:
                category_lower = category.lower()
                if category_lower not in self.category_to_ids:
                    self.category_to_ids[category_lower] = set()
                self.category_to_ids[category_lower].add(concept_id)
            
            # Create a new concept with the updated categories
            concept = ConceptNode(
                id=concept.id,
                name=concept.name,
                properties=concept.properties,
                relations=concept.relations,
                aliases=concept.aliases,
                categories=categories
            )
        
        # Update the concept in the knowledge graph
        self.concepts[concept_id] = concept
        
        # Update the concept in the self-organizing structure
        self.self_organizing_structure.update_concept(concept, self.concepts)
        
        return concept
    
    def remove_concept(self, concept_id: str) -> bool:
        """
        Remove a concept from the knowledge graph.
        
        Args:
            concept_id: The ID of the concept to remove.
            
        Returns:
            True if the concept was removed, False if it didn't exist.
        """
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return False
        
        # Remove the concept from the name mapping
        if concept.name.lower() in self.concept_name_to_id:
            del self.concept_name_to_id[concept.name.lower()]
        
        # Remove aliases
        for alias in concept.aliases:
            if alias.lower() in self.alias_to_id and self.alias_to_id[alias.lower()] == concept_id:
                del self.alias_to_id[alias.lower()]
        
        # Remove categories
        for category in concept.categories:
            category_lower = category.lower()
            if category_lower in self.category_to_ids and concept_id in self.category_to_ids[category_lower]:
                self.category_to_ids[category_lower].remove(concept_id)
        
        # Remove relations
        for relation in concept.get_all_relations():
            self.remove_relation(relation.id)
        
        # Remove the concept from the self-organizing structure
        self.self_organizing_structure.remove_concept(concept_id)
        
        # Remove the concept from the knowledge graph
        del self.concepts[concept_id]
        
        return True
    
    def add_relation(self, source_id: str, target_id: str, relation_type: str,
                    properties: Dict[str, Union[str, PropertyValue]] = None,
                    bidirectional: bool = False) -> Optional[Relation]:
        """
        Add a relation between two concepts.
        
        Args:
            source_id: The ID of the source concept.
            target_id: The ID of the target concept.
            relation_type: The type of the relation.
            properties: A dictionary mapping property names to values or PropertyValue instances.
            bidirectional: Whether the relation is bidirectional.
            
        Returns:
            The Relation instance for the new relation, or None if either concept doesn't exist.
        """
        source = self.get_concept_by_id(source_id)
        target = self.get_concept_by_id(target_id)
        
        if not source or not target:
            return None
        
        # Generate a unique ID for the relation
        relation_id = str(uuid.uuid4())
        
        # Convert property values to PropertyValue instances
        property_values = {}
        if properties:
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, PropertyValue):
                    property_values[prop_name] = prop_value
                else:
                    property_values[prop_name] = PropertyValue(value=str(prop_value))
        
        # Create the relation
        relation = Relation(
            id=relation_id,
            type=relation_type,
            source_concept_id=source_id,
            target_concept_id=target_id,
            properties=property_values,
            bidirectional=bidirectional
        )
        
        # Add the relation to the source concept
        self.concepts[source_id] = source.add_relation(relation)
        
        # If the relation is bidirectional, add it to the target concept as well
        if bidirectional:
            self.concepts[target_id] = target.add_relation(relation)
        
        # Add the relation to the type mapping
        relation_type_lower = relation_type.lower()
        if relation_type_lower not in self.relation_type_to_ids:
            self.relation_type_to_ids[relation_type_lower] = set()
        self.relation_type_to_ids[relation_type_lower].add(relation_id)
        
        # Add the relation to the set of all relation IDs
        self.relation_ids.add(relation_id)
        
        return relation
    
    def update_relation(self, relation_id: str, relation_type: Optional[str] = None,
                       properties: Dict[str, Union[str, PropertyValue]] = None,
                       bidirectional: Optional[bool] = None) -> Optional[Relation]:
        """
        Update an existing relation in the knowledge graph.
        
        Args:
            relation_id: The ID of the relation to update.
            relation_type: The new type for the relation, or None to keep the current type.
            properties: A dictionary mapping property names to values or PropertyValue instances.
            bidirectional: Whether the relation is bidirectional, or None to keep the current value.
            
        Returns:
            The updated Relation instance, or None if the relation doesn't exist.
        """
        # Find the relation
        relation = None
        source_concept = None
        
        for concept in self.concepts.values():
            for rel_type in concept.get_relation_types():
                for rel in concept.get_relations(rel_type):
                    if rel.id == relation_id:
                        relation = rel
                        source_concept = concept
                        break
                if relation:
                    break
            if relation:
                break
        
        if not relation or not source_concept:
            return None
        
        # Update the relation type
        if relation_type and relation_type != relation.type:
            # Remove the relation from the old type mapping
            old_type_lower = relation.type.lower()
            if old_type_lower in self.relation_type_to_ids and relation_id in self.relation_type_to_ids[old_type_lower]:
                self.relation_type_to_ids[old_type_lower].remove(relation_id)
            
            # Add the relation to the new type mapping
            new_type_lower = relation_type.lower()
            if new_type_lower not in self.relation_type_to_ids:
                self.relation_type_to_ids[new_type_lower] = set()
            self.relation_type_to_ids[new_type_lower].add(relation_id)
            
            # Create a new relation with the updated type
            relation = Relation(
                id=relation.id,
                type=relation_type,
                source_concept_id=relation.source_concept_id,
                target_concept_id=relation.target_concept_id,
                properties=relation.properties,
                bidirectional=relation.bidirectional
            )
        
        # Update properties
        if properties:
            new_properties = dict(relation.properties)
            
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value, PropertyValue):
                    new_properties[prop_name] = prop_value
                else:
                    new_properties[prop_name] = PropertyValue(value=str(prop_value))
            
            # Create a new relation with the updated properties
            relation = Relation(
                id=relation.id,
                type=relation.type,
                source_concept_id=relation.source_concept_id,
                target_concept_id=relation.target_concept_id,
                properties=new_properties,
                bidirectional=relation.bidirectional
            )
        
        # Update bidirectionality
        if bidirectional is not None and bidirectional != relation.bidirectional:
            # Create a new relation with the updated bidirectionality
            relation = Relation(
                id=relation.id,
                type=relation.type,
                source_concept_id=relation.source_concept_id,
                target_concept_id=relation.target_concept_id,
                properties=relation.properties,
                bidirectional=bidirectional
            )
            
            # Update the target concept if necessary
            target_concept = self.get_concept_by_id(relation.target_concept_id)
            if target_concept:
                if bidirectional:
                    # Add the relation to the target concept
                    self.concepts[relation.target_concept_id] = target_concept.add_relation(relation)
                else:
                    # Remove the relation from the target concept
                    self.concepts[relation.target_concept_id] = target_concept.remove_relation(relation_id)
        
        # Update the source concept
        self.concepts[source_concept.id] = source_concept.add_relation(relation)
        
        return relation
    
    def remove_relation(self, relation_id: str) -> bool:
        """
        Remove a relation from the knowledge graph.
        
        Args:
            relation_id: The ID of the relation to remove.
            
        Returns:
            True if the relation was removed, False if it didn't exist.
        """
        # Find the relation
        relation = None
        source_concept = None
        
        for concept in self.concepts.values():
            for rel_type in concept.get_relation_types():
                for rel in concept.get_relations(rel_type):
                    if rel.id == relation_id:
                        relation = rel
                        source_concept = concept
                        break
                if relation:
                    break
            if relation:
                break
        
        if not relation or not source_concept:
            return False
        
        # Remove the relation from the source concept
        self.concepts[source_concept.id] = source_concept.remove_relation(relation_id)
        
        # If the relation is bidirectional, remove it from the target concept as well
        if relation.bidirectional:
            target_concept = self.get_concept_by_id(relation.target_concept_id)
            if target_concept:
                self.concepts[relation.target_concept_id] = target_concept.remove_relation(relation_id)
        
        # Remove the relation from the type mapping
        relation_type_lower = relation.type.lower()
        if relation_type_lower in self.relation_type_to_ids and relation_id in self.relation_type_to_ids[relation_type_lower]:
            self.relation_type_to_ids[relation_type_lower].remove(relation_id)
        
        # Remove the relation from the set of all relation IDs
        if relation_id in self.relation_ids:
            self.relation_ids.remove(relation_id)
        
        return True
    
    def find_similar_concepts(self, concept_or_name: Union[ConceptNode, str],
                             threshold: float = 0.7, limit: int = 10) -> List[Tuple[ConceptNode, float]]:
        """
        Find concepts similar to a given concept or name.
        
        Args:
            concept_or_name: The concept or name to find similar concepts for.
            threshold: The minimum similarity score required.
            limit: The maximum number of similar concepts to return.
            
        Returns:
            A list of tuples, where each tuple contains a similar concept and its similarity score.
        """
        if isinstance(concept_or_name, str):
            concept = self.get_concept_by_name(concept_or_name)
            if not concept:
                # If the concept doesn't exist, find similar concepts by name
                return self.semantic_similarity.find_similar_by_text(
                    concept_or_name, list(self.concepts.values()), threshold, limit
                )
        else:
            concept = concept_or_name
        
        return self.semantic_similarity.find_similar_concepts(
            concept, list(self.concepts.values()), threshold, limit
        )
    
    def reorganize(self) -> int:
        """
        Reorganize the knowledge graph.
        
        This method reorganizes the knowledge graph by merging similar clusters
        and splitting large clusters.
        
        Returns:
            The number of changes made during reorganization.
        """
        return self.self_organizing_structure.reorganize(self.concepts)
    
    def get_concept_count(self) -> int:
        """
        Get the number of concepts in the knowledge graph.
        
        Returns:
            The number of concepts in the knowledge graph.
        """
        return len(self.concepts)
    
    def get_relation_count(self) -> int:
        """
        Get the number of relations in the knowledge graph.
        
        Returns:
            The number of relations in the knowledge graph.
        """
        return len(self.relation_ids)
    
    def get_category_count(self) -> int:
        """
        Get the number of categories in the knowledge graph.
        
        Returns:
            The number of categories in the knowledge graph.
        """
        return len(self.category_to_ids)
    
    def get_all_concepts(self) -> List[ConceptNode]:
        """
        Get all concepts in the knowledge graph.
        
        Returns:
            A list of all ConceptNode instances in the knowledge graph.
        """
        return list(self.concepts.values())
    
    def get_all_categories(self) -> List[str]:
        """
        Get all categories in the knowledge graph.
        
        Returns:
            A list of all categories in the knowledge graph.
        """
        return list(self.category_to_ids.keys())
    
    def get_all_relation_types(self) -> List[str]:
        """
        Get all relation types in the knowledge graph.
        
        Returns:
            A list of all relation types in the knowledge graph.
        """
        return list(self.relation_type_to_ids.keys())
    
    def clear(self) -> None:
        """
        Clear the knowledge graph.
        
        This method removes all concepts and relations from the knowledge graph.
        """
        self.concepts.clear()
        self.concept_name_to_id.clear()
        self.alias_to_id.clear()
        self.category_to_ids.clear()
        self.relation_type_to_ids.clear()
        self.relation_ids.clear()
        
        # Reinitialize the self-organizing structure
        self.self_organizing_structure = SelfOrganizingStructure(semantic_similarity=self.semantic_similarity)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save the knowledge graph to a file.
        
        Args:
            file_path: The path to the file to save to.
            
        Returns:
            True if the knowledge graph was saved successfully, False otherwise.
        """
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Convert the knowledge graph to a dictionary
            data = self.to_dict()
            
            # Save the dictionary to a JSON file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving knowledge graph to file: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['KnowledgeGraph']:
        """
        Load a knowledge graph from a file.
        
        Args:
            file_path: The path to the file to load from.
            
        Returns:
            A new KnowledgeGraph instance, or None if the file couldn't be loaded.
        """
        try:
            # Load the dictionary from a JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Create a new knowledge graph from the dictionary
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading knowledge graph from file: {e}")
            return None
    
    def to_dict(self) -> dict:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the knowledge graph.
        """
        return {
            "uncertainty_handler": self.uncertainty_handler.to_dict(),
            "semantic_similarity": self.semantic_similarity.to_dict(),
            "self_organizing_structure": self.self_organizing_structure.to_dict(),
            "concepts": {concept_id: concept.to_dict() for concept_id, concept in self.concepts.items()},
            "concept_name_to_id": self.concept_name_to_id,
            "alias_to_id": self.alias_to_id,
            "category_to_ids": {category: list(concept_ids) for category, concept_ids in self.category_to_ids.items()},
            "relation_type_to_ids": {rel_type: list(relation_ids) for rel_type, relation_ids in self.relation_type_to_ids.items()},
            "relation_ids": list(self.relation_ids)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'KnowledgeGraph':
        """
        Create a KnowledgeGraph instance from a dictionary.
        
        Args:
            data: A dictionary representation of a knowledge graph.
            
        Returns:
            A new KnowledgeGraph instance.
        """
        # Create the uncertainty handler
        uncertainty_handler = UncertaintyHandler.from_dict(data.get("uncertainty_handler", {}))
        
        # Create the semantic similarity calculator
        semantic_similarity = SemanticSimilarity.from_dict(data.get("semantic_similarity", {}))
        
        # Create the knowledge graph
        kg = cls(
            uncertainty_handler=uncertainty_handler,
            semantic_similarity=semantic_similarity
        )
        
        # Load the concepts
        concepts_data = data.get("concepts", {})
        for concept_id, concept_data in concepts_data.items():
            kg.concepts[concept_id] = ConceptNode.from_dict(concept_data)
        
        # Load the mappings
        kg.concept_name_to_id = data.get("concept_name_to_id", {})
        kg.alias_to_id = data.get("alias_to_id", {})
        
        # Load the category mapping
        category_to_ids_data = data.get("category_to_ids", {})
        for category, concept_ids in category_to_ids_data.items():
            kg.category_to_ids[category] = set(concept_ids)
        
        # Load the relation type mapping
        relation_type_to_ids_data = data.get("relation_type_to_ids", {})
        for relation_type, relation_ids in relation_type_to_ids_data.items():
            kg.relation_type_to_ids[relation_type] = set(relation_ids)
        
        # Load the relation IDs
        kg.relation_ids = set(data.get("relation_ids", []))
        
        # Load the self-organizing structure
        self_organizing_structure_data = data.get("self_organizing_structure", {})
        kg.self_organizing_structure = SelfOrganizingStructure.from_dict(
            self_organizing_structure_data, semantic_similarity
        )
        
        return kg