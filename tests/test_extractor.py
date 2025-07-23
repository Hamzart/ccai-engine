from pathlib import Path

from ccai.core.graph import ConceptGraph
from ccai.nlp.extractor import InformationExtractor
from ccai.nlp.primitives import PrimitiveManager


def test_ingest_creates_nodes(tmp_path):
    graph = ConceptGraph(tmp_path)
    pm = PrimitiveManager(Path("primitives.json"))
    extractor = InformationExtractor(graph, pm)

    extractor.ingest_text("A knife is a tool.")

    assert graph.get_node("knife") is not None
    knife = graph.get_node("knife")
    assert "is_a" in knife.relations
