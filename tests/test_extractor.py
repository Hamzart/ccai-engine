from pathlib import Path

import spacy
from ccai.core.graph import ConceptGraph
from ccai.nlp.extractor import InformationExtractor
from ccai.nlp.primitives import PrimitiveManager


def test_ingest_without_model(monkeypatch, tmp_path):
    def raise_oserror(name, *args, **kwargs):
        raise OSError("model missing")

    monkeypatch.setattr(spacy, "load", raise_oserror)

    graph = ConceptGraph(tmp_path)
    pm = PrimitiveManager(Path("primitives.json"))
    extractor = InformationExtractor(graph, pm)

    extractor.ingest_text("A knife is a tool.")

    assert graph.get_node("knife") is None
