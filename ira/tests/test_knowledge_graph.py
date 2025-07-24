"""
Test script for the Knowledge Graph component.

This script demonstrates the usage of the Knowledge Graph component
and verifies that the implementation works correctly.
"""

import sys
import os
import uuid

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ira.core.knowledge import (
    PropertyValue,
    Relation,
    ConceptNode,
    UncertaintyHandler,
    SemanticSimilarity,
    SelfOrganizingStructure,
    KnowledgeGraph
)


def test_property_value():
    """Test the PropertyValue class."""
    print("\n=== Testing PropertyValue ===")
    
    # Create a property value
    prop1 = PropertyValue(value="red", confidence=0.8)
    print(f"Property value: {prop1.get_value()}, confidence: {prop1.get_confidence()}")
    
    # Create another property value
    prop2 = PropertyValue(value="blue", confidence=0.6)
    print(f"Property value: {prop2.get_value()}, confidence: {prop2.get_confidence()}")
    
    # Merge the property values
    merged = prop1.merge(prop2)
    print(f"Merged value: {merged.get_value()}, confidence: {merged.get_confidence()}")
    
    # Convert to dictionary and back
    prop_dict = prop1.to_dict()
    print(f"Dictionary representation: {prop_dict}")
    prop_from_dict = PropertyValue.from_dict(prop_dict)
    print(f"From dictionary: {prop_from_dict.get_value()}, confidence: {prop_from_dict.get_confidence()}")


def test_relation():
    """Test the Relation class."""
    print("\n=== Testing Relation ===")
    
    # Create a relation
    relation = Relation(
        id=str(uuid.uuid4()),
        type="is_a",
        source_concept_id="cat",
        target_concept_id="animal",
        properties={"confidence": PropertyValue(value="high", confidence=0.9)},
        bidirectional=False
    )
    
    print(f"Relation type: {relation.type}")
    print(f"Source concept ID: {relation.source_concept_id}")
    print(f"Target concept ID: {relation.target_concept_id}")
    print(f"Bidirectional: {relation.bidirectional}")
    print(f"Properties: {relation.properties}")
    
    # Convert to dictionary and back
    relation_dict = relation.to_dict()
    print(f"Dictionary representation: {relation_dict}")
    relation_from_dict = Relation.from_dict(relation_dict)
    print(f"From dictionary: {relation_from_dict.type}, {relation_from_dict.source_concept_id} -> {relation_from_dict.target_concept_id}")


def test_concept_node():
    """Test the ConceptNode class."""
    print("\n=== Testing ConceptNode ===")
    
    # Create a concept
    concept = ConceptNode(
        id="cat",
        name="Cat",
        properties={
            "color": PropertyValue(value="various", confidence=0.9),
            "legs": PropertyValue(value="4", confidence=1.0)
        },
        aliases=["feline", "kitty"],
        categories=["mammal", "pet"]
    )
    
    print(f"Concept ID: {concept.get_id()}")
    print(f"Concept name: {concept.get_name()}")
    print(f"Properties: {concept.get_properties()}")
    print(f"Aliases: {concept.get_aliases()}")
    print(f"Categories: {concept.get_categories()}")
    
    # Add a property
    concept = concept.set_property("sound", PropertyValue(value="meow", confidence=1.0))
    print(f"Added property: {concept.get_property('sound')}")
    
    # Add a relation
    relation = Relation(
        id=str(uuid.uuid4()),
        type="is_a",
        source_concept_id="cat",
        target_concept_id="animal",
        properties={},
        bidirectional=False
    )
    concept = concept.add_relation(relation)
    print(f"Relations: {concept.get_relation_types()}")
    
    # Convert to dictionary and back
    concept_dict = concept.to_dict()
    print(f"Dictionary representation: {concept_dict}")
    concept_from_dict = ConceptNode.from_dict(concept_dict)
    print(f"From dictionary: {concept_from_dict.get_name()}, properties: {concept_from_dict.get_properties()}")


def test_uncertainty_handler():
    """Test the UncertaintyHandler class."""
    print("\n=== Testing UncertaintyHandler ===")
    
    # Create an uncertainty handler
    handler = UncertaintyHandler(confidence_threshold=0.7, conflict_threshold=0.3)
    
    # Test combining confidence scores
    scores = [0.8, 0.6, 0.9]
    combined = handler.combine_confidence_scores(scores)
    print(f"Combined confidence score: {combined}")
    
    # Test combining property values
    values = [
        PropertyValue(value="red", confidence=0.8),
        PropertyValue(value="blue", confidence=0.6),
        PropertyValue(value="red", confidence=0.7)
    ]
    combined_value = handler.combine_property_values(values)
    print(f"Combined property value: {combined_value.get_value()}, confidence: {combined_value.get_confidence()}")
    
    # Test conflict detection
    value1 = PropertyValue(value="red", confidence=0.8)
    value2 = PropertyValue(value="blue", confidence=0.7)
    in_conflict = handler.are_values_in_conflict(value1, value2)
    print(f"Values in conflict: {in_conflict}")
    
    # Test conflict resolution
    resolved = handler.resolve_conflict(value1, value2)
    print(f"Resolved value: {resolved.get_value()}, confidence: {resolved.get_confidence()}")


