from pathlib import Path

from ccai.core.graph import ConceptGraph
from ccai.nlp.extractor import InformationExtractor
from ccai.nlp.primitives import PrimitiveManager
import pytest


@pytest.fixture
def extractor(tmp_path):
    """Create a fresh extractor with an empty graph for each test."""
    graph = ConceptGraph(tmp_path)
    pm = PrimitiveManager(Path("primitives.json"))
    return InformationExtractor(graph, pm), graph


def test_ingest_creates_nodes(extractor):
    ext, graph = extractor
    ext.ingest_text("A knife is a tool.")

    assert graph.get_node("knife") is not None
    knife = graph.get_node("knife")
    assert "is_a" in knife.relations
    assert "tool" in knife.relations["is_a"]


def test_extract_alias(extractor):
    ext, graph = extractor
    ext.ingest_text("A car is called automobile.")

    car = graph.get_node("car")
    assert car is not None
    assert "automobile" in car.aliases
    # Alias lookup should also return the original node
    auto = graph.get_node("automobile")
    assert auto is car


def test_extract_has_part(extractor):
    ext, graph = extractor
    ext.ingest_text("A car has wheels.")

    car = graph.get_node("car")
    assert car is not None
    assert "has_part" in car.relations
    assert "wheels" in car.relations["has_part"]


def test_extract_used_for(extractor):
    ext, graph = extractor
    ext.ingest_text("A knife is used for cutting.")

    knife = graph.get_node("knife")
    assert knife is not None
    assert "used_for" in knife.relations
    assert "cutting" in knife.relations["used_for"]


def test_extract_can_do(extractor):
    ext, graph = extractor
    ext.ingest_text("A bird can fly.")

    bird = graph.get_node("bird")
    assert bird is not None
    assert "can_do" in bird.relations
    assert "fly" in bird.relations["can_do"]


def test_extract_agent_action_object(extractor):
    ext, graph = extractor
    ext.ingest_text("The cat chases the mouse.")

    # Check agent-action relationship
    cat = graph.get_node("cat")
    assert cat is not None
    assert "performs" in cat.relations
    assert "chase" in cat.relations["performs"]
    
    # Check action-object relationship
    chase = graph.get_node("chase")
    assert chase is not None
    assert "affects" in chase.relations
    assert "mouse" in chase.relations["affects"]


def test_multiple_extractions(extractor):
    ext, graph = extractor
    ext.ingest_text("""
    A dog is an animal.
    Dogs have fur.
    Dogs can bark.
    A dog chases the cat.
    Dogs are used for companionship.
    """)

    dog = graph.get_node("dog")
    assert dog is not None
    assert "is_a" in dog.relations
    assert "animal" in dog.relations["is_a"]
    assert "has_part" in dog.relations
    assert "fur" in dog.relations["has_part"]
    assert "can_do" in dog.relations
    assert "bark" in dog.relations["can_do"]
    assert "performs" in dog.relations
    assert "chase" in dog.relations["performs"]
    assert "used_for" in dog.relations
    assert "companionship" in dog.relations["used_for"]
