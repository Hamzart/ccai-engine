# Knowledge Graph Component

The Knowledge Graph component is a core part of the IRA (Ideom Resolver AI) architecture, responsible for representing, organizing, and reasoning with knowledge.

## Overview

The Knowledge Graph component provides a flexible, dynamic, and self-organizing knowledge representation system that can handle uncertainty, ambiguity, and continuous learning. It is designed to be the foundation for the IRA's understanding of the world and its ability to reason about concepts and their relationships.

## Features

- **Flexible Knowledge Representation**: Represents concepts, properties, and relations with support for uncertainty and confidence scores.
- **Dynamic Self-Organization**: Automatically organizes and reorganizes knowledge based on semantic similarity and learning.
- **Uncertainty Handling**: Manages and reasons with uncertain knowledge, combining evidence and resolving conflicts.
- **Semantic Similarity**: Calculates semantic similarity between concepts, properties, and values.
- **Concept Clustering**: Groups related concepts into clusters for efficient retrieval and reasoning.
- **Path Finding**: Finds paths between concepts through their relations.
- **Persistence**: Saves and loads the knowledge graph to/from files.

## Components

The Knowledge Graph component consists of the following classes:

- **PropertyValue**: Represents a property value with a confidence score.
- **Relation**: Represents a relation between two concepts.
- **ConceptNode**: Represents a concept in the knowledge graph.
- **UncertaintyHandler**: Manages and reasons with uncertain knowledge.
- **SemanticSimilarity**: Calculates semantic similarity between concepts, properties, and values.
- **SelfOrganizingStructure**: Dynamically organizes and reorganizes the knowledge graph.
- **KnowledgeGraph**: The main class that integrates all the other classes and provides a unified interface.

## Usage

Here's a simple example of how to use the Knowledge Graph component:

```python
from ira.core.knowledge import KnowledgeGraph, PropertyValue

# Create a knowledge graph
kg = KnowledgeGraph()

# Add some concepts
cat = kg.add_concept(
    name="Cat",
    properties={
        "color": "various",
        "legs": "4",
        "sound": "meow"
    },
    aliases=["feline", "kitty"],
    categories=["mammal", "pet"]
)

dog = kg.add_concept(
    name="Dog",
    properties={
        "color": "various",
        "legs": "4",
        "sound": "bark"
    },
    aliases=["canine", "puppy"],
    categories=["mammal", "pet"]
)

animal = kg.add_concept(
    name="Animal",
    properties={
        "alive": "yes",
        "kingdom": "Animalia"
    },
    categories=["living_thing"]
)

# Add some relations
cat_is_animal = kg.add_relation(
    source_id=cat.get_id(),
    target_id=animal.get_id(),
    relation_type="is_a",
    bidirectional=False
)

dog_is_animal = kg.add_relation(
    source_id=dog.get_id(),
    target_id=animal.get_id(),
    relation_type="is_a",
    bidirectional=False
)

# Get concepts by category
pets = kg.get_concepts_by_category("pet")
print(f"Pets: {[pet.get_name() for pet in pets]}")

# Find similar concepts
similar_to_cat = kg.find_similar_concepts("Cat", threshold=0.3)
print(f"Similar to Cat: {[(concept.get_name(), score) for concept, score in similar_to_cat]}")

# Find path between concepts
paths = kg.find_path_between_concepts(cat.get_id(), animal.get_id())
print(f"Path from Cat to Animal: {paths}")

# Save the knowledge graph
kg.save_to_file("knowledge_graph.json")

# Load the knowledge graph
loaded_kg = KnowledgeGraph.load_from_file("knowledge_graph.json")
```

## Integration with IRA

The Knowledge Graph component is designed to integrate with the other components of the IRA architecture:

- It provides knowledge to the Unified Reasoning Core for reasoning and learning.
- It receives updates from the Unified Reasoning Core based on learning and experience.
- It provides information to the Conversation Manager for generating responses.
- It receives updates from the Conversation Manager based on user interactions.

## Future Enhancements

- **Distributed Knowledge Graph**: Support for distributed knowledge representation across multiple nodes.
- **Knowledge Extraction**: Automatic extraction of knowledge from text and other sources.
- **Ontology Integration**: Integration with existing ontologies and knowledge bases.
- **Reasoning Enhancements**: More advanced reasoning capabilities, including inductive and abductive reasoning.
- **Visualization**: Tools for visualizing the knowledge graph and its structure.