def test_semantic_similarity():
    """Test the SemanticSimilarity class."""
    print("\n=== Testing SemanticSimilarity ===")
    
    # Create a semantic similarity calculator
    similarity = SemanticSimilarity(embedding_dimension=256)
    
    # Test text similarity
    text1 = "cat"
    text2 = "dog"
    text3 = "feline"
    
    sim1 = similarity.text_similarity(text1, text2)
    sim2 = similarity.text_similarity(text1, text3)
    
    print(f"Similarity between '{text1}' and '{text2}': {sim1}")
    print(f"Similarity between '{text1}' and '{text3}': {sim2}")
    
    # Test concept similarity
    concept1 = ConceptNode(
        id="cat",
        name="Cat",
        properties={"legs": PropertyValue(value="4", confidence=1.0)},
        categories=["mammal", "pet"]
    )
    
    concept2 = ConceptNode(
        id="dog",
        name="Dog",
        properties={"legs": PropertyValue(value="4", confidence=1.0)},
        categories=["mammal", "pet"]
    )
    
    concept3 = ConceptNode(
        id="fish",
        name="Fish",
        properties={"legs": PropertyValue(value="0", confidence=1.0)},
        categories=["animal", "pet"]
    )
    
    sim1 = similarity.concept_similarity(concept1, concept2)
    sim2 = similarity.concept_similarity(concept1, concept3)
    
    print(f"Similarity between '{concept1.get_name()}' and '{concept2.get_name()}': {sim1}")
    print(f"Similarity between '{concept1.get_name()}' and '{concept3.get_name()}': {sim2}")


def test_self_organizing_structure():
    """Test the SelfOrganizingStructure class."""
    print("\n=== Testing SelfOrganizingStructure ===")
    
    # Create a semantic similarity calculator
    similarity = SemanticSimilarity(embedding_dimension=256)
    
    # Create a self-organizing structure
    structure = SelfOrganizingStructure(
        semantic_similarity=similarity,
        reorganization_threshold=0.5,
        max_cluster_size=10,
        min_cluster_size=2
    )
    
    # Create some concepts
    concepts = [
        ConceptNode(id="cat", name="Cat", categories=["mammal", "pet"]),
        ConceptNode(id="dog", name="Dog", categories=["mammal", "pet"]),
        ConceptNode(id="fish", name="Fish", categories=["animal", "pet"]),
        ConceptNode(id="bird", name="Bird", categories=["animal", "pet"]),
        ConceptNode(id="car", name="Car", categories=["vehicle"]),
        ConceptNode(id="truck", name="Truck", categories=["vehicle"]),
        ConceptNode(id="bike", name="Bike", categories=["vehicle"]),
        ConceptNode(id="apple", name="Apple", categories=["fruit"]),
        ConceptNode(id="banana", name="Banana", categories=["fruit"]),
        ConceptNode(id="orange", name="Orange", categories=["fruit"])
    ]
    
    # Initialize the structure
    structure.initialize(concepts)
    
    # Get the clusters
    clusters = structure.get_all_clusters()
    print(f"Number of clusters: {len(clusters)}")
    
    for i, cluster in enumerate(clusters):
        print(f"Cluster {i}: {cluster}")
    
    # Add a new concept
    concepts_by_id = {concept.get_id(): concept for concept in concepts}
    new_concept = ConceptNode(id="grape", name="Grape", categories=["fruit"])
    added_to_existing = structure.add_concept(new_concept, concepts_by_id)
    
    print(f"Added to existing cluster: {added_to_existing}")
    
    # Get the updated clusters
    clusters = structure.get_all_clusters()
    print(f"Number of clusters after adding: {len(clusters)}")
    
    for i, cluster in enumerate(clusters):
        print(f"Cluster {i}: {cluster}")


def test_knowledge_graph():
    """Test the KnowledgeGraph class."""
    print("\n=== Testing KnowledgeGraph ===")
    
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
    
    # Print the knowledge graph
    print(f"Number of concepts: {kg.get_concept_count()}")
    print(f"Number of relations: {kg.get_relation_count()}")
    print(f"Number of categories: {kg.get_category_count()}")
    
    # Get a concept by name
    cat_by_name = kg.get_concept_by_name("Cat")
    print(f"Got concept by name: {cat_by_name.get_name()}")
    
    # Get a concept by alias
    cat_by_alias = kg.get_concept_by_alias("feline")
    print(f"Got concept by alias: {cat_by_alias.get_name()}")
    
    # Get concepts by category
    pets = kg.get_concepts_by_category("pet")
    print(f"Got concepts by category 'pet': {[pet.get_name() for pet in pets]}")
    
    # Get related concepts
    related_to_cat = kg.get_related_concepts(cat.get_id())
    print(f"Concepts related to Cat: {[concept.get_name() for concept in related_to_cat]}")
    
    # Find similar concepts
    similar_to_cat = kg.find_similar_concepts("Cat", threshold=0.3)
    print(f"Concepts similar to Cat: {[(concept.get_name(), score) for concept, score in similar_to_cat]}")
    
    # Find path between concepts
    paths = kg.find_path_between_concepts(cat.get_id(), animal.get_id())
    print(f"Paths between Cat and Animal: {paths}")
    
    # Update a concept
    updated_cat = kg.update_concept(
        concept_id=cat.get_id(),
        properties={"color": "various", "legs": "4", "sound": "meow", "lifespan": "15 years"}
    )
    
    print(f"Updated Cat properties: {updated_cat.get_properties()}")
    
    # Reorganize the knowledge graph
    changes = kg.reorganize()
    print(f"Made {changes} changes during reorganization")
    
    # Save and load the knowledge graph
    kg.save_to_file("test_knowledge_graph.json")
    loaded_kg = KnowledgeGraph.load_from_file("test_knowledge_graph.json")
    
    if loaded_kg:
        print(f"Loaded knowledge graph with {loaded_kg.get_concept_count()} concepts")
    else:
        print("Failed to load knowledge graph")


def run_all_tests():
    """Run all tests."""
    test_property_value()
    test_relation()
    test_concept_node()
    test_uncertainty_handler()
    test_semantic_similarity()
    test_self_organizing_structure()
    test_knowledge_graph()


if __name__ == "__main__":
    run_all_tests()