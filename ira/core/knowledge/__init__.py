"""
Knowledge Graph package for the IRA architecture.

This package contains the classes for the knowledge graph component
of the IRA (Ideom Resolver AI) architecture.
"""

from .property_value import PropertyValue
from .relation import Relation
from .concept_node import ConceptNode
from .uncertainty_handler import UncertaintyHandler
from .semantic_similarity import SemanticSimilarity
from .self_organizing_structure import SelfOrganizingStructure
from .knowledge_graph import KnowledgeGraph

__all__ = [
    'PropertyValue',
    'Relation',
    'ConceptNode',
    'UncertaintyHandler',
    'SemanticSimilarity',
    'SelfOrganizingStructure',
    'KnowledgeGraph',
